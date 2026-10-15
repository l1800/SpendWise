# services/category_types_service.py

from dto.lookups.CategogyTypeDto import CategoryTypeDTO
from repositories.lookups.CategoryTypes import CategoryTypesRepository
from models.lookups.CategogyType import CategoryType


class CategoryTypesService:
    def __init__(self, repo: CategoryTypesRepository):
        self.repo = repo



    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, category_type_id: int):
        return self.repo.get_by_id(category_type_id)


    """
        def update(self, category_type_id: int, dto: CategoryTypeDTO):
        return self.repo.update(
            category_type_id,
            category_type_name=dto.category_type_name
        )

    def delete(self, category_type_id: int):
        return self.repo.delete_by_id(category_type_id)
       def create(self, dto: CategoryTypeDTO):
        obj = CategoryType(
            category_type_name=dto.category_type_name
        )
        self.repo.add(obj)
        return obj
    """