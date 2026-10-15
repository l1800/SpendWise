from dto.Finance.IncomeCategories import IncomeCategoryCreateDTO
from models.Finance.IncomeCategory import IncomeCategory
from repositories.Finance.IncomeCategories import IncomeCategoriesRepository

class IncomeCategoryService:
    def __init__(self, repository: IncomeCategoriesRepository):
        self.repo = repository

    def create_category(self, dto: IncomeCategoryCreateDTO) -> IncomeCategory:
        category = IncomeCategory(category_name=dto.category_name)
        self.repo.add(category)
        return category

    def get_all_categories(self):
        return self.repo.get_all()

    def get_category_by_id(self, category_id: int):
        return self.repo.get_by_id(category_id)

    def update_category(self, category_id: int, dto: IncomeCategoryCreateDTO):
        return self.repo.update(category_id, category_name=dto.category_name)

    def delete_category(self, category_id: int):
        return self.repo.delete_by_id(category_id)