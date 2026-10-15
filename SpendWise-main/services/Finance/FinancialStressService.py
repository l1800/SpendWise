class FinancialStressService:


    def __init__(self, repo, monthly_service):
        self.repo = repo
        self.monthly_service = monthly_service

    # =========================
    # שכבה 1: קבלת נתונים
    # =========================
    def get_data(self, user_id, year, month):
        return self.repo.get_category_spike_data(user_id, year, month)

    # =========================
    # שכבה 2: חישוב שינוי קטגוריה
    # =========================
    def calculate_category_stress(self, current, previous, essential):

        if current == 0 and previous == 0:
            return 0

        if previous == 0:
            # אין היסטוריה → לא סכנה, אלא אי ודאות לפי גודל ההוצאה
            if current < 100:
                change = 20
            elif current < 500:
                change = 50
            else:
                change = 80
        else:
            change = ((current - previous) / previous) * 100

        abs_change = abs(change)

        # דירוג בסיסי
        if abs_change <= 5:
            score = 5
        elif abs_change <= 15:
            score = 25
        elif abs_change <= 30:
            score = 60
        else:
            score = 100

        # התאמה לפי הכרחיות
        if essential:
            score *= 0.7
        else:
            score *= 1.2

        return min(100, score)

    # =========================
    # שכבה 3: חישוב כולל
    # =========================
    def calculate_spike_stress(self, user_id, year, month):

        rows = self.get_data(user_id, year, month)

        if not rows:
            return {"spike_stress": 0}

        total_score = 0
        total_weight = 0

        for r in rows:

            current = r.get("current_month_amount", 0)
            previous = r.get("previous_month_amount", 0)
            essential = r.get("is_essential", False)

            category_score = self.calculate_category_stress(
                current,
                previous,
                essential
            )

            weight = max(current, previous)
            total_score += category_score * weight
            total_weight += weight

        final_score = total_score / total_weight if total_weight else 0

        final_score = max(0, min(100, int(final_score)))

        return {
            "spike_stress": final_score
        }