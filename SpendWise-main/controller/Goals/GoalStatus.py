# controllers/goal_status_controller.py

from flask import Blueprint, request, jsonify
from dto.Goals.GoalStatusDto import GoalStatusDTO
from services.Goals.GoalStatus import GoalStatusService
from repositories.Goals.GoalStatus import GoalStatusRepository
from db_connection import SessionLocal

session = SessionLocal()
repo = GoalStatusRepository(session)
service = GoalStatusService(repo)

goal_status_bp = Blueprint("goal_status", __name__)

# CREATE
@goal_status_bp.route('', methods=['POST'])
def create_status():
    dto = GoalStatusDTO(**request.get_json())
    status = service.create_status(dto)
    return jsonify({"status_id": status.status_id}), 201


# READ ALL
@goal_status_bp.route('', methods=['GET'])
def get_all():
    data = service.get_all()
    return jsonify([
        {
            "status_id": s.status_id,
            "status_name": s.status_name
        } for s in data
    ])


# READ BY ID
@goal_status_bp.route('/<int:status_id>', methods=['GET'])
def get_by_id(status_id):
    status = service.get_by_id(status_id)

    if not status:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        "status_id": status.status_id,
        "status_name": status.status_name
    })


# UPDATE
@goal_status_bp.route('/<int:status_id>', methods=['PUT'])
def update(status_id):
    dto = GoalStatusDTO(**request.get_json())
    status = service.update(status_id, dto)

    if not status:
        return jsonify({"error": "not found"}), 404

    return jsonify({"message": "updated"})


# DELETE
@goal_status_bp.route('/<int:status_id>', methods=['DELETE'])
def delete(status_id):
    status = service.delete(status_id)

    if not status:
        return jsonify({"error": "not found"}), 404

    return jsonify({"message": "deleted"})