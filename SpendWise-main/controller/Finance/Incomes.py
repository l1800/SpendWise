from flask import Blueprint, request, jsonify, g

from dto.Finance.IncomesDto import IncomeCreateDTO, IncomeResponseDTO
from services.Finance.Incomes import IncomeService
from repositories.Finance.Incomes import IncomesRepository
from repositories.Finance.IncomeCategories import IncomeCategoriesRepository
from db_connection import SessionLocal
from models.Finance.Incomes import Income

# יצירת סשן
session = SessionLocal()

# רפוזיטורי של הכנסות
repo = IncomesRepository(session)

# רפוזיטורי של קטגוריות הכנסות
categories_repo = IncomeCategoriesRepository(session)

# יצירת שירות
service = IncomeService(repo, categories_repo)

# יצירת Blueprint
income_blueprint = Blueprint(
    "income",
    __name__, url_prefix='/income'
)


@income_blueprint.route('', methods=['POST'])
def add_income():
    payload = request.get_json() or {}
    payload["user_id"] = g.current_user.user_id
    dto = IncomeCreateDTO(**payload)
    income = service.add_income(dto)
    return jsonify({"transaction_id": income.transaction_id}), 201


@income_blueprint.route('', methods=['GET'])
def get_incomes():
    incomes = service.get_all_incomes()
    return jsonify([
        IncomeResponseDTO.model_validate(income).model_dump(mode="json")
        for income in incomes
    ])


@income_blueprint.route('/<int:transaction_id>', methods=['GET'])
def get_income(transaction_id):
    income = service.get_income_by_id(transaction_id)
    if not income:
        return jsonify({"error": "Income not found"}), 404
    return jsonify(IncomeResponseDTO.model_validate(income).model_dump(mode="json"))


@income_blueprint.route('/<int:transaction_id>', methods=['PUT'])
def update_income(transaction_id):
    payload = request.get_json() or {}
    payload["user_id"] = g.current_user.user_id
    dto = IncomeCreateDTO(**payload)
    income = service.update_income(transaction_id, dto)
    if not income:
        return jsonify({"error": "Income not found"}), 404
    return jsonify({"message": "Income updated"})


@income_blueprint.route('/<int:transaction_id>', methods=['DELETE'])
def delete_income(transaction_id):
    income = service.delete_income(transaction_id)
    if not income:
        return jsonify({"error": "Income not found"}), 404
    return jsonify({"message": "Income deleted"})