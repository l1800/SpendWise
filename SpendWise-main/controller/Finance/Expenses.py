from flask import Blueprint, request, jsonify, g
from dto.Finance.ExpensesDto import ExpenseCreateDTO, ExpenseResponseDTO
from services.Finance.Expenses import ExpenseService
from repositories.Finance.Expenses import ExpenseRepository
from repositories.system.MonthlyExpensesSummary import MonthlyExpensesSummaryRepository
from repositories.system.SpecialPeriodSummary import SpecialPeriodSummaryRepository
from services.system.MonthlyExpensesSummary import MonthlyExpensesSummaryService
from services.system.SpecialPeriodSummary import SpecialPeriodService
from db_connection import SessionLocal

expenses_blueprint = Blueprint('expenses', __name__, url_prefix='/expenses')


def get_service():
    session = SessionLocal()
    repo = ExpenseRepository(session)
    special_repo = SpecialPeriodSummaryRepository(session)
    summary_repo = MonthlyExpensesSummaryRepository(session)
    service = ExpenseService(
        repo,
        SpecialPeriodService(special_repo),
        MonthlyExpensesSummaryService(summary_repo)
    )
    return session, service


# ==================== יצירת הוצאה (POST) ====================
@expenses_blueprint.route('/', methods=['POST'])
def add_expense():
    session, service = get_service()
    try:
        payload = request.get_json() or {}
        payload["user_id"] = g.current_user.user_id
        dto = ExpenseCreateDTO(**payload)
        expense = service.add_expense(dto)
        return jsonify({"transaction_id": expense.transaction_id}), 201
    finally:
        session.close()


# ==================== קבלת כל ההוצאות (GET) ====================
@expenses_blueprint.route('/', methods=['GET'])
def get_expenses():
    session, service = get_service()
    try:
        expenses = service.get_all_expenses()
        return jsonify([ExpenseResponseDTO.from_orm(e).dict() for e in expenses])
    finally:
        session.close()


# ==================== קבלת הוצאה לפי ID (GET) ====================
@expenses_blueprint.route('/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    session, service = get_service()
    try:
        expense = service.get_expense_by_id(expense_id)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify(ExpenseResponseDTO.from_orm(expense).dict())
    finally:
        session.close()


# ==================== עדכון הוצאה (PUT) ====================
@expenses_blueprint.route('/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    session, service = get_service()
    try:
        payload = request.get_json() or {}
        payload["user_id"] = g.current_user.user_id
        dto = ExpenseCreateDTO(**payload)
        expense = service.update_expense(expense_id, dto)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify({"message": "Expense updated"})
    finally:
        session.close()


# ==================== מחיקת הוצאה (DELETE) ====================
@expenses_blueprint.route('/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    session, service = get_service()
    try:
        expense = service.delete_expense(expense_id)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify({"message": "Expense deleted"})
    finally:
        session.close()

