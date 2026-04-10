from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from data.db import Base

utc = lambda: datetime.now(timezone.utc)


class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    
    items = relationship("Item", back_populates="category")

class Item(Base):
    __tablename__ = "items"
    
    item_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    price = Column(Float, nullable=False)
    quantity = Column(Integer) 
    current_stock = Column(Integer, nullable=False)
    unit = Column(String)
    reorder_level = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), default=utc)
    updated_at = Column(DateTime(timezone=True), default=utc, onupdate=utc)
    
    category = relationship("Category", back_populates="items")
    stock_adjustments = relationship("StockAdjust", back_populates="item")
    conditions = relationship("ItemCondition", back_populates="item")
    slow_moving = relationship("SlowMovingOverstock", back_populates="item")

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)
    
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utc)
    
    stock_adjustments = relationship("StockAdjust", back_populates="user")
    reports = relationship("Report", back_populates="user")

class StockAdjust(Base):
    __tablename__ = "stock_adjust"
    
    adjust_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    adjust_type = Column(String)
    quantity = Column(Integer)
    reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), default=utc)
    adjusted_at = Column(DateTime(timezone=True), default=utc)
    
    item = relationship("Item", back_populates="stock_adjustments")
    user = relationship("User", back_populates="stock_adjustments")

class ItemCondition(Base):
    __tablename__ = "item_conditions"
    
    condition_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"))
    condition_type = Column(String)
    quantity = Column(Integer)
    reason = Column(Text)
    cause = Column(Text)
    cost_impact = Column(Float)
    
    recorded_at = Column(DateTime(timezone=True), default=utc)
    
    item = relationship("Item", back_populates="conditions")

class Report(Base):
    __tablename__ = "reports"
    
    report_id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String)
    
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))

    generated_at = Column(DateTime(timezone=True), default=utc)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    parameters = Column(Text) 
    report_data = Column(Text)
    
    user = relationship("User", back_populates="reports")

class SlowMovingOverstock(Base):
    __tablename__ = "slow_moving_overstock"
    
    sm_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"))
    last_adjust_id = Column(Integer, ForeignKey("stock_adjust.adjust_id"))
    
    flagged_at = Column(DateTime(timezone=True), default=utc)
    last_sold_date = Column(DateTime(timezone=True))
    stock_quantity = Column(Integer)
    threshold_days = Column(Integer)
    threshold_quantity = Column(Integer)
    suggested_action = Column(Text)
    
    item = relationship("Item", back_populates="slow_moving")

class Config(Base):
    __tablename__ = "config"
    
    config_id = Column(Integer, primary_key=True, index=True)
    parameter_name = Column(String, unique=True)
    parameter_value = Column(String)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
