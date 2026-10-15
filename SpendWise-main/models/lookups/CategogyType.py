from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base

class CategoryType(Base):
    __tablename__ = 'Category_Types'
    category_type_id = Column(Integer, primary_key=True)
    category_type_name = Column(String(50), unique=True, nullable=False)
    categories = relationship("Category", back_populates="category_type")
