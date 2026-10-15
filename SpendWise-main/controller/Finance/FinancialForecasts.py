from flask import Blueprint, request, jsonify
from dto.Finance.FinancialForecastsDto import FinancialForecastCreateDto, FinancialForecastDto
from services.Finance.FinancialForecasts import FinancialForecastService
from repositories.Finance.FinancialForecasts import FinancialForecastsRepository
from db_connection import SessionLocal

# יצירת סשן
session = SessionLocal()
repo = FinancialForecastsRepository(session)
service = FinancialForecastService(repo)

financial_forecasts_blueprint = Blueprint('financial_forecasts', __name__, url_prefix='/financial_forecasts')


# --- CREATE ---
@financial_forecasts_blueprint.route('', methods=['POST'])
def add_forecast():
    dto = FinancialForecastCreateDto(**request.get_json())  # DTO מיוחד ליצירה
    forecast = service.add_forecast(dto)
    return jsonify({"forecast_id": forecast.forecast_id}), 201


# --- READ ALL ---
@financial_forecasts_blueprint.route('', methods=['GET'])
def get_forecasts():
    forecasts = service.get_all_forecasts()
    return jsonify([{
        "forecast_id": f.forecast_id,
        "user_id": f.user_id,
        "category_id": f.category_id,
        "forecast_date": f.forecast_date.isoformat(),
        "forecast_count": f.forecast_count,
        "range_id": f.range_id
    } for f in forecasts])


# --- READ BY USER ---
@financial_forecasts_blueprint.route('/user/<int:user_id>', methods=['GET'])
def get_forecasts_by_user(user_id):
    forecasts = service.get_forecasts_by_user(user_id)
    return jsonify([{
        "forecast_id": f.forecast_id,
        "category_id": f.category_id,
        "forecast_date": f.forecast_date.isoformat(),
        "forecast_count": f.forecast_count,
        "range_id": f.range_id
    } for f in forecasts])


# --- READ BY ID ---
@financial_forecasts_blueprint.route('/<int:forecast_id>', methods=['GET'])
def get_forecast(forecast_id):
    forecast = service.get_forecast_by_id(forecast_id)
    if not forecast:
        return jsonify({"error": "Forecast not found"}), 404
    return jsonify({
        "forecast_id": forecast.forecast_id,
        "user_id": forecast.user_id,
        "category_id": forecast.category_id,
        "forecast_date": forecast.forecast_date.isoformat(),
        "forecast_count": forecast.forecast_count,
        "range_id": forecast.range_id
    })


# --- UPDATE ---
@financial_forecasts_blueprint.route('/<int:forecast_id>', methods=['PUT'])
def update_forecast(forecast_id):
    dto = FinancialForecastCreateDto(**request.get_json())  # DTO ליצירה מתאים גם לעדכון
    forecast = service.update_forecast(forecast_id, dto)
    if not forecast:
        return jsonify({"error": "Forecast not found"}), 404
    return jsonify({"message": "Forecast updated"})


# --- DELETE ---
@financial_forecasts_blueprint.route('/<int:forecast_id>', methods=['DELETE'])
def delete_forecast(forecast_id):
    forecast = service.delete_forecast(forecast_id)
    if not forecast:
        return jsonify({"error": "Forecast not found"}), 404
    return jsonify({"message": "Forecast deleted"})