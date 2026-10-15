class BudgetPlanService:
    """
    Business logic for the full budget plan pipeline.
    """

    def __init__(
            self,
            budget_service,
            cut_ranking_service,
            cut_allocation_service,
            builder_service,
            recommendation_service,
            early_warning_service,
            budget_plan_repository,
            financial_health_service=None,
            user_repository=None
    ):
        self.budget_service = budget_service
        self.cut_ranking_service = cut_ranking_service
        self.cut_allocation_service = cut_allocation_service
        self.builder_service = builder_service
        self.recommendation_service = recommendation_service
        self.early_warning_service = early_warning_service  # <-- חדש
        self.budget_plan_repository = budget_plan_repository
        self.financial_health_service = financial_health_service
        self.user_repository = user_repository
    def build_plan(self, user_id, year, month):

        # =========================
        # STEP 1 — NET BUDGET
        # =========================
        net_budget = self.budget_service.calculate_net_budget(user_id, year, month)

        # =========================
        # STEP 2 — RANKING
        # =========================
        ranking_result = self.cut_ranking_service.rank_categories(user_id, year, month)

        ranking = (
            ranking_result.get("ranking", [])
            if isinstance(ranking_result, dict)
            else ranking_result
        )

        # VALIDATION
        ranking = [
            r for r in ranking
            if isinstance(r, dict)
            and "current_amount" in r
            and "recommended_cut_pct" in r
            and "category_id" in r
        ]

        # =========================
        # STEP 3 — TOTAL CUT
        # =========================
        stress_score = 50
        if self.financial_health_service:
            try:
                health_result = self.financial_health_service.calculate_financial_score(user_id, year, month)
                stress_score = health_result.get("ציון", stress_score)
            except Exception:
                pass

        user = self.user_repository.get_by_id(user_id) if self.user_repository else None
        family_size = getattr(user, "family_size", 1) or 1

        total_cut = self.cut_allocation_service.calculate_total_cut_needed(
            ranking=ranking,
            net_budget=net_budget,
            stress_score=stress_score,
            user_id=user_id,
            family_size=family_size,
            year=year,
            month=month
        )

        # =========================
        # STEP 4 — ALLOCATION
        # =========================
        allocation = self.cut_allocation_service.allocate_cuts(
            ranking=ranking,
            total_cut=total_cut
        )

        if isinstance(allocation, dict):
            allocation = allocation.get("allocation", [])

        # VALIDATION
        allocation = [
            a for a in allocation
            if isinstance(a, dict)
            and "category_id" in a
            and "cut_amount" in a
        ]

        # =========================
        # STEP 5 — BUILD PLAN
        # =========================
        plan = self.builder_service.build_next_month_budget(
            ranking=ranking,
            allocation=allocation,
            net_budget=net_budget,
            total_cut_needed=total_cut
        )

        # =========================
        # STEP 5.5 — SAVE PLAN TO DB
        # =========================
        self.budget_plan_repository.save_plan_for_month(
            user_id, year, month, plan
        )

        # =========================
        # STEP 6 —  TEXT LAYER
        # =========================
        health = self._calc_health(plan)

        plan["health_score"] = health
        # save_plan הוסר — אין כרגע טבלת Budget_Plans.
        # Early Warning (שלב 8) כותב ל-EarlyWarning_Alerts.

        # =========================
        # STEP 7 —HEALTH
        #         SCORE(FIXED)

        # =========================
        text = self.recommendation_service.generate(plan)


        # =========================
        # STEP 8 — EARLY WARNING
        # =========================
        early_warning = self.early_warning_service.check_spending_vs_budget(
            user_id, year, month, plan
        )

        # =========================
        # RESPONSE
        # =========================
        remaining_gap = round(
            max(0, plan.get("total_cut_needed", 0) - plan.get("actual_cut", 0)),
            2
        )

        return {
            "net_budget": plan.get("net_budget"),
            "total_cut_needed": plan.get("total_cut_needed"),
            "monthly_limit": plan.get("monthly_limit"),
            "planned_spending": plan.get("planned_spending"),
            "actual_cut": plan.get("actual_cut"),
            "remaining_gap": remaining_gap,
            "budget": plan.get("budget", []),
            "health_score": self._calc_health(plan),
            "headline": text.get("headline", ""),
            "sections": text.get("sections", []),
            "raw_messages": text.get("raw_messages", []),
            "early_warning": early_warning,
        }

    # =========================
    # HEALTH SCORE (ROBUST)
    # =========================
    def _calc_health(self, plan):

        income = plan.get("net_budget", 0)
        spending = plan.get("planned_spending", 0)

        if income <= 0:
            return -1

        base = (income - spending) / income

        # penalty על חריגה אמיתית
        if spending > income:
            base -= 0.3

        return round(max(-1, min(base, 1)), 2)