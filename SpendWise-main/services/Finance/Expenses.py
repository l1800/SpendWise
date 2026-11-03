from models.Finance.Expenses import Expense


class ExpenseService:

    def __init__(self, repo, special_service, monthly_service):
        self.repo = repo
        self.special_service = special_service
        self.monthly_service = monthly_service

    # =====================================================
    # ADD EXPENSE FLOW
    # =====================================================
    def add_expense(self, dto):

        # =================================================
        # 1. חישוב סכום (דריסה / חוקים מיוחדים)
        # =================================================
        amount = self.special_service.handle_expense(
            user_id=dto.user_id,
            category_id=dto.category_id,
            amount=dto.amount,
            expense_date=dto.date
        )

        # =================================================
        # 2. שמירה ב-DB
        # =================================================
        expense = Expense(
            user_id=dto.user_id,
            amount=amount,
            date=dto.date,
            expense_type_id=dto.expense_type_id,
            category_id=dto.category_id
        )

        saved = self.repo.add(expense)

        # =================================================
        # 3. עדכון סיכום חודשי
        # =================================================
        self.monthly_service.update_monthly_summary(
            user_id=dto.user_id,
            category_id=dto.category_id,
            amount=amount,
            expense_date=dto.date
        )

        return saved

    # =====================================================
    # READ ALL
    # =====================================================
    def get_all_expenses(self):
        return self.repo.get_all()

    # =====================================================
    # READ BY ID
    # =====================================================
    def get_expense_by_id(self, expense_id: int):
        return self.repo.get_by_id(expense_id)

    # =====================================================
    # UPDATE
    # =====================================================
    def update_expense(self, expense_id: int, dto):
        previous = self.repo.get_by_id(expense_id)
        updated = self.repo.update(
            expense_id,
            user_id=dto.user_id,
            amount=dto.amount,
            date=dto.date,
            expense_type_id=dto.expense_type_id,
            category_id=dto.category_id
        )
        if updated:
            # העריכה יכולה לשנות גם סכום וגם חודש — לכן בונים מחדש את שני החודשים
            self._rebuild_months(dto.user_id, previous.date if previous else None, dto.date)
        return updated

    # =====================================================
    # DELETE
    # =====================================================
    def delete_expense(self, expense_id: int):
        previous = self.repo.get_by_id(expense_id)
        if not previous:
            return None
        user_id, removed_date = previous.user_id, previous.date
        deleted = self.repo.delete_by_id(expense_id)
        if deleted:
            self._rebuild_months(user_id, removed_date)
        return deleted

    # =====================================================
    # עזר — רענון הסיכום החודשי אחרי שינוי בהוצאה
    # =====================================================
    def _rebuild_months(self, user_id, *dates):
        seen = set()
        for value in dates:
            if value is None:
                continue
            key = (value.year, value.month)
            if key in seen:
                continue
            seen.add(key)
            self.monthly_service.recompute_month(user_id, value.year, value.month)