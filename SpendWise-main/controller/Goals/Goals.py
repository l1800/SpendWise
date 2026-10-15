# controllers/goals_controller.py
from flask import Blueprint, request, jsonify
from dto.Goals.GoalsDto import GoalCreateDTO, GoalResponseDTO
from services.Goals.Goals import GoalsService
from repositories.Goals.Goals import GoalsRepository
from db_connection import SessionLocal

# יצירת סשן ורפוזיטורי
session = SessionLocal()
goals_repo = GoalsRepository(session)
service = GoalsService(goals_repo)

# יצירת Blueprint
goals_bp = Blueprint("goals", __name__, url_prefix='/goals')

# ---------- Goals ----------
@goals_bp.route('', methods=['POST'])
def create_goal():
    dto = GoalCreateDTO(**request.get_json())
    goal = service.create_goal(dto)
    return jsonify({"goal_id": goal.goal_id}), 201

@goals_bp.route('', methods=['GET'])
def get_goals():
    data = service.get_all_goals()
    return jsonify([{
        "goal_id": g.goal_id,
        "user_id": g.user_id,
        "goal_created_date": g.goal_created_date.isoformat()
    } for g in data])

@goals_bp.route('/<int:goal_id>', methods=['GET'])
def get_goal(goal_id):
    goal = service.get_goal_by_id(goal_id)
    if not goal:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "goal_id": goal.goal_id,
        "user_id": goal.user_id,
        "goal_created_date": goal.goal_created_date.isoformat()
    })

@goals_bp.route('/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    dto = GoalCreateDTO(**request.get_json())
    goal = service.update_goal(goal_id, dto)
    if not goal:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "updated"})

@goals_bp.route('/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    goal = service.delete_goal(goal_id)
    if not goal:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})