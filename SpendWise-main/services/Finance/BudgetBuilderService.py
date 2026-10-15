class BudgetBuilderService:
    """
    שלב 11 — בניית תוכנית תקציבית לחודש הבא.

    שירות טהור — ללא גישה ל-DB.
    מקבל תוצאות מחושבות מראש ומארגן אותן לתכנית חודשית מלאה.

    Pipeline:
        CutRankingService.rank_categories()              → ranking[]
        CutAllocationService.calculate_total_cut_needed() → total_cut
        CutAllocationService.allocate_cuts()              → allocation[]
        BudgetBuilderService.build_next_month_budget()    → תוכנית חודשית ← אתה כאן
    """

    # =========================
    # MAIN API
    # =========================
    def build_next_month_budget(self, ranking, allocation, net_budget, total_cut_needed):
        """
        בונה תוכנית תקציבית לחודש הבא.

        Args:
            ranking: list[dict]  — פלט CutRankingService.rank_categories()
            allocation: list[dict] — פלט CutAllocationService.allocate_cuts()
            net_budget: dict | float — פלט BudgetService.calculate_net_budget()
            total_cut_needed: float — יעד הקיצוץ הכולל

        Returns:
            dict עם תוכנית חודשית מלאה
        """

        base_income = self._extract_net_budget(net_budget)

        alloc_map = {
            item["category_id"]: item
            for item in allocation
        }

        budget = []
        missing_allocation_names = []

        # =========================
        # בניית תקציב בסיסי + pain
        # =========================
        for item in ranking:

            cid = item["category_id"]
            alloc = alloc_map.get(cid)

            if alloc is None:
                missing_allocation_names.append(item["category_name"])
                cut_amount = 0
                effective_pct = 0
            else:
                cut_amount = alloc.get("cut_amount", 0)
                effective_pct = alloc.get("effective_pct", 0)

            planned = max(0, item["current_amount"] - cut_amount)

            budget.append({
                "category_id": cid,
                "category_name": item["category_name"],
                "current_amount": item["current_amount"],
                "planned_amount": round(planned, 2),
                "cut_amount": round(cut_amount, 2),
                "cut_percent": effective_pct,
                "is_essential": item.get("is_essential", False),
                "is_fixed_cost": item.get("is_fixed_cost", False),
                "pain_level": self._calc_pain_level(item, alloc),
                "status": self._calc_status(item, cut_amount),
                "note": self._build_note(item, cut_amount, effective_pct),
            })

        total_spending = sum(b["planned_amount"] for b in budget)
        monthly_limit = max(0, base_income - total_cut_needed)

        # =========================
        # IMPOSSIBLE — הוצאות עולות על הכנסה
        # =========================
        if total_spending > base_income:
            return {
                "net_budget": base_income,
                "total_cut_needed": total_cut_needed,
                "monthly_limit": round(monthly_limit, 2),
                "planned_spending": round(total_spending, 2),
                "actual_cut": 0,
                "remaining_balance": round(base_income - total_spending, 2),
                "remaining_deficit": total_cut_needed,
                "budget_health_score": round(
                    self._calc_health_score(base_income, total_spending, monthly_limit), 2
                ),
                "status": "IMPOSSIBLE_BUDGET",
                "message": "לא ניתן לאזן תקציב — ההוצאות עולות על ההכנסה גם אחרי קיצוץ",
                "budget": budget,
                "warnings": self._build_warnings(missing_allocation_names, monthly_limit),
            }

        # =========================
        # תיקון חכם אם יש חריגה
        # =========================
        if total_spending > monthly_limit:

            deficit = total_spending - monthly_limit

            for b in sorted(budget, key=lambda x: x["pain_level"]):

                if deficit <= 0:
                    break

                if b["pain_level"] >= 8:
                    continue

                max_extra_pct = 0.2 if b["pain_level"] <= 3 else 0.1

                extra_cut = min(
                    b["planned_amount"] * max_extra_pct,
                    deficit
                )

                b["planned_amount"] -= extra_cut
                b["cut_amount"] += extra_cut
                b["planned_amount"] = round(b["planned_amount"], 2)
                b["cut_amount"] = round(b["cut_amount"], 2)
                deficit -= extra_cut

        total_spending = sum(b["planned_amount"] for b in budget)
        actual_cut = sum(b["cut_amount"] for b in budget)
        health_score = self._calc_health_score(base_income, total_spending, monthly_limit)
        warnings = self._build_warnings(missing_allocation_names, monthly_limit)

        return {
            "net_budget": base_income,
            "total_cut_needed": total_cut_needed,
            "monthly_limit": round(monthly_limit, 2),
            "planned_spending": round(total_spending, 2),
            "actual_cut": round(actual_cut, 2),
            "remaining_balance": round(base_income - total_spending, 2),
            "remaining_deficit": round(max(0, total_cut_needed - actual_cut), 2),
            "budget_health_score": round(health_score, 2),
            "status": self._calc_overall_status(total_spending, base_income, monthly_limit),
            "budget": budget,
            "warnings": warnings,
        }

    # =========================
    # PAIN ENGINE
    # =========================
    def _calc_pain_level(self, item, alloc):
        """
        מחשב עד כמה הקיצוץ "כואב" — 0 (לא כואב) עד 10 (בלתי אפשרי).

        מרכיבים:
            is_essential          → +4
            is_fixed_cost         → 10 (קיר — לא נוגעים)
            effective_pct > 30%   → +3
            effective_pct > 15%   → +1
            importance_score > 70 → +3
            importance_score > 40 → +1

        כש-allocation חסר — משתמש ב-recommended_cut_pct מה-ranking.
        """

        pain = 0

        if item.get("is_essential"):
            pain += 4

        if item.get("is_fixed_cost"):
            return 10

        # effective_pct: מ-allocation אם קיים, אחרת recommended_cut_pct מה-ranking
        if alloc:
            cut_pct = alloc.get("effective_pct", 0)
        else:
            cut_pct = item.get("recommended_cut_pct", 0)

        if cut_pct > 30:
            pain += 3
        elif cut_pct > 15:
            pain += 1

        importance = item.get("importance_score", 50)

        if importance > 70:
            pain += 3
        elif importance > 40:
            pain += 1

        return min(pain, 10)

    # =========================
    # STATUS
    # =========================
    def _calc_status(self, item, cut_amount):
        """
        קובע סטטוס לכל קטגוריה:
            protected  — קבועה, לא ניתנת לקיצוץ
            reduced    — קוצצה
            unchanged  — לא קוצצה
        """

        if item.get("is_fixed_cost"):
            return "protected"

        if cut_amount > 0:
            return "reduced"

        return "unchanged"

    def _calc_overall_status(self, total_spending, base_income, monthly_limit):
        """
        סטטוס כללי של התוכנית.
        """

        if total_spending > base_income:
            return "IMPOSSIBLE_BUDGET"

        if total_spending > monthly_limit:
            return "LIMIT_EXCEEDED"

        return "OK"

    # =========================
    # HEALTH SCORE
    # =========================
    def _calc_health_score(self, base_income, total_spending, monthly_limit=0):
        """
        ציון בריאות תקציבית:
            > 0.2   → בריא
            0–0.2   → גבולי
            0       → מתוח
            < 0     → סיכון
            -0.5    → חמור (monthly_limit = 0)

        כש-monthly_limit אפס — זה מצב חמור במיוחד, הציון מוגבל ל-≤ -0.5.
        """

        if base_income <= 0:
            return 0

        score = (base_income - total_spending) / base_income

        if monthly_limit <= 0:
            score = min(score, -0.5)

        return score

    # =========================
    # NOTE — הסבר טקסטואלי
    # =========================
    def _build_note(self, item, cut_amount, effective_pct):
        """
        בונה טקסט הסבר בעברית לכל קטגוריה.
        """

        status = self._calc_status(item, cut_amount)

        if status == "protected":
            if item.get("is_fixed_cost"):
                return "הוצאה קבועה — לא ניתנת לקיצוץ"
            return "קטגוריה חיונית — נשמרה ללא קיצוץ"

        if status == "reduced":
            if item.get("is_essential"):
                return (
                    f"קוצץ ב-{effective_pct}% ({int(cut_amount)}₪) — "
                    f"חיוני, קיצוץ מוגבל"
                )
            return f"קוצץ ב-{effective_pct}% ({int(cut_amount)}₪)"

        # unchanged — אבל allocation כן היה קיים
        if effective_pct == 0 and cut_amount == 0:
            return "הוקצה 0% קיצוץ — הקטגוריה נותרה ללא שינוי"

        return "ללא שינוי"

    # =========================
    # WARNINGS
    # =========================
    def _build_warnings(self, missing_allocation_names, monthly_limit):
        """
        אוסף התראות על בעיות שזוהו.
        """

        warnings = []

        if missing_allocation_names:
            names = ", ".join(missing_allocation_names)
            warnings.append(
                f"אזהרה: {len(missing_allocation_names)} קטגוריות חסרות בנתוני הקיצוץ "
                f"({names}) — הוקצה 0% קיצוץ"
            )

        if monthly_limit <= 0:
            warnings.append(
                "אזהרה חמורה: יעד הקיצוץ גבוה או שווה להכנסה הפנויה — "
                "לא נותר תקציב פנוי לחודש"
            )

        return warnings if warnings else None

    # =========================
    # NET BUDGET SAFE EXTRACT
    # =========================
    def _extract_net_budget(self, net_budget):
        """
        מחלץ net_budget — תומך גם ב-dict (כפי שמגיע מ-BudgetService)
        וגם ב-float (לנוחות בדיקות).
        """

        if isinstance(net_budget, dict):
            return net_budget.get("net_budget", 0)

        return float(net_budget)