from sqlalchemy import Column, Integer, Text as SQLText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from models.base import Base

class Text(Base):
    __tablename__ = "Texts"

    text_id = Column(Integer, primary_key=True)
    the_text = Column(SQLText, nullable=False)

    recommendations = relationship(
        "Recommendation",
        back_populates="text"
    )
