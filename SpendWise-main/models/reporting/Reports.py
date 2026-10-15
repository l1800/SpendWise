from sqlalchemy import Column, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base


class Report(Base):
    __tablename__ = 'Reports'
    report_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False)
    report_type_id = Column(Integer, ForeignKey('Report_Types.report_type_id'), nullable=False)
    report_date = Column(Date, nullable=False)
    report_data = Column(Text)

    user = relationship("User", back_populates="reports")
    report_type = relationship("ReportType", back_populates="reports")
# Reports.py - models
