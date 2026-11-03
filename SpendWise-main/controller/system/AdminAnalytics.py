"""API אנליטיקה למנהל המערכת — סטטיסטיקות מצטברות על פני כל משקי הבית.

כל החישובים דטרמיניסטיים ומבוצעים ב-SQL/Python, ללא שום קריאה חיצונית.
"""
import statistics
from collections import defaultdict
from datetime import date

from flask import Blueprint, jsonify, request, g
from sqlalchemy import func

from db_connection import SessionLocal
from models.core.Users import User
from models.core.Categories import Category
from models.core.CategoryStandard import CategoryStandard
from models.core.SavingsGoal import SavingsGoal
from models.Finance.Expenses import Expense
from models.Finance.Incomes import Income
from models.system.EarlyWarningAlert import EarlyWarningAlert


admin_analytics_bp = Blueprint("admin_analytics", __name__, url_prefix="/admin/analytics")

SEVERITY_BANDS = ((90, "excellent"), (75, "good"), (55, "watch"), (0, "risk"))


def _month_range(year, month):
    """מחזיר (start, end) כתאריכים — end בלעדי."""
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


def _parse_period():
    today = date.today()
    try:
        year = int(request.args.get("year", today.year))
        month = int(request.args.get("month", today.month))
    except (TypeError, ValueError):
        raise ValueError("שנה או חודש אינם תקינים")
    if not 1 <= month <= 12 or not 2000 <= year <= 2100:
        raise ValueError("שנה או חודש מחוץ לטווח תקין")
    return year, month


def _household_ids(db):
    """כל המשתמשים הרשומים בפועל — גם חשבון המנהל מחזיק משק בית משלו."""
    return [row[0] for row in db.query(User.user_id).order_by(User.user_id).all()]


def _sum_by_user(db, model, user_ids, start, end):
    if not user_ids:
        return {}
    rows = (
        db.query(model.user_id, model.amount)
        .filter(model.user_id.in_(user_ids), model.date >= start, model.date < end)
        .all()
    )
    totals = defaultdict(float)
    for user_id, amount in rows:
        totals[user_id] += float(amount or 0)
    return totals


def _category_targets(db, user_ids):
    """יעד חודשי לכל (משתמש, קטגוריה) = amount_per_person × family_size."""
    if not user_ids:
        return {}
    rows = (
        db.query(User.user_id, User.family_size)
        .filter(User.user_id.in_(user_ids))
        .all()
    )
    family_size = {user_id: size or 1 for user_id, size in rows}
    standards = db.query(CategoryStandard).all()
    per_person = {row.category_id: float(row.amount_per_person or 0) for row in standards}
    return {
        user_id: {category_id: amount * family_size[user_id] for category_id, amount in per_person.items()}
        for user_id in family_size
    }


def _expenses_by_user_category(db, user_ids, start, end):
    if not user_ids:
        return {}
    rows = (
        db.query(Expense.user_id, Expense.category_id, Expense.amount)
        .filter(Expense.user_id.in_(user_ids), Expense.date >= start, Expense.date < end)
        .all()
    )
    grouped = defaultdict(lambda: defaultdict(float))
    for user_id, category_id, amount in rows:
        grouped[user_id][category_id] += float(amount or 0)
    return grouped


def _health_score(income, expense):
    """ציון 0–100: יחס הוצאה/הכנסה, עם ענישה על חריגה."""
    if income <= 0:
        return 0.0 if expense > 0 else 100.0
    ratio = expense / income
    if ratio <= 0.6:
        return 100.0
    if ratio <= 0.85:
        return 100.0 - (ratio - 0.6) / 0.25 * 25.0
    if ratio <= 1.0:
        return 75.0 - (ratio - 0.85) / 0.15 * 25.0
    return max(0.0, 50.0 - (ratio - 1.0) * 50.0)


def _band(score):
    for threshold, label in SEVERITY_BANDS:
        if score >= threshold:
            return label
    return "risk"


def _safe_avg(values):
    return round(statistics.fmean(values), 2) if values else 0.0


def _safe_median(values):
    return round(statistics.median(values), 2) if values else 0.0


def _require_admin():
    user = getattr(g, "current_user", None)
    if user is None or user.role != "admin":
        return False
    return True


_guard = _require_admin


def _latest_activity_period():
    """החודש האחרון שבו קיימת פעילות — כדי שלוח הבקרה לא ייפתח ריק."""
    db = SessionLocal()
    try:
        newest = None
        for model in (Expense, Income):
            value = db.query(func.max(model.date)).scalar()
            if value is not None and (newest is None or value > newest):
                newest = value
        return (newest.year, newest.month) if newest else None
    finally:
        db.close()


@admin_analytics_bp.route("/latest-period", methods=["GET"])
def latest_period():
    """מחזיר את החודש האחרון עם נתונים, או את החודש הנוכחי אם אין נתונים כלל."""
    if not _guard():
        return jsonify({"error": "אין הרשאת מנהל"}), 403
    latest = _latest_activity_period()
    if latest is None:
        today = date.today()
        latest = (today.year, today.month)
    return jsonify({"year": latest[0], "month": latest[1]}), 200


@admin_analytics_bp.route("/overview", methods=["GET"])
def overview():
    if not _guard():
        return jsonify({"error": "אין הרשאת מנהל"}), 403
    try:
        year, month = _parse_period()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    start, end = _month_range(year, month)
    db = SessionLocal()
    try:
        user_ids = _household_ids(db)
        incomes = _sum_by_user(db, Income, user_ids, start, end)
        expenses = _sum_by_user(db, Expense, user_ids, start, end)
        targets = _category_targets(db, user_ids)
        spent = _expenses_by_user_category(db, user_ids, start, end)

        active = [uid for uid in user_ids if incomes.get(uid, 0) > 0 or expenses.get(uid, 0) > 0]
        income_values = [incomes.get(uid, 0.0) for uid in user_ids]
        expense_values = [expenses.get(uid, 0.0) for uid in user_ids]

        over_budget = 0
        total_overage = 0.0
        scored = []
        for uid in user_ids:
            income = incomes.get(uid, 0.0)
            expense = expenses.get(uid, 0.0)
            score = _health_score(income, expense)
            scored.append((uid, score, income, expense))

            user_overage = 0.0
            for category_id, target in targets.get(uid, {}).items():
                actual = spent.get(uid, {}).get(category_id, 0.0)
                if target > 0 and actual > target:
                    user_overage += actual - target
            if user_overage > 0:
                over_budget += 1
                total_overage += user_overage

        open_alerts = (
            db.query(EarlyWarningAlert)
            .filter(EarlyWarningAlert.user_id.in_(user_ids), EarlyWarningAlert.status == "ACTIVE")
            .count() if user_ids else 0
        )
        active_goals = (
            db.query(SavingsGoal)
            .filter(SavingsGoal.user_id.in_(user_ids), SavingsGoal.current_balance > 0)
            .count() if user_ids else 0
        )
        total_income = sum(income_values)
        total_expense = sum(expense_values)

        return jsonify({
            "period": {"year": year, "month": month},
            "households_total": len(user_ids),
            "households_active": len(active),
            "households_over_budget": over_budget,
            "open_alerts": open_alerts,
            "active_savings_goals": active_goals,
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "savings_rate": round((total_income - total_expense) / total_income * 100, 1) if total_income > 0 else 0.0,
            "avg_income": _safe_avg(income_values),
            "avg_expense": _safe_avg(expense_values),
            "median_expense": _safe_median(expense_values),
            "total_overage": round(total_overage, 2),
            "avg_health_score": _safe_avg([score for _, score, _, _ in scored]),
            "risk_households": sum(1 for _, score, _, _ in scored if _band(score) == "risk"),
        }), 200
    finally:
        db.close()


@admin_analytics_bp.route("/averages", methods=["GET"])
def averages():
    """ממוצעים וחציון לפי קטגוריה, לנפש ולמשק בית."""
    if not _guard():
        return jsonify({"error": "אין הרשאת מנהל"}), 403
    try:
        year, month = _parse_period()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    start, end = _month_range(year, month)
    db = SessionLocal()
    try:
        user_ids = _household_ids(db)
        if not user_ids:
            return jsonify({"period": {"year": year, "month": month}, "categories": []}), 200

        families = dict(db.query(User.user_id, User.family_size).filter(User.user_id.in_(user_ids)).all())
        names = dict(db.query(Category.category_id, Category.category_name).all())
        essentials = dict(db.query(CategoryStandard.category_id, CategoryStandard.is_essential).all())
        spent = _expenses_by_user_category(db, user_ids, start, end)
        targets = _category_targets(db, user_ids)

        category_ids = set()
        for per_user in spent.values():
            category_ids.update(per_user.keys())

        rows = []
        for category_id in category_ids:
            values = [spent[uid].get(category_id, 0.0) for uid in user_ids]
            per_person = [
                spent[uid].get(category_id, 0.0) / max(families.get(uid) or 1, 1)
                for uid in user_ids
            ]
            target_total = sum(targets.get(uid, {}).get(category_id, 0.0) for uid in user_ids)
            actual_total = sum(values)
            household_targets = [
                targets.get(uid, {}).get(category_id, 0.0) for uid in user_ids
            ]
            overage_households = sum(
                1 for uid in user_ids
                if targets.get(uid, {}).get(category_id, 0.0) > 0
                and spent[uid].get(category_id, 0.0) > targets[uid][category_id]
            )
            rows.append({
                "category_id": category_id,
                "category_name": names.get(category_id, f"קטגוריה {category_id}"),
                "is_essential": bool(essentials.get(category_id, False)),
                "total_spent": round(actual_total, 2),
                "avg_per_household": _safe_avg(values),
                "median_per_household": _safe_median(values),
                "avg_per_person": _safe_avg(per_person),
                "max_per_household": round(max(values), 2) if values else 0.0,
                "target_total": round(target_total, 2),
                "avg_target_per_household": _safe_avg(household_targets),
                "variance_percent": round((actual_total - target_total) / target_total * 100, 1) if target_total > 0 else 0.0,
                "households_spending": sum(1 for value in values if value > 0),
                "households_over_target": overage_households,
            })

        rows.sort(key=lambda row: row["total_spent"], reverse=True)
        return jsonify({"period": {"year": year, "month": month}, "categories": rows}), 200
    finally:
        db.close()


@admin_analytics_bp.route("/trends", methods=["GET"])
def trends():
    """מגמות ב-N חודשים אחורה — הכנסות, הוצאות, יחס חיסכון."""
    if not _guard():
        return jsonify({"error": "אין הרשאת מנהל"}), 403
    try:
        year, month = _parse_period()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    try:
        months_back = max(1, min(int(request.args.get("months", 6)), 24))
    except (TypeError, ValueError):
        return jsonify({"error": "מספר החודשים אינו תקין"}), 400

    db = SessionLocal()
    try:
        user_ids = _household_ids(db)
        points = []
        cursor_year, cursor_month = year, month
        for _ in range(months_back):
            start, end = _month_range(cursor_year, cursor_month)
            incomes = _sum_by_user(db, Income, user_ids, start, end)
            expenses = _sum_by_user(db, Expense, user_ids, start, end)
            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            points.append({
                "year": cursor_year,
                "month": cursor_month,
                "income": round(total_income, 2),
                "expense": round(total_expense, 2),
                "balance": round(total_income - total_expense, 2),
                "savings_rate": round((total_income - total_expense) / total_income * 100, 1) if total_income > 0 else 0.0,
                "active_households": len([uid for uid in user_ids if incomes.get(uid, 0) > 0 or expenses.get(uid, 0) > 0]),
            })
            cursor_month -= 1
            if cursor_month == 0:
                cursor_month = 12
                cursor_year -= 1
        points.reverse()
        return jsonify({"months": points}), 200
    finally:
        db.close()


@admin_analytics_bp.route("/health", methods=["GET"])
def health():
    """דירוג בריאות פיננסית לכל משק בית — ירוק/צהוב/אדום."""
    if not _guard():
        return jsonify({"error": "אין הרשאת מנהל"}), 403
    try:
        year, month = _parse_period()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    start, end = _month_range(year, month)
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.user_id).all()
        user_ids = [user.user_id for user in users]
        incomes = _sum_by_user(db, Income, user_ids, start, end)
        expenses = _sum_by_user(db, Expense, user_ids, start, end)
        targets = _category_targets(db, user_ids)
        spent = _expenses_by_user_category(db, user_ids, start, end)
        alert_counts = defaultdict(int)
        for user_id, in (
            db.query(EarlyWarningAlert.user_id)
            .filter(EarlyWarningAlert.user_id.in_(user_ids), EarlyWarningAlert.status == "ACTIVE")
            .all() if user_ids else []
        ):
            alert_counts[user_id] += 1

        rows = []
        for user in users:
            income = incomes.get(user.user_id, 0.0)
            expense = expenses.get(user.user_id, 0.0)
            score = _health_score(income, expense)
            overage = 0.0
            overage_categories = 0
            for category_id, target in targets.get(user.user_id, {}).items():
                actual = spent.get(user.user_id, {}).get(category_id, 0.0)
                if target > 0 and actual > target:
                    overage += actual - target
                    overage_categories += 1
            rows.append({
                "user_id": user.user_id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "family_size": user.family_size,
                "income": round(income, 2),
                "expense": round(expense, 2),
                "balance": round(income - expense, 2),
                "expense_ratio": round(expense / income * 100, 1) if income > 0 else (100.0 if expense > 0 else 0.0),
                "health_score": round(score, 1),
                "band": _band(score),
                "overage_total": round(overage, 2),
                "overage_categories": overage_categories,
                "open_alerts": alert_counts.get(user.user_id, 0),
            })

        rows.sort(key=lambda row: row["health_score"])
        bands = {label: sum(1 for row in rows if row["band"] == label) for _, label in SEVERITY_BANDS}
        return jsonify({
            "period": {"year": year, "month": month},
            "bands": bands,
            "households": rows,
        }), 200
    finally:
        db.close()
