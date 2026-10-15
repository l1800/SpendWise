# controllers/Reports/ReportTypesController.py
from flask import Blueprint, request, jsonify
from services.Reports.ReportTypes import ReportTypesService
from repositories.reporting.ReportTypes import ReportTypesRepository
from db_connection import SessionLocal

session = SessionLocal()
repo = ReportTypesRepository(session)
service = ReportTypesService(repo)

report_types_bp = Blueprint("report_types", __name__, url_prefix="/report_types")

@report_types_bp.route("", methods=["GET"])
def get_all():
    data = service.get_all()
    return jsonify([{"report_type_id": r.report_type_id, "report_type_name": r.report_type_name} for r in data])

@report_types_bp.route("/<int:report_type_id>", methods=["GET"])
def get_by_id(report_type_id):
    r = service.get_by_id(report_type_id)
    if not r:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"report_type_id": r.report_type_id, "report_type_name": r.report_type_name})


"""
@report_types_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    r = service.create(data["report_type_name"])
    return jsonify({"report_type_id": r.report_type_id}), 201

@report_types_bp.route("/<int:report_type_id>", methods=["PUT"])
def update(report_type_id):
    data = request.get_json()
    r = service.update(report_type_id, data["report_type_name"])
    if not r:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "updated"})

@report_types_bp.route("/<int:report_type_id>", methods=["DELETE"])
def delete(report_type_id):
    success = service.delete(report_type_id)
    if not success:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "deleted"})
"""