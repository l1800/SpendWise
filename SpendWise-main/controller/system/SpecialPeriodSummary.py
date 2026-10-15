from flask import Blueprint, request, jsonify
from db_connection import SessionLocal

from repositories.system.SpecialPeriodSummary import SpecialPeriodSummaryRepository
from services.system.SpecialPeriodSummary import SpecialPeriodService

special_period_summary_blueprint = Blueprint(
    "special_period_summary",
    __name__,
    url_prefix="/special_period_summary"
)


def get_service():
    session = SessionLocal()
    repo = SpecialPeriodSummaryRepository(session)
    service = SpecialPeriodService(repo)
    return session, service


# ================= GET ALL =================
@special_period_summary_blueprint.route("", methods=["GET"])
def get_all():
    session, service = get_service()
    try:
        data = service.get_all()
        return jsonify([{
            "summary_id": x.summary_id,
            "user_id": x.user_id,
            "category_id": x.category_id,
            "spent_amount": x.spent_amount,
            "approved_amount": x.approved_amount
        } for x in data])
    finally:
        session.close()


# ================= GET BY ID =================
@special_period_summary_blueprint.route("/<int:summary_id>", methods=["GET"])
def get_by_id(summary_id):
    session, service = get_service()
    try:
        obj = service.get_by_id(summary_id)
        if not obj:
            return jsonify({"error": "not found"}), 404

        return jsonify({
            "summary_id": obj.summary_id,
            "user_id": obj.user_id,
            "category_id": obj.category_id,
            "spent_amount": obj.spent_amount,
            "approved_amount": obj.approved_amount
        })
    finally:
        session.close()


# ================= PUT =================
@special_period_summary_blueprint.route("/<int:summary_id>", methods=["PUT"])
def update(summary_id):
    session, service = get_service()
    try:
        data = request.get_json()

        obj = service.update(
            summary_id,
            data.get("spent_amount"),
            data.get("approved_amount")
        )

        if not obj:
            return jsonify({"error": "not found"}), 404

        return jsonify({"message": "updated"})
    finally:
        session.close()


# ================= DELETE =================
@special_period_summary_blueprint.route("/<int:summary_id>", methods=["DELETE"])
def delete(summary_id):
    session, service = get_service()
    try:
        ok = service.delete(summary_id)

        if not ok:
            return jsonify({"error": "not found"}), 404

        return jsonify({"message": "deleted"})
    finally:
        session.close()


# ================= BUSINESS LOGIC =================
@special_period_summary_blueprint.route("/handle", methods=["POST"])
def handle():
    session, service = get_service()
    try:
        data = request.get_json()

        result = service.handle_expense(
            user_id=data["user_id"],
            category_id=data["category_id"],
            amount=data["amount"],
            expense_date=data["expense_date"]
        )

        return jsonify(result)
    finally:
        session.close()