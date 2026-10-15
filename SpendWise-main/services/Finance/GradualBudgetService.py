"""
GradualBudgetService — 6-month gradual budget system with learning.

Heart of the system:
- Month 1: learning mode (observe only, no cuts)
- Months 2-6: gradual reduction based on behavior patterns
- Smart transfers: unused budget → overspent categories
- Personalization: user preferences + behavior history
"""
from datetime import date
from sqlalchemy import extract, func
from models.Finance.Expenses import Expense


class GradualBudgetService:

    def __init__(
        self,
        session,
        budget_service,
        monthly_analysis_service,
        behavior_stress_service,
        category_behavior_service,
        holiday_adjustment_service,
        special_period_service,
        budget_plan_repository,
        user_goal_repo,
        preference_repo,
        standard_repo,
    ):
        self.session = session
        self.budget_service = budget_service
        self.monthly_analysis_service = monthly_analysis_service
        self.behavior_stress_service = behavior_stress_service
        self.category_behavior_service = category_behavior_service
        self.holiday_adjustment_service = holiday_adjustment_service
        self.special_period_service = special_period_service
        self.budget_plan_repository = budget_plan_repository
        self.user_goal_repo = user_goal_repo
        self.preference_repo = preference_repo
        self.standard_repo = standard_repo

    # ==================================================================
    # PUBLIC API
    # ==================================================================
    def build_plan(self, user_id, year, month):
        """
        Builds a gradual monthly budget plan with learning.

        Program timeline (6 months):
          Month 1 — learning (observe only, no cuts)
          Months 2–6 — gradual (increasing reduction pace)
          Month 7+ — maintenance (use targets, no reductions)
        """

        # =========================
        # STEP 1 — Basic info & program phase
        # =========================
        from models.core.Users import User
        user = self.session.query(User).filter_by(user_id=user_id).first()
        family_size = user.family_size if user else 1
        join_date = user.join_date if user else date.today()

        # Program phase: count how many months of Budget_Plans exist for this user
        # Each month with a plan = one program month (max 6)
        program_month = self._count_program_months(user_id)
        # program_month: 0 (no plans yet) → about to start month 1 (learning)
        #                1..5 → month 2..6 (gradual)
        #                6+ → completed

        MAX_PROGRAM_MONTHS = 6
        if program_month < 1:
            # First plan ever — learning mode
            learning_mode = True
            completed = False
        elif program_month < MAX_PROGRAM_MONTHS:
            # Month 2–6 — gradual mode
            learning_mode = False
            completed = False
        else:
            # Month 7+ — program completed, maintenance mode
            learning_mode = False
            completed = True

        # The month we're about to build (1-indexed)
        current_program_month = program_month + 1
        months_active = program_month  # backwards-compatible

        # =========================
        # STEP 2 — Net budget
        # =========================
        net_data = self.budget_service.calculate_net_budget(user_id, year, month)
        base_income = net_data.get("net_budget", 0) if isinstance(net_data, dict) else float(net_data)

        # =========================
        # STEP 2.5 — Overall behavior stress (0–100)
        # =========================
        stress_result = self.behavior_stress_service.calculate_behavior_stress(user_id, year, month)
        overall_stress = stress_result.get("behavior_stress", 50) if isinstance(stress_result, dict) else 50

        # =========================
        # STEP 3 — Spending history (last 3 months)
        # =========================
        history = self._get_spending_history(user_id, year, month, months=3)

        # =========================
        # STEP 4 — Ideal targets
        # =========================
        targets = self.user_goal_repo.get_targets_map(user_id)

        # =========================
        # STEP 5 — Trends & behavior
        # =========================
        analysis = self.monthly_analysis_service.calculate_category_analysis(user_id, year, month)
        analysis_map = {
            c["category_id"]: {
                "monthly_change": c.get("monthly_change_percent", 0),
                "long_term_change": c.get("long_term_change_percent", 0),
            }
            for c in analysis.get("categories", [])
        }

        # =========================
        # STEP 6 — User preferences
        # =========================
        prefs = self.preference_repo.get_by_user(user_id)
        pref_map = {}
        for p in prefs:
            score = p.importance_score
            if score > 1:
                score = score / 100.0
            pref_map[p.category_id] = max(0.0, min(1.0, score))

        # =========================
        # STEP 7 — Category standards
        # =========================
        standards = self.standard_repo.get_all()
        std_map = {
            s.category_id: {
                "is_essential": s.is_essential,
                "is_fixed_cost": s.is_fixed_cost,
                "max_cut_percent": s.max_cut_percent / 100.0 if s.max_cut_percent and s.max_cut_percent > 1 else (s.max_cut_percent or 1.0),
            }
            for s in standards
        }

        # =========================
        # STEP 8 — Holiday check
        # =========================
        period, holiday_ratios = self.special_period_service.resolve_period_ratios(year, month)
        holiday_name = period.holiday_name if period else None

        # =========================
        # STEP 9 — Category names
        # =========================
        from models.core.Categories import Category
        cat_rows = self.session.query(Category).all()
        cat_names = {c.category_id: c.category_name for c in cat_rows}

        # =========================
        # STEP 10 — LEARN FROM HISTORY
        # =========================
        # Analyze the last 3 months per category to understand user behavior.
        # current = last month's spending (history[-1])
        last_month = history[-1] if history else {}
        current_map = {k: v["actual"] for k, v in last_month.items()}

        # Build per-category behavior profile from history
        behavior_profile = self._analyze_history(history, targets, std_map)

        # =========================
        # STEP 11 — LEARNING MODE (month 1)
        # =========================
        if months_active < 1:
            learning_mode = True
        else:
            learning_mode = False

        # =========================
        # STEP 12 — SMART TRANSFERS
        # =========================
        # Find permanently underspent categories → available funds
        # Find permanently overspent categories → need funds
        # Transfer unused budget from underspent to overspent (non-fixed only)
        transfers = []
        if not learning_mode:
            transfers = self._calculate_transfers(behavior_profile, std_map)

        # =========================
        # STEP 12.5 — ADD TARGET CATEGORIES WITH NO SPENDING
        # If User_Category_Goal has a target but no recent spending,
        # still include it — user might need it.
        # =========================
        all_relevant_cids = set(behavior_profile.keys()) | set(targets.keys())
        for cid in targets:
            if cid not in behavior_profile and targets[cid] > 0:
                behavior_profile[cid] = {
                    "avg_spending": targets[cid],
                    "avg_planned": targets[cid],
                    "underspent_pct": 0,
                    "overspent_pct": 0,
                    "target": targets[cid],
                    "is_essential": (std_map.get(cid, {}).get("is_essential", False)),
                    "is_fixed_cost": (std_map.get(cid, {}).get("is_fixed_cost", False)),
                }
                current_map[cid] = targets[cid]

        # =========================
        # STEP 13 — THE CALCULATION (per category)
        # =========================
        budget_items = []
        total_planned = 0

        for cid in all_relevant_cids:
            profile = behavior_profile.get(cid)
            if not profile:
                continue
            current = current_map.get(cid, profile["avg_spending"])
            target = targets.get(cid, current)
            ana = analysis_map.get(cid, {})
            monthly_change = ana.get("monthly_change", 0)
            long_term_change = ana.get("long_term_change", 0)
            importance = pref_map.get(cid, 0.5)
            std = std_map.get(cid, {})
            is_essential = std.get("is_essential", False)
            is_fixed_cost = std.get("is_fixed_cost", False)
            max_cut_pct = std.get("max_cut_percent", 1.0)
            ratio = holiday_ratios.get(cid, 0)
            name = cat_names.get(cid, f"cat {cid}")
            profile_underspent_pct = profile.get("underspent_pct", 0)
            profile_overspent_pct = profile.get("overspent_pct", 0)

            # ── gap ──
            gap = current - target

            # ── LEARNING MODE: no reduction ──
            if learning_mode:
                reduction = 0
                reduction_pct = 0
                planned = current
                status = "learning"
                months_to_target = 0

            elif completed:
                # ── MAINTENANCE MODE: program completed, use targets ──
                reduction = 0
                reduction_pct = 0
                planned = target
                months_to_target = 0
                if gap <= 0:
                    status = "on_target"
                else:
                    status = "maintenance"
                # Still apply holiday adjustment
                if ratio > 0:
                    planned = round(planned * (1 + ratio), 2)

            else:
                # ── months remaining (tied to actual program) ──
                # remaining_months = 6 - current_program_month + 1
                # Month 2 (first gradual): 5 months left → slower pace
                # Month 6 (last gradual): 1 month left → aggressive pace
                remaining_program_months = max(1, MAX_PROGRAM_MONTHS - current_program_month + 1)

                # ── PROGRAM URGENCY MULTIPLIER ──
                # As we approach month 6, cuts become more aggressive:
                # Month 2: ×1.00 | Month 3: ×1.12 | Month 4: ×1.25
                # Month 5: ×1.37 | Month 6: ×1.50
                urgency_mult = 1.0 + (current_program_month - 2) * 0.125
                urgency_mult = max(1.0, min(1.5, urgency_mult))

                if gap <= 0:
                    months_remaining = 1
                else:
                    months_remaining = remaining_program_months

                # ── reduction ──
                if gap <= 0:
                    reduction = 0
                    reduction_pct = 0
                else:
                    # Base reduction: spread the gap over remaining months
                    base_pct = (gap / current) / months_remaining
                    # Allow wider range: 1%–10% (instead of old 1%–5%)
                    # With urgency, the effective max becomes ~15%
                    base_pct = max(0.01, min(0.10, base_pct))
                    reduction = current * base_pct

                    # === PROGRAM URGENCY — increase cut as deadline approaches ===
                    reduction *= urgency_mult

                    # === BEHAVIOR ADJUSTMENT ===
                    # Only apply if we have enough history (at least 2 months of data).
                    # When monthly_change=0 and long_term_change=0 (no history),
                    # the behavior score would be artificially low (~15), causing
                    # the system to ease up on categories it knows nothing about.
                    has_enough_history = (
                        abs(monthly_change) > 0.01 or abs(long_term_change) > 0.01
                    )
                    if has_enough_history:
                        behavior_score = self.category_behavior_service.calculate_category_behavior(
                            monthly_change, long_term_change, is_essential
                        )
                        if behavior_score < 30:
                            reduction *= 0.7  # improving — go easier
                        elif behavior_score > 60:
                            pass  # worsening — stay the course

                    # === OVERALL STRESS — higher stress = more aggressive ===
                    stress_mult = 1.0 + (overall_stress - 50) / 100
                    stress_mult = max(0.7, min(1.5, stress_mult))
                    reduction *= stress_mult

                    # === CONSISTENTLY OVERSPENT — don't cut too hard ===
                    if profile_overspent_pct > 0.6:
                        reduction *= 0.5

                    # === CONSISTENTLY UNDERSPENT — can cut more ===
                    if profile_underspent_pct > 0.6:
                        reduction *= 1.3

                    # === IMPORTANCE ===
                    reduction *= (1 - importance * 0.5)

                    # === ESSENTIAL ===
                    if is_essential:
                        reduction *= 0.5

                    # === FIXED COST ===
                    if is_fixed_cost:
                        reduction = 0

                    # === DYNAMIC CAP ===
                    # Floor: minimum 10₪ if there's a real gap
                    # Ceiling: max of current × 0.15 or gap / 2 (whichever smaller)
                    # (raised from 0.10 to 0.15 to allow more aggressive cuts)
                    if reduction > 0 and gap > 0:
                        reduction = max(reduction, min(10, gap))
                        ceiling = min(current * 0.15, gap / 2)
                        reduction = min(reduction, ceiling)

                    # === MAX CUT CAP (from standards) ===
                    reduction = min(reduction, current * max_cut_pct)
                    reduction_pct = round((reduction / current) * 100, 1) if current > 0 else 0

                # ── planned ──
                planned = max(target, current - reduction)

                # ── SMART TRANSFER: apply incoming/outgoing ──
                tf = transfers.get(cid, None)
                if tf:
                    planned += tf["amount"]
                    planned = round(planned, 2)

                # ── holiday ──
                if ratio > 0:
                    planned = round(planned * (1 + ratio), 2)

                # ── status ──
                if gap <= 0:
                    status = "on_target"
                elif profile_overspent_pct > 0.6:
                    status = "persistent_overspend"
                elif profile_underspent_pct > 0.6:
                    status = "underused"
                elif reduction > 0:
                    status = "reducing"
                elif reduction == 0 and is_fixed_cost:
                    status = "protected"
                else:
                    status = "unchanged"

                months_to_target = months_remaining if gap > 0 else 0

            item = {
                "category_id": cid,
                "category_name": name,
                "current_amount": round(current, 2),
                "target_amount": round(target, 2),
                "planned_amount": round(planned, 2),
                "reduction": round(reduction, 2),
                "reduction_pct": reduction_pct,
                "gap": round(gap, 2),
                "months_to_target": months_to_target,
                "is_essential": is_essential,
                "is_fixed_cost": is_fixed_cost,
                "importance": round(importance, 2),
                "status": status,
            }
            budget_items.append(item)
            total_planned += item["planned_amount"]

        # =========================
        # STEP 14 — Smart correction
        # =========================
        warnings = []
        monthly_limit = base_income

        if total_planned > monthly_limit and budget_items and not learning_mode:
            deficit = total_planned - monthly_limit

            def pain(item):
                if item["is_fixed_cost"]:
                    return 10
                if item["is_essential"]:
                    return 5
                return 1

            # ── Phase 1: Targeted cuts per category ──
            # Non-fixed, non-essential: up to 30%
            # Essential (non-fixed): up to 15%
            for b in sorted(budget_items, key=lambda x: (pain(x), x["reduction_pct"])):
                if deficit <= 0:
                    break
                if pain(b) >= 10:   # fixed cost — never touch
                    continue
                if pain(b) >= 5:    # essential
                    max_extra_pct = 0.15
                else:               # flexible
                    max_extra_pct = 0.30
                extra_cut = min(b["planned_amount"] * max_extra_pct, deficit)
                if extra_cut <= 0:
                    continue
                b["planned_amount"] = round(b["planned_amount"] - extra_cut, 2)
                b["reduction"] = round(b["reduction"] + extra_cut, 2)
                deficit -= extra_cut
            total_planned = sum(b["planned_amount"] for b in budget_items)

            # ── Phase 2: Proportional scaling on all non-fixed ──
            if total_planned > monthly_limit:
                flexible_items = [b for b in budget_items if not b["is_fixed_cost"]]
                flexible_total = sum(b["planned_amount"] for b in flexible_items)
                fixed_total = sum(b["planned_amount"] for b in budget_items if b["is_fixed_cost"])

                if flexible_total > 0 and monthly_limit > fixed_total:
                    target_flexible = monthly_limit - fixed_total
                    scale = target_flexible / flexible_total
                    total_cut_this_phase = flexible_total - target_flexible

                    # Track how much was already cut per category, to know
                    # if this additional scaling is "severe" for the user.
                    already_cut_on_flexible = sum(
                        b["current_amount"] - b["planned_amount"]
                        for b in flexible_items
                        if b.get("current_amount", 0) > b["planned_amount"]
                    )
                    additional_cut = max(0, total_cut_this_phase - already_cut_on_flexible)
                    additional_pct = (additional_cut / flexible_total) * 100 if flexible_total > 0 else 0

                    # Apply the scaling silently
                    for b in flexible_items:
                        old_planned = b["planned_amount"]
                        b["planned_amount"] = round(b["planned_amount"] * scale, 2)
                        b["reduction"] = round(b["reduction"] + (old_planned - b["planned_amount"]), 2)
                        current_amt = b.get("current_amount", old_planned)
                        if current_amt > 0:
                            b["reduction_pct"] = round((b["reduction"] / current_amt) * 100, 1)

                    total_planned = sum(b["planned_amount"] for b in budget_items)

                    # Only warn if the additional cut is extreme (> 25% extra
                    # on top of what was already cut). If it's manageable,
                    # just handle it silently.
                    if additional_pct > 25:
                        warnings.append(
                            "גם לאחר קיצוץ ממוקד בכל קטגוריה, התקציב עדיין חורג "
                            "ב-{:,.0f}₪. נדרש קיצוץ נוסף של {:.0f}% בכל הקטגוריות הגמישות — "
                            "זה קיצוץ משמעותי. שקול להגדיל הכנסה או לבדוק הוצאות קבועות."
                            .format(total_cut_this_phase, additional_pct)
                        )

                elif monthly_limit <= fixed_total:
                    # Fixed costs alone exceed income
                    warnings.append(
                        "ההוצאות הקבועות ({:,.0f}₪) עולות על ההכנסה הפנויה ({:,.0f}₪). "
                        "יש להגדיל הכנסה."
                        .format(fixed_total, monthly_limit)
                    )

            # After all correction — still over budget?
            if total_planned > monthly_limit:
                warnings.append(
                    "לא ניתן לאזן את התקציב — סך ההוצאות המתוכננות "
                    "({:,.0f}₪) עדיין גבוה מההכנסה הפנויה ({:,.0f}₪)"
                    .format(total_planned, monthly_limit)
                )

        # ── Warnings: missing history ──
        no_history = [
            b["category_name"]
            for b in budget_items
            if b.get("status") != "learning"
            and b["category_id"] not in [
                cid for cid, p in behavior_profile.items()
                if p["avg_spending"] > 0 or p["avg_planned"] > 0
            ]
        ]
        if no_history:
            warnings.append(
                f"אין היסטוריית הוצאות ל-{len(no_history)} קטגוריות "
                f"({', '.join(no_history[:5])}{'...' if len(no_history) > 5 else ''}) — "
                f"התקציב מבוסס על יעד בלבד"
            )

        # ── Warnings: zero monthly limit ──
        if monthly_limit <= 0:
            warnings.append(
                "אזהרה חמורה: ההכנסה הפנויה היא אפס או שלילית — לא ניתן לבנות תקציב מאוזן"
            )

        # =========================
        # STEP 15 — Save plan
        # =========================
        plan_to_save = {
            "budget": budget_items,
            "planned_spending": round(total_planned, 2),
            "total_cut_needed": 0,
            "actual_cut": 0,
            "net_budget": base_income,
            "monthly_limit": round(monthly_limit, 2),
        }
        self.budget_plan_repository.save_plan_for_month(user_id, year, month, plan_to_save)

        # =========================
        # STEP 16 — Holiday info
        # =========================
        holiday_info = None
        if holiday_name:
            holiday_info = {
                "name": holiday_name,
                "start_date": period.start_date.isoformat() if period and period.start_date else None,
                "end_date": period.end_date.isoformat() if period and period.end_date else None,
                "ratios": holiday_ratios,
            }

        # =========================
        # Overall status
        # =========================
        if total_planned > base_income:
            overall_status = "IMPOSSIBLE_BUDGET"
            if not warnings:
                warnings.append(
                    "לא ניתן לאזן תקציב — ההוצאות המתוכננות "
                    f"({total_planned:,.0f}₪) עולות על ההכנסה הפנויה ({base_income:,.0f}₪)"
                )
        elif monthly_limit <= 0:
            overall_status = "CRITICAL"
        elif base_income > 0 and (base_income - total_planned) / base_income > 0.15:
            overall_status = "HEALTHY"
        elif base_income > 0 and (base_income - total_planned) / base_income > 0:
            overall_status = "TIGHT"
        else:
            overall_status = "BALANCED"

        # =========================
        # RETURN
        # =========================
        # Determine mode string
        if learning_mode:
            mode_str = "learning"
        elif completed:
            mode_str = "maintenance"
        else:
            mode_str = "gradual"

        return {
            "year": year,
            "month": month,
            "mode": mode_str,
            "status": overall_status,
            "net_budget": base_income,
            "monthly_limit": round(monthly_limit, 2),
            "planned_spending": round(total_planned, 2),
            "saved_this_month": round(max(0, base_income - total_planned), 2),
            "months_active": months_active,  # backwards-compatible
            "program_phase": mode_str,
            "program_month": current_program_month,
            "holiday": holiday_info,
            "budget": budget_items,
            "warnings": warnings or None,
        }

    # ==================================================================
    # PROGRAM SUMMARY — Before/After Report
    # ==================================================================
    def generate_program_summary(self, user_id):
        """
        Generates a before/after comparison report for a completed program.
        Compares month 1 (learning) vs the last gradual month (month 6).

        Returns a dict with:
        - before/after comparison per category
        - total savings
        - most improved categories
        - categories needing attention
        - monthly progression
        - Hebrew overall verdict
        """
        from models.Finance.BudgetPlan import BudgetPlan
        from models.core.Categories import Category

        # Find all distinct program months for this user
        rows = (
            self.session.query(
                BudgetPlan.year,
                BudgetPlan.month,
                BudgetPlan.category_id,
                BudgetPlan.planned_amount,
            )
            .filter(BudgetPlan.user_id == user_id)
            .order_by(BudgetPlan.year, BudgetPlan.month)
            .all()
        )

        if not rows:
            return {"error": "אין נתוני תוכנית למשתמש זה"}

        # Group by (year, month)
        months_map = {}
        for r in rows:
            key = (r.year, r.month)
            if key not in months_map:
                months_map[key] = {}
            months_map[key][r.category_id] = r.planned_amount

        sorted_months = sorted(months_map.keys())
        total_months = len(sorted_months)

        if total_months < 2:
            return {
                "error": "צריך לפחות 2 חודשי תוכנית להשוואה",
                "total_months": total_months,
            }

        # "Before" = first month (learning)
        # "After" = last month (month 6 or the most recent)
        before_key = sorted_months[0]
        after_key = sorted_months[-1]
        before_data = months_map[before_key]
        after_data = months_map[after_key]

        # Category names
        cat_rows = self.session.query(Category).all()
        cat_names = {c.category_id: c.category_name for c in cat_rows}

        # Per-category comparison
        all_cids = set(list(before_data.keys()) + list(after_data.keys()))
        comparisons = []

        total_before = 0
        total_after = 0

        for cid in sorted(all_cids):
            before = before_data.get(cid, 0)
            after = after_data.get(cid, 0)
            absolute_change = before - after  # positive = saved
            if before > 0:
                percent_change = round((absolute_change / before) * 100, 1)
            else:
                percent_change = 0

            if percent_change > 5:
                perf_status = "improved"
            elif percent_change < -5:
                perf_status = "worsened"
            else:
                perf_status = "stable"

            comparisons.append({
                "category_id": cid,
                "category_name": cat_names.get(cid, f"קטגוריה {cid}"),
                "before_amount": round(before, 2),
                "after_amount": round(after, 2),
                "absolute_change": round(absolute_change, 2),
                "percent_change": percent_change,
                "status": perf_status,
            })
            total_before += before
            total_after += after

        total_savings = total_before - total_after
        savings_percent = round((total_savings / total_before) * 100, 1) if total_before > 0 else 0

        # Sort: most improved first
        sorted_comparisons = sorted(comparisons, key=lambda x: x["percent_change"], reverse=True)
        most_improved = [c for c in sorted_comparisons if c["status"] == "improved"][:3]
        needs_attention = [c for c in sorted_comparisons if c["status"] == "worsened"][:3]

        # Monthly progression
        monthly_progress = []
        for i, (yr, mo) in enumerate(sorted_months):
            total = sum(months_map[(yr, mo)].values())
            monthly_progress.append({
                "month_number": i + 1,
                "year": yr,
                "month": mo,
                "total_planned": round(total, 2),
                "phase": "learning" if i == 0 else ("gradual" if i < 6 else "maintenance"),
            })

        # Hebrew verdict
        if savings_percent > 10:
            verdict = (
                f"מעולה! הצלחת לחסוך {total_savings:,.0f}₪ בחודש — "
                f"זו ירידה של {savings_percent}% בהוצאות לעומת החודש הראשון. "
                f"הקטגוריות שהכי השתפרו: "
                f"{', '.join(c['category_name'] for c in most_improved[:3])}."
            )
        elif savings_percent > 0:
            verdict = (
                f"כל הכבוד! חסכת {total_savings:,.0f}₪ ({savings_percent}%) לעומת החודש הראשון. "
                f"יש עוד מקום לשיפור, אבל אתה בכיוון הנכון."
            )
        elif savings_percent == 0:
            verdict = "ההוצאות נשארו יציבות לאורך התוכנית. נסה לבדוק איפה אפשר לצמצם."
        else:
            verdict = (
                f"ההוצאות עלו ב-{abs(savings_percent)}% לעומת החודש הראשון. "
                f"כדאי לבדוק את הקטגוריות: "
                f"{', '.join(c['category_name'] for c in needs_attention[:3])}."
            )

        return {
            "user_id": user_id,
            "program_months": total_months,
            "first_month": {"year": before_key[0], "month": before_key[1]},
            "last_month": {"year": after_key[0], "month": after_key[1]},
            "total_before": round(total_before, 2),
            "total_after": round(total_after, 2),
            "total_savings": round(total_savings, 2),
            "savings_percent": savings_percent,
            "category_comparisons": sorted_comparisons,
            "most_improved": most_improved,
            "needs_attention": needs_attention,
            "monthly_progress": monthly_progress,
            "overall_verdict": verdict,
        }

    # ==================================================================
    # HISTORY ANALYSIS
    # ==================================================================
    def _get_spending_history(self, user_id, year, month, months=3):
        """
        Returns list of dicts, one per month (most recent last):
        [{category_id: {"actual": X, "planned": Y}}, ...]

        actual = from Expenses
        planned = from Budget_Plans (if exists)
        """
        result = []
        for i in range(months - 1, -1, -1):
            y, m = self._subtract_months(year, month, i)
            # actual spending
            rows = (
                self.session.query(
                    Expense.category_id,
                    func.sum(Expense.amount).label("total")
                )
                .filter(
                    Expense.user_id == user_id,
                    extract("year", Expense.date) == y,
                    extract("month", Expense.date) == m
                )
                .group_by(Expense.category_id)
                .all()
            )
            actual_map = {row.category_id: float(row.total) for row in rows}

            # planned from Budget_Plans
            from models.Finance.BudgetPlan import BudgetPlan
            plans = (
                self.session.query(BudgetPlan)
                .filter_by(user_id=user_id, year=y, month=m)
                .all()
            )
            planned_map = {p.category_id: p.planned_amount for p in plans}

            month_data = {}
            all_cids = set(list(actual_map.keys()) + list(planned_map.keys()))
            for cid in all_cids:
                month_data[cid] = {
                    "actual": actual_map.get(cid, 0),
                    "planned": planned_map.get(cid, 0),
                }
            result.append(month_data)
        return result

    def _analyze_history(self, history, targets, std_map):
        """
        For each category across history:
        - underspent_pct: % of months where actual < planned (budget not fully used)
        - overspent_pct:  % of months where actual > planned (overspent)
        - avg_spending:   average actual spending
        - avg_planned:    average planned budget
        - trend:          "stable" / "improving" / "worsening"
        """
        all_cids = set()
        for month_data in history:
            all_cids.update(month_data.keys())

        profile = {}
        for cid in all_cids:
            actuals = []
            planneds = []
            underspent_count = 0
            overspent_count = 0
            months_with_data = 0

            for month_data in history:
                d = month_data.get(cid, {"actual": 0, "planned": 0})
                actual = d["actual"]
                planned = d["planned"]
                actuals.append(actual)
                if planned > 0:
                    planneds.append(planned)
                    months_with_data += 1
                    if actual < planned * 0.9:
                        underspent_count += 1
                    if actual > planned * 1.1:
                        overspent_count += 1

            avg_spending = sum(actuals) / len(actuals) if actuals else 0
            avg_planned = sum(planneds) / len(planneds) if planneds else avg_spending

            underspent_pct = underspent_count / months_with_data if months_with_data > 0 else 0
            overspent_pct = overspent_count / months_with_data if months_with_data > 0 else 0

            target = targets.get(cid, avg_spending)
            std = std_map.get(cid, {})

            profile[cid] = {
                "avg_spending": avg_spending,
                "avg_planned": avg_planned,
                "underspent_pct": underspent_pct,
                "overspent_pct": overspent_pct,
                "target": target,
                "is_essential": std.get("is_essential", False),
                "is_fixed_cost": std.get("is_fixed_cost", False),
            }

        return profile

    def _calculate_transfers(self, profile, std_map):
        """
        Smart budget transfers:
        - Find categories that are ALWAYS underspent (underspent_pct > 0.5) → source
        - Find categories that are CONSISTENTLY overspent (overspent_pct > 0.5) → target
        - Transfer up to the average unused amount from source to target.
        - Only from non-essential, non-fixed categories.
        """
        donors = []
        receivers = []

        for cid, p in profile.items():
            std = std_map.get(cid, {})
            if std.get("is_fixed_cost"):
                continue
            if p["underspent_pct"] > 0.5 and p["avg_planned"] > p["avg_spending"]:
                available = (p["avg_planned"] - p["avg_spending"]) * 0.5
                if available > 0:
                    donors.append({"cid": cid, "available": available, "pct": p["underspent_pct"]})
            if p["overspent_pct"] > 0.5 and p["avg_spending"] > p["avg_planned"]:
                need = (p["avg_spending"] - p["avg_planned"]) * 0.5
                if need > 0:
                    receivers.append({"cid": cid, "need": need, "pct": p["overspent_pct"]})

        donors.sort(key=lambda x: x["pct"], reverse=True)
        receivers.sort(key=lambda x: x["pct"], reverse=True)

        transfers = {}
        for recv in receivers:
            need = recv["need"]
            for donor in donors:
                if need <= 0:
                    break
                if donor["available"] <= 0:
                    continue
                take = min(need, donor["available"])
                transfers[recv["cid"]] = {"from_cid": donor["cid"], "to_cid": recv["cid"],
                                          "amount": take, "reason": "העברה חכמה — תקציב לא מנוצל"}
                transfers[donor["cid"]] = {"from_cid": donor["cid"], "to_cid": recv["cid"],
                                           "amount": -take, "reason": "העברה חכמה — תקציב לא מנוצל"}
                need -= take
                donor["available"] -= take

        return transfers

    # ==================================================================
    # PROGRAM TRACKING
    # ==================================================================
    def _count_program_months(self, user_id):
        """
        Counts how many distinct months of Budget_Plans exist for this user.
        This is the REAL program month count — not based on join_date.

        Returns 0 if no plans exist yet (user is about to start month 1).
        """
        from models.Finance.BudgetPlan import BudgetPlan
        from sqlalchemy import distinct

        months = (
            self.session.query(
                distinct(BudgetPlan.year * 100 + BudgetPlan.month)
            )
            .filter(BudgetPlan.user_id == user_id)
            .all()
        )
        return len(months)

    def _get_program_phase_info(self, user_id):
        """
        Returns {phase, program_month, remaining_months} for the current program.
        - phase: "learning" | "gradual" | "completed"
        - program_month: 1..N (which month we're on)
        - remaining_months: how many months left in the 6-month program (0..5)
        """
        completed_months = self._count_program_months(user_id)
        MAX_PROGRAM_MONTHS = 6

        if completed_months < 1:
            return {
                "phase": "learning",
                "program_month": 1,
                "remaining_months": MAX_PROGRAM_MONTHS - 1,
            }
        elif completed_months < MAX_PROGRAM_MONTHS:
            return {
                "phase": "gradual",
                "program_month": completed_months + 1,
                "remaining_months": MAX_PROGRAM_MONTHS - completed_months,
            }
        else:
            return {
                "phase": "completed",
                "program_month": completed_months + 1,
                "remaining_months": 0,
            }

    # ==================================================================
    # HELPERS
    # ==================================================================
    def _months_between(self, start_date, end_date):
        if not start_date:
            return 0
        return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    def _prev_month(self, year, month):
        if month == 1:
            return year - 1, 12
        return year, month - 1

    def _subtract_months(self, year, month, n):
        total = year * 12 + month - 1 - n
        return total // 12, (total % 12) + 1
