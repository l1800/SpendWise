# repositories/enums/category_types_repository.py

# נכון
from models.lookups.CategogyType import CategoryType
from repositories.base_repository import BaseRepository


class CategoryTypesRepository(BaseRepository):

    def get_by_id(self, category_type_id):
        return (
            self.session.query(CategoryType)
            .filter_by(category_type_id=category_type_id)
            .first()
        )

    def get_all(self):
        return self.session.query(CategoryType).all()


    """
      def update(self, category_type_id, **kwargs):
        category_type = self.get_by_id(category_type_id)

        if not category_type:
            return None

        for key, value in kwargs.items():
            setattr(category_type, key, value)

        self.session.commit()
        return category_type

    def delete_by_id(self, category_type_id):
        category_type = self.get_by_id(category_type_id)

        if category_type:
            self.delete(category_type)

        return category_type
    """