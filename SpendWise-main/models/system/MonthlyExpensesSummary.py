import datetime

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from models.base import Base
from sqlalchemy import Float

class MonthlyExpensesSummary(Base):
    __tablename__ = "Monthly_Expenses_Summary"

    summary_id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("Categories.category_id"),
        nullable=False
    )

    month_year = Column(String(7), nullable=False)  # YYYY-MM

    total_amount = Column(Float, nullable=False)

    user = relationship(
        "User",
        back_populates="monthly_expense_summaries"
    )

    category = relationship(
        "Category",
        back_populates="monthly_expense_summaries"
    )