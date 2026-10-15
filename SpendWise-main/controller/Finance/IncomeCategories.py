from flask import Blueprint, request, jsonify
from dto.Finance.IncomeCategories import IncomeCategoryCreateDTO, IncomeCategoryResponseDTO
from services.Finance.IncomeCategories import IncomeCategoryService
from repositories.Finance.IncomeCategories import IncomeCategoriesRepository
from db_connection import SessionLocal

session = SessionLocal()
repo = IncomeCategoriesRepository(session)
service = IncomeCategoryService(repo)

income_categories_blueprint = Blueprint(
    "income_categories",
    __name__, url_prefix='/income_categories'
)

@income_categories_blueprint.route('', methods=['POST'])
def create_category():
    dto = IncomeCategoryCreateDTO(**request.get_json())
    category = service.create_category(dto)
    return jsonify({"category_id": category.category_id}), 201

@income_categories_blueprint.route('', methods=['GET'])
def get_categories():
    categories = service.get_all_categories()

    return jsonify([
        IncomeCategoryResponseDTO.model_validate(
            category
        ).model_dump(mode="json")
        for category in categories
    ])
@income_categories_blueprint.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = service.get_category_by_id(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    return jsonify(IncomeCategoryResponseDTO.model_validate(category).model_dump(mode="json"))

@income_categories_blueprint.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    dto = IncomeCategoryCreateDTO(**request.get_json())
    category = service.update_category(category_id, dto)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    return jsonify({"message": "Category updated"})

@income_categories_blueprint.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = service.delete_category(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    return jsonify({"message": "Category deleted"})