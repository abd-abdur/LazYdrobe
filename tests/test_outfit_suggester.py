# tests/test_outfit_suggester.py

import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from unittest.mock import patch

# Add project root to sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import models and functions
from models import Base, User, WardrobeItem, FashionTrend, WeatherData
from outfit_suggester import suggest_outfits

# Setup in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    """Fixture to create a new database session for each test."""
    session = TestingSessionLocal()
    yield session
    session.close()

def test_suggest_outfits(db):
    # Create a user
    user = User(
        username="test_user",
        email="test@example.com",
        password="hashedpassword",
        user_ip="127.0.0.1",
        location="Test City,TC",
        preferences=["Casual"],
        gender="Non-binary"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Add a wardrobe item
    item = WardrobeItem(
        user_id=user.user_id,
        clothing_type="Jacket",
        for_weather="Cool",
        color=["Black"],
        size="M",
        tags=["Leather Jacket"],
        image_url="http://example.com/jacket.jpg"
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    # Add weather data
    weather = WeatherData(
        date=datetime.now(timezone.utc),  # Using timezone-aware datetime
        location="Test City,TC",
        temp_max=20.0,
        temp_min=10.0,
        feels_max=20.0,
        feels_min=10.0,
        wind_speed=5.0,
        humidity=50.0,
        precipitation=0.0,
        precipitation_probability=0.0,
        special_condition="Partially cloudy",
        weather_icon="partly-cloudy-day",
        user_id=user.user_id
    )
    db.add(weather)
    db.commit()

    # Add a fashion trend
    trend = FashionTrend(
        trend_name="Leather Revival",
        trend_description="Leather jackets are making a major comeback this season, offering both style and functionality.",
        date_added=datetime.now(timezone.utc),  # Using timezone-aware datetime
        user_id=None
    )
    db.add(trend)
    db.commit()

    # Mock `fetch_similar_ebay_products` to avoid actual API calls
    mock_ebay_links = ["http://ebay.com/itm/Leather-Jacket-1", "http://ebay.com/itm/Leather-Jacket-2"]

    # Correctly patch `fetch_similar_ebay_products` in `outfit_suggester` context
    with patch('outfit_suggester.fetch_similar_ebay_products', return_value=mock_ebay_links):
        # Call `suggest_outfits`
        outfit_suggestion = suggest_outfits(user.user_id, db)

        # Assertions
        assert outfit_suggestion is not None
        assert outfit_suggestion.user_id == user.user_id
        assert len(outfit_suggestion.outfit_details) == 1  # One outfit
        assert len(outfit_suggestion.outfit_details[0]) == 1  # One component

        # Check eBay links in the component
        component = outfit_suggestion.outfit_details[0][0]
        assert component['eBay_link'] == mock_ebay_links
