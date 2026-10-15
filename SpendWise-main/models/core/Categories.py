from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Category(Base):
    __tablename__ = 'Categories'

    category_id = Column(Integer, primary_key=True, autoincrement=True)

    category_name = Column(String(100), nullable=False)

    category_type_id = Column(
        Integer,
        ForeignKey('Category_Types.category_type_id'),
        nullable=False
    )

    category_description = Column(Text)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # ===== relationships =====

    category_type = relationship(
        "CategoryType",
        back_populates="categories"
    )

    category_standard = relationship(
        "CategoryStandard",
        back_populates="category",
        uselist=False
    )

    expenses = relationship(
        "Expense",
        back_populates="category"
    )

    special_expenses = relationship(
        "SpecialExpense",
        back_populates="category"
    )

    forecasts = relationship(
        "FinancialForecast",
        back_populates="category"
    )

    holiday_summaries = relationship(
        "HolidayCategorySummary",
        back_populates="category"
    )

    monthly_expense_summaries = relationship(
        "MonthlyExpensesSummary",
        back_populates="category"
    )

    special_period_summaries = relationship(
        "SpecialPeriodSummary",
        back_populates="category"
    )

    category_goals = relationship(
        "UserCategoryGoal",
        back_populates="category"
    )
    user_category_preferences = relationship(
        "UserCategoryPreference",
        back_populates="category"
    )
    early_warning_alerts = relationship(
        "EarlyWarningAlert",
        back_populates="category"
    )

    budget_plans = relationship(
        "BudgetPlan",
        back_populates="category"
    )