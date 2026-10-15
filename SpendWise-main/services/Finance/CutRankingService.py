class CutRankingService:
    """
    פונקציה #9 — דירוג קטגוריות לקיצוץ.
    מחזיר רק אחוזים, בלי סכומים.
    """

    def __init__(self, budget_service, preference_repo, standard_repo, analysis_service):
        self.budget_service = budget_service
        self.preference_repo = preference_repo
        self.standard_repo = standard_repo
        self.analysis_service = analysis_service

    def rank_categories(self, user_id, year, month):
        # שלב 1: משיכת הוצאות לפי קטגוריות (פונקציה #2 שלך)
        expenses_data = self.budget_service.get_monthly_expenses_by_category(user_id, year, month)
        categories = expenses_data.get("categories", [])

        if not categories:
            return {"ranking": [], "total_expenses": 0}

        # שלב 2: העדפות משתמש
        prefs = self.preference_repo.get_by_user(user_id)
        pref_map = {}
        for p in prefs:
            score = p.importance_score
            if score > 1:
                score = score / 100
            pref_map[p.category_id] = score

        # שלב 3: סטנדרטים (is_fixed_cost)
        standards = self.standard_repo.get_all()
        std_map = {
            s.category_id: {
                "is_essential": s.is_essential,
                "is_fixed_cost": s.is_fixed_cost,
                "max_cut_percent": s.max_cut_percent,
            }
            for s in standards
        }

        # שלב 4: מגמות (פונקציה #5 שלך)
        analysis = self.analysis_service.calculate_category_analysis(user_id, year, month)
        analysis_map = {
            c["category_id"]: c.get("long_term_change_percent", 0)
            for c in analysis.get("categories", [])
        }

        # שלב 5: חישוב total
        total = sum(c["total_amount"] for c in categories)

        # שלב 6: ציון לכל קטגוריה
        ranked = []
        for c in categories:
            cid = c["category_id"]
            amount = c["total_amount"]

            std = std_map.get(cid, {})
            is_essential = std.get("is_essential", c.get("is_essential", False))
            is_fixed = std.get("is_fixed_cost", False)

            # מרכיב 1: אי-חיוניות (35%)
            if is_essential:
                non_ess = 0.0
            else:
                non_ess = 1.0
            if is_fixed and not is_essential:
                non_ess *= 0.5

            # מרכיב 2: חשיבות נמוכה למשתמש (20%)
            importance = pref_map.get(cid, 0.5)
            low_imp = 1.0 - importance

            # מרכיב 3: משקל בתקציב (25%)
            weight = amount / total if total > 0 else 0

            # מרכיב 4: מגמה (20%)
            lt = analysis_map.get(cid, 0)
            if lt > 10:
                trend = 1.0
            elif lt > 0:
                trend = 0.5
            elif lt < -5:
                trend = 0.0
            else:
                trend = 0.3

            # ציון סופי
            score = non_ess * 0.35 + low_imp * 0.20 + weight * 0.25 + trend * 0.20

            # אחוז קיצוץ (רק אחוז!)
            if is_essential and is_fixed:
                pct = 0
            elif is_essential:
                pct = 5 if score > 0.4 else (3 if score > 0.2 else 0)
            else:
                if score > 0.7:
                    pct = 30
                elif score > 0.4:
                    pct = 20
                elif score > 0.2:
                    pct = 10
                else:
                    pct = 0

            max_pct = std.get("max_cut_percent", 100)
            pct = min(pct, max_pct)

            # הסבר
            reasons = []
            if is_essential and is_fixed:
                reasons.append("קבוע")
            elif is_essential:
                reasons.append("חיוני — מוגבל")
            if not is_essential:
                reasons.append("לא חיוני")
            if weight > 0.2:
                reasons.append("חלק גדול מהתקציב")
            if lt > 10:
                reasons.append("במגמת עלייה")
            elif lt < -5:
                reasons.append("במגמת ירידה")

            ranked.append({
                "category_id": cid,
                "category_name": c["category_name"],
                "is_essential": is_essential,
                "cut_score": round(score, 3),
                "recommended_cut_pct": pct,
                "max_pct": max_pct,
                "importance_score": pref_map.get(cid, 0.5) * 100,
                "current_amount": amount,  # 🔥 זה מה שחסר לך
                "reason": " | ".join(reasons),
            })

        ranked.sort(key=lambda x: x["cut_score"], reverse=True)

        return {"ranking": ranked, "total_expenses": total}