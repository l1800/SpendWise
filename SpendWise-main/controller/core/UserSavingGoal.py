from flask import Blueprint, request, jsonify
from db_connection import SessionLocal

from services.core.UserSavingGoalService import UserSavingGoalService
from repositories.core.UserSavingGoalRepository import UserSavingGoalRepository
from dto.core.UserSavingGoalDTO import UserSavingGoalDTO


saving_blueprint = Blueprint("saving", __name__, url_prefix="/saving")


def get_service():
    session = SessionLocal()
    repo = UserSavingGoalRepository(session)
    service = UserSavingGoalService(repo)
    return session, service


@saving_blueprint.route('/goal', methods=['POST'])
def save_goal():

    session, service = get_service()

    try:
        data = request.get_json()

        dto = UserSavingGoalDTO(
            user_id=data["user_id"],
            saving_mode=data.get("saving_mode"),
            target_percent=data.get("target_percent"),
            target_amount=data.get("target_amount")
        )

        result = service.save_goal(dto)

        return jsonify({
            "message": "goal saved",
            "user_id": result.user_id,
            "saving_mode": result.saving_mode,
            "target_percent": result.target_percent,
            "target_amount": result.target_amount
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        session.close()


@saving_blueprint.route('/goal/<int:user_id>', methods=['GET'])
def get_goal(user_id):

    session, service = get_service()

    try:
        goal = service.get_goal(user_id)

        if not goal:
            return jsonify({"goal": None}), 200

        return jsonify({
            "user_id": goal.user_id,
            "saving_mode": goal.saving_mode,
            "target_percent": goal.target_percent,
            "target_amount": goal.target_amount
        }), 200

    finally:
        session.close()