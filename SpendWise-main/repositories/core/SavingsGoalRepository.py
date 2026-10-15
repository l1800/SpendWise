from models.core.SavingsGoal import SavingsGoal, SavingsTransaction
from repositories.base_repository import BaseRepository


class SavingsGoalRepository(BaseRepository):

    # ================= GOALS CRUD =================

    def get_all(self):
        return self.session.query(SavingsGoal).all()

    def get_by_id(self, id):
        return self.session.query(SavingsGoal).filter_by(id=id).first()

    def get_by_user(self, user_id):
        return self.session.query(SavingsGoal).filter_by(user_id=user_id).all()

    def create_goal(self, user_id, name, target_amount=None, category_id=None):
        goal = SavingsGoal(
            user_id=user_id,
            name=name,
            target_amount=target_amount,
            category_id=category_id,
            current_balance=0
        )
        self.session.add(goal)
        self.session.commit()
        self.session.refresh(goal)
        return goal

    def delete_goal(self, id):
        goal = self.get_by_id(id)
        if goal:
            self.delete(goal)
        return goal

    # ================= TRANSACTIONS =================

    def add_transaction(self, goal_id, amount, description=None):
        """
        הפקדה (amount חיובי) או משיכה (amount שלילי).
        מעדכן אוטומטית את current_balance.
        """
        goal = self.get_by_id(goal_id)
        if not goal:
            return None

        txn = SavingsTransaction(
            goal_id=goal_id,
            amount=amount,
            description=description
        )
        goal.current_balance += amount

        self.session.add(txn)
        self.session.commit()
        self.session.refresh(txn)
        if goal.current_balance < 0:
            print(f"WARNING: Balance negative for savings '{goal.name}': {goal.current_balance}")
        return txn

    def deposit(self, goal_id, amount, description="הפקדה"):
        return self.add_transaction(goal_id, abs(amount), description)

    def withdraw(self, goal_id, amount, description="משיכה"):
        return self.add_transaction(goal_id, -abs(amount), description)

    def get_transactions(self, goal_id):
        return (
            self.session.query(SavingsTransaction)
            .filter_by(goal_id=goal_id)
            .order_by(SavingsTransaction.date.desc())
            .all()
        )

    def get_total_balance(self, user_id):
        """סך כל החסכונות של משתמש."""
        goals = self.get_by_user(user_id)
        return sum(g.current_balance for g in goals)

    def get_balances_map(self, user_id):
        """מחזיר dict: {goal_name: current_balance}"""
        goals = self.get_by_user(user_id)
        return {g.name: g.current_balance for g in goals}
