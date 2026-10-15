from models.core.CategoryStandard import CategoryStandard


class CategoryStandardService:

    def __init__(self, repo):
        self.repo = repo

    def get_all(self):
        return self.repo.get_all()

    def get_by_category(self, category_id):
        return self.repo.get_by_category(category_id)

    def create_standard(self, dto):

        obj = CategoryStandard(
            category_id=dto.category_id,
            amount_per_person=dto.amount_per_person,
            is_essential=dto.is_essential,
            rule_description=dto.rule_description
        )

        return self.repo.create(obj)

    def update_standard(self, benchmark_id, dto):

        obj = self.repo.get_by_id(benchmark_id)
        if not obj:
            return None

        obj.category_id = dto.category_id
        obj.amount_per_person = dto.amount_per_person
        obj.is_essential = dto.is_essential
        obj.rule_description = dto.rule_description

        return self.repo.update(obj)

    def delete_standard(self, benchmark_id):

        obj = self.repo.get_by_id(benchmark_id)
        if not obj:
            return False

        self.repo.delete(obj)
        return True