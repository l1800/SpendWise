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
        return self.repo.update(
            expense_id,
            user_id=dto.user_id,
            amount=dto.amount,
            date=dto.date,
            expense_type_id=dto.expense_type_id,
            category_id=dto.category_id
        )

    # =====================================================
    # DELETE
    # =====================================================
    def delete_expense(self, expense_id: int):
        return self.repo.delete_by_id(expense_id)