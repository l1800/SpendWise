from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class FinancialForecast(Base):
    __tablename__ = 'Financial_Forecasts'

    forecast_id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey('Users.user_id'),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey('Categories.category_id'),
        nullable=False
    )

    forecast_date = Column(
        Date,
        nullable=False
    )

    forecast_count = Column(
        Integer,
        nullable=False
    )

    range_id = Column(
        Integer,
        ForeignKey('Forecast_Ranges.range_id'),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="forecasts"
    )
    category = relationship(
        "Category",
        back_populates="forecasts"
    )

    range = relationship(
        "ForecastRange",
        back_populates="financial_forecasts"
    )