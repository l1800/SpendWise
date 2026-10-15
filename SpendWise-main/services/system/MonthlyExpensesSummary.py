class MonthlyExpensesSummaryService:

    def __init__(self, repository):
        self.repository = repository

    def update_monthly_summary(self, user_id, category_id, amount, expense_date):
        month_year = expense_date.strftime("%Y-%m")
        return self.repository.add_amount(user_id, category_id, month_year, amount)

    def calculate_category_analysis(self, user_id, year, month):

        rows = self.repository.get_category_analysis_data(user_id, year, month)

        if not rows:
            return {"categories": []}

        categories = []

        for r in rows:

            current = r.get("current_month_amount", 0)
            previous = r.get("previous_month_amount", 0)

            expense_type = r.get("expense_type_id", 2)

            # =========================
            # שינוי חודשי (תיקון חשוב)
            # =========================
            if current == 0 and previous == 0:
                monthly_change = 0

            elif previous == 0:
                # במקום 100% פייק → קפיצה חדשה
                monthly_change = 0

            else:
                monthly_change = ((current - previous) / previous) * 100

            # =========================
            # מגמה 6 חודשים
            # =========================
            history = r.get("last_6_months", [])

            if len(history) < 2:
                long_term_change = 0

            else:
                weights = [2 ** i for i in range(len(history))]
                weighted_sum = sum(a * b for a, b in zip(history, weights))
                total_weights = sum(weights)

                weighted_avg = weighted_sum / total_weights if total_weights else 0
                prev_avg = sum(history[:-1]) / len(history[:-1])

                if prev_avg == 0:
                    long_term_change = 0
                else:
                    long_term_change = ((weighted_avg - prev_avg) / prev_avg) * 100

            # =========================
            # התאמות לפי סוג הוצאה
            # =========================
            if expense_type == 1:
                long_term_change *= 0.2

            elif expense_type == 3:
                monthly_change *= 0.7
                long_term_change *= 0.5

            categories.append({
                "category_id": r.get("category_id"),
                "category_name": r.get("category_name", "Unknown"),
                "is_essential": r.get("is_essential", False),
                "expense_type": expense_type,
                "monthly_change_percent": round(monthly_change, 2),
                "long_term_change_percent": round(long_term_change, 2)
            })

        return {"categories": categories}