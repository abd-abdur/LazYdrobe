import requests
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from datetime import datetime

# Import necessary models and DB session dependency
from models import WeatherData
from main import get_db

# Load environment variables
load_dotenv()

# Get API key function
def get_api_key(key_name: str) -> str:
    api_key = os.getenv(key_name)
    if not api_key:
        raise ValueError(f"{key_name} not found in environment variables.")
    return api_key

# Fetch weather data from Visual Crossing API
def fetch_weather_data(api_key: str, location_part1: str, location_part2: str):
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_part1},{location_part2}?key={api_key}'
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Failed to fetch weather data. Check inputs and API key.")
        return None

    data = response.json()
    if 'days' not in data:
        print("No weather data available.")
        return None

    # Structure data for DB insertion
    return [
        {
            'date': datetime.strptime(day['datetime'], "%Y-%m-%d"),
            'location': f'{location_part1},{location_part2}',
            'temp_max': day.get('tempmax', 0),
            'temp_min': day.get('tempmin', 0),
            'feels_max': day.get('feelslikemax', 0),
            'feels_min': day.get('feelslikemin', 0),
            'wind_speed': day.get('windspeed', 0),
            'humidity': day.get('humidity', 0),
            'precipitation': day.get('precip', 0),
            'precipitation_probability': day.get('precipprob', 0),
            'special_condition': day.get('conditions', 'Unknown')
        }
        for day in data["days"]
    ]

# Insert weather data into database
def insert_weather_data_to_db(data: list):
    if not data:
        print("No data to insert into the database.")
        return

    # Use get_db() from main.py to open a session
    db: Session = next(get_db())
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
            special_condition=entry['special_condition']
        )
        db.add(weather_record)

    try:
        db.commit()
        print("Weather data successfully inserted into the database.")
    except Exception as e:
        db.rollback()
        print(f"Error inserting data: {e}")
    finally:
        db.close()

# Retrieve location data from the user
def get_location():
    choice = input("Do you have the latitude and longitude? (1. Yes, 2. No): ")
    
    if choice == '1':
        while True:
            try:
                latitude = float(input("Enter latitude: "))
                longitude = float(input("Enter longitude: "))
                return str(latitude), str(longitude)
            except ValueError:
                print("Please enter valid latitude and longitude as numbers.")
    else:
        city = input("Enter city or state: ")
        country_code = input("Enter country code: ")
        return city, country_code

def main():
    try:
        # Retrieve API Key
        api_key = get_api_key('visualcrossing_API_KEY')
        
        # Get location information
        location_part1, location_part2 = get_location()
        
        # Fetch weather data
        data = fetch_weather_data(api_key, location_part1, location_part2)
        
        # Insert data into the database
        insert_weather_data_to_db(data)
    
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
