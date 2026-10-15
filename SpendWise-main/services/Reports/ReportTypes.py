# services/Reports/ReportTypes.py

from dto.reporting.ReportTypesDto import ReportTypeCreateDTO, ReportTypeResponseDTO
from repositories.reporting.ReportTypes import ReportTypesRepository
from models.reporting.ReportTypes import ReportType


class ReportTypesService:
    def __init__(self, repo: ReportTypesRepository):
        self.repo = repo


    def get_all(self) -> list[ReportType]:
        return self.repo.get_all()

    def get_by_id(self, report_type_id: int) -> ReportType | None:
        return self.repo.get_by_id(report_type_id)


    """
        def update(self, report_type_id: int, dto: ReportTypeCreateDTO) -> ReportType | None:
        report_type = self.repo.get_by_id(report_type_id)
        if not report_type:
            return None

        report_type.report_type_name = dto.report_type_name
        return self.repo.update(report_type)

    def delete(self, report_type_id: int) -> bool:
        return self.repo.delete_by_id(report_type_id)
        
        def create(self, dto: ReportTypeCreateDTO) -> ReportType:
        # יוצרים מופע חדש של ReportType
        report_type = ReportType(report_type_name=dto.report_type_name)
        return self.repo.create(report_type)
   
    """