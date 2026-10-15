from sqlalchemy import func, extract
from models.Finance.Incomes import Income
from models.Finance.Expenses import Expense
from models.core.Categories import Category
from models.core.CategoryStandard import CategoryStandard


class FinancialRepository:

    def __init__(self, session):
        self.session = session

    # ==========================================
    # סך הכנסות
    # ==========================================
    def get_total_income(self, user_id, year, month):

        return (
            self.session.query(func.sum(Income.amount))
            .filter(
                Income.user_id == user_id,
                extract("year", Income.date) == year,
                extract("month", Income.date) == month
            )
            .scalar()
        ) or 0

    # ==========================================
    # סך הוצאות
    # ==========================================
    def get_total_expenses(self, user_id, year, month):

        return (
            self.session.query(func.sum(Expense.amount))
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month
            )
            .scalar()
        ) or 0

    # ==========================================
    # הוצאות קבועות (FIXED COSTS)
    # ==========================================
    def get_fixed_costs(self, user_id, year, month):

        return (
            self.session.query(func.sum(Expense.amount))
            .join(Category, Expense.category_id == Category.category_id)
            .join(CategoryStandard,
                  Category.category_id == CategoryStandard.category_id)
            .filter(
                Expense.user_id == user_id,
                CategoryStandard.is_fixed_cost == True,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month
            )
            .scalar()
        ) or 0

    # ==========================================
    # 💰 לחץ פיננסי (NEW - שכבתי)
    # ==========================================
    def get_financial_pressure(self, user_id, year, month):

        income = self.get_total_income(user_id, year, month)
        expenses = self.get_total_expenses(user_id, year, month)
        fixed = self.get_fixed_costs(user_id, year, month)

        # =========================
        # בדיקות קצה
        # =========================
        if income == 0:
            return 100  # אין הכנסה → לחץ מקסימלי

        disposable = income - fixed

        if disposable <= 0:
            return 100  # אין כסף פנוי

        # =========================
        # יחס הוצאות מול כסף פנוי
        # =========================
        ratio = expenses / disposable

        # =========================
        # המרה לציון לחץ 0–100
        # =========================
        if ratio <= 0.5:
            score = 10
        elif ratio <= 0.7:
            score = 30
        elif ratio <= 0.9:
            score = 60
        elif ratio <= 1.1:
            score = 80
        else:
            score = 100

        return round(score, 2)

    # ==========================================
    # קטגוריות לניתוח לחץ קצר טווח
    # ==========================================
    def get_category_spike_data(self, user_id, year, month):

        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1

        current = (
            self.session.query(
                Expense.category_id,
                func.sum(Expense.amount).label("current_month_amount"),
                Category.category_name,
                CategoryStandard.is_fixed_cost
            )
            .join(Category, Expense.category_id == Category.category_id)
            .join(CategoryStandard, Category.category_id == CategoryStandard.category_id)
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month
            )
            .group_by(
                Expense.category_id,
                Category.category_name,
                CategoryStandard.is_fixed_cost
            )
            .all()
        )

        previous = (
            self.session.query(
                Expense.category_id,
                func.sum(Expense.amount).label("previous_month_amount")
            )
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == prev_year,
                extract("month", Expense.date) == prev_month
            )
            .group_by(Expense.category_id)
            .all()
        )

        prev_map = {p.category_id: p.previous_month_amount for p in previous}

        result = []

        for c in current:
            result.append({
                "category_id": c.category_id,
                "category_name": c.category_name,
                "current_month_amount": c.current_month_amount or 0,
                "previous_month_amount": prev_map.get(c.category_id, 0),
                "is_essential": c.is_fixed_cost or False
            })

        return result

    def get_category_analysis_data(self, user_id, year, month):

        # חודש נוכחי
        current = (
            self.session.query(
                Expense.category_id,
                func.sum(Expense.amount).label("current_month_amount"),
                Category.category_name,
                CategoryStandard.is_essential,
                Category.category_type_id.label("expense_type_id")
            )
            .join(Category, Expense.category_id == Category.category_id)
            .join(CategoryStandard, Category.category_id == CategoryStandard.category_id)
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month
            )
            .group_by(
                Expense.category_id,
                Category.category_name,
                CategoryStandard.is_essential,
                Category.category_type_id
            )
            .all()
        )

        if not current:
            return []

        # חודש קודם
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        previous = (
            self.session.query(
                Expense.category_id,
                func.sum(Expense.amount).label("previous_month_amount")
            )
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == prev_year,
                extract("month", Expense.date) == prev_month
            )
            .group_by(Expense.category_id)
            .all()
        )

        prev_map = {p.category_id: p.previous_month_amount or 0 for p in previous}

        # 6 חודשים אחרונים (לא כולל נוכחי)
        result = []
        for c in current:

            # שליפת 6 חודשים אחרונים לפי קטגוריה
            history_rows = (
                self.session.query(
                    extract("year", Expense.date).label("y"),
                    extract("month", Expense.date).label("m"),
                    func.sum(Expense.amount).label("monthly_total")
                )
                .filter(
                    Expense.user_id == user_id,
                    Expense.category_id == c.category_id,
                    (
                        (extract("year", Expense.date) < year) |
                        ((extract("year", Expense.date) == year) & (extract("month", Expense.date) < month))
                    )
                )
                .group_by(
                    extract("year", Expense.date),
                    extract("month", Expense.date)
                )
                .order_by(
                    extract("year", Expense.date).desc(),
                    extract("month", Expense.date).desc()
                )
                .limit(6)
                .all()
            )

            # היפוך — oldest first
            history_rows = list(reversed(history_rows))
            last_6_months = [h.monthly_total or 0 for h in history_rows]

            result.append({
                "category_id": c.category_id,
                "category_name": c.category_name,
                "is_essential": c.is_essential or False,
                "expense_type_id": c.expense_type_id or 2,
                "current_month_amount": c.current_month_amount or 0,
                "previous_month_amount": prev_map.get(c.category_id, 0),
                "last_6_months": last_6_months,
            })

        return result

    # ==========================================
    # חריגות (placeholder)
    # ==========================================
    def get_over_budget(self, user_id, year, month):
        return 0
