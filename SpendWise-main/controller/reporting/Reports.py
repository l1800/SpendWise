# controllers/reports_controller.py

from flask import Blueprint, request, jsonify

from dto.reporting.ReportsDto import ReportCreateDTO
from services.Reports.Reports import ReportsService
from repositories.reporting.Reports import ReportsRepository
from db_connection import SessionLocal

session = SessionLocal()
repo = ReportsRepository(session)
service = ReportsService(repo)

reports_bp = Blueprint("reports", __name__, url_prefix='/reports')


@reports_bp.route('', methods=['POST'])
def create():
    dto = ReportCreateDTO(**request.get_json())
    report = service.create_report(dto)
    return jsonify({"report_id": report.report_id}), 201


@reports_bp.route('', methods=['GET'])
def get_all():
    data = service.get_all()
    return jsonify([
        {
            "report_id": r.report_id,
            "user_id": r.user_id,
            "report_type_id": r.report_type_id,
            "report_date": r.report_date.isoformat(),
            "report_data": r.report_data
        }
        for r in data
    ])


@reports_bp.route('/<int:report_id>', methods=['GET'])
def get_by_id(report_id):
    r = service.get_by_id(report_id)

    if not r:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        "report_id": r.report_id,
        "user_id": r.user_id,
        "report_type_id": r.report_type_id,
        "report_date": r.report_date.isoformat(),
        "report_data": r.report_data
    })


@reports_bp.route('/user/<int:user_id>', methods=['GET'])
def get_by_user(user_id):
    data = service.get_by_user(user_id)

    return jsonify([
        {
            "report_id": r.report_id,
            "user_id": r.user_id,
            "report_type_id": r.report_type_id,
            "report_date": r.report_date.isoformat(),
            "report_data": r.report_data
        }
        for r in data
    ])


@reports_bp.route('/<int:report_id>', methods=['PUT'])
def update(report_id):
    dto = ReportCreateDTO(**request.get_json())
    r = service.update(report_id, dto)

    if not r:
        return jsonify({"error": "not found"}), 404

    return jsonify({"message": "updated"})


@reports_bp.route('/<int:report_id>', methods=['DELETE'])
def delete(report_id):
    r = service.delete(report_id)

    if not r:
        return jsonify({"error": "not found"}), 404

    return jsonify({"message": "deleted"})