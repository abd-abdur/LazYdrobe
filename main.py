# main.py

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import logging

# Import models from models.py
from models import Base, User, EcommerceProduct, WardrobeItem, Outfit, FashionTrend, WeatherData

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL is not set in the environment variables.")
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the database. This is equivalent to "Create Table" statements in raw SQL.
# Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="LazYdrobe API",
    description="API for LazYdrobe Wardrobe Management Application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust based on your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    user_ip: Optional[str] = None
    location: Optional[str] = None
    preferences: Optional[List[str]] = None  # Expecting a list

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    user_id: int
    date_joined: datetime

    class Config:
        orm_mode = True


# Login Schemas

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


# Weather Schemas

class WeatherRequest(BaseModel):
    location_part1: str
    location_part2: Optional[str] = None  # e.g., City, CountryCode


class WeatherResponse(BaseModel):
    date: datetime
    location: str
    temp_max: float
    temp_min: float
    feels_max: float
    feels_min: float
    wind_speed: float
    humidity: float
    precipitation: float
    precipitation_probability: float
    special_condition: str

    class Config:
        orm_mode = True


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Utility Functions

def hash_password(password: str) -> str:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def get_api_key(key_name: str) -> str:
    api_key = os.getenv(key_name)
    if not api_key:
        logger.error(f"{key_name} not found in environment variables.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"{key_name} not found in environment variables.")
    return api_key


def fetch_weather_data(api_key: str, location_part1: str, location_part2: Optional[str] = None) -> List[dict]:
    """
    Fetch weather data for today from Visual Crossing API.
    """
    if location_part2:
        location = f"{location_part1},{location_part2}"
    else:
        location = location_part1

    # URL-encode the location to handle spaces and special characters
    location_encoded = requests.utils.quote(location)

    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_encoded}/next5days?key={api_key}&unitGroup=us&iconSet=icons2&include=days&elements=datetime,tempmax,tempmin,feelslikemax,feelslikemin,windspeed,humidity,precip,precipprob,conditions'
    response = requests.get(url)

    if response.status_code != 200:
        error_message = response.text
        logger.error(f"Failed to fetch weather data. Status Code: {response.status_code}, Message: {error_message}")
        raise HTTPException(status_code=response.status_code, detail=error_message)

    data = response.json()
    if 'days' not in data or not data['days']:
        logger.error("No weather data available for today.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No weather data available for today.")

    # Structure data for DB insertion
    weather_entries = []
    for day in data["days"]:
        # Handle missing fields with default values
        weather_entry = {
            'date': datetime.strptime(day['datetime'], "%Y-%m-%d"),
            'location': location,
            'temp_max': day.get('tempmax', 0.0),
            'temp_min': day.get('tempmin', 0.0),
            'feels_max': day.get('feelslikemax', 0.0),
            'feels_min': day.get('feelslikemin', 0.0),
            'wind_speed': day.get('windspeed', 0.0),
            'humidity': day.get('humidity', 0.0),
            'precipitation': day.get('precip', 0.0),
            'precipitation_probability': day.get('precipprob', 0.0),
            'special_condition': day.get('conditions', 'Unknown'),
            'weather_icon': day.get('weather_icon', '')
        }
        weather_entries.append(weather_entry)

    return weather_entries

def fetch_today_weather_data(api_key: str, location_part1: str, location_part2: Optional[str] = None) -> List[dict]:
    """
    Fetch weather data for today from Visual Crossing API.
    """
    if location_part2:
        location = f"{location_part1},{location_part2}"
    else:
        location = location_part1

    # URL-encode the location to handle spaces and special characters
    location_encoded = requests.utils.quote(location)

    # Update the endpoint from 'next5days' to 'today'
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_encoded}/today?key={api_key}&unitGroup=us&iconSet=icons2&include=days&elements=datetime,tempmax,tempmin,feelslikemax,feelslikemin,windspeed,humidity,precip,precipprob,conditions'
    response = requests.get(url)

    if response.status_code != 200:
        error_message = response.text
        logger.error(f"Failed to fetch weather data. Status Code: {response.status_code}, Message: {error_message}")
        raise HTTPException(status_code=response.status_code, detail=error_message)

    data = response.json()
    if 'days' not in data or not data['days']:
        logger.error("No weather data available for today.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No weather data available for today.")

    # Structure data for DB insertion
    weather_entries = []
    for day in data["days"]:
        # Handle missing fields with default values
        weather_entry = {
            'date': datetime.strptime(day['datetime'], "%Y-%m-%d"),
            'location': location,
            'temp_max': day.get('tempmax', 0.0),
            'temp_min': day.get('tempmin', 0.0),
            'feels_max': day.get('feelslikemax', 0.0),
            'feels_min': day.get('feelslikemin', 0.0),
            'wind_speed': day.get('windspeed', 0.0),
            'humidity': day.get('humidity', 0.0),
            'precipitation': day.get('precip', 0.0),
            'precipitation_probability': day.get('precipprob', 0.0),
            'special_condition': day.get('conditions', 'Unknown'),
            'weather_icon': day.get('weather_icon')
        }
        weather_entries.append(weather_entry)

    return weather_entries

def insert_weather_data_to_db(data: List[dict], user_id: Optional[int] = None):
    """
    Insert fetched weather data into the database using a new DB session.
    """
    db = SessionLocal()
    if not data:
        logger.info("No data to insert into the database.")
        db.close()
        return

    try:
        for entry in data:
            weather_record = WeatherData(
                date=entry['date'],
                location=entry['location'],
                temp_max=entry['temp_max'],
                temp_min=entry['temp_min'],
                feels_max=entry['feels_max'],
                feels_min=entry['feels_min'],
                wind_speed=entry['wind_speed'],
                humidity=entry['humidity'],
                precipitation=entry['precipitation'],
                precipitation_probability=entry['precipitation_probability'],
                special_condition=entry['special_condition'],
                weather_icon=entry['weather_icon'],
                user_id=user_id
            )
            db.add(weather_record)
        db.commit()
        logger.info("Weather data successfully inserted into the database.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inserting data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert weather data into the database.")
    finally:
        db.close()


# API Routes

## User Registration

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating user with email: {user.email}")
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning(f"Email {user.email} already registered.")
        raise HTTPException(status_code=400, detail="Email already registered.")
    
    # Hash the password
    hashed_password = hash_password(user.password)
    
    # Create User instance
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        user_ip=user.user_ip,
        location=user.location,
        preferences=user.preferences
    )
    
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        logger.info(f"User {user.email} created successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
    
    return db_user


## User Login

@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Attempting login for email: {request.email}")
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        logger.warning(f"Login failed for email: {request.email} - User not found.")
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    
    if not verify_password(request.password, user.password):
        logger.warning(f"Login failed for email: {request.email} - Incorrect password.")
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    
    logger.info(f"User {request.email} logged in successfully.")
    return LoginResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email
    )


## Get User by ID

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching user with ID: {user_id}")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found.")
    
    logger.info(f"User with ID {user_id} retrieved successfully.")
    return user


## Weather Endpoint

@app.post("/weather/", response_model=List[WeatherResponse], status_code=status.HTTP_200_OK)
def get_weather_data(weather_request: WeatherRequest, background_tasks: BackgroundTasks):
    """
    Fetch weather data for the given location and return it.
    Optionally, insert the data into the database.
    """
    logger.info(f"Received weather data request for: {weather_request}")
    
    try:
        api_key = get_api_key('VISUAL_CROSSING_API_KEY')
        logger.info("Retrieved Visual Crossing API key successfully.")
    except ValueError as e:
        logger.error(f"API Key Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        # Fetch weather data
        weather_data = fetch_weather_data(api_key, weather_request.location_part1, weather_request.location_part2)
        logger.info("Fetched weather data successfully.")
    except HTTPException as he:
        logger.error(f"HTTPException during weather data fetch: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during weather data fetch: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching weather data.")
    
    try:
        # Insert into DB as a background task with a new session
        background_tasks.add_task(insert_weather_data_to_db, weather_data, user_id=None)  # Replace user_id if needed
        logger.info("Scheduled weather data insertion as a background task.")
    except Exception as e:
        logger.error(f"Error scheduling background task for weather data insertion: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule weather data insertion.")
    
    # Return the data
    logger.info("Returning weather data to the client.")
    return weather_data
