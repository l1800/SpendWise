from flask import Blueprint, request, jsonify
from dto.Finance.ExpenseTypeDto import ExpenseTypeDTO, ExpenseTypeCreateDTO
from services.Finance.ExpenseTypes import ExpenseTypeService
from repositories.Finance.ExpenseTypes import ExpenseTypesRepository
from db_connection import SessionLocal

# יצירת סשן
session = SessionLocal()
repo = ExpenseTypesRepository(session)
service = ExpenseTypeService(repo)

expense_types_blueprint = Blueprint('expense_types', __name__, url_prefix='/expense_types')

# ==================== CREATE ====================
@expense_types_blueprint.route('', methods=['POST'])
def add_expense_type():
    dto = ExpenseTypeCreateDTO(**request.get_json())
    expense_type = service.add_expense_type(dto)
    return jsonify({"ExpenseTypeId": expense_type.expenseTypeId}), 201

# ==================== GET ALL ====================
@expense_types_blueprint.route('', methods=['GET'])
def get_expense_types():
    types = service.get_all_expense_types()
    return jsonify([
        {"ExpenseTypeId": t.expenseTypeId, "ExpenseTypeName": t.expenseTypeName}
        for t in types
    ])

# ==================== GET BY ID ====================
@expense_types_blueprint.route('/<int:type_id>', methods=['GET'])
def get_expense_type(type_id):
    expense_type = service.get_expense_type_by_id(type_id)
    if not expense_type:
        return jsonify({"error": "Expense type not found"}), 404
    return jsonify({"ExpenseTypeId": expense_type.expenseTypeId, "ExpenseTypeName": expense_type.expenseTypeName})

# ==================== UPDATE ====================
@expense_types_blueprint.route('/<int:type_id>', methods=['PUT'])
def update_expense_type(type_id):
    dto = ExpenseTypeCreateDTO(**request.get_json())
    expense_type = service.update_expense_type(type_id, dto)
    if not expense_type:
        return jsonify({"error": "Expense type not found"}), 404
    return jsonify({"message": "Expense type updated"})

# ==================== DELETE ====================
@expense_types_blueprint.route('/<int:type_id>', methods=['DELETE'])
def delete_expense_type(type_id):
    expense_type = service.delete_expense_type(type_id)
    if not expense_type:
        return jsonify({"error": "Expense type not found"}), 404
    return jsonify({"message": "Expense type deleted"})