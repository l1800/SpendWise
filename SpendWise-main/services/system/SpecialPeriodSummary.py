from models.system.SpecialPeriodSummary import SpecialPeriodSummary


class SpecialPeriodService:

    def __init__(self, repo):
        self.repo = repo

    def handle_expense(self, user_id, category_id, amount, expense_date):
        period = self.repo.resolve_period(expense_date)
        if not period:
            return amount  # אין תקופה → מחיר רגיל

        # בדיקה: האם חרגנו מהתקציב
        summary = self.repo.get_summary(user_id, category_id, period.type_id)

        if summary and summary.approved_amount > 0 and summary.spent_amount >= summary.approved_amount:
            # חריגה — מחיר רגיל פחות 5%
            return amount * 0.95

        ratio = self.repo.get_ratio(period.type_id, category_id)
        if ratio is None:
            ratio = 0

        if ratio > 1:
            ratio = ratio / 100

        ratio = max(0, min(ratio, 1))

        if not summary:
            summary = SpecialPeriodSummary(
                user_id=user_id,
                category_id=category_id,
                special_period_id=period.type_id,
                spent_amount=0,
                approved_amount=0
            )
            self.repo.create(summary)

        final_price = amount * (1 - ratio)

        summary.spent_amount += final_price
        summary.approved_amount += amount * ratio

        self.repo.update(summary)

        return final_price
