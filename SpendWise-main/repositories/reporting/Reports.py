# repositories/reports_forecasts/reports_repository.py

from models.reporting.Reports import Report
from repositories.base_repository import BaseRepository


class ReportsRepository(BaseRepository):

    def get_by_id(self, report_id):
        return (
            self.session.query(Report)
            .filter_by(report_id=report_id)
            .first()
        )

    def get_all(self):
        return self.session.query(Report).all()

    def get_by_user(self, user_id):
        return (
            self.session.query(Report)
            .filter_by(user_id=user_id)
            .all()
        )

    def update(self, report_id, **kwargs):
        report = self.get_by_id(report_id)

        if not report:
            return None

        for key, value in kwargs.items():
            setattr(report, key, value)

        self.session.commit()
        return report

    def delete_by_id(self, report_id):
        report = self.get_by_id(report_id)

        if report:
            self.delete(report)

        return report
