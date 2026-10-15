# repositories/goals/goal_types_repository.py

from models.Goals.GoalTypes import GoalType
from repositories.base_repository import BaseRepository


class GoalTypesRepository(BaseRepository):

    def get_by_id(self, goal_type_id):
        return (
            self.session.query(GoalType)
            .filter_by(goal_type_id=goal_type_id)
            .first()
        )

    def get_all(self):
        return self.session.query(GoalType).all()

    def update(self, goal_type_id, **kwargs):
        obj = self.get_by_id(goal_type_id)

        if not obj:
            return None

        for key, value in kwargs.items():
            setattr(obj, key, value)

        self.session.commit()
        return obj

    def delete_by_id(self, goal_type_id):
        obj = self.get_by_id(goal_type_id)

        if obj:
            self.delete(obj)

        return obj
