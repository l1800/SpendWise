from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, relationship

from models.base import Base


class ExpenseType(Base):
    __tablename__ = "ExpenseTypes"

    expenseTypeId = Column(
        Integer,
        primary_key=True,
        autoincrement=True  # <- הוסף את זה
    )

    expenseTypeName = Column(
        String(50),
        nullable=False,
        unique=True
    )

    expenses = relationship(
        "Expense",
        back_populates="expense_type"
    )