class BudgetService:

    def __init__(self, repo):
        # שכבת גישה לנתונים (Repository)
        # כאן אנחנו מקבלים את כל הפונקציות מה-DB
        self.repo = repo


    # ==========================================
    # חישוב תקציב נטו (כסף פנוי לחודש)
    # ==========================================
    def calculate_net_budget(self, user_id, year, month):

        # שליפת כל ההכנסות של המשתמש לפי חודש
        incomes = self.repo.get_incomes_by_month(user_id, year, month)

        # סכימת כל ההכנסות
        total_income = sum(i.amount for i in incomes)

        # שליפת כל ההוצאות הקבועות (שכירות, הלוואות וכו')
        fixed_costs = self.repo.get_fixed_costs_by_month(user_id, year, month)

        # חישוב כסף נטו פנוי
        net_budget = total_income - fixed_costs

        # החזרת תוצאה מסודרת
        return {
            "user_id": user_id,
            "year": year,
            "month": month,
            "total_income": total_income,
            "fixed_costs": fixed_costs,
            "net_budget": net_budget
        }


    # ==========================================
    # הוצאות לפי קטגוריה (חיוני / רצון)
    # ==========================================
    def get_monthly_expenses_by_category(self, user_id, year, month):

        # שליפת נתונים מקובצים כבר מה-DB (GROUP BY)
        rows = self.repo.get_monthly_expenses_by_category(
            user_id, year, month
        )

        # סך כל ההוצאות החיוניות
        essential_total = 0

        # סך כל ההוצאות הלא חיוניות
        non_essential_total = 0

        # רשימת קטגוריות לתוצאה הסופית
        categories = []

        # מעבר על כל קטגוריה שהגיעה מה-DB
        for row in rows:

            # המרה ל-float כדי למנוע Decimal issues
            amount = float(row.total_amount)

            # בדיקה אם הקטגוריה חיונית לפי Category_Standards
            if row.is_essential:
                essential_total += amount
                category_type = "צורך חיוני"
            else:
                non_essential_total += amount
                category_type = "רצון"

            # בניית אובייקט לכל קטגוריה
            categories.append({
                "category_id": row.category_id,
                "category_name": row.category_name,
                "is_essential": row.is_essential,
                "category_type": category_type,
                "total_amount": amount
            })

        # החזרת סיכום מלא
        return {
            "user_id": user_id,
            "year": year,
            "month": month,
            "categories": categories,
            "essential_total": essential_total,
            "non_essential_total": non_essential_total
        }

    # ==========================================
    # תקציב סטנדרטי לפי משפחה (Benchmark)
    # ==========================================
    def get_standard_budget(self, family_size):

        # שליפת כל הסטנדרטים מה-DB
        rows = self.repo.get_category_standards()

        result = []

        # מעבר על כל קטגוריה
        for row in rows:
            # חישוב תקציב מומלץ
            recommended_budget = row.amount_per_person * family_size

            result.append({
                "category_id": row.category_id,
                "category_name": row.category_name,
                "recommended_budget": recommended_budget
            })

        return {
            "family_size": family_size,
            "standards": result
        }

    def get_previous_month_deficit(self, user_id, year, month):

        # חישוב חודש קודם
        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year

        incomes = self.repo.get_incomes_by_month(user_id, prev_year, prev_month)
        expenses = self.repo.get_expenses_by_month(user_id, prev_year, prev_month)

        total_income = sum(i.amount for i in incomes)
        total_expenses = sum(e.amount for e in expenses)

        deficit = total_expenses - total_income

        return max(deficit, 0)
