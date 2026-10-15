from models.core.Categories import Category
from repositories.base_repository import BaseRepository


class CategoriesRepository(BaseRepository):

    def create(self, category):
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)

        return category

    def get_by_id(self, category_id):
        return (
            self.session.query(Category)
            .filter_by(category_id=category_id)
            .first()
        )

    def get_all_categories(self):
        return self.session.query(Category).all()

    def update(self, category_id, **kwargs):
        category = self.get_by_id(category_id)

        if not category:
            return None

        for key, value in kwargs.items():
            setattr(category, key, value)

        self.session.commit()
        self.session.refresh(category)

        return category

    def delete_by_id(self, category_id):
        category = self.get_by_id(category_id)

        if not category:
            return None

        self.session.delete(category)
        self.session.commit()

        return category