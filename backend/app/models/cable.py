from sqlalchemy import Column, Float, Integer, String

from .base import Base


class Cable(Base):
    __tablename__ = "cables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(1024), nullable=True)
    diameter_mm = Column(Float, nullable=True)
