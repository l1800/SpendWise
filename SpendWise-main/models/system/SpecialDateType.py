from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base


class SpecialDateType(Base):
    __tablename__ = "Special_Date_Types"

    type_id = Column(Integer, primary_key=True)
    type_name = Column(String(50))

