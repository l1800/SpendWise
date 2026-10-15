from models.system.Recommendations import Recommendation
from repositories.base_repository import BaseRepository


class RecommendationRepository(BaseRepository):

    def create(self, obj_data: dict):
        obj = Recommendation(**obj_data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, recommendation_id: int):
        return (
            self.session.query(Recommendation)
            .filter_by(recommendation_id=recommendation_id)
            .first()
        )

    def get_all(self):
        return self.session.query(Recommendation).all()

    def get_by_user(self, user_id: int):
        return (
            self.session.query(Recommendation)
            .filter_by(user_id=user_id)
            .all()
        )

    def update(self, recommendation_id: int, **kwargs):
        obj = self.get_by_id(recommendation_id)
        if not obj:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete_by_id(self, recommendation_id: int):
        obj = self.get_by_id(recommendation_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False