from models.system.HolidayCategorySummary import HolidayCategorySummary
from repositories.base_repository import BaseRepository

class HolidayCategorySummaryRepository(BaseRepository):

    def get_by_id(self, summary_id):
        return (
            self.session.query(HolidayCategorySummary)
            .filter_by(summary_id=summary_id)
            .first()
        )

    def get_all(self):
        return self.session.query(HolidayCategorySummary).all()

    def get_by_user(self, user_id):
        return (
            self.session.query(HolidayCategorySummary)
            .filter_by(user_id=user_id)
            .all()
        )

    def get_by_user_and_category(self, user_id, category_id):
        return (
            self.session.query(HolidayCategorySummary)
            .filter_by(user_id=user_id, category_id=category_id)
            .first()
        )

    def update(self, summary_id, **kwargs):
        summary = self.get_by_id(summary_id)
        if not summary:
            return None
        for key, value in kwargs.items():
            setattr(summary, key, value)
        self.session.commit()
        return summary

    def delete_by_id(self, summary_id):
        summary = self.get_by_id(summary_id)
        if summary:
            self.delete(summary)
        return summary

    # --- פונקציית create שנוספה ---
    def create(self, obj_data: dict):
        obj = HolidayCategorySummary(**obj_data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj