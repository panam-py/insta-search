from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique = True, nullable = False)
    password = Column(String, nullable = False)
    created_at = Column(DateTime(timezone=True), server_default = func.now())
    updated_at = Column(DateTime(timezone=True), onupdate = func.now())

