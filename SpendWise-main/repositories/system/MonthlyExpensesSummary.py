from sqlalchemy import desc
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

        # =========================
        # one-time covered expenses — sum per category for current month
        # these should NOT be counted in analysis because savings covered them
        # =========================
        from models.Finance.Expenses import Expense
        from sqlalchemy import func

        one_time_covered = (
            self.session.query(
                Expense.category_id,
                func.sum(Expense.amount).label("covered_total")
            )
            .filter(Expense.user_id == user_id)
            .filter(Expense.is_one_time == True)
            .filter(Expense.covered_by_savings == True)
            .filter(func.format(Expense.date, "yyyy-MM") == current_month)
            .group_by(Expense.category_id)
            .all()
        )
        covered_map = {
            row.category_id: row.covered_total
            for row in one_time_covered
        }

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

            # subtract one-time covered expenses — they don't distort trends
            raw_amount = ms.total_amount or 0
            covered = covered_map.get(ms.category_id, 0)
            adjusted_amount = max(0, raw_amount - covered)

            result.append({
                "category_id": ms.category_id,
                "category_name": cat.category_name,
                "is_essential": cat.category_type_id == 1,
                "expense_type_id": getattr(ms, "expense_type_id", 2),

                "current_month_amount": adjusted_amount,
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