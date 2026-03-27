from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
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
    balance = Column(Float, default=0.0)
    
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    lzt_item_id = Column(Integer, unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="RUB")
    
    # Encrypted credentials
    login_encrypted = Column(Text, nullable=False)
    password_encrypted = Column(Text, nullable=False)
    extra_data_encrypted = Column(Text)
    
    is_available = Column(Boolean, default=True)
    is_guaranteed = Column(Boolean, default=False)
    guarantee_hours = Column(Integer, default=0)
    
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = relationship("Order", back_populates="account")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    status = Column(String(50), default="pending")
    payment_method = Column(String(50))
    payment_id = Column(String(255))
    amount_paid = Column(Float)
    currency = Column(String(10), default="RUB")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="orders")
    account = relationship("Account", back_populates="orders")

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="cart_items")
    account = relationship("Account")

class PaymentLog(Base):
    __tablename__ = "payment_logs"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    event_type = Column(String(50))
    payload = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)