from datetime import datetime
from models.system.EarlyWarningAlert import EarlyWarningAlert
from repositories.base_repository import BaseRepository

class EarlyWarningAlertRepository(BaseRepository):

    def get_active_alerts(self, user_id, year, month):
        return (
            self.session.query(EarlyWarningAlert)
            .filter(
                EarlyWarningAlert.user_id == user_id,
                EarlyWarningAlert.year == year,
                EarlyWarningAlert.month == month,
                EarlyWarningAlert.status == "ACTIVE"
            )
            .order_by(EarlyWarningAlert.severity.desc())
            .all()
        )

    def get_existing_alert(self, user_id, year, month, category_id, alert_type):
        return (
            self.session.query(EarlyWarningAlert)
            .filter(
                EarlyWarningAlert.user_id == user_id,
                EarlyWarningAlert.year == year,
                EarlyWarningAlert.month == month,
                EarlyWarningAlert.category_id == category_id,
                EarlyWarningAlert.alert_type == alert_type,
                EarlyWarningAlert.status == "ACTIVE"
            )
            .first()
        )

    def get_all_alerts_for_month(self, user_id, year, month):
        return (
            self.session.query(EarlyWarningAlert)
            .filter(
                EarlyWarningAlert.user_id == user_id,
                EarlyWarningAlert.year == year,
                EarlyWarningAlert.month == month
            )
            .order_by(EarlyWarningAlert.created_at.desc())
            .all()
        )

    def resolve_alert(self, alert_id):
        alert = self.session.query(EarlyWarningAlert).filter_by(
            alert_id=alert_id
        ).first()
        if alert:
            alert.status = "RESOLVED"
            alert.resolved_at = datetime.utcnow()
            self.session.commit()
        return alert

    def dismiss_alert(self, alert_id):
        alert = self.session.query(EarlyWarningAlert).filter_by(
            alert_id=alert_id
        ).first()
        if alert:
            alert.status = "DISMISSED"
            alert.resolved_at = datetime.utcnow()
            self.session.commit()
        return alert

    def resolve_all_for_category(self, user_id, year, month, category_id):
        self.session.query(EarlyWarningAlert).filter(
            EarlyWarningAlert.user_id == user_id,
            EarlyWarningAlert.year == year,
            EarlyWarningAlert.month == month,
            EarlyWarningAlert.category_id == category_id,
            EarlyWarningAlert.status == "ACTIVE"
        ).update({
            "status": "RESOLVED",
            "resolved_at": datetime.utcnow()
        })
        self.session.commit()

    def close_previous_alerts(self, user_id, year, month):

        self.session.query(EarlyWarningAlert).filter(
            EarlyWarningAlert.user_id == user_id,
            EarlyWarningAlert.year == year,
            EarlyWarningAlert.month == month,
            EarlyWarningAlert.status == "ACTIVE"
        ).update({
            "status": "RESOLVED",
            "resolved_at": datetime.utcnow()
        })

        self.session.commit()