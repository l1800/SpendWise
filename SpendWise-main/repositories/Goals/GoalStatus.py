# repositories/enums/goal_status_repository.py

from models.Goals.GoalStatus import GoalStatus
from repositories.base_repository import BaseRepository


class GoalStatusRepository(BaseRepository):

    def get_by_id(self, status_id):
        return (
            self.session.query(GoalStatus)
            .filter_by(status_id=status_id)
            .first()
        )

    def get_all(self):
        return self.session.query(GoalStatus).all()

    def update(self, status_id, **kwargs):
        status = self.get_by_id(status_id)

        if not status:
            return None

        for key, value in kwargs.items():
            setattr(status, key, value)

        self.session.commit()
        return status

    def delete_by_id(self, status_id):
        status = self.get_by_id(status_id)

        if status:
            self.delete(status)

        return status
