from datetime import datetime
from sqlalchemy import func, extract
from models.Finance.Expenses import Expense
from models.core.Categories import Category
from models.system.MonthlyExpensesSummary import MonthlyExpensesSummary
from models.system.EarlyWarningAlert import EarlyWarningAlert

class EarlyWarningService:

    def __init__(self, session, alert_repo):
        self.session = session
        self.alert_repo = alert_repo

    # =========================
    def check_spending_vs_budget(self, user_id, year, month, budget_plan):

        now = datetime.now()
        is_current_month = (now.year == year and now.month == month)

        if month == 12:
            days_in_month = 31
        else:
            days_in_month = (datetime(year, month + 1, 1) - datetime(year, month, 1)).days

        if is_current_month:
            days_elapsed = now.day
        else:
            days_elapsed = days_in_month

        days_elapsed_pct = min((days_elapsed / days_in_month) * 100, 100)

        actual_rows = (
            self.session.query(
                Expense.category_id,
                Category.category_name,
                func.sum(Expense.amount).label("total")
            )
            .join(Category, Expense.category_id == Category.category_id)
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month
            )
            .group_by(Expense.category_id, Category.category_name)
            .all()
        )

        spent_map = {
            row.category_id: {
                "category_name": row.category_name,
                "total": float(row.total)
            }
            for row in actual_rows
        }

        total_spent = sum(v["total"] for v in spent_map.values())
        monthly_limit = budget_plan.get("monthly_limit", 0)
        budget_items = budget_plan.get("budget", [])
        budget_map = {}
        for b in budget_items:
            cid = b.get("category_id")
            planned = b.get("current_amount", 0) - b.get("cut_amount", 0)
            budget_map[cid] = {
                "category_name": b.get("category_name", ""),
                "planned": max(0, planned)
            }

        budget_used_pct = (total_spent / monthly_limit * 100) if monthly_limit > 0 else 0

        general_status = "OK"
        general_message = ""
        general_severity = "LOW"

        if budget_used_pct > 100:
            general_status = "DANGER"
            general_severity = "HIGH"
            general_message = (
                f"⚠️ חרגת מהתקציב החודשי! "
                f"נוצלו {total_spent:.0f} ש״ח — {budget_used_pct:.0f}% מהתקציב."
            )
        elif budget_used_pct > days_elapsed_pct * 1.3:
            general_status = "WARNING"
            general_severity = "MEDIUM"
            general_message = (
                f"⚡ קצב ההוצאות גבוה מהצפוי. "
                f"עברו {days_elapsed_pct:.0f}% מהחודש אבל נוצלו {budget_used_pct:.0f}% מהתקציב."
            )
        else:
            general_message = (
                f"✅ קצב הוצאות תקין — {budget_used_pct:.0f}% נוצל, "
                f"{days_elapsed_pct:.0f}% מהחודש עבר."
            )

        if general_status in ("WARNING", "DANGER"):
            self._upsert_general_alert(
                user_id, year, month,
                general_status, general_severity, general_message,
                monthly_limit, total_spent
            )
        else:
            self._resolve_general_if_ok(user_id, year, month)

        category_alerts = []
        for cid, budget_data in budget_map.items():
            planned = budget_data["planned"]
            if planned <= 0:
                continue

            spent = spent_map.get(cid, {}).get("total", 0)
            spent_pct = (spent / planned) * 100

            if spent > planned:
                category_alerts.append({
                    "category_id": cid,
                    "category_name": budget_data["category_name"],
                    "type": "OVERSPENT",
                    "severity": "HIGH",
                    "budget_amount": round(planned, 2),
                    "spent_so_far": round(spent, 2),
                    "remaining": 0,
                    "message": (
                        f"🔴 חרגת מתקציב {budget_data['category_name']}! "
                        f"הוצאת {spent:.0f} ש״ח מתוך תקציב של {planned:.0f} ש״ח."
                    )
                })
            elif spent_pct > days_elapsed_pct * 1.5:
                category_alerts.append({
                    "category_id": cid,
                    "category_name": budget_data["category_name"],
                    "type": "DANGEROUS_TREND",
                    "severity": "MEDIUM",
                    "budget_amount": round(planned, 2),
                    "spent_so_far": round(spent, 2),
                    "remaining": round(planned - spent, 2),
                    "message": (
                        f"🟠 קצב גבוה ב{budget_data['category_name']}: "
                        f"{spent_pct:.0f}% מהתקציב נוצל — {spent:.0f} מתוך {planned:.0f} ש״ח."
                    )
                })

        for alert_data in category_alerts:
            self._upsert_category_alert(user_id, year, month, alert_data)

        alerted_cids = {a["category_id"] for a in category_alerts}
        self._resolve_ok_categories(user_id, year, month, alerted_cids)

        return {
            "status": general_status,
            "general": {
                "days_elapsed_pct": round(days_elapsed_pct, 1),
                "budget_used_pct": round(budget_used_pct, 1),
                "total_spent": round(total_spent, 2),
                "monthly_limit": monthly_limit,
                "message": general_message
            },
            "alerts": category_alerts
        }

    # =========================
    def check_single_expense(self, user_id, year, month, amount, category_id, category_name=""):
        self.alert_repo.close_previous_alerts(
            user_id,
            year,
            month
        )
        avg_history = (
            self.session.query(
                func.avg(MonthlyExpensesSummary.total_amount)
            )
            .filter(
                MonthlyExpensesSummary.user_id == user_id,
                MonthlyExpensesSummary.category_id == category_id
            )
            .scalar()
        ) or 0

        if avg_history > 0 and amount > avg_history * 2:
            message = (
                f"📊 הוצאה חריגה ({amount:.0f} ש״ח) בקטגוריה {category_name} — "
                f"כמעט פי {amount / avg_history:.1f} מהממוצע החודשי ({avg_history:.0f} ש״ח)."
            )

            alert = EarlyWarningAlert(
                user_id=user_id,
                category_id=category_id,
                year=year,
                month=month,
                alert_type="SINGLE_SPIKE",
                severity="MEDIUM",
                title=f"הוצאה חריגה — {category_name}",
                message=message,
                budget_amount=avg_history,
                spent_so_far=amount,
                status="ACTIVE"
            )
            self.alert_repo.add(alert)

            return {
                "is_spike": True,
                "message": message
            }

        return None

    # =========================
    # helpers — UPSERT
    # =========================
    def _upsert_general_alert(self, user_id, year, month, status, severity, message,
                               budget_amount, spent_so_far):
        alert_type = "OVERSPENT" if status == "DANGER" else "DANGEROUS_TREND"
        existing = self.alert_repo.get_existing_alert(
            user_id, year, month, None, alert_type
        )
        if existing:
            existing.spent_so_far = spent_so_far
            existing.budget_amount = budget_amount
            existing.message = message
            self.session.commit()
            return

        alert = EarlyWarningAlert(
            user_id=user_id,
            category_id=None,
            year=year,
            month=month,
            alert_type=alert_type,
            severity=severity,
            title="חריגה תקציבית כללית",
            message=message,
            budget_amount=budget_amount,
            spent_so_far=spent_so_far,
            status="ACTIVE"
        )
        self.alert_repo.add(alert)

    def _upsert_category_alert(self, user_id, year, month, alert_data):
        existing = self.alert_repo.get_existing_alert(
            user_id, year, month,
            alert_data["category_id"],
            alert_data["type"]
        )
        if existing:
            existing.spent_so_far = alert_data["spent_so_far"]
            existing.message = alert_data["message"]
            self.session.commit()
            return

        alert = EarlyWarningAlert(
            user_id=user_id,
            category_id=alert_data["category_id"],
            year=year,
            month=month,
            alert_type=alert_data["type"],
            severity=alert_data["severity"],
            title=f"חריגה — {alert_data['category_name']}",
            message=alert_data["message"],
            budget_amount=alert_data["budget_amount"],
            spent_so_far=alert_data["spent_so_far"],
            status="ACTIVE"
        )
        self.alert_repo.add(alert)

    def _resolve_general_if_ok(self, user_id, year, month):
        self.session.query(EarlyWarningAlert).filter(
            EarlyWarningAlert.user_id == user_id,
            EarlyWarningAlert.year == year,
            EarlyWarningAlert.month == month,
            EarlyWarningAlert.category_id.is_(None),
            EarlyWarningAlert.status == "ACTIVE"
        ).update({
            "status": "RESOLVED",
            "resolved_at": datetime.utcnow()
        })
        self.session.commit()

    def _resolve_ok_categories(self, user_id, year, month, active_alerted_cids):
        if not active_alerted_cids:
            self.session.query(EarlyWarningAlert).filter(
                EarlyWarningAlert.user_id == user_id,
                EarlyWarningAlert.year == year,
                EarlyWarningAlert.month == month,
                EarlyWarningAlert.category_id.isnot(None),
                EarlyWarningAlert.status == "ACTIVE"
            ).update({
                "status": "RESOLVED",
                "resolved_at": datetime.utcnow()
            })
        else:
            self.session.query(EarlyWarningAlert).filter(
                EarlyWarningAlert.user_id == user_id,
                EarlyWarningAlert.year == year,
                EarlyWarningAlert.month == month,
                EarlyWarningAlert.category_id.isnot(None),
                EarlyWarningAlert.category_id.notin_(active_alerted_cids),
                EarlyWarningAlert.status == "ACTIVE"
            ).update({
                "status": "RESOLVED",
                "resolved_at": datetime.utcnow()
            })
        self.session.commit()

    # =========================
    def get_active_alerts(self, user_id, year, month):
        return self.alert_repo.get_active_alerts(user_id, year, month)

    def get_all_alerts(self, user_id, year, month):
        return self.alert_repo.get_all_alerts_for_month(user_id, year, month)
