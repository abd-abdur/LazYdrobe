# main.py

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests
import logging

# Import models from models.py
from models import Base, User, EcommerceProduct, WardrobeItem, Outfit, FashionTrend, WeatherData, OutfitSuggestion

# Import fashion_trends function
from fashion_trends import fetch_and_update_fashion_trends

from outfit_suggester import suggest_outfits

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL is not set in the environment variables.")
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)  # Set echo to False for production

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    location: str  # Now required
    preferences: Optional[List[str]] = None
    gender: Optional[str] = None

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    user_ip: Optional[str] = None
    location: Optional[str] = None
    preferences: Optional[List[str]] = None  # Expecting a list
    gender: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)

    class Config:
        orm_mode = True


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
    user_id: int 

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
    weather_icon: str

    class Config:
        orm_mode = True

class FashionTrendResponse(BaseModel):
    trend_id: int
    trend_name: str
    trend_description: str
    date_added: datetime

    class Config:
        orm_mode = True

# Wardrobe Item Schemas

class WardrobeItemBase(BaseModel):
    clothing_type: Optional[str] = Field(..., min_length=3, max_length=50)
    for_weather: Optional[str] = None
    color: Optional[List[str]] = None
    size: Optional[str] = Field(..., min_length=1, max_length=50)
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None

    class Config:
        orm_mode = True


class WardrobeItemCreate(WardrobeItemBase):
    user_id: int


class WardrobeItemUpdate(BaseModel):
    clothing_type: Optional[str] = Field(None, min_length=3, max_length=50)
    for_weather: Optional[str] = Field(None, min_length=3, max_length=50)
    color: Optional[List[str]] = None
    size: Optional[str] = Field(None, min_length=1, max_length=50)
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None

    class Config:
        orm_mode = True


class WardrobeItemResponse(WardrobeItemBase):
    item_id: int
    clothing_type: str
    for_weather: str
    color: List[str]
    size: str
    tags: List[str]
    image_url: Optional[str] = None

    class Config:
        orm_mode = True

# Outfit

class OutfitBase(BaseModel):
    occasion: Optional[List[str]] = None
    for_weather: Optional[str] = None
    clothings: Optional[List[int]] = None
    source_url: Optional[str] = None

class OutfitCreate(OutfitBase):
    user_id: int

class OutfitResponse(OutfitBase):
    outfit_id: int
    clothings: List[int]
    occasion: List[str]
    for_weather: Optional[str]

    class Config:
        orm_mode = True

class OutfitUpdate(BaseModel):
    occasion: Optional[List[str]] = None
    for_weather: Optional[str] = None

# Outfit Suggestion

class OutfitComponent(BaseModel):
    clothing_type: str
    item_id: int
    product_name: str
    image_url: Optional[str] = None
    eBay_link: Optional[List[str]] = None 
    
    class Config:
        orm_mode = True


class OutfitSuggestionResponse(BaseModel):
    suggestion_id: int
    outfit_details: List[List[OutfitComponent]]
    date_suggested: datetime

    class Config:
        orm_mode = True
        
class OutfitSuggestionRequest(BaseModel):
    user_id: int

class OutfitSuggestionCreateResponse(BaseModel):
    suggestion_id: int
    outfit_details: List[List[OutfitComponent]]
    date_suggested: datetime

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

def fetch_weather_data_from_db(location:str) -> List[dict]:
    """
    Try to fetch 5 days of weather data in location from database
    Returns all five or []
    """    
    today = datetime.utcnow().date()
    db = SessionLocal()

    weather_data = []
    logger.info(f"Fetching data from database")

    try:
        for i in range(4):
            date = today + timedelta(days=i)
            entry = (
                db.query(WeatherData)
                .filter(WeatherData.location == location, WeatherData.date == date)
                .first()
            )
            if entry:
                weather_data.append({
                    'date': entry.date,
                    'location': entry.location,
                    'temp_max': entry.temp_max,
                    'temp_min': entry.temp_min,
                    'feels_max': entry.feels_max,
                    'feels_min': entry.feels_min,
                    'wind_speed': entry.wind_speed,
                    'humidity': entry.humidity,
                    'precipitation': entry.precipitation,
                    'precipitation_probability': entry.precipitation_probability,
                    'special_condition': entry.special_condition,
                    'weather_icon': entry.weather_icon,
                })
                logger.info(f"Obtained weather data for {date}")
            else:
                break;
    except Exception as e:
        logger.error(f"Error fetching data from database: {e}")
        return []
    finally:
        db.close()
    
    logger.info(weather_data)
    if len(weather_data) == 4:
        return weather_data  
    return []

def fetch_weather_data(api_key: str, location: str) -> List[dict]:
    """
    Try to get weather data from DB,
    Fetch weather data from Visual Crossing API.
    """

    weather_entries=fetch_weather_data_from_db(location)

    if (weather_entries):
        return weather_entries

    # URL-encode the location to handle spaces and special characters
    location_encoded = requests.utils.quote(location)

    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_encoded}/next3days?key={api_key}&unitGroup=us&iconSet=icons2'
    response = requests.get(url)
    logger.info("Getting weather data from API")

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
            'weather_icon': day.get('icon', '')
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
            existing_record = db.query(WeatherData).filter_by(
                date=entry['date'], location=entry['location']
            ).first()

            if existing_record:
                # Update the existing record
                existing_record.temp_max = entry['temp_max']
                existing_record.temp_min = entry['temp_min']
                existing_record.feels_max = entry['feels_max']
                existing_record.feels_min = entry['feels_min']
                existing_record.wind_speed = entry['wind_speed']
                existing_record.humidity = entry['humidity']
                existing_record.precipitation = entry['precipitation']
                existing_record.precipitation_probability = entry['precipitation_probability']
                existing_record.special_condition = entry['special_condition']
                existing_record.weather_icon = entry['weather_icon']
                existing_record.user_id = user_id
                logger.info(f"Updated existing weather record for {entry['date']} at {entry['location']}.")
            else:
                # Else input
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
        logger.info("Weather data successfully updated or inserted into the database.")
        db.commit()
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
        location=user.location,  # Now required
        preferences=user.preferences,
        gender=user.gender 
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


## Update User Information

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating user with ID: {user_id}")
    logger.debug(f"Update data received: {user_update.dict()}")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found.")

    # If password is being updated, hash it
    if user_update.password:
        logger.debug("Updating password.")
        user.password = hash_password(user_update.password)

    # Update other fields if provided
    update_data = user_update.dict(exclude_unset=True, exclude={"password"})
    logger.debug(f"Updating fields: {update_data}")
    for key, value in update_data.items():
        setattr(user, key, value)

    try:
        db.commit()
        db.refresh(user)
        logger.info(f"User with ID {user_id} updated successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

    return user


## Delete User

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting user with ID: {user_id}")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found.")

    try:
        db.delete(user)
        db.commit()
        logger.info(f"User with ID {user_id} deleted successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

    return


## Create Wardrobe Item

@app.post("/wardrobe_item/", response_model=WardrobeItemResponse, status_code=status.HTTP_201_CREATED)
def create_wardrobe_item(item: WardrobeItemCreate, db: Session = Depends(get_db)):
    logger.info(f"Adding wardrobe item for user ID: {item.user_id}")

    # Create a new WardrobeItem instance
    db_item = WardrobeItem(
        user_id=item.user_id,
        product_id=None, 
        clothing_type=item.clothing_type,
        for_weather=item.for_weather,
        color=item.color,
        size=item.size,
        tags=item.tags,
        image_url=item.image_url
    )

    # Add the item to the database
    db.add(db_item)
    try:
        db.commit()
        db.refresh(db_item)
        logger.info(f"Wardrobe item with ID {db_item.item_id} created successfully.")
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create wardrobe item: {e}")
        raise HTTPException(status_code=500, detail="Failed to create wardrobe item.")

## Get Wardrobe Items for User

@app.get("/wardrobe_items/user/{user_id}", response_model=List[WardrobeItemResponse])
def get_all_wardrobe_items(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching wardrobe item for user ID: {user_id}")
    items = db.query(WardrobeItem).filter(WardrobeItem.user_id == user_id).all()
    if not items:
        raise HTTPException(status_code=404, detail="No wardrobe items found for this user.")
    return items

## Get Wardrobe Item Information

@app.get("/wardrobe_items/{item_id}", response_model=WardrobeItemResponse)
def read_wardrobe_item(item_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching wardrobe item with ID: {item_id}")

    wardrobe_item = db.query(WardrobeItem).filter(WardrobeItem.item_id == item_id).first()
    if not wardrobe_item:
        logger.warning(f"Wardrobe item with ID {item_id} not found.")
        raise HTTPException(status_code=404, detail="Wardrobe item not found.")

    logger.info(f"Wardrobe item with ID {item_id} retrieved successfully.")
    return wardrobe_item


## Update Wardrobe Item Information

@app.put("/wardrobe_items/{item_id}", response_model=WardrobeItemResponse)
def update_wardrobe_item(item_id: int, item_update: WardrobeItemUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating wardrobe item with ID: {item_id}")
    logger.debug(f"Update data received: {item_update.dict()}")

    wardrobe_item = db.query(WardrobeItem).filter(WardrobeItem.item_id == item_id).first()
    if not wardrobe_item:
        logger.warning(f"Wardrobe item with ID {item_id} not found.")
        raise HTTPException(status_code=404, detail="Wardrobe item not found.")

    # Update fields from the incoming request if they are provided
    update_data = item_update.dict(exclude_unset=True)
    logger.debug(f"Updating fields: {update_data}")
    for key, value in update_data.items():
        setattr(wardrobe_item, key, value)

    try:
        db.commit()
        db.refresh(wardrobe_item)
        logger.info(f"Wardrobe item with ID {item_id} updated successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update wardrobe item: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update wardrobe item: {str(e)}")

    return wardrobe_item


## Delete Wardrobe Item

@app.delete("/wardrobe_items", status_code=status.HTTP_204_NO_CONTENT)
def delete_wardrobe_item(item_ids: List[int] = Body(..., embed=True), db: Session = Depends(get_db)):
    logger.info(f"Deleting wardrobe item with IDs: {item_ids}")

    not_found_items = []
    for item_id in item_ids:
        wardrobe_item = db.query(WardrobeItem).filter(WardrobeItem.item_id == item_id).first()
        if not wardrobe_item:
            not_found_items.append(item_id)
        else:
            try:
                db.delete(wardrobe_item)
                db.commit()
                logger.info(f"Wardrobe item with ID {item_id} deleted successfully.")
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to delete wardrobe item with ID {item_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to delete wardrobe item with ID {item_id}: {str(e)}")

    # If there are any items not found, return a 404 error
    if not_found_items:
        raise HTTPException(status_code=404, detail=f"Wardrobe items with IDs {', '.join(map(str, not_found_items))} not found.")

    return


## Weather Endpoint

@app.post("/weather/", response_model=List[WeatherResponse], status_code=status.HTTP_200_OK)
def get_weather_data(weather_request: WeatherRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Fetch weather data for the given user based on their stored location and insert it into the database.
    """
    logger.info(f"Received weather data request for user_id={weather_request.user_id}")

    # Fetch user from DB to get location
    user = db.query(User).filter(User.user_id == weather_request.user_id).first()
    if not user:
        logger.error(f"User with ID {weather_request.user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found.")

    if not user.location:
        logger.error(f"User with ID {weather_request.user_id} does not have a location set.")
        raise HTTPException(status_code=400, detail="User location not set.")

    location = user.location

    try:
        weather_data = fetch_weather_data_from_db(location)
        if not weather_data:
            logger.info(weather_data)
            raise ValueError(f"No full weather data for {location} found in the database.")
        
    except ValueError:
        try:
            api_key = get_api_key('VISUAL_CROSSING_API_KEY')
            logger.info("Retrieved Visual Crossing API key successfully.")
        except ValueError as e:
            logger.error(f"API Key Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        try:
            weather_data = fetch_weather_data(api_key, location)
            logger.info("Fetched weather data successfully.")
        except HTTPException as he:
            logger.error(f"HTTPException during weather data fetch: {he.detail}")
            raise he
        except Exception as e:
            logger.error(f"Unexpected error during weather data fetch: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching weather data.")

        try:
            # Insert into DB as a background task with the provided user_id
            background_tasks.add_task(insert_weather_data_to_db, weather_data, user_id=weather_request.user_id)
            logger.info("Scheduled weather data insertion as a background task.")
        except Exception as e:
            logger.error(f"Error scheduling background task for weather data insertion: {e}")
            raise HTTPException(status_code=500, detail="Failed to schedule weather data insertion.")

    # Return the data
    logger.info("Returning weather data to the client.")
    return weather_data



## Fashion Trends Endpoints

@app.post("/fashion_trends/update", status_code=status.HTTP_202_ACCEPTED)
def update_fashion_trends_endpoint(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Endpoint to trigger the fetching and updating of fashion trends.
    """
    background_tasks.add_task(fetch_and_update_fashion_trends, db)
    logger.info("Fashion trends update initiated via API.")
    return {"message": "Fashion trends update initiated."}

@app.get("/fashion_trends/", response_model=List[FashionTrendResponse], status_code=status.HTTP_200_OK)
def get_fashion_trends(db: Session = Depends(get_db)):
    """
    Retrieve the latest fashion trends from the database.
    """
    trends = db.query(FashionTrend).order_by(FashionTrend.date_added.desc()).all()
    return trends

## Create Custom Outfit
@app.post("/outfit/", response_model=OutfitResponse, status_code=status.HTTP_201_CREATED)
def create_outfit(outfit: OutfitCreate, db: Session = Depends(get_db)):
    """
    Create a customized outfit and save it to the database
    """
    db_outfit = Outfit(
        user_id=outfit.user_id,
        occasion=outfit.occasion,
        for_weather=outfit.for_weather,
        clothings=outfit.clothings
    )

    db.add(db_outfit)
    try:
        db.commit()
        db.refresh(db_outfit)
        logger.info(f"Outfit with ID {db_outfit.outfit_id} created successfully.")
        return db_outfit
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create outfit: {e}")
        raise HTTPException(status_code=400, detail="Failed to create outfit")

## Get Outfits for User

@app.get("/outfits/user/{user_id}", response_model=List[OutfitResponse])
def get_all_outfits(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching outfits for user ID: {user_id}")
    outfits = db.query(Outfit).filter(Outfit.user_id == user_id).all()

    if not outfits:
        raise HTTPException(status_code=404, detail="No outfits found for this user.")
    
    return outfits

## Get Outfit Information

@app.get("/outfits/{outfit_id}", response_model=OutfitResponse)
def read_outfit(outfit_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching outfit with ID: {outfit_id}")
    outfit = db.query(Outfit).filter(Outfit.outfit_id == outfit_id).first()

    if not outfit:
        logger.warning(f"Outfit with ID {outfit_id} not found.")
        raise HTTPException(status_code=404, detail="Outfit not found.")

    logger.info(f"Outfit with ID {outfit_id} retrieved successfully.")
    return outfit

## Delete Outfits

@app.delete("/outfits/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outfit(outfit_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting outfits with ID: {outfit_id}")

    outfit = db.query(Outfit).filter(Outfit.outfit_id == outfit_id).first()
    if not outfit:
        logger.warning(f"Outfit with ID {outfit_id} not found.")
        raise HTTPException(status_code=404, detail="Outfit not found.")

    try:
        db.delete(outfit)
        db.commit()
        logger.info(f"Outfit with ID {outfit_id} deleted successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete outfit with ID {outfit_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete outfit with ID {outfit_id}: {str(e)}")
    return

## Update Outfit Information

@app.put("/outfits/{outfit_id}", response_model=OutfitResponse)
def update_outfit(outfit_id: int, outfit_update: OutfitUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating outfit with ID: {outfit_id}")
    logger.info(f"Update data received: {outfit_update.dict()}")
    logger.debug(f"Update data received: {outfit_update.dict()}")

    outfit = db.query(Outfit).filter(Outfit.outfit_id == outfit_id).first()
    if not outfit:
        logger.warning(f"Outfit with ID {outfit_id} not found.")
        raise HTTPException(status_code=404, detail="Outfit not found.")

    # Update fields from the incoming request if they are provided
    update_data = outfit_update.dict(exclude_unset=True)
    logger.debug(f"Updating fields: {update_data}")
    for key, value in update_data.items():
        setattr(outfit, key, value)

    try:
        db.commit()
        db.refresh(outfit)
        logger.info(f"Outfit with ID {outfit_id} updated successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update outfit: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update outfit: {str(e)}")

    return outfit


# Outfit suggest

@app.post("/outfits/suggest", response_model=OutfitSuggestionCreateResponse, status_code=status.HTTP_201_CREATED)
def suggest_outfit(request: OutfitSuggestionRequest, db: Session = Depends(get_db)):
    """
    Suggests outfits for the user based on current weather and fashion trends.
    Does not consider the user's existing wardrobe.
    """
    logger.info(f"Received outfit suggestion request for user_id={request.user_id}")
    
    try:
        outfit_suggestion = suggest_outfits(request.user_id, db)
        return outfit_suggestion
    except ValueError as ve:
        logger.error(f"ValueError during outfit suggestion: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error during outfit suggestion: {e}")
        raise HTTPException(status_code=500, detail="Failed to suggest outfits.")



from sqlalchemy.orm import joinedload

@app.get("/outfits/suggestions/{user_id}", response_model=List[OutfitSuggestionResponse], status_code=status.HTTP_200_OK)
def get_outfit_suggestions(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all outfit suggestions for the specified user.
    """
    suggestions = db.query(OutfitSuggestion).options(joinedload(OutfitSuggestion.user)).filter(OutfitSuggestion.user_id == user_id).order_by(OutfitSuggestion.date_suggested.desc()).all()
    if not suggestions:
        raise HTTPException(status_code=404, detail="No outfit suggestions found for this user.")
    return suggestions

# @app.post("/fashion_trends/test_update", status_code=status.HTTP_200_OK)
# def test_update_fashion_trends(db: Session = Depends(get_db)):
#     """
#     Temporary endpoint to test fetching and updating fashion trends synchronously.
#     """
#     try:
#         fetch_and_update_fashion_trends(db)
#         return {"message": "Fashion trends update completed successfully."}
#     except Exception as e:
#         logger.error(f"Error during test fashion trends update: {e}")
#         raise HTTPException(status_code=500, detail=f"Error during update: {str(e)}")


## Exception Handlers

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )
