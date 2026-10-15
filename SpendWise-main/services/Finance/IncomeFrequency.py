from dto.Finance.IncomeFrequencyDto import IncomeFrequencyDTO
from repositories.Finance.IncomeFrequency import IncomeFrequencyRepository
from models.Finance.IncomeFrequency import IncomeFrequency


class IncomeFrequencyService:
    def __init__(self, repository: IncomeFrequencyRepository):
        self.repo = repository



    def get_all_frequencies(self):
        return self.repo.get_all()

    def get_frequency_by_id(self, frequency_id: int):
        return self.repo.get_by_id(frequency_id)


    """
       def add_frequency(self, dto: IncomeFrequencyDTO) -> IncomeFrequency:
        frequency = IncomeFrequency(
            frequency_name=dto.frequency_name
        )

        self.repo.add(frequency)
        return frequency
      def update_frequency(self, frequency_id: int, dto: IncomeFrequencyDTO):
        return self.repo.update(
            frequency_id,
            frequency_name=dto.frequency_name
        )

    def delete_frequency(self, frequency_id: int):
        return self.repo.delete_by_id(frequency_id)
    
    """
