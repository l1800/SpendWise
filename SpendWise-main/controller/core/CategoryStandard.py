from flask import Blueprint, request, jsonify

from services.core.CategoryStandard import CategoryStandardService
from repositories.core.CategoryStandard import CategoryStandardRepository
from db_connection import SessionLocal

category_standard_bp = Blueprint(
    "category_standard",
    __name__,
    url_prefix="/category-standards"
)

repo = CategoryStandardRepository(SessionLocal())
service = CategoryStandardService(repo)


# =========================
# GET ALL
# =========================
@category_standard_bp.route("/", methods=["GET"])
def get_all():
    data = service.get_all()

    return jsonify([
        {
            "benchmark_id": x.benchmark_id,
            "category_id": x.category_id,
            "amount_per_person": x.amount_per_person,
            "is_essential": x.is_essential,
            "rule_description": x.rule_description
        }
        for x in data
    ])


# =========================
# GET BY CATEGORY
# =========================
@category_standard_bp.route("/<int:category_id>", methods=["GET"])
def get_by_category(category_id):
    data = service.get_by_category(category_id)

    if not data:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        "benchmark_id": data.benchmark_id,
        "category_id": data.category_id,
        "amount_per_person": data.amount_per_person,
        "is_essential": data.is_essential,
        "rule_description": data.rule_description
    })


# =========================
# CREATE
# =========================
@category_standard_bp.route("/", methods=["POST"])
def create():
    dto = request.json
    result = service.create_standard(dto)

    return jsonify({"benchmark_id": result.benchmark_id})


# =========================
# UPDATE
# =========================
@category_standard_bp.route("/<int:id>", methods=["PUT"])
def update(id):
    dto = request.json
    result = service.update_standard(id, dto)

    if not result:
        return jsonify({"error": "not found"}), 404

    return jsonify({"status": "updated"})


# =========================
# DELETE
# =========================
@category_standard_bp.route("/<int:id>", methods=["DELETE"])
def delete(id):
    result = service.delete_standard(id)

    if not result:
        return jsonify({"error": "not found"}), 404

    return jsonify({"status": "deleted"})