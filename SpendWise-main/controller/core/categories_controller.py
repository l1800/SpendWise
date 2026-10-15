from flask import Blueprint, request, jsonify

from dto.core.category_dto import CategoryCreateDTO
from services.core.Categories import CategoriesService
from repositories.core.Categories import CategoriesRepository
from db_connection import SessionLocal


categories_blueprint = Blueprint(
    "categories",
    __name__,
    url_prefix="/categories"
)


def get_service():
    session = SessionLocal()

    repo = CategoriesRepository(session)
    service = CategoriesService(repo)

    return session, service


@categories_blueprint.route('', methods=['POST'])
def add_category():

    session, service = get_service()

    try:
        dto = CategoryCreateDTO(**request.get_json())

        category = service.add_category(dto)

        return jsonify({
            "category_id": category.category_id,
            "message": "Category added"
        }), 201

    except Exception as e:
        session.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        session.close()


@categories_blueprint.route('', methods=['GET'])
def get_all_categories():

    session, service = get_service()

    try:
        categories = service.get_all_categories()

        return jsonify([
            {
                "category_id": c.category_id,
                "category_name": c.category_name,
                "category_type_id": c.category_type_id,
                "category_description": c.category_description,
                "user_id": c.user_id,
                "created_at": c.created_at.isoformat()
            }
            for c in categories
        ])

    finally:
        session.close()


@categories_blueprint.route('/<int:category_id>', methods=['GET'])
def get_category_by_id(category_id):

    session, service = get_service()

    try:
        category = service.get_category_by_id(category_id)

        if not category:
            return jsonify({
                "message": "Category not found"
            }), 404

        return jsonify({
            "category_id": category.category_id,
            "category_name": category.category_name,
            "category_type_id": category.category_type_id,
            "category_description": category.category_description,
            "user_id": category.user_id,
            "created_at": category.created_at.isoformat()
        })

    finally:
        session.close()


@categories_blueprint.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):

    session, service = get_service()

    try:
        dto = CategoryCreateDTO(**request.get_json())

        category = service.update_category(
            category_id,
            dto
        )

        if not category:
            return jsonify({
                "message": "Category not found"
            }), 404

        return jsonify({
            "message": "Category updated"
        })

    except Exception as e:
        session.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        session.close()


@categories_blueprint.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):

    session, service = get_service()

    try:
        category = service.delete_category(category_id)

        if not category:
            return jsonify({
                "message": "Category not found"
            }), 404

        return jsonify({
            "message": "Category deleted"
        })

    except Exception as e:
        session.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        session.close()