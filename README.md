# LazYdrobe
Trouble picking out fits for the upcoming days? 
Too much clothes to keep track of?
Look no further. Our revolutionary app is here to assist you in keeping up with fashion trends and weather.
Simply upload items in your wardrobe so that we can suggest future outfits based on the weather conditions and the current fashion trend for you while providing clothing suggestions to fill in the gaps in your wardrobe.

## Features
- Suggest outfit ideas based on weather and fashion trend
- Suggest clothing pieces to purchase that is not in wardrobe

## Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- MySQL server

## Why SQL
We chose to use SQL for our project because: 
- The information that we are handling generally all follow a structured format
- There are clear relationships between our data tables

## Our data model
1. users
   Stores user specific information
2. clothing
   Stores individual clothing pieces as its own object
4. fashion
   Stores fashion trend data
6. weatherData
   Stores weather information for a location
8. outfit
   Stores outfits by pairing up clothing pieces and fashion trend
10. eCommerceProduct
    Stores information on clothing items available for purchase from online
 
# Setup
1. Clone this repository or download the source code. `git clone https://github.com/abd-abdur/LazYdrobe.git`
2. Navigate to the project directory:
   ```
   cd path/to/LazYdrobe
   ```
3. Optional: Create a virtual environment
    ```
    python -m venv .venv 

    # On Windows:
    .venv\Scripts\activate

    # On macOS and Linux:
    source .venv/bin/activate

    ```
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the project root directory and add the following:
   ```
   visualcrossing_API_KEY=your_key_here
   ```
   Replace `your_key_here` with your visualcrossing connection string from [Visual Crossing](https://www.visualcrossing.com/)

## Usage
To run the application:
```
python main.py
```
Currently, this only creates a live csv file of weather forcast as we are waiting to get access to APIs. The rest of the database are currently dummy data that we have put together.
