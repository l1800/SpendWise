# models/reporting/ReportTypes.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base

class ReportType(Base):
    __tablename__ = 'Report_Types'

    report_type_id = Column(Integer, primary_key=True, autoincrement=True)
    report_type_name = Column(String(50), unique=True, nullable=False)

    # קשר ל-Report אם קיים טבלת דו"חות
    reports = relationship("Report", back_populates="report_type", cascade="all, delete-orphan")