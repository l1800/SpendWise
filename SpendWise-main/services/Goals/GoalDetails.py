from dto.Goals.GoalDetailsDto import GoalDetailsDto
from repositories.Goals.GoalDetails import GoalDetailsRepository
from models.Goals.GoalDetails import GoalDetail


class GoalDetailsService:
    def __init__(self, repository: GoalDetailsRepository):
        self.repo = repository

    def add_detail(self, dto: GoalDetailsDto) -> GoalDetail:
        detail = GoalDetail(
            goal_id=dto.goal_id,
            goal_type_id=dto.goal_type_id,
            goal_description=dto.goal_description,
            goal_target_date=dto.goal_target_date,
            status_id=dto.status_id
        )

        self.repo.add(detail)
        return detail

    def get_all_details(self):
        return self.repo.get_all()

    def get_detail_by_id(self, detail_id: int):
        return self.repo.get_by_id(detail_id)

    def get_details_by_goal(self, goal_id: int):
        return self.repo.get_by_goal(goal_id)

    def update_detail(self, detail_id: int, dto: GoalDetailsDto):
        return self.repo.update(
            detail_id,
            goal_id=dto.goal_id,
            goal_type_id=dto.goal_type_id,
            goal_description=dto.goal_description,
            goal_target_date=dto.goal_target_date,
            status_id=dto.status_id
        )

    def delete_detail(self, detail_id: int):
        return self.repo.delete_by_id(detail_id)
