class UserSavingGoalService:

    def __init__(self, repo):
        self.repo = repo

    def save_goal(self, dto):
        return self.repo.upsert(dto)

    def get_goal(self, user_id):
        return self.repo.get_by_user(user_id)

    # =========================
    # לוגיקה לשימוש ב־#10
    # =========================
    def calculate_saving_target(self, goal, net_budget):

        if not goal:
            return 0

        if goal.target_amount:
            return goal.target_amount

        if goal.target_percent:
            return net_budget * (goal.target_percent / 100)

        if goal.saving_mode == "HIGH":
            return net_budget * 0.15

        if goal.saving_mode == "MEDIUM":
            return net_budget * 0.08

        if goal.saving_mode == "LOW":
            return net_budget * 0.03

        return 0