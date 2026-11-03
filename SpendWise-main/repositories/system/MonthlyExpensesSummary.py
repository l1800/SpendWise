from datetime import date

from sqlalchemy import desc, func
from models.Finance.Expenses import Expense
from models.system.MonthlyExpensesSummary import MonthlyExpensesSummary
from models.core.Categories import Category
from repositories.base_repository import BaseRepository


class MonthlyExpensesSummaryRepository(BaseRepository):

    def add_amount(self, user_id, category_id, month_year, amount):

        obj = self.get_by_user_category_month(user_id, category_id, month_year)

        if obj:
            obj.total_amount += amount
        else:
            obj = MonthlyExpensesSummary(
                user_id=user_id,
                category_id=category_id,
                month_year=month_year,
                total_amount=amount
            )
            self.session.add(obj)

        self.session.commit()
        self.session.refresh(obj)
        return obj

    # ================= GET =================
    def get_by_user_category_month(self, user_id, category_id, month_year):
        return (
            self.session.query(MonthlyExpensesSummary)
            .filter_by(
                user_id=user_id,
                category_id=category_id,
                month_year=month_year
            )
            .first()
        )

    def get_last_6_months(self, user_id, category_id):
        return (
            self.session.query(MonthlyExpensesSummary)
            .filter_by(user_id=user_id, category_id=category_id)
            .order_by(desc(MonthlyExpensesSummary.month_year))
            .limit(6)
            .all()
        )

    def rebuild_month(self, user_id, year, month):
        """מחשב מחדש את סיכום החודש מתוך טבלת ההוצאות ומחזיר את מספר הקטגוריות."""
        month_year = f"{year}-{month:02d}"
        start = date(year, month, 1)
        end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

        totals = dict(
            self.session.query(Expense.category_id, func.sum(Expense.amount))
            .filter(Expense.user_id == user_id, Expense.date >= start, Expense.date < end)
            .group_by(Expense.category_id)
            .all()
        )

        self.session.query(MonthlyExpensesSummary).filter_by(
            user_id=user_id, month_year=month_year
        ).delete()

        for category_id, total in totals.items():
            self.session.add(MonthlyExpensesSummary(
                user_id=user_id,
                category_id=category_id,
                month_year=month_year,
                total_amount=float(total or 0),
            ))

        self.session.commit()
        return len(totals)

    # ================= ANALYSIS =================
    def get_category_analysis_data(self, user_id, year, month):

        current_month = f"{year}-{month:02d}"

        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1

        previous_month = f"{prev_year}-{prev_month:02d}"

        # JOIN נכון לפי category_id
        current_rows = (
            self.session.query(
                MonthlyExpensesSummary,
                Category
            )
            .join(Category, MonthlyExpensesSummary.category_id == Category.category_id)
            .filter(MonthlyExpensesSummary.user_id == user_id)
            .filter(MonthlyExpensesSummary.month_year == current_month)
            .all()
        )

        previous_rows = (
            self.session.query(MonthlyExpensesSummary)
            .filter_by(user_id=user_id, month_year=previous_month)
            .all()
        )

        prev_map = {
            r.category_id: r.total_amount
            for r in previous_rows
        }

        result = []

        for ms, cat in current_rows:

            result.append({
                "category_id": ms.category_id,
                "category_name": cat.category_name,
                "is_essential": cat.category_type_id == 1,
                "expense_type_id": getattr(ms, "expense_type_id", 2),

                "current_month_amount": float(ms.total_amount or 0),
                "previous_month_amount": prev_map.get(ms.category_id, 0),

                "last_6_months": self.get_last_6_months_values(
                    user_id, ms.category_id
                )
            })

        return result

    # ================= helper =================
    def get_last_6_months_values(self, user_id, category_id):

        rows = self.get_last_6_months(user_id, category_id)

        return [r.total_amount or 0 for r in rows]