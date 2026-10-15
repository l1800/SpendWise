from sqlalchemy import Column, Integer, Date, String
from sqlalchemy.orm import relationship
from models.base import Base


class SpecialDate(Base):
    __tablename__ = "Special_Dates"

    type_id = Column(Integer, primary_key=True, autoincrement=True)
    holiday_name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    special_period_summaries = relationship(
        "SpecialPeriodSummary",
        back_populates="special_period"
    )

    holiday_category_summaries = relationship(
        "HolidayCategorySummary",
        back_populates="special_period"
    )