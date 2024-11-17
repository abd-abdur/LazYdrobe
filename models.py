# models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    JSON,
    Text,
    BigInteger,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    user_ip = Column(String(255))
    location = Column(String(255))
    preferences = Column(JSON, nullable=True)
    gender = Column(String(50), nullable=True)
    date_joined = Column(DateTime, server_default=func.now())

    wardrobe_items = relationship("WardrobeItem", back_populates="owner", cascade="all, delete-orphan")
    outfits = relationship("Outfit", back_populates="user", cascade="all, delete-orphan")
    ecommerce_products = relationship("EcommerceProduct", back_populates="user", cascade="all, delete-orphan")
    weather_data = relationship("WeatherData", back_populates="user", cascade="all, delete-orphan")
    fashion_trends = relationship("FashionTrend", back_populates="user", cascade="all, delete-orphan")
    outfit_suggestions = relationship("OutfitSuggestion", back_populates="user", cascade="all, delete-orphan")

class EcommerceProduct(Base):
    __tablename__ = "ecommerce_products"

    product_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    ebay_item_id = Column(String(50), unique=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    suggested_item_type = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False) 
    product_url = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=True)
    date_suggested = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    user = relationship("User", back_populates="ecommerce_products")
    wardrobe_items = relationship("WardrobeItem", back_populates="product")

class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    product_id = Column(BigInteger, ForeignKey("ecommerce_products.product_id"), nullable=True)
    clothing_type = Column(String(255), nullable=False)
    for_weather = Column(String(255), nullable=True)
    color = Column(JSON, nullable=True)
    size = Column(String(50), nullable=True)
    tags = Column(JSON, nullable=True)
    image_url = Column(String(255), nullable=True)
    date_added = Column(DateTime, server_default=func.now())

    owner = relationship("User", back_populates="wardrobe_items")
    product = relationship("EcommerceProduct", back_populates="wardrobe_items")

class Outfit(Base):
    __tablename__ = "outfits"

    outfit_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    occasion = Column(JSON, nullable=True)
    for_weather = Column(String(255), nullable=True)
    source_url = Column(String(255), nullable=True)
    date_suggested = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="outfits")

class FashionTrend(Base):
    __tablename__ = "fashion_trends"

    trend_id = Column(Integer, primary_key=True, autoincrement=True)
    trend_name = Column(String(255), nullable=False, index=True)
    trend_description = Column(Text, nullable=False)
    date_added = Column(DateTime, server_default=func.now())
    trend_search_phrase = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    user = relationship("User", back_populates="fashion_trends")

class WeatherData(Base):
    __tablename__ = "weather_data"

    weather_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    location = Column(String(255), nullable=False)
    temp_max = Column(Float, nullable=False)
    temp_min = Column(Float, nullable=False)
    feels_max = Column(Float, nullable=False)
    feels_min = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    precipitation = Column(Float, nullable=False)
    precipitation_probability = Column(Float, nullable=False)
    special_condition = Column(String(255), nullable=True)
    weather_icon = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

    user = relationship("User", back_populates="weather_data")

class OutfitSuggestion(Base):
    __tablename__ = "outfit_suggestions"

    suggestion_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    outfit_details = Column(JSON, nullable=False)  # Stores outfit components and eBay links
    date_suggested = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="outfit_suggestions")
