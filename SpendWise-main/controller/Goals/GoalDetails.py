from flask import Blueprint, request, jsonify

from dto.Goals.GoalDetailsDto import GoalDetailsDto
from services.Goals.GoalDetails import GoalDetailsService
from repositories.Goals.GoalDetails import GoalDetailsRepository
from db_connection import SessionLocal

session = SessionLocal()

repo = GoalDetailsRepository(session)
service = GoalDetailsService(repo)

goal_details_blueprint = Blueprint(
    "goal_details",
    __name__, url_prefix='/goal_details'
)


@goal_details_blueprint.route('', methods=['POST'])
def add_detail():
    dto = GoalDetailsDto(**request.get_json())

    detail = service.add_detail(dto)

    return jsonify({
        "detail_id": detail.detail_id
    }), 201


@goal_details_blueprint.route('', methods=['GET'])
def get_details():
    details = service.get_all_details()

    return jsonify([
        {
            "detail_id": d.detail_id,
            "goal_id": d.goal_id,
            "goal_type_id": d.goal_type_id,
            "goal_description": d.goal_description,
            "goal_target_date": d.goal_target_date.isoformat(),
            "status_id": d.status_id
        }
        for d in details
    ])


@goal_details_blueprint.route('/<int:detail_id>', methods=['GET'])
def get_detail(detail_id):
    detail = service.get_detail_by_id(detail_id)

    if not detail:
        return jsonify({
            "error": "Goal detail not found"
        }), 404

    return jsonify({
        "detail_id": detail.detail_id,
        "goal_id": detail.goal_id,
        "goal_type_id": detail.goal_type_id,
        "goal_description": detail.goal_description,
        "goal_target_date": detail.goal_target_date.isoformat(),
        "status_id": detail.status_id
    })


@goal_details_blueprint.route('/goal/<int:goal_id>', methods=['GET'])
def get_details_by_goal(goal_id):
    details = service.get_details_by_goal(goal_id)

    return jsonify([
        {
            "detail_id": d.detail_id,
            "goal_id": d.goal_id,
            "goal_type_id": d.goal_type_id,
            "goal_description": d.goal_description,
            "goal_target_date": d.goal_target_date.isoformat(),
            "status_id": d.status_id
        }
        for d in details
    ])


@goal_details_blueprint.route('/<int:detail_id>', methods=['PUT'])
def update_detail(detail_id):
    dto = GoalDetailsDto(**request.get_json())

    detail = service.update_detail(
        detail_id,
        dto
    )

    if not detail:
        return jsonify({
            "error": "Goal detail not found"
        }), 404

    return jsonify({
        "message": "Goal detail updated"
    })


@goal_details_blueprint.route('/<int:detail_id>', methods=['DELETE'])
def delete_detail(detail_id):
    detail = service.delete_detail(detail_id)

    if not detail:
        return jsonify({
            "error": "Goal detail not found"
        }), 404

    return jsonify({
        "message": "Goal detail deleted"
    })