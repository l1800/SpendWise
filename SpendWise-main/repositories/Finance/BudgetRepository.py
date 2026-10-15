from sqlalchemy import func, extract
from models.Finance.Incomes import Income
from models.Finance.Expenses import Expense
from models.core.Categories import Category
from models.core.CategoryStandard import CategoryStandard


class BudgetRepository:

    def __init__(self, session):
        # חיבור למסד הנתונים (SQLAlchemy Session)
        self.session = session


    # ==========================================
    # הכנסות לפי חודש
    # ==========================================
    def get_incomes_by_month(self, user_id, year, month):

        # שליפת כל ההכנסות של המשתמש לפי שנה + חודש
        return (
            self.session.query(Income)
            .filter(
                Income.user_id == user_id,
                extract("year", Income.date) == year,
                extract("month", Income.date) == month
            )
            .all()
        )


    # ==========================================
    # הוצאות קבועות לפי חודש
    # ==========================================
    def get_fixed_costs_by_month(self, user_id, year, month):

        # סכימת כל ההוצאות הקבועות בלבד
        total = (
            self.session.query(func.sum(Expense.amount))

            # חיבור לטבלת סטנדרט כדי לדעת מה קבוע
            .join(CategoryStandard,
                  Expense.category_id == CategoryStandard.category_id)

            .filter(
                Expense.user_id == user_id,

                # רק הוצאות שמוגדרות קבועות
                CategoryStandard.is_fixed_cost == True,

                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month
            )
            .scalar()
        )

        # אם אין נתונים מחזירים 0
        return total or 0


    # ==========================================
    # הוצאות לפי קטגוריה (GROUP BY)
    # ==========================================
    def get_monthly_expenses_by_category(self, user_id, year, month):

        return (
            self.session.query(

                # מזהה קטגוריה
                Category.category_id,

                # שם הקטגוריה
                Category.category_name,

                # האם חיוני / לא חיוני
                CategoryStandard.is_essential,

                # סכום כל ההוצאות בקטגוריה
                func.sum(Expense.amount).label("total_amount")
            )

            # חיבור בין הוצאות לקטגוריה
            .join(Category, Expense.category_id == Category.category_id)

            # חיבור לסטנדרט (חיוני / רצון)
            .join(CategoryStandard,
                  Category.category_id == CategoryStandard.category_id)

            # סינון לפי משתמש + חודש
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month
            )

            # קיבוץ לפי קטגוריה
            .group_by(
                Category.category_id,
                Category.category_name,
                CategoryStandard.is_essential
            )

            .all()
        )

    def get_category_standards(self):
        return (
            self.session.query(
                Category.category_id,
                Category.category_name,
                CategoryStandard.amount_per_person
            )
            .join(CategoryStandard, Category.category_id == CategoryStandard.category_id)
            .filter(CategoryStandard.is_fixed_cost == False)
            .all()
        )

        # ==========================================
        # הוצאות לפי חודש
        # ==========================================

    def get_expenses_by_month(self, user_id, year, month):
        return (
            self.session.query(Expense)
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month
            )
            .all()
        )