from dto.Finance.FinancialForecastsDto import FinancialForecastDto, FinancialForecastCreateDto
from repositories.Finance.FinancialForecasts import FinancialForecastsRepository
from models.Finance.FinancialForecasts import FinancialForecast


class FinancialForecastService:
    def __init__(self, repository: FinancialForecastsRepository):
        self.repo = repository

    # --- CREATE ---
    def add_forecast(self, dto: FinancialForecastCreateDto) -> FinancialForecast:
        forecast = FinancialForecast(
            user_id=dto.user_id,
            category_id=dto.category_id,
            forecast_date=dto.forecast_date,
            forecast_count=dto.forecast_count,
            range_id=dto.range_id
        )
        self.repo.add(forecast)
        return forecast

    # --- READ ALL ---
    def get_all_forecasts(self):
        return self.repo.get_all()

    # --- READ BY ID ---
    def get_forecast_by_id(self, forecast_id: int):
        return self.repo.get_by_id(forecast_id)

    # --- READ BY USER ---
    def get_forecasts_by_user(self, user_id: int):
        return self.repo.get_by_user(user_id)

    # --- UPDATE ---
    def update_forecast(self, forecast_id: int, dto: FinancialForecastCreateDto):
        forecast = self.repo.get_by_id(forecast_id)

        if not forecast:
            return None

        forecast.user_id = dto.user_id
        forecast.category_id = dto.category_id
        forecast.forecast_date = dto.forecast_date
        forecast.forecast_count = dto.forecast_count
        forecast.range_id = dto.range_id

        self.repo.session.commit()
        return forecast

    # --- DELETE ---
    def delete_forecast(self, forecast_id: int):
        return self.repo.delete_by_id(forecast_id)