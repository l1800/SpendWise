from dto.Finance.ForecastRangesDto import ForecastRangeDTO
from repositories.Finance.ForecastRanges import ForecastRangesRepository
from models.Finance.ForecastRanges import ForecastRange


class ForecastRangeService:
    def __init__(self, repository: ForecastRangesRepository):
        self.repo = repository

    def add_range(self, dto: ForecastRangeDTO) -> ForecastRange:
        forecast_range = ForecastRange(
            range_name=dto.range_name
        )

        self.repo.add(forecast_range)
        return forecast_range

    def get_all_ranges(self):
        return self.repo.get_all()

    def get_range_by_id(self, range_id: int):
        return self.repo.get_by_id(range_id)

    def update_range(self, range_id: int, dto: ForecastRangeDTO):
        return self.repo.update(
            range_id,
            range_name=dto.range_name
        )

