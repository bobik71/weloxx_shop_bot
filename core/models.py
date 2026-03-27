# core/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    registered_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="user")

class Order(Base):
    """Запись о покупке"""
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    lzt_item_id = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    sell_price = Column(Float, nullable=False)
    
    login_encrypted = Column(Text, nullable=False)
    password_encrypted = Column(Text, nullable=False)
    
    payment_id = Column(String(255))
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")