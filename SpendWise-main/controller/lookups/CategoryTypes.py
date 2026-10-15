# controllers/category_types_controller.py

from flask import Blueprint, request, jsonify

from dto.lookups.CategogyTypeDto import CategoryTypeDTO
from services.lookups.CategoryTypes import CategoryTypesService
from repositories.lookups.CategoryTypes import CategoryTypesRepository
from db_connection import SessionLocal

session = SessionLocal()
repo = CategoryTypesRepository(session)
service = CategoryTypesService(repo)

category_types_bp = Blueprint("category_types", __name__, url_prefix='/category_types')



@category_types_bp.route('', methods=['GET'])
def get_all():
    data = service.get_all()
    return jsonify([
        {
            "category_type_id": c.category_type_id,
            "category_type_name": c.category_type_name
        } for c in data
    ])


@category_types_bp.route('/<int:category_type_id>', methods=['GET'])
def get_by_id(category_type_id):
    obj = service.get_by_id(category_type_id)

    if not obj:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        "category_type_id": obj.category_type_id,
        "category_type_name": obj.category_type_name
    })



"""
@category_types_bp.route('', methods=['POST'])
def create():
    dto = CategoryTypeDTO(**request.get_json())
    obj = service.create(dto)
    return jsonify({"category_type_id": obj.category_type_id}), 201


@category_types_bp.route('/<int:category_type_id>', methods=['PUT'])
def update(category_type_id):
    dto = CategoryTypeDTO(**request.get_json())
    obj = service.update(category_type_id, dto)

    if not obj:
        return jsonify({"error": "not found"}), 404

    return jsonify({"message": "updated"})


@category_types_bp.route('/<int:category_type_id>', methods=['DELETE'])
def delete(category_type_id):
    obj = service.delete(category_type_id)

    if not obj:
        return jsonify({"error": "not found"}), 404

    return jsonify({"message": "deleted"})
"""