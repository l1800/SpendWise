from flask import Blueprint, request, jsonify

from dto.Finance.ForecastRangesDto import ForecastRangeDTO
from services.Finance.ForecastRanges import ForecastRangeService
from repositories.Finance.ForecastRanges import ForecastRangesRepository
from db_connection import SessionLocal

session = SessionLocal()

repo = ForecastRangesRepository(session)
service = ForecastRangeService(repo)

forecast_ranges_blueprint = Blueprint(
    'forecast_ranges',
    __name__, url_prefix='/forecast_ranges'
)

@forecast_ranges_blueprint.route('', methods=['POST'])
def add_range():
    dto = ForecastRangeDTO(**request.get_json())

    forecast_range = service.add_range(dto)

    return jsonify({
        "range_id": forecast_range.range_id
    }), 201

@forecast_ranges_blueprint.route('', methods=['GET'])
def get_ranges():
    ranges = service.get_all_ranges()

    return jsonify([
        {
            "range_id": r.range_id,
            "range_name": r.range_name
        }
        for r in ranges
    ])


@forecast_ranges_blueprint.route('/<int:range_id>', methods=['GET'])
def get_range(range_id):
    forecast_range = service.get_range_by_id(range_id)

    if not forecast_range:
        return jsonify({
            "error": "Range not found"
        }), 404

    return jsonify({
        "range_id": forecast_range.range_id,
        "range_name": forecast_range.range_name
    })


@forecast_ranges_blueprint.route('/<int:range_id>', methods=['PUT'])
def update_range(range_id):
    dto = ForecastRangeDTO(**request.get_json())

    forecast_range = service.update_range(
        range_id,
        dto
    )

    if not forecast_range:
        return jsonify({
            "error": "Range not found"
        }), 404

    return jsonify({
        "message": "Range updated"
    })


