from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class CategoryStandard(Base):
    __tablename__ = "Category_Standards"

    benchmark_id = Column(Integer, primary_key=True, autoincrement=True)

    category_id = Column(
        Integer,
        ForeignKey("Categories.category_id"),
        nullable=False
    )

    amount_per_person = Column(Float, nullable=False)
    is_fixed_cost = Column(Boolean, default=False)

    is_essential = Column(Boolean, nullable=False)

    rule_description = Column(String(255))

    category = relationship(
        "Category",
        back_populates="category_standard"
    )
    max_cut_percent = Column(Float, default=100)