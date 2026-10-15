from sqlalchemy import Column, Integer, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Float
from models.base import Base

class Expense(Base):
    __tablename__ = "Expenses"

    transaction_id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=False
    )

    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    expense_type_id = Column(
        Integer,
        ForeignKey("ExpenseTypes.expenseTypeId")
    )

    category_id = Column(
        Integer,
        ForeignKey("Categories.category_id"),
        nullable=False
    )

    expense_type = relationship(
        "ExpenseType",
        back_populates="expenses"
    )

    user = relationship(
        "User",
        back_populates="expenses"
    )

    category = relationship(
        "Category",
        back_populates="expenses"
    )