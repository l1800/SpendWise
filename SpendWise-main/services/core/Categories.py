from models.core.Categories import Category


class CategoriesService:

    def __init__(self, repo):
        self.repo = repo

    def add_category(self, dto):

        category = Category(
            category_name=dto.category_name,
            category_type_id=dto.category_type_id,
            category_description=dto.category_description,
            user_id=dto.user_id
        )

        return self.repo.create(category)

    def get_all_categories(self):
        return self.repo.get_all_categories()

    def get_category_by_id(self, category_id):
        return self.repo.get_by_id(category_id)

    def update_category(self, category_id, dto):

        return self.repo.update(
            category_id,
            category_name=dto.category_name,
            category_type_id=dto.category_type_id,
            category_description=dto.category_description,
            user_id=dto.user_id
        )

    def delete_category(self, category_id):
        return self.repo.delete_by_id(category_id)