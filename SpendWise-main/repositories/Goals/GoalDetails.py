# repositories/goals/goal_details_repository.py
from models.Goals.GoalDetails import GoalDetail
from repositories.base_repository import BaseRepository


class GoalDetailsRepository(BaseRepository):

    def get_by_id(self, detail_id):
        return (
            self.session.query(GoalDetail)
            .filter_by(detail_id=detail_id)
            .first()
        )


    def get_all(self):
        return self.session.query(GoalDetail).all()

    def get_by_goal(self, goal_id):
        return (
            self.session.query(GoalDetail)
            .filter_by(goal_id=goal_id)
            .all()
        )

    def update(self, detail_id, **kwargs):
        detail = self.get_by_id(detail_id)

        if not detail:
            return None

        for key, value in kwargs.items():
            setattr(detail, key, value)

        self.session.commit()
        return detail

    def delete_by_id(self, detail_id):
        detail = self.get_by_id(detail_id)

        if detail:
            self.delete(detail)

        return detail
