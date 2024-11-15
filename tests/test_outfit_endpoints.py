# tests/test_outfit_endpoints.py

import pytest
from fastapi.testclient import TestClient
from main import app
from models import User, WardrobeItem, FashionTrend, WeatherData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def db():
    db = TestingSessionLocal()
    yield db
    db.close()

def setup_user_and_data(db):
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashedpassword",
        location="Test City",
        preferences=["Casual", "Eco-Friendly"],
        gender="Non-Binary"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Add wardrobe items
    item1 = WardrobeItem(
        user_id=user.user_id,
        clothing_type="Jacket",
        for_weather="Cool",
        color=["Black"],
        size="M",
        tags=["Leather Jacket"],
        image_url="url1"
    )
    item2 = WardrobeItem(
        user_id=user.user_id,
        clothing_type="Sweater",
        for_weather="Cool",
        color=["Blue"],
        size="L",
        tags=["Oversized Sweater"],
        image_url="url2"
    )
    db.add_all([item1, item2])
    db.commit()

    # Add fashion trends
    trend = FashionTrend(
        trend_name="Eco-Friendly Materials",
        trend_description="Sustainable and eco-friendly materials are gaining popularity.",
        user_id=user.user_id
    )
    db.add(trend)
    db.commit()

    # Add weather data
    weather = WeatherData(
        user_id=user.user_id,
        date=datetime.utcnow(),
        location="Test City",
        temp_max=20,
        temp_min=15,
        feels_max=20,
        feels_min=15,
        wind_speed=5,
        humidity=50,
        precipitation=0,
        precipitation_probability=0,
        special_condition="Sunny",
        weather_icon="sunny.png"
    )
    db.add(weather)
    db.commit()

    return user.user_id

def test_suggest_outfit(client, db):
    user_id = setup_user_and_data(db)
    response = client.post("/outfits/suggest", json={"user_id": user_id})
    assert response.status_code == 201
    data = response.json()
    assert "suggestion_id" in data
    assert len(data["outfit_details"]) > 0

def test_get_outfit_suggestions(client, db):
    user_id = setup_user_and_data(db)
    # First, create a suggestion
    client.post("/outfits/suggest", json={"user_id": user_id})
    # Now, retrieve suggestions
    response = client.get(f"/outfits/suggestions/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "outfit_details" in data[0]
