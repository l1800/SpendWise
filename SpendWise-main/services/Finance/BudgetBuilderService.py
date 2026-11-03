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

        # יעד הקיצוץ (stretch goal) אינו מוקצה על ידי allocation של
        # CutAllocationService, ולכן כמעט תמיד "חסר" — הוא נשאר ליעד חיסכון.
        # מן המסגרת מורידים רק את הקיצוץ שקרה בפועל, כלומר שנים-עשר חודשי
        # חיים בתוך ההכנסה; אחרת השלב הבא יקרוס 90% מכל קטגוריה גמישה
        # בשביל יעד שלא הוקצה.
        monthly_limit = max(0, base_income - sum(b["cut_amount"] for b in budget))

        # =========================
        # שלב א׳ — הוצאה קבועה ושכר דירה
        # (המסגרת כאן היא ההכנסה הפנויה; יעד הקיצוץ נשאר כלשונו ב-total_cut_needed)
        # ה"תקרה" היא התשלומים הקשיחים בלבד: הוצאות שעליהן שילמנו (קבועות,
        # וכן חיוניות בהיקף ההוצאה שהתקיים בפועל). החיוני-גמיש שמעל ההוצאה
        # הקיימת (למשל ארנונה שאינה מסומנת קבועה) אינו תקרה — הוא החריגה
        # עצמה. לכן אם ההוצאות הקשיחות לבדן עוברות את ההכנסה, המסגרת
        # מתרחבת עד אליהן, והמשפחה מקבלת "גירעון קשיח" מפורש במקום
        # קיצוץ דמיוני של 100% בכל הקטגוריות באשר הן.
        # =========================
        fixed_total = self._fixed_total(budget)
        rigid_total = fixed_total + self._essential_spent(budget)
        rigid_overrun = max(0.0, rigid_total - base_income)

        for b in budget:
            if b.get("is_fixed_cost") and rigid_overrun > 0:
                b["status"] = "covered"
                b["note"] = "הוצאה קבועה — לא קוצצה (מסגרת התקיימה גם בגירעון)"

        # =========================
        # שלב ב׳ — תיקון הוצאות גמישות (לעולם לא קבועות)
        # =========================
        target = min(monthly_limit, base_income)
        flexible_room = max(0.0, target - fixed_total)
        deficit = total_spending - max(flexible_room, rigid_total)
        overrun = total_spending - base_income

        # ---------------------------------------------------
        # שלב ג׳ — קיצוץ עדין: עד 20% / 10% מכל קטגוריה גמישה בפעם אחת
        # ---------------------------------------------------
        adjusted = False
        if deficit > 0:
            for b in self._cuttable(budget):

                if deficit <= 0:
                    break

                # חיוני-גמיש נחתך רק מעבר להתחייבות שעליה שילם בפועל
                floor = b["current_amount"] if b.get("is_essential") else 0
                room = max(0.0, b["planned_amount"] - floor)
                if room <= 0:
                    continue

                max_extra_pct = 0.2 if b["pain_level"] <= 3 else 0.1

                extra_cut = min(
                    room * max_extra_pct,
                    deficit
                )

                b["planned_amount"] -= extra_cut
                b["cut_amount"] += extra_cut
                b["planned_amount"] = round(b["planned_amount"], 2)
                b["cut_amount"] = round(b["cut_amount"], 2)
                b["cut_percent"] = self._calc_cut_percent(b["cut_amount"], b["current_amount"])
                b["status"] = self._calc_status(b, b["cut_amount"])
                b["note"] = self._build_note(b, b["cut_amount"], b["cut_percent"])
                deficit -= extra_cut
                adjusted = True

        # ---------------------------------------------------
        # שלב ד׳ — בורא מסגרת: קוטמים את ההוצאות הגמישות ביחס שהן עצמן
        # ייצרו. הגמישות נדחסות יחד ליתרתם (הוצאה פחות התקרה הקשיחה),
        # ורק אם גם זה לא מספיק — עד אפס.
        # ---------------------------------------------------
        total_spending = sum(b["planned_amount"] for b in budget)
        flexible_spent = sum(b["planned_amount"] for b in self._cuttable(budget))

        if total_spending > base_income and flexible_spent > 0:
            affordable = max(0.0, base_income - (total_spending - flexible_spent))
            scale = min(1.0, affordable / flexible_spent)

            if scale < 1.0:
                for b in self._cuttable(budget):
                    new_planned = round(b["planned_amount"] * scale, 2)
                    b["cut_amount"] = round(b["cut_amount"] + b["planned_amount"] - new_planned, 2)
                    b["cut_percent"] = self._calc_cut_percent(b["cut_amount"], b["current_amount"])
                    b["planned_amount"] = new_planned
                    b["status"] = self._calc_status(b, b["cut_amount"])
                    b["note"] = self._build_note(b, b["cut_amount"], b["cut_percent"])
                adjusted = True

        # ---------------------------------------------------
        # קטגוריה קבועה שמוצגת תמיד נעולה; מוצגת כ"covered" אם הייתה חריגה
        # ---------------------------------------------------
        for b in budget:
            if b.get("is_fixed_cost") and b["status"] != "covered":
                b["status"] = "protected"
                b["note"] = "הוצאה קבועה — לא ניתנת לקיצוץ"

        total_spending = sum(b["planned_amount"] for b in budget)
        actual_cut = sum(b["cut_amount"] for b in budget)
        remaining_deficit = round(max(0.0, total_spending - base_income), 2)
        health_score = self._calc_health_score(base_income, total_spending, monthly_limit)

        status = self._calc_overall_status(
            total_spending, base_income, monthly_limit,
            rigid_total=rigid_total, flexible_room=flexible_room,
            fixed_total=fixed_total,
        )

        warnings = self._build_warnings(missing_allocation_names, monthly_limit)

        if rigid_overrun > 0:
            warnings = warnings or []
            warnings.append(
                f"גירעון קשיח: ההוצאות הקבועות וההוצאה החיונית שכבר שולמה "
                f"עולות על ההכנסה. ההכנסה או ההוצאות הקבועות הן שדורשות "
                f"טיפול — לא קיצוץ הוצאות משתנות."
            )
        elif remaining_deficit > 0:
            warnings = warnings or []
            warnings.append(
                f"נותר גירעון של {int(remaining_deficit)}₪ גם אחרי צמצום ההוצאות הגמישות."
            )

        message = None
        if status == "IMPOSSIBLE_BUDGET":
            message = (
                "ההוצאות הקשיחות (קבועות + חיוניות) עולות על ההכנסה — "
                "המסגרת הועמדה על ההוצאות עצמן, ואין מקום לקיצוץ הוצאות משתנות"
            )

        return {
            "net_budget": base_income,
            "total_cut_needed": total_cut_needed,
            "monthly_limit": round(monthly_limit, 2),
            "planned_spending": round(total_spending, 2),
            "actual_cut": round(actual_cut, 2),
            "remaining_balance": round(base_income - total_spending, 2),
            "remaining_deficit": remaining_deficit,
            "rigid_total": round(rigid_total, 2),
            "rigid_overrun": round(rigid_overrun, 2),
            "budget_health_score": round(health_score, 2),
            "status": status,
            "message": message,
            "budget": budget,
            "fixed_costs": round(fixed_total, 2),
            "adjusted": adjusted,
            "warnings": warnings,
        }

    # =========================
    # FIXED / CUTTABLE
    # =========================
    def _fixed_total(self, budget):
        """סך ההוצאות הקבועות — שכר דירה, הלוואות וכל סעיף שסומן כקבוע."""
        return sum(b["planned_amount"] for b in budget if b.get("is_fixed_cost"))

    def _essential_spent(self, budget):
        """ההוצאה החיונית (שאינה קבועה) שכבר שולמה בפועל — התקרה שלה."""
        return sum(
            b["current_amount"]
            for b in budget
            if b.get("is_essential") and not b.get("is_fixed_cost")
        )

    def _calc_cut_percent(self, cut_amount, current_amount):
        """אחוז הקיצוץ בפועל — מעודכן בכל שינוי של planned_amount."""
        if current_amount <= 0:
            return 0
        return round(cut_amount / current_amount * 100, 1)

    def _headroom(self, budget):
        """המרווח שנותר בקטגוריה גמישה בין התכנית לתקרה שלה."""
        floor = budget["current_amount"] if budget.get("is_essential") else 0
        return max(0.0, budget["planned_amount"] - floor)

    def _cuttable(self, budget):
        """ההוצאות שניתן להקטין, מן הכי פחות כואבת. קבועות ואטומות — בחוץ."""
        return [
            b for b in sorted(budget, key=lambda x: x["pain_level"])
            if not b.get("is_fixed_cost") and b["pain_level"] < 8
        ]

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
            covered    — קבועה שהייתה חריגה, ולכן הורחבה המסגרת ולא קוצצה
            protected  — קבועה, לא ניתנת לקיצוץ
            reduced    — קוצצה
            unchanged  — לא קוצצה
        """

        if item.get("is_fixed_cost"):
            return "protected"

        if cut_amount > 0:
            return "reduced"

        return "unchanged"

    def _calc_overall_status(self, total_spending, base_income, monthly_limit,
                             rigid_total=0, flexible_room=0, fixed_total=0):
        """
        סטטוס כללי של התוכנית.

            OK                 — התכנית בתוך ההכנסה ובתוך יעד הקיצוץ
            FRAME_RAISED       — הוצאה קבועה חייבה להרחיב את המסגרת, אבל
                                 התכנית עדיין בתוך ההכנסה (מכוסה, לא חריגה)
            LIMIT_EXCEEDED     — התכנית בתוך ההכנסה, אבל מעל יעד הקיצוץ
            DEFICIT            — גם אחרי צמצום כל ההוצאות הגמישות נותר גירעון
            IMPOSSIBLE_BUDGET  — ההוצאות הקשיחות לבדן עולות על ההכנסה
        """

        if rigid_total > base_income:
            return "IMPOSSIBLE_BUDGET"

        if total_spending > base_income:
            return "DEFICIT"

        if total_spending > max(monthly_limit, rigid_total):
            return "LIMIT_EXCEEDED"

        if fixed_total > monthly_limit:
            return "FRAME_RAISED"

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