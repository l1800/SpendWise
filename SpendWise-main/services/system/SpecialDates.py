from models.system.SpecialDate import SpecialDate
from repositories.system.SpecialDates import SpecialDateRepository
from dto.system.SpecialDateDto import SpecialDateCreateDTO


class SpecialDateService:

    def __init__(self, repo: SpecialDateRepository):
        self.repo = repo

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, type_id: int):
        return self.repo.get_by_id(type_id)

    def update(self, type_id: int, dto: SpecialDateCreateDTO):
        return self.repo.update(
            type_id,
            holiday_name=dto.holiday_name,
            start_date=dto.start_date,
            end_date=dto.end_date
        )

    def delete(self, type_id: int):
        return self.repo.delete_by_id(type_id)