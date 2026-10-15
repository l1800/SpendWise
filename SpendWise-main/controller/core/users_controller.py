from flask import Blueprint, request, jsonify

from dto.core.usersDto import UserCreateDTO, UserUpdateDTO
from services.core.Users import UsersService
from repositories.core.Users import UserRepository
from db_connection import SessionLocal

users_blueprint = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)


def get_service():
    db_session = SessionLocal()
    repo = UserRepository(db_session)
    service = UsersService(repo)

    return db_session, service


# ==================== יצירת משתמש (POST) ====================
@users_blueprint.route('', methods=['POST'])
def create_user():
    db_session, service = get_service()

    try:
        dto = UserCreateDTO(**request.get_json())
        user = service.create_user(dto)

        return jsonify({
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
        }), 201

    finally:
        db_session.close()


# ==================== קבלת כל המשתמשים (GET) ====================
@users_blueprint.route('', methods=['GET'])
def get_all_users():
    db_session, service = get_service()

    try:
        users = service.get_all_users()

        return jsonify([
            {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "join_date": user.join_date.isoformat() if user.join_date else None
            }
            for user in users
        ])

    finally:
        db_session.close()


# ==================== קבלת משתמש לפי ID (GET) ====================
@users_blueprint.route('/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    db_session, service = get_service()

    try:
        user = service.get_user_by_id(user_id)

        if user is None:
            return jsonify({"message": "User not found"}), 404

        return jsonify({
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "join_date": user.join_date.isoformat() if user.join_date else None
        })

    finally:
        db_session.close()


# ==================== עדכון משתמש (PUT) ====================
@users_blueprint.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    db_session, service = get_service()

    try:
        dto = UserUpdateDTO(**request.get_json())

        updated_user = service.update_user(user_id, dto)

        if updated_user is None:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"message": "User updated"})

    finally:
        db_session.close()


# ==================== מחיקת משתמש (DELETE) ====================
@users_blueprint.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_session, service = get_service()

    try:
        deleted_user = service.delete_user(user_id)

        if deleted_user is None:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"message": "User deleted"})

    finally:
        db_session.close()


# ==================== שם מלא של משתמש (GET) ====================
@users_blueprint.route('/<int:user_id>/full-name', methods=['GET'])
def get_user_full_name(user_id):
    db_session, service = get_service()

    try:
        full_name = service.get_user_full_name(user_id)

        if full_name is None:
            return jsonify({"message": "User not found"}), 404

        return jsonify({
            "user_id": user_id,
            "full_name": full_name
        })

    finally:
        db_session.close()