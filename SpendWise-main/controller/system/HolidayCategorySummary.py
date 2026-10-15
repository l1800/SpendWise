from flask import Blueprint, request, jsonify
from db_connection import SessionLocal

from dto.system.HolidayCategorySummaryDto import (
    HolidayCategorySummaryCreateDTO,
    HolidayCategorySummaryResponseDTO
)
from services.system.HolidayCategorySummary import HolidayCategorySummaryService
from repositories.system.HolidayCategorySummary import HolidayCategorySummaryRepository


holiday_summary_blueprint = Blueprint(
    "holiday_summary",
    __name__,
    url_prefix="/holiday_summary"
)


def get_service():
    session = SessionLocal()
    repo = HolidayCategorySummaryRepository(session)
    service = HolidayCategorySummaryService(repo)
    return session, service


# ==================== GET ALL ====================
@holiday_summary_blueprint.route("", methods=["GET"])
def get_all():
    session, service = get_service()
    try:
        results = service.get_all()
        return jsonify([r.model_dump() for r in results])
    finally:
        session.close()


# ==================== GET BY ID ====================
@holiday_summary_blueprint.route("/<int:summary_id>", methods=["GET"])
def get_by_id(summary_id):
    session, service = get_service()
    try:
        result = service.get_by_id(summary_id)

        if not result:
            return jsonify({"message": "Not found"}), 404

        return jsonify(result.model_dump())
    finally:
        session.close()


# ==================== GET BY USER ====================
@holiday_summary_blueprint.route("/user/<int:user_id>", methods=["GET"])
def get_by_user(user_id):
    session, service = get_service()
    try:
        results = service.get_by_user(user_id)
        return jsonify([r.model_dump() for r in results])
    finally:
        session.close()


# ==================== GET BY USER + CATEGORY ====================
@holiday_summary_blueprint.route("/user/<int:user_id>/category/<int:category_id>", methods=["GET"])
def get_by_user_and_category(user_id, category_id):
    session, service = get_service()
    try:
        result = service.get_by_user_and_category(user_id, category_id)

        if not result:
            return jsonify({"message": "Not found"}), 404

        return jsonify(result.model_dump())
    finally:
        session.close()


# ==================== CREATE ====================
@holiday_summary_blueprint.route("", methods=["POST"])
def create():
    session, service = get_service()
    try:
        data = request.get_json()
        dto = HolidayCategorySummaryCreateDTO.model_validate(data)

        result = service.create(dto)

        return jsonify(result.model_dump()), 201

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400

    finally:
        session.close()


# ==================== UPDATE ====================
@holiday_summary_blueprint.route("/<int:summary_id>", methods=["PUT"])
def update(summary_id):
    session, service = get_service()
    try:
        data = request.get_json()
        change_ratio = data.get("change_ratio")

        result = service.update(summary_id, change_ratio)

        if not result:
            return jsonify({"message": "Not found"}), 404

        return jsonify(result.model_dump())
    finally:
        session.close()


# ==================== DELETE ====================
@holiday_summary_blueprint.route("/<int:summary_id>", methods=["DELETE"])
def delete(summary_id):
    session, service = get_service()
    try:
        success = service.delete(summary_id)

        if not success:
            return jsonify({"message": "Not found"}), 404

        return jsonify({"success": True})
    finally:
        session.close()