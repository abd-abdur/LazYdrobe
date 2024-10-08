import requests
import pandas as pd
import os
from dotenv import load_dotenv

# For web can refer to https://www.w3schools.com/jsref/prop_geo_coordinates.asp
# to get latitude and longitude of user
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
def weather_forcast(visualcrossing_API_KEY, part1, part2):
    if visualcrossing_API_KEY == None:
        print("No key")
        return
    
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{part1},{part2}?key={visualcrossing_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if 'days' not in data:
        print("Unable to get weather data")
        return []
    
    days = data["days"]
    report = []
    for day in days:
        info = {
            'datetime': day['datetime'],
            'location': f'{part1},{part2}',
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
    print("Successfully retrieved!")
    return report

# Convert weather data to csv file    
def weather_to_file(data):
    df = pd.DataFrame(data)
    # Make datetime first column
    cols = ['datetime'] + [col for col in df.columns if col != 'datetime']
    df = df[cols] # Reorder the columns

    # Clean CSV file
    df.columns = df.columns.str.lower().str.replace(' ', '_') # Make all columns lower space and replacing spaces with _
    df = df.apply(lambda col: col.fillna(0) if col.dtype in ['int64', 'float64'] else col.fillna('Unknown'))
    df.to_csv(f'weather_data.csv', index=False)
    print("Check your folder for weather data.")

# Get desired location for weather data
def get_location():
    ans = input(f"Do you know the latitude and longitude of your location?\nRespond with 1 or 2:\n1. Yes\n2. No\n")
    while (ans != '1' and ans != '2'):
        ans = input(f"Do you know the latitude and longitude of your location?\nRespond with 1 or 2:\n1. Yes\n2. No\n")
    if ans == '1':
        part1 = input("Enter the latitude: ")
        part2 = input("Enter the longitude: ")
        while (True):
            try:
                part1 = float(part1)
                break
            except:
                part1 = input("Please enter the latitude as a float: ")
        while (True):
            try:
                part2 = float(part2)
                break
            except:
                part2 = input("Please enter the longitude as a float: ")
    else:
        part1 = input("Enter the city or state: ")
        part2 = input("Enter the country code: ")
        while(type(part1) != str):
            part1 = input("Please enter the city: ")
        while(type(part2) != str):
            part2 = input("Please enter the country code: ")
    print("Attempting to retrieve weather data from given input")
    return part1, part2

def get_weather():
    # Get key
    visualcrossing_API_KEY = get_API_KEY('visualcrossing_API_KEY')

    # Testing getting weather info from API
    # For most accurate, use latitude and longitude
    # else input State, Country code for best guess
    part1, part2 = get_location()
    data = weather_forcast(visualcrossing_API_KEY, part1, part2)
    weather_to_file(data)
    return

if __name__ == "__main__":
    get_weather()