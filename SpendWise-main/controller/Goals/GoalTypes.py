# controllers/goal_types_controller.py

from flask import Blueprint, request, jsonify

from dto.Goals.GoalTypesDto import GoalTypesDto
from services.Goals.GoalTypes import GoalTypesService
from repositories.Goals.GoalTypes import GoalTypesRepository
from db_connection import SessionLocal

session = SessionLocal()
repo = GoalTypesRepository(session)
service = GoalTypesService(repo)

goal_types_bp = Blueprint("goal_types", __name__)


@goal_types_bp.route('', methods=['POST'])
def create():
    dto = GoalTypesDto(**request.get_json())
    obj = service.create_goal_type(dto)
    return jsonify({"goal_type_id": obj.goal_type_id}), 201


@goal_types_bp.route('', methods=['GET'])
def get_all():
    data = service.get_all()
    return jsonify([
        {
            "goal_type_id": g.goal_type_id,
            "goal_type_name": g.goal_type_name
        } for g in data
    ])


@goal_types_bp.route('/<int:goal_type_id>', methods=['GET'])
def get_by_id(goal_type_id):
    obj = service.get_by_id(goal_type_id)

    if not obj:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        "goal_type_id": obj.goal_type_id,
        "goal_type_name": obj.goal_type_name
    })


@goal_types_bp.route('/<int:goal_type_id>', methods=['PUT'])
def update(goal_type_id):
    dto = GoalTypesDto(**request.get_json())
    obj = service.update(goal_type_id, dto)

    if not obj:
        return jsonify({"error": "not found"}), 404

    return jsonify({"message": "updated"})


@goal_types_bp.route('/<int:goal_type_id>', methods=['DELETE'])
def delete(goal_type_id):
    obj = service.delete(goal_type_id)

    if not obj:
        return jsonify({"error": "not found"}), 404

    return jsonify({"message": "deleted"})