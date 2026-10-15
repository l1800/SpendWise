# services/goal_types_service.py

from dto.Goals.GoalTypesDto import GoalTypesDto
from repositories.Goals.GoalTypes import GoalTypesRepository
from models.Goals.GoalTypes import GoalType


class GoalTypesService:
    def __init__(self, repo: GoalTypesRepository):
        self.repo = repo

    def create_goal_type(self, dto: GoalTypesDto):
        goal_type = GoalType(
            goal_type_name=dto.goal_type_name
        )
        self.repo.add(goal_type)
        return goal_type

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, goal_type_id: int):
        return self.repo.get_by_id(goal_type_id)

    def update(self, goal_type_id: int, dto: GoalTypesDto):
        return self.repo.update(
            goal_type_id,
            goal_type_name=dto.goal_type_name
        )

    def delete(self, goal_type_id: int):
        return self.repo.delete_by_id(goal_type_id)
