from models.Goals.Goals import Goal
from repositories.base_repository import BaseRepository


class GoalsRepository(BaseRepository):

    def get_by_id(self, goal_id):
        return (
            self.session.query(Goal)
            .filter_by(goal_id=goal_id)
            .first()
        )

    def get_all(self):
        return self.session.query(Goal).all()

    def update(self, goal_id, **kwargs):
        goal = self.get_by_id(goal_id)

        if not goal:
            return None

        for key, value in kwargs.items():
            setattr(goal, key, value)

        self.session.commit()
        return goal

    def delete_by_id(self, goal_id):
        goal = self.get_by_id(goal_id)

        if goal:
            self.delete(goal)

        return goal
