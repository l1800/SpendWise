from flask import Blueprint, request, jsonify

from dto.core.UserCategoryPreferenceCreateDTO import (
    UserCategoryPreferenceCreateDTO
)

from services.core.UserCategoryPreferenceService import UserCategoryPreferenceService
from repositories.core.UserCategoryPreferenceRepository import UserCategoryPreferenceRepository
from db_connection import SessionLocal


user_preferences_blueprint = Blueprint(
    "user_preferences",
    __name__,
    url_prefix="/user-preferences"
)


def get_service():
    session = SessionLocal()

    repo = UserCategoryPreferenceRepository(session)
    service = UserCategoryPreferenceService(repo)
    print("USER PREF BLUEPRINT LOADED")
    return session, service


@user_preferences_blueprint.route('', methods=['POST'])
def set_preferences():

    session, service = get_service()

    try:
        data = request.get_json()

        dto_list = [
            UserCategoryPreferenceCreateDTO(**item)
            for item in data.get("preferences", [])
        ]

        service.save_preferences(dto_list)

        return jsonify({
            "message": "Preferences saved"
        }), 201

    except Exception as e:
        session.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        session.close()


@user_preferences_blueprint.route('/<int:user_id>', methods=['GET'])
def get_preferences(user_id):

    session, service = get_service()

    try:
        result = service.get_preferences_map(user_id)

        return jsonify({
            "user_id": user_id,
            "preferences": result
        })

    finally:
        session.close()
@user_preferences_blueprint.route('', methods=['GET'])
def get_all():

    session, service = get_service()

    try:
        result = service.get_all()

        return jsonify(result)

    finally:
        session.close()