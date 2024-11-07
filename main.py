# main.py

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# Import models from models.py
from models import (
    Base,
    User,
    EcommerceProduct,
    WardrobeItem,
    Outfit,
    FashionTrend,
    WeatherData
)

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(bind=engine)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    user_ip: Optional[str] = None
    location: Optional[str] = None
    preferences: Optional[List[str]] = None

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    user_id: int
    date_joined: datetime

    class Config:
        orm_mode = True

# Login Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize FastAPI app
app = FastAPI(
    title="LazYdrobe API",
    description="API for LazYdrobe Wardrobe Management Application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production (e.g., ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility Functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# API Routes

## User Registration
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_pwd = hash_password(user.password)
    # Store preferences as a comma-separated string or an empty string
    preferences_str = ','.join(user.preferences) if user.preferences else ''
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_pwd,
        user_ip=user.user_ip,
        location=user.location,
        preferences=preferences_str
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error.")
    return db_user

## User Login
@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    return LoginResponse(user_id=user.user_id, username=user.username, email=user.email)

## Get User by ID
@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Convert preferences from string to list
    if user.preferences:
        preferences_list = user.preferences.split(',') if user.preferences else []
    else:
        preferences_list = []
    
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        user_ip=user.user_ip,
        location=user.location,
        preferences=preferences_list,
        date_joined=user.date_joined
    )