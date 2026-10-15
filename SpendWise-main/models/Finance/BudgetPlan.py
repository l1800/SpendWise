from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from models.base import Base


class BudgetPlan(Base):
    __tablename__ = "Budget_Plans"

    plan_id = Column(Integer, primary_key=True, autoincrement=True)

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

    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    planned_amount = Column(Float, nullable=False, default=0)

    holiday_adjustment = Column(Float, nullable=False, default=0)

    holiday_name = Column(String(100), nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # ── relationships ──

    user = relationship(
        "User",
        back_populates="budget_plans"
    )

    category = relationship(
        "Category",
        back_populates="budget_plans"
    )
