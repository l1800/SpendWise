# services/goal_status_service.py

from dto.Goals.GoalStatusDto import GoalStatusDTO
from repositories.Goals.GoalStatus import GoalStatusRepository
from models.Goals.GoalStatus import GoalStatus


class GoalStatusService:
    def __init__(self, repo: GoalStatusRepository):
        self.repo = repo

    def create_status(self, dto: GoalStatusDTO):
        status = GoalStatus(
            status_name=dto.status_name
        )
        self.repo.add(status)
        return status

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, status_id: int):
        return self.repo.get_by_id(status_id)

    def update(self, status_id: int, dto: GoalStatusDTO):
        return self.repo.update(
            status_id,
            status_name=dto.status_name
        )

    def delete(self, status_id: int):
        return self.repo.delete_by_id(status_id)
