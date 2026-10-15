from flask import Blueprint, request, jsonify
from dto.system.SpecialDateDto import SpecialDateCreateDTO, SpecialDateResponseDTO
from services.system.SpecialDates import SpecialDateService
from repositories.system.SpecialDates import SpecialDateRepository
from db_connection import SessionLocal


special_dates_blueprint = Blueprint(
    "special_dates",
    __name__,
    url_prefix="/special_dates"
)


def get_service():
    session = SessionLocal()
    repo = SpecialDateRepository(session)
    service = SpecialDateService(repo)
    return session, service


# ==================== GET ALL ====================
@special_dates_blueprint.route("", methods=["GET"])
def get_all():
    session, service = get_service()
    try:
        data = service.get_all()
        return jsonify([
            SpecialDateResponseDTO.model_validate(x).model_dump(mode="json")
            for x in data
        ])
    finally:
        session.close()


# ==================== GET BY ID ====================
@special_dates_blueprint.route("/<int:type_id>", methods=["GET"])
def get_by_id(type_id):
    session, service = get_service()
    try:
        obj = service.get_by_id(type_id)
        if not obj:
            return jsonify({"error": "not found"}), 404

        return jsonify(
            SpecialDateResponseDTO.model_validate(obj).model_dump(mode="json")
        )
    finally:
        session.close()


# ==================== UPDATE ====================
@special_dates_blueprint.route("/<int:type_id>", methods=["PUT"])
def update(type_id):
    session, service = get_service()
    try:
        dto = SpecialDateCreateDTO(**request.get_json())
        obj = service.update(type_id, dto)

        if not obj:
            return jsonify({"error": "not found"}), 404

        return jsonify({"message": "updated"})
    finally:
        session.close()


# ==================== DELETE ====================
@special_dates_blueprint.route("/<int:type_id>", methods=["DELETE"])
def delete(type_id):
    session, service = get_service()
    try:
        obj = service.delete(type_id)

        if not obj:
            return jsonify({"error": "not found"}), 404

        return jsonify({"message": "deleted"})
    finally:
        session.close()