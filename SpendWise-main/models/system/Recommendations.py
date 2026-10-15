from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .Texts import Base as text

from models.base import Base

class Recommendation(Base):
    __tablename__ = 'Recommendations'
    recommendation_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False)
    text_id = Column(Integer, ForeignKey('Texts.text_id'), nullable=False)
    recommendation_date = Column(Date, nullable=False)

    user = relationship("User", back_populates="recommendations")
    text = relationship(
        "Text",
        back_populates="recommendations"
    )
"""
המלצות
"""
