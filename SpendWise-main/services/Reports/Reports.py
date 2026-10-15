# services/reports_service.py

from dto.reporting.ReportsDto import ReportCreateDTO
from repositories.reporting.Reports import ReportsRepository
from models.reporting.Reports import Report


class ReportsService:
    def __init__(self, repo: ReportsRepository):
        self.repo = repo

    def create_report(self, dto: ReportCreateDTO):
        report = Report(
            user_id=dto.user_id,
            report_type_id=dto.report_type_id,
            report_date=dto.report_date,
            report_data=dto.report_data
        )
        self.repo.add(report)
        return report

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, report_id: int):
        return self.repo.get_by_id(report_id)

    def get_by_user(self, user_id: int):
        return self.repo.get_by_user(user_id)

    def update(self, report_id: int, dto: ReportCreateDTO):
        return self.repo.update(
            report_id,
            user_id=dto.user_id,
            report_type_id=dto.report_type_id,
            report_date=dto.report_date,
            report_data=dto.report_data
        )

    def delete(self, report_id: int):
        return self.repo.delete_by_id(report_id)