# repositories/enums/income_frequency_repository.py

from models.Finance.IncomeFrequency import IncomeFrequency
from repositories.base_repository import BaseRepository


class IncomeFrequencyRepository(BaseRepository):

    def get_by_id(self, frequency_id):
        return (
            self.session.query(IncomeFrequency)
            .filter_by(frequency_id=frequency_id)
            .first()
        )

    def get_all(self):
        return self.session.query(IncomeFrequency).all()


    """
     def update(self, frequency_id, **kwargs):
        frequency = self.get_by_id(frequency_id)

        if not frequency:
            return None

        for key, value in kwargs.items():
            setattr(frequency, key, value)

        self.session.commit()
        return frequency

    def delete_by_id(self, frequency_id):
        frequency = self.get_by_id(frequency_id)

        if frequency:
            self.delete(frequency)

        return frequency
    """
