from flask import Blueprint, request, jsonify

from dto.system.MonthlyExpensesSummary import (
    MonthlyExpensesSummaryCreateDTO,
    MonthlyExpensesSummaryResponseDTO
)

from services.system.MonthlyExpensesSummary import MonthlyExpensesSummaryService
from repositories.system.MonthlyExpensesSummary import MonthlyExpensesSummaryRepository
from db_connection import SessionLocal


monthly_expenses_summary_blueprint = Blueprint(
    "monthly_expenses_summary",
    __name__,
    url_prefix="/monthly_expenses_summary"
)


def get_service():
    session = SessionLocal()
    repo = MonthlyExpensesSummaryRepository(session)
    service = MonthlyExpensesSummaryService(repo)
    return session, service


@monthly_expenses_summary_blueprint.route("", methods=["GET"])
def get_all():
    session, service = get_service()
    try:
        data = service.get_all()
        return jsonify([
            MonthlyExpensesSummaryResponseDTO.model_validate(x).model_dump(mode="json")
            for x in data
        ])
    finally:
        session.close()


@monthly_expenses_summary_blueprint.route("/<int:summary_id>", methods=["GET"])
def get_by_id(summary_id):
    session, service = get_service()
    try:
        obj = service.get_by_id(summary_id)
        if not obj:
            return jsonify({"error": "not found"}), 404

        return jsonify(
            MonthlyExpensesSummaryResponseDTO.model_validate(obj).model_dump(mode="json")
        )
    finally:
        session.close()


@monthly_expenses_summary_blueprint.route("", methods=["POST"])
def create():
    session, service = get_service()
    try:
        dto = MonthlyExpensesSummaryCreateDTO(**request.get_json())
        obj = service.create(dto)
        return jsonify(
            MonthlyExpensesSummaryResponseDTO.model_validate(obj).model_dump(mode="json")
        ), 201
    finally:
        session.close()


@monthly_expenses_summary_blueprint.route("/<int:summary_id>", methods=["PUT"])
def update(summary_id):
    session, service = get_service()
    try:
        data = request.get_json()
        obj = service.update(summary_id, data["total_amount"])

        if not obj:
            return jsonify({"error": "not found"}), 404

        return jsonify({"message": "updated"})
    finally:
        session.close()


@monthly_expenses_summary_blueprint.route("/<int:summary_id>", methods=["DELETE"])
def delete(summary_id):
    session, service = get_service()
    try:
        ok = service.delete(summary_id)
        if not ok:
            return jsonify({"error": "not found"}), 404

        return jsonify({"message": "deleted"})
    finally:
        session.close()