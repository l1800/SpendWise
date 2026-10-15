from flask import Blueprint, request, jsonify
from db_connection import SessionLocal

from services.core.SavingsGoalService import SavingsGoalService
from repositories.core.SavingsGoalRepository import SavingsGoalRepository
from dto.core.SavingsGoalDto import OneTimeExpenseDTO

savings_blueprint = Blueprint("savings", __name__, url_prefix="/savings")


def get_service():
    session = SessionLocal()
    repo = SavingsGoalRepository(session)
    service = SavingsGoalService(repo)
    return session, service


# ================= GOALS =================

@savings_blueprint.route("/goals", methods=["GET"])
def get_all():
    session, service = get_service()
    try:
        results = service.get_all()
        return jsonify([
            {"id": g.id, "user_id": g.user_id, "name": g.name,
             "category_id": g.category_id,
             "current_balance": g.current_balance, "target_amount": g.target_amount}
            for g in results
        ])
    finally:
        session.close()


@savings_blueprint.route("/goals/user/<int:user_id>", methods=["GET"])
def get_by_user(user_id):
    session, service = get_service()
    try:
        results = service.get_by_user(user_id)
        return jsonify([
            {"id": g.id, "name": g.name,
             "current_balance": g.current_balance, "target_amount": g.target_amount}
            for g in results
        ])
    finally:
        session.close()


@savings_blueprint.route("/goals", methods=["POST"])
def create_goal():
    session, service = get_service()
    try:
        data = request.get_json()
        goal = service.create_goal(
            user_id=data["user_id"],
            name=data["name"],
            target_amount=data.get("target_amount"),
            category_id=data.get("category_id")
        )
        return jsonify({"id": goal.id, "name": goal.name}), 201
    finally:
        session.close()


@savings_blueprint.route("/goals/<int:id>", methods=["DELETE"])
def delete_goal(id):
    session, service = get_service()
    try:
        service.delete_goal(id)
        return jsonify({"success": True})
    finally:
        session.close()


# ================= TRANSACTIONS =================

@savings_blueprint.route("/goals/<int:goal_id>/deposit", methods=["POST"])
def deposit(goal_id):
    session, service = get_service()
    try:
        data = request.get_json()
        txn = service.deposit(goal_id, data["amount"],
                              data.get("description", "הפקדה"))
        return jsonify({"id": txn.id, "amount": txn.amount, "description": txn.description}), 201
    finally:
        session.close()


@savings_blueprint.route("/goals/<int:goal_id>/withdraw", methods=["POST"])
def withdraw(goal_id):
    session, service = get_service()
    try:
        data = request.get_json()
        txn = service.withdraw(goal_id, data["amount"],
                               data.get("description", "משיכה"))
        return jsonify({"id": txn.id, "amount": txn.amount, "description": txn.description}), 201
    finally:
        session.close()


@savings_blueprint.route("/goals/<int:goal_id>/transactions", methods=["GET"])
def get_transactions(goal_id):
    session, service = get_service()
    try:
        txns = service.get_transactions(goal_id)
        return jsonify([
            {"id": t.id, "amount": t.amount, "description": t.description,
             "date": t.date.isoformat() if t.date else None}
            for t in txns
        ])
    finally:
        session.close()


@savings_blueprint.route("/balances/<int:user_id>", methods=["GET"])
def get_balances(user_id):
    session, service = get_service()
    try:
        balances = service.get_balances_map(user_id)
        return jsonify({"balances": balances, "total": sum(balances.values())})
    finally:
        session.close()


# ================= ONE-TIME EXPENSE =================

@savings_blueprint.route("/one-time-expense/check", methods=["POST"])
def check_one_time_expense():
    """
    שלב 1 — בדיקה לפני רישום הוצאה.
    POST JSON:
    {
        "user_id": 1,
        "category_id": 18,
        "amount": 3000
    }

    Response: {can_cover, balance, after, message}
    """
    session, service = get_service()
    try:
        data = request.get_json()
        result = service.check_savings_for_expense(
            user_id=data["user_id"],
            category_id=data["category_id"],
            amount=data["amount"]
        )
        return jsonify(result), 200
    finally:
        session.close()


@savings_blueprint.route("/one-time-expense/process", methods=["POST"])
def process_one_time_expense():
    """
    שלב 2 — ביצוע ההוצאה אחרי אישור המשתמש.
    POST JSON:
    {
        "user_id": 1,
        "category_id": 18,
        "amount": 3000,
        "description": "קניית ספה"
    }

    Response: {expense_id, amount, covered_by_savings, shortfall, fully_covered, message}
    """
    session, service = get_service()
    try:
        data = request.get_json()
        result = service.process_one_time_expense(
            user_id=data["user_id"],
            category_id=data["category_id"],
            amount=data["amount"],
            description=data.get("description")
        )
        return jsonify(result), 201
    finally:
        session.close()
