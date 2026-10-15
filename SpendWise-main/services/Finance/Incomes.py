from dto.Finance.IncomesDto import IncomeCreateDTO
from repositories.Finance.Incomes import IncomesRepository

class IncomeService:
    def __init__(self, repository: IncomesRepository, categories_repo):
        self.repo = repository
        self.categories_repo = categories_repo

    def add_income(self, dto: IncomeCreateDTO):
        income = self.repo.model(  # יוצרים את האובייקט SQLAlchemy
            user_id=dto.user_id,
            frequency_id=dto.frequency_id,
            category_id=dto.category_id,
            amount=dto.amount,
            date=dto.date
        )
        self.repo.add(income)
        return income

    def get_all_incomes(self):
        return self.repo.get_all()

    def get_income_by_id(self, transaction_id: int):
        return self.repo.get_by_id(transaction_id)

    def update_income(self, transaction_id: int, dto: IncomeCreateDTO):
        return self.repo.update(
            transaction_id,
            user_id=dto.user_id,
            frequency_id=dto.frequency_id,
            category_id=dto.category_id,
            amount=dto.amount,
            date=dto.date
        )

    def delete_income(self, transaction_id: int):
        return self.repo.delete_by_id(transaction_id)

    def get_total_income(self, user_id):
        incomes = self.repo.get_by_user(user_id)
        return sum(i.amount for i in incomes)

    def get_incomes_by_category(self, user_id):
        incomes = self.repo.get_by_user(user_id)
        categories = {}
        for i in incomes:
            cat_name = self.categories_repo.get_by_id(i.category_id).category_name
            categories[cat_name] = categories.get(cat_name, 0) + i.amount
        return categories