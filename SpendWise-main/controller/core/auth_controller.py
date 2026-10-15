import os
import re
from datetime import datetime

from flask import Blueprint, g, jsonify, request, session
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from db_connection import SessionLocal
from models.core.SavingsGoal import SavingsGoal
from models.core.Users import User
from models.core.Categories import Category
from models.lookups.CategogyType import CategoryType
from models.core.CategoryStandard import CategoryStandard
from models.core.UserCategoryGoal import UserCategoryGoal
from models.Finance.Expenses import Expense
from models.Finance.ExpenseType import ExpenseType
from models.Finance.IncomeCategory import IncomeCategory
from models.Finance.IncomeFrequency import IncomeFrequency
from models.Finance.Incomes import Income
from models.system.EarlyWarningAlert import EarlyWarningAlert
from services.core.HouseholdSetupService import HouseholdSetupService


auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")


class RegistrationInput(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=10, max_length=128)
    family_size: int = Field(ge=1, le=20)


class LoginInput(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=1, max_length=128)


def _user_response(user):
    return {
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "family_size": user.family_size,
        "role": user.role,
        "join_date": user.join_date.isoformat() if user.join_date else None,
    }


def _valid_email(email):
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email))


@auth_blueprint.route("/register", methods=["POST"])
def register():
    try:
        data = RegistrationInput.model_validate(request.get_json() or {})
    except ValidationError as error:
        return jsonify({"error": "פרטי ההרשמה אינם תקינים"}), 400

    if not _valid_email(data.email):
        return jsonify({"error": "כתובת אימייל אינה תקינה"}), 400

    db = SessionLocal()
    try:
        email = str(data.email).lower()
        if db.query(User).filter(User.email == email).first():
            return jsonify({"error": "כתובת האימייל כבר רשומה"}), 409

        user = User(
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            email=email,
            password_hash=generate_password_hash(data.password),
            role="household",
            family_size=data.family_size,
            join_date=datetime.utcnow(),
        )
        db.add(user)
        db.flush()
        HouseholdSetupService.ensure_defaults(db, user)
        db.commit()
        db.refresh(user)
        session.clear()
        session.permanent = True
        session["user_id"] = user.user_id
        return jsonify(_user_response(user)), 201
    except IntegrityError:
        db.rollback()
        return jsonify({"error": "כתובת האימייל כבר רשומה"}), 409
    finally:
        db.close()


@auth_blueprint.route("/login", methods=["POST"])
def login():
    try:
        data = LoginInput.model_validate(request.get_json() or {})
    except ValidationError:
        return jsonify({"error": "כתובת אימייל או סיסמה שגויות"}), 401

    if not _valid_email(data.email):
        return jsonify({"error": "כתובת אימייל או סיסמה שגויות"}), 401

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == str(data.email).lower()).first()
        if not user or not check_password_hash(user.password_hash, data.password):
            return jsonify({"error": "כתובת אימייל או סיסמה שגויות"}), 401
        if user.role != "admin":
            HouseholdSetupService.ensure_defaults(db, user)
            db.commit()
        session.clear()
        session.permanent = True
        session["user_id"] = user.user_id
        return jsonify(_user_response(user)), 200
    finally:
        db.close()


@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True}), 200


@auth_blueprint.route("/me", methods=["GET"])
def me():
    return jsonify(_user_response(g.current_user)), 200


@auth_blueprint.route("/catalog", methods=["GET"])
def household_catalog():
    db = SessionLocal()
    try:
        rows = (
            db.query(Category, CategoryStandard)
            .join(CategoryStandard, Category.category_id == CategoryStandard.category_id)
            .all()
        )
        expense_type_id = db.query(CategoryType.category_type_id).filter_by(category_type_name="expense").scalar()
        categories = [
            {
                "category_id": category.category_id,
                "category_name": category.category_name,
                "is_essential": standard.is_essential,
                "is_fixed_cost": standard.is_fixed_cost,
                "max_cut_percent": standard.max_cut_percent,
                "recommended_budget": standard.amount_per_person * (g.current_user.family_size or 1),
            }
            for category, standard in rows
            if category.category_type_id == expense_type_id
        ]
        income_categories = db.query(IncomeCategory).order_by(IncomeCategory.category_name).all()
        expense_types = db.query(ExpenseType).order_by(ExpenseType.expenseTypeId).all()
        frequencies = db.query(IncomeFrequency).order_by(IncomeFrequency.frequency_id).all()
        return jsonify({
            "categories": categories,
            "income_categories": [{"category_id": item.category_id, "category_name": item.category_name} for item in income_categories],
            "expense_types": [{"ExpenseTypeId": item.expenseTypeId, "ExpenseTypeName": item.expenseTypeName} for item in expense_types],
            "income_frequencies": [{"frequency_id": item.frequency_id, "frequency_name": item.frequency_name} for item in frequencies],
        }), 200
    finally:
        db.close()


@auth_blueprint.route("/households", methods=["GET"])
def households():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.role != "admin").order_by(User.join_date.desc()).all()
        return jsonify([_user_response(user) for user in users]), 200
    finally:
        db.close()


@auth_blueprint.route("/households/<int:user_id>/role", methods=["PUT"])
def update_household_role(user_id):
    data = request.get_json() or {}
    role = data.get("role")
    if role not in {"household", "admin"}:
        return jsonify({"error": "תפקיד לא תקין"}), 400

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return jsonify({"error": "משק הבית לא נמצא"}), 404
        if user.role == "admin" and role != "admin":
            admin_count = db.query(User).filter(User.role == "admin").count()
            if admin_count <= 1:
                return jsonify({"error": "לא ניתן להסיר את הרשאת המנהלת האחרונה"}), 409
        user.role = role
        db.commit()
        return jsonify(_user_response(user)), 200
    finally:
        db.close()


@auth_blueprint.route("/households/<int:user_id>", methods=["PUT"])
def update_household(user_id):
    data = request.get_json() or {}
    try:
        family_size = int(data.get("family_size"))
    except (TypeError, ValueError):
        return jsonify({"error": "מספר בני הבית אינו תקין"}), 400
    if not 1 <= family_size <= 20:
        return jsonify({"error": "מספר בני הבית חייב להיות בין 1 ל־20"}), 400

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id, User.role != "admin").first()
        if not user:
            return jsonify({"error": "משק הבית לא נמצא"}), 404
        user.family_size = family_size
        goals = (
            db.query(UserCategoryGoal, CategoryStandard)
            .join(CategoryStandard, UserCategoryGoal.category_id == CategoryStandard.category_id)
            .filter(UserCategoryGoal.user_id == user_id)
            .all()
        )
        for goal, standard in goals:
            goal.target_amount = standard.amount_per_person * family_size
        db.commit()
        return jsonify(_user_response(user)), 200
    finally:
        db.close()


def register_auth_middleware(app):
    public_endpoints = {"auth.login", "auth.register", "auth.logout", "home", "static"}
    admin_endpoints = {"auth.me", "auth.logout", "auth.households", "auth.update_household_role", "auth.update_household"}
    household_endpoints = {
        "auth.me", "auth.household_catalog", "users.get_user_by_id",
        "budget.get_budget", "budget.get_expenses_by_category", "budget.get_standard_budget", "budget.get_stress",
        "budget_plan.get_budget_plan_route", "budget_plan.get_budget_status",
        "financial.get_financial_stress",
        "early_warning.get_alerts", "early_warning.dismiss_alert",
        "expenses.add_expense", "expenses.get_expense", "expenses.update_expense", "expenses.delete_expense",
        "income.add_income", "income.get_income", "income.update_income", "income.delete_income",
        "expense_types.get_expense_types", "income_categories.get_categories", "income_frequency.get_frequencies",
        "savings.get_by_user", "savings.create_goal", "savings.delete_goal", "savings.deposit", "savings.withdraw", "savings.get_transactions", "savings.get_balances",
    }

    @app.before_request
    def authenticate_request():
        if request.method == "OPTIONS" or request.endpoint in public_endpoints:
            return None

        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "נדרשת התחברות"}), 401

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                session.clear()
                return jsonify({"error": "ההתחברות פגה, נא להתחבר מחדש"}), 401

            g.current_user = user
            is_admin = user.role == "admin"
            if is_admin:
                if request.endpoint in admin_endpoints:
                    return None
                return jsonify({"error": "מסך זה אינו זמין למנהלי מערכת"}), 403

            if request.endpoint == "users.create_user":
                return jsonify({"error": "יש להשתמש בנתיב ההרשמה המאובטח"}), 403

            if request.endpoint == "users.get_all_users" or request.endpoint not in household_endpoints:
                return jsonify({"error": "אין הרשאה לפעולה זו"}), 403

            request_user_id = (request.view_args or {}).get("user_id")
            if request_user_id is None:
                request_user_id = request.args.get("user_id", type=int)
            payload = request.get_json(silent=True) or {}
            if request_user_id is None:
                request_user_id = payload.get("user_id")
            if request_user_id is not None and int(request_user_id) != user.user_id:
                return jsonify({"error": "אין הרשאה למשק בית זה"}), 403

            owned_resource = _get_owned_resource(db, request.endpoint, request.view_args or {})
            if owned_resource is False:
                return jsonify({"error": "הרשומה לא נמצאה"}), 404
            if owned_resource is not None and owned_resource != user.user_id:
                return jsonify({"error": "אין הרשאה לרשומה זו"}), 403
            return None
        finally:
            db.close()


def _get_owned_resource(db, endpoint, arguments):
    if "expense_id" in arguments:
        row = db.query(Expense.user_id).filter(Expense.transaction_id == arguments["expense_id"]).first()
    elif "transaction_id" in arguments and endpoint.startswith("income."):
        row = db.query(Income.user_id).filter(Income.transaction_id == arguments["transaction_id"]).first()
    elif "alert_id" in arguments:
        row = db.query(EarlyWarningAlert.user_id).filter(EarlyWarningAlert.alert_id == arguments["alert_id"]).first()
    elif "goal_id" in arguments or ("id" in arguments and endpoint.startswith("savings.")):
        goal_id = arguments.get("goal_id", arguments.get("id"))
        row = db.query(SavingsGoal.user_id).filter(SavingsGoal.id == goal_id).first()
    else:
        return None
    return row[0] if row else False