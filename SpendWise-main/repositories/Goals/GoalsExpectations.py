# repositories/goals/goals_expectations_repository.py

from models.Goals.GoalsExpectations import GoalExpectation
from repositories.base_repository import BaseRepository


class GoalsExpectationsRepository(BaseRepository):

    def get_by_id(self, expectation_id):
        return (
            self.session.query(GoalExpectation)
            .filter_by(expectation_id=expectation_id)
            .first()
        )

    def get_all(self):
        return self.session.query(GoalExpectation).all()

    def get_by_user(self, user_id):
        return (
            self.session.query(GoalExpectation)
            .filter_by(user_id=user_id)
            .all()
        )

    def update(self, expectation_id, **kwargs):
        obj = self.get_by_id(expectation_id)

        if not obj:
            return None

        for key, value in kwargs.items():
            setattr(obj, key, value)

        self.session.commit()
        return obj

    def delete_by_id(self, expectation_id):
        obj = self.get_by_id(expectation_id)

        if obj:
            self.delete(obj)

        return obj
