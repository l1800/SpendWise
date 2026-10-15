class SavingsGoalService:

    def __init__(self, repo):
        self.repo = repo

    # ================= GOALS =================

    def get_all(self):
        return self.repo.get_all()

    def get_by_user(self, user_id):
        return self.repo.get_by_user(user_id)

    def create_goal(self, user_id, name, target_amount=None, category_id=None):
        return self.repo.create_goal(user_id, name, target_amount, category_id)

    def delete_goal(self, id):
        return self.repo.delete_goal(id)

    # ================= TRANSACTIONS =================

    def deposit(self, goal_id, amount, description="הפקדה"):
        return self.repo.deposit(goal_id, amount, description)

    def withdraw(self, goal_id, amount, description="משיכה"):
        return self.repo.withdraw(goal_id, amount, description)

    def get_transactions(self, goal_id):
        return self.repo.get_transactions(goal_id)

    def get_total_balance(self, user_id):
        return self.repo.get_total_balance(user_id)

    def get_balances_map(self, user_id):
        return self.repo.get_balances_map(user_id)

    # ================= ONE-TIME EXPENSE =================

    def check_savings_for_expense(self, user_id, category_id, amount):
        """
        שלב 1 — בדיקה לפני שההוצאה נרשמת.
        מחפש Savings_Goals עם category_id תואם.
        מחזיר:
        - can_cover: bool — האם יש מספיק
        - goal: האובייקט או None
        - balance: יתרה נוכחית
        - after: מה תהיה היתרה אחרי
        - message: טקסט למשתמש
        """
        goals = self.repo.get_by_user(user_id)
        goal = next((g for g in goals if g.category_id == category_id), None)

        if not goal:
            return {
                "can_cover": False,
                "goal_name": None,
                "goal_id": None,
                "balance": 0,
                "after": 0,
                "message": "אין חיסכון לקטגוריה זו",
            }

        if goal.current_balance >= amount:
            return {
                "can_cover": True,
                "goal_name": goal.name,
                "goal_id": goal.id,
                "balance": goal.current_balance,
                "after": goal.current_balance - amount,
                "message": f"יש לך {goal.current_balance}₪ בחיסכון '{goal.name}'. "
                           f"אם תוציא {amount}₪, תישאר יתרה של {goal.current_balance - amount}₪.",
            }

        return {
            "can_cover": False,
            "goal_name": goal.name,
            "goal_id": goal.id,
            "balance": goal.current_balance,
            "after": 0,
            "message": f"אזהרה: אין מספיק בחיסכון '{goal.name}'. "
                       f"יתרה: {goal.current_balance}₪, נדרש: {amount}₪. "
                       f"חסר {amount - goal.current_balance}₪.",
        }

    def process_one_time_expense(self, user_id, category_id, amount, description=None):
        """
        שלב 2 — אחרי שהמשתמש אישר, מבצע את ההוצאה.
        1. בודק יתרה
        2. מושך מה-goal את מה שאפשר
        3. יוצר רשומת Expense עם is_one_time=True, covered_by_savings=...
        4. מחזיר את תוצאת ההוצאה
        """
        from datetime import date
        from models.Finance.Expenses import Expense

        # resolve the goal from DB
        goal_id = check.get("goal_id")
        goal = None
        if goal_id:
            goal = self.repo.get_by_id(goal_id)

        covered = 0
        if goal and goal.current_balance > 0:
            covered = min(goal.current_balance, amount)
            self.repo.withdraw(goal.id, covered,
                               description=description or f"הוצאה חד-פעמית — {goal.name}")

        shortfall = amount - covered

        # create expense record
        expense = Expense(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            date=date.today(),
            is_one_time=True,
            covered_by_savings=(covered == amount),
            savings_goal_id=goal.id if goal else None,
        )

        # need separate session handling — the repo's session
        self.repo.session.add(expense)
        self.repo.session.commit()
        self.repo.session.refresh(expense)

        return {
            "expense_id": expense.transaction_id,
            "amount": amount,
            "covered_by_savings": covered,
            "shortfall": shortfall,
            "fully_covered": covered == amount,
            "goal_name": check.get("goal_name"),
            "message": check["message"],
        }
