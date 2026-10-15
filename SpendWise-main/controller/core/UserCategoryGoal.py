from flask import Blueprint, request, jsonify, g
from db_connection import SessionLocal

from dto.core.UserCategoryGoalDto import (
    UserCategoryGoalCreateDTO
)

from services.core.UserCategoryGoalService import UserCategoryGoalService
from repositories.core.UserCategoryGoalRepository import UserCategoryGoalRepository


user_goal_blueprint = Blueprint(
    "user_goal",
    __name__,
    url_prefix="/user_goal"
)


def get_service():
    session = SessionLocal()
    repo = UserCategoryGoalRepository(session)
    service = UserCategoryGoalService(repo)
    return session, service


@user_goal_blueprint.route("", methods=["GET"])
def get_all():
    session, service = get_service()
    try:
        results = service.get_all()
        return jsonify([r.model_dump() for r in results])
    finally:
        session.close()


@user_goal_blueprint.route("/<int:id>", methods=["GET"])
def get_by_id(id):
    session, service = get_service()
    try:
        result = service.get_by_id(id)

        if not result:
            return jsonify({"message": "Not found"}), 404

        return jsonify(result.model_dump())
    finally:
        session.close()


@user_goal_blueprint.route("/user/<int:user_id>", methods=["GET"])
def get_by_user(user_id):
    session, service = get_service()
    try:
        results = service.get_by_user(user_id)
        return jsonify([r.model_dump() for r in results])
    finally:
        session.close()


@user_goal_blueprint.route("", methods=["POST"])
def create():
    session, service = get_service()
    try:
        data = request.get_json() or {}
        data["user_id"] = g.current_user.user_id
        dto = UserCategoryGoalCreateDTO.model_validate(data)

        result = service.create(dto)

        return jsonify(result.model_dump()), 201
    finally:
        session.close()


@user_goal_blueprint.route("/<int:id>", methods=["PUT"])
def update(id):
    session, service = get_service()
    try:
        data = request.get_json()

        result = service.update(id, data.get("target_amount"))

        if not result:
            return jsonify({"message": "Not found"}), 404

        return jsonify(result.model_dump())
    finally:
        session.close()


@user_goal_blueprint.route("/<int:id>", methods=["DELETE"])
def delete(id):
    session, service = get_service()
    try:
        success = service.delete(id)

        if not success:
            return jsonify({"message": "Not found"}), 404

        return jsonify({"success": True})
    finally:
        session.close()