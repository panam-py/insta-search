from sqlalchemy import Column, DateTime, String, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique = True, nullable = False)
    password = Column(String, nullable = False)
    created_at = Column(DateTime(timezone=True), server_default = func.now())
    updated_at = Column(DateTime(timezone=True), onupdate = func.now())

class Influencer(Base):
    __tablename__ = "influencers"
    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete = 'CASCADE'), nullable = False)
    username = Column(String, unique = True, nullable = False)
    follower_count = Column(Integer, nullable = False)
    bio = Column(String)
    created_at = Column(DateTime(timezone=True), server_default = func.now())
    updated_at = Column(DateTime(timezone=True), onupdate = func.now())
    user = relationship('User')