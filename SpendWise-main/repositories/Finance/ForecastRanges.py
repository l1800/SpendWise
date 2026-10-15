# repositories/enums/forecast_ranges_repository.py

from models.Finance.ForecastRanges import ForecastRange
from repositories.base_repository import BaseRepository


class ForecastRangesRepository(BaseRepository):

    def get_by_id(self, range_id):
        return (
            self.session.query(ForecastRange)
            .filter_by(range_id=range_id)
            .first()
        )

    def get_all(self):
        return self.session.query(ForecastRange).all()

    def update(self, range_id, **kwargs):
        forecast_range = self.get_by_id(range_id)

        if not forecast_range:
            return None

        for key, value in kwargs.items():
            setattr(forecast_range, key, value)

        self.session.commit()
        return forecast_range


