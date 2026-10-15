from models.Finance.Expenses import Expense
from repositories.base_repository import BaseRepository


class ExpenseRepository(BaseRepository):

    # ---------------- CREATE ----------------
    def add(self, expense):
        self.session.add(expense)
        self.session.commit()
        self.session.refresh(expense)
        return expense

    # ---------------- READ BY ID ----------------
    def get_by_id(self, expense_id):
        return (
            self.session.query(Expense)
            .filter_by(transaction_id=expense_id)
            .first()
        )

    # ---------------- READ ALL ----------------
    def get_all(self):
        return self.session.query(Expense).all()

    # ---------------- UPDATE ----------------
    def update(self, transaction_id: int, **kwargs):
        expense = self.get_by_id(transaction_id)

        if not expense:
            return None

        for key, value in kwargs.items():
            setattr(expense, key, value)

        self.session.commit()
        self.session.refresh(expense)
        return expense

    # ---------------- DELETE ----------------
    def delete_by_id(self, transaction_id: int):
        expense = self.get_by_id(transaction_id)

        if not expense:
            return None

        self.session.delete(expense)
        self.session.commit()
        return expense