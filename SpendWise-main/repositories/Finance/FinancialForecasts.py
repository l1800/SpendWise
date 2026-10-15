# repositories/reports_forecasts/financial_forecasts_repository.py

from models.Finance.FinancialForecasts import FinancialForecast
from repositories.base_repository import BaseRepository


class FinancialForecastsRepository(BaseRepository):

    def get_by_id(self, forecast_id):
        return (
            self.session.query(FinancialForecast)
            .filter_by(forecast_id=forecast_id)
            .first()
        )

    def get_all(self):
        return self.session.query(FinancialForecast).all()

    def get_by_user(self, user_id):
        return (
            self.session.query(FinancialForecast)
            .filter_by(user_id=user_id)
            .all()
        )

    def update(self, forecast_id, **kwargs):
        forecast = self.get_by_id(forecast_id)

        if not forecast:
            return None

        for key, value in kwargs.items():
            setattr(forecast, key, value)

        self.session.commit()
        return forecast

    def delete_by_id(self, forecast_id):
        forecast = self.get_by_id(forecast_id)

        if forecast:
            self.delete(forecast)

        return forecast
