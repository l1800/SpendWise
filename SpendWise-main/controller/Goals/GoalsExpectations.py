# controllers/goals_expectations_controller.py
from flask import Blueprint, request, jsonify
from dto.Goals.GoalsExpectationsDto import GoalsExpectationsDto
from services.Goals.GoalsExpectations import GoalsExpectationsService
from repositories.Goals.GoalsExpectations import GoalsExpectationsRepository
from db_connection import SessionLocal

session = SessionLocal()
repo = GoalsExpectationsRepository(session)
service = GoalsExpectationsService(repo)

expectations_bp = Blueprint("goals_expectations", __name__)

@expectations_bp.route('', methods=['POST'])
def create_expectation():
    dto = GoalsExpectationsDto(**request.get_json())
    expectation = service.create_expectation(dto)
    return jsonify({"expectation_id": expectation.expectation_id}), 201

@expectations_bp.route('', methods=['GET'])
def get_all_expectations():
    expectations = service.get_all_expectations()
    return jsonify([{
        "expectation_id": e.expectation_id,
        "user_id": e.user_id,
        "goal_type_id": e.goal_type_id,
        "goal_description": e.goal_description,
        "goal_target_date": e.goal_target_date.isoformat(),
        "status_id": e.status_id,
        "goal_created_date": e.goal_created_date.isoformat()
    } for e in expectations])

@expectations_bp.route('/user/<int:user_id>', methods=['GET'])
def get_expectations_by_user(user_id):
    expectations = service.get_expectations_by_user(user_id)
    return jsonify([{
        "expectation_id": e.expectation_id,
        "user_id": e.user_id,
        "goal_type_id": e.goal_type_id,
        "goal_description": e.goal_description,
        "goal_target_date": e.goal_target_date.isoformat(),
        "status_id": e.status_id,
        "goal_created_date": e.goal_created_date.isoformat()
    } for e in expectations])

@expectations_bp.route('/<int:expectation_id>', methods=['PUT'])
def update_expectation(expectation_id):
    dto = GoalsExpectationsDto(**request.get_json())
    expectation = service.update_expectation(expectation_id, dto)
    if not expectation:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "updated"})

@expectations_bp.route('/<int:expectation_id>', methods=['DELETE'])
def delete_expectation(expectation_id):
    expectation = service.delete_expectation(expectation_id)
    if not expectation:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})