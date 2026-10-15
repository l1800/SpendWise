from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class SpecialPeriodSummary(Base):
    __tablename__ = "Special_Period_Summary"

    summary_id = Column(Integer, primary_key=True, autoincrement=True)

    special_period_id = Column(Integer, ForeignKey("Special_Dates.type_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("Categories.category_id"), nullable=False)

    spent_amount = Column(Integer, nullable=False, default=0)
    approved_amount = Column(Integer, nullable=False)

    user = relationship("User", back_populates="special_period_summaries")
    category = relationship("Category", back_populates="special_period_summaries")

    special_period = relationship("SpecialDate", back_populates="special_period_summaries")