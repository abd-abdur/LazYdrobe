import requests
import pandas as pd
import os
from dotenv import load_dotenv

# For web can refer to https://www.w3schools.com/jsref/prop_geo_coordinates.asp
# to get latitude and logitude of user
# Retrieve API key
def get_API_KEY(key):
    load_dotenv()
    API_KEY = os.getenv(key)
    if API_KEY:
        print(f"{key} retrieved successfully!")
        return API_KEY
    else:
        print("Failed to retrieve {key}. Please check your setup.")
        return None

# City for latitude, country for longtitude
def weather_forcast(api_key, city, country):

    if api_key == None:
        print("No key")
        return
    
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city},{country}?key={visualcrossing_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if 'days' not in data:
        print("Unable to get weather data")
        return
    
    days = data["days"]
    report = []
    for day in days:
        info = {
            'datetime': day['datetime'],
            'location': f'{city},{country}',
            'temp_max': day['tempmax'],
            'temp_min': day['tempmin'],
            'feels_max': day['feelslikemax'],
            'feels_min': day['feelslikemin'],
            'wind_speed': day['windspeed'],
            'humidity': day['humidity'],
            'precipitation': day['precip'],
            'precipitation_probability': day['precipprob'],
            'special_condition': day['conditions']
        }
        report.append(info)
    return report
    
def weather_to_file(data):
    df = pd.DataFrame(data)
    # Make datetime first column
    cols = ['datetime'] + [col for col in df.columns if col != 'datetime']
    df = df[cols] # Reoder the columns

    # Clean CSV file
    df.columns = df.columns.str.lower().str.replace(' ', '_') # Make all columns lower space and replacing spaces with _
    df = df.apply(lambda col: col.fillna(0) if col.dtype in ['int64', 'float64'] else col.fillna('Unknown'))
    df.to_csv(f'weather_data.csv', index=False)

def get_weather():
    # Get key
    visualcrossing_API_KEY = get_API_KEY('visualcrossing_API_KEY')

    # Testing getting weather info from API
    # For most accurate, use latitude and longitude
    # else input State, Country code for best guess
    latitude = 40.7167923
    longitude = -73.9925411
    data = weather_forcast(visualcrossing_API_KEY, latitude, longitude)
    weather_to_file(data)
    return

if __name__ == "__main__":
    get_weather()