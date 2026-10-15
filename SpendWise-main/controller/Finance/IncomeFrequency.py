from flask import Blueprint, request, jsonify

from dto.Finance.IncomeFrequencyDto import IncomeFrequencyDTO
from services.Finance.IncomeFrequency import IncomeFrequencyService
from repositories.Finance.IncomeFrequency import (
    IncomeFrequencyRepository
)
from db_connection import SessionLocal

session = SessionLocal()

repo = IncomeFrequencyRepository(session)
service = IncomeFrequencyService(repo)

income_frequency_blueprint = Blueprint(
    "income_frequency",
    __name__, url_prefix='/income_frequency'
)




@income_frequency_blueprint.route('', methods=['GET'])
def get_frequencies():
    frequencies = service.get_all_frequencies()

    return jsonify([
        {
            "frequency_id": f.frequency_id,
            "frequency_name": f.frequency_name
        }
        for f in frequencies
    ])


@income_frequency_blueprint.route('/<int:frequency_id>', methods=['GET'])
def get_frequency(frequency_id):
    frequency = service.get_frequency_by_id(frequency_id)

    if not frequency:
        return jsonify({
            "error": "Frequency not found"
        }), 404

    return jsonify({
        "frequency_id": frequency.frequency_id,
        "frequency_name": frequency.frequency_name
    })
"""
@income_frequency_blueprint.route('', methods=['POST'])
def add_frequency():
    dto = IncomeFrequencyDTO(**request.get_json())

    frequency = service.add_frequency(dto)

    return jsonify({
        "frequency_id": frequency.frequency_id
    }), 201

@income_frequency_blueprint.route('/<int:frequency_id>', methods=['PUT'])
def update_frequency(frequency_id):
    dto = IncomeFrequencyDTO(**request.get_json())

    frequency = service.update_frequency(
        frequency_id,
        dto
    )

    if not frequency:
        return jsonify({
            "error": "Frequency not found"
        }), 404

    return jsonify({
        "message": "Frequency updated"
    })


@income_frequency_blueprint.route('/<int:frequency_id>', methods=['DELETE'])
def delete_frequency(frequency_id):
    frequency = service.delete_frequency(frequency_id)

    if not frequency:
        return jsonify({
            "error": "Frequency not found"
        }), 404

    return jsonify({
        "message": "Frequency deleted"
    })
"""

