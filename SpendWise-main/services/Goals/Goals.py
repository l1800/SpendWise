# services/goals_service.py
from dto.Goals.GoalsDto import GoalCreateDTO, GoalResponseDTO
from repositories.Goals.Goals import GoalsRepository
from models.Goals.Goals import Goal


class GoalsService:
    def __init__(self, goals_repo: GoalsRepository):
        self.goals_repo = goals_repo

    # Goals
    def create_goal(self, dto: GoalCreateDTO):
        goal = Goal(
            user_id=dto.user_id,
            goal_created_date=dto.goal_created_date
        )
        self.goals_repo.add(goal)
        return goal

    def get_all_goals(self):
        return self.goals_repo.get_all()

    def get_goal_by_id(self, goal_id: int):
        return self.goals_repo.get_by_id(goal_id)

    def update_goal(self, goal_id: int, dto: GoalCreateDTO):
        return self.goals_repo.update(
            goal_id,
            user_id=dto.user_id,
            goal_created_date=dto.goal_created_date
        )

    def delete_goal(self, goal_id: int):
        return self.goals_repo.delete_by_id(goal_id)

