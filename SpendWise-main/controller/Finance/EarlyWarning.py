from flask import Blueprint, request, jsonify
from dto.system.EarlyWarningAlertDto import EarlyWarningAlertResponseDto
from repositories.system.EarlyWarningAlert import EarlyWarningAlertRepository
from db_connection import SessionLocal

early_warning_bp = Blueprint("early_warning", __name__)

def get_repo():
    session = SessionLocal()
    repo = EarlyWarningAlertRepository(session)
    return session, repo

@early_warning_bp.route("/api/early-warning/alerts", methods=["GET"])
def get_alerts():
    user_id = request.args.get("user_id", type=int)
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    session, repo = get_repo()
    try:
        alerts = repo.get_all_alerts_for_month(user_id, year, month)
        return jsonify(
            [EarlyWarningAlertResponseDto.model_validate(a).model_dump() for a in alerts]
        ), 200
    finally:
        session.close()

@early_warning_bp.route("/api/early-warning/alerts/<int:alert_id>/dismiss", methods=["PUT"])
def dismiss_alert(alert_id):
    session, repo = get_repo()
    try:
        alert = repo.dismiss_alert(alert_id)
        if not alert:
            return jsonify({"error": "Alert not found"}), 404
        return jsonify(EarlyWarningAlertResponseDto.model_validate(alert).model_dump()), 200
    finally:
        session.close()
