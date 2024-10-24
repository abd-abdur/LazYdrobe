from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd
from typing import List

# Database configuration
SQLALCHEMY_DATABASE_URL = "postgresql://lazydrobe:k6@059Of:OpD@UpO@34.44.42.132:5432/lazydrobe"  
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# SQLAlchemy model for Wardrobe Items
class WardrobeItems(Base):
    __tablename__ = "wardrobe_items"
    item_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    type = Column(String, nullable=False)
    season = Column(String)
    fabric = Column(String)
    color = Column(String)
    size = Column(String)
    tags = Column(String)
    image_url = Column(String)

# SQLAlchemy model for Users (minimal version)
class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to display users table
def display_users_table():
    # Create a database session
    db = SessionLocal()
    # Query all users
    users = db.query(Users).all()
    # Convert the query results to a Pandas DataFrame for tabular display
    users_df = pd.DataFrame([{
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email
    } for user in users])
    db.close()
    return users_df

# Function to display wardrobe items table
def display_wardrobe_items_table():
    # Create a database session
    db = SessionLocal()
    # Query all wardrobe items
    wardrobe_items = db.query(WardrobeItems).all()
    # Convert the query results to a Pandas DataFrame for tabular display
    wardrobe_df = pd.DataFrame([{
        'item_id': item.item_id,
        'user_id': item.user_id,
        'type': item.type,
        'season': item.season,
        'fabric': item.fabric,
        'color': item.color,
        'size': item.size,
        'tags': item.tags,
        'image_url': item.image_url
    } for item in wardrobe_items])
    db.close()
    return wardrobe_df

# Sample function to insert a user
def insert_sample_user():
    db = SessionLocal()
    new_user = Users(username="example_user", email="example_user@example.com")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

# Sample function to insert wardrobe items
def insert_sample_wardrobe_item():
    db = SessionLocal()
    new_item = WardrobeItems(user_id=1, type="T-shirt", season="Summer", fabric="Cotton", color="Blue", size="M", tags="casual", image_url="https://example.com/tshirt.jpg")
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    db.close()

# Insert sample data
insert_sample_user()
insert_sample_wardrobe_item()

# Display tables as outputs
users_df = display_users_table()
wardrobe_df = display_wardrobe_items_table()

# Show users table
print("Users Table:")
users_df

# Show wardrobe items table
print("Wardrobe Items Table:")
wardrobe_df
