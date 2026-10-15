from models.Finance.IncomeCategory import IncomeCategory
from repositories.base_repository import BaseRepository

class IncomeCategoriesRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session)
        self.model = IncomeCategory

    def get_by_id(self, category_id):
        return self.session.query(IncomeCategory).filter_by(category_id=category_id).first()

    def get_all(self):
        return self.session.query(IncomeCategory).all()

    def update(self, category_id, **kwargs):
        category = self.get_by_id(category_id)
        if not category:
            return None
        for key, value in kwargs.items():
            setattr(category, key, value)
        self.session.commit()
        return category

    def delete_by_id(self, category_id):
        category = self.get_by_id(category_id)
        if category:
            self.delete(category)
        return category