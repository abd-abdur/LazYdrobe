# LazYdrobe

Trouble picking outfits for the upcoming days?  
Too much clothes to keep track of?  
Look no further. Our revolutionary app is here to assist you in keeping up with fashion trends and weather.  
Simply upload items in your wardrobe so that we can suggest future outfits based on the weather conditions and the current fashion trend for you while providing clothing suggestions to fill in the gaps in your wardrobe.

# LazYdrobe Backend

This is the backend for the LazYdrobe Wardrobe Management Application. It is built with FastAPI and provides endpoints for user management, wardrobe items, outfit suggestions, weather integration, and more.


## Features

- **User Management**: Registration, authentication, profile updates, and account deletion.
- **Wardrobe Management**: CRUD operations for wardrobe items.
- **Outfit Suggestions**: Generate personalized outfit recommendations.
- **Weather Integration**: Fetch and store weather data to inform outfit suggestions.
- **Fashion Trends**: Update and retrieve current fashion trends.
- **E-commerce Integration**: Suggest products from online stores based on wardrobe gaps.

## Database Overview

The **LazYdrobe** database manages user data, wardrobe items, outfit suggestions, weather data, fashion trends, and e-commerce products. It uses a **SQL relational model** for efficient data retrieval and manipulation.

## Prerequisites

Before you set up **LazYdrobe** ensure that you have the following tools installed:

- **MySQL** or a MySQL-compatible database management system (DBMS), such as MariaDB.
- **Python** (version 3.7 or higher).
- **Git** (optional, for cloning the repository).
- **A MySQL Query Editor** (e.g., MySQL Workbench, phpMyAdmin, or DBeaver).
- **Pip** (to manage Python package installations).

## Database Setup and Usage Instructions

### Features of the SQL Script:
Database Creation: Automatically creates the required tables with appropriate fields and relationships, if they don't already exist.
Sample Data Insertion: Inserts initial data to simulate a real-world environment, making it easy for developers to test and interact with the system.
Relationship Management: Defines foreign key constraints to maintain data integrity across multiple related tables.

### Step 1: Clone the Repository
First, clone the repository where the SQL script is stored. This will allow you to access the SQL file required to set up the database.
```
git clone https://github.com/abd-abdur/LazYdrobe.git
```

### Step 2: Navigate to the Project Directory
After cloning the repository, navigate to the directory containing the project.
```
cd path/to/LazYdrobe
```

### Step 3: Set Up a Virtual Environment
For Python-based projects, it's recommended to use a virtual environment to isolate project dependencies.
```
python -m venv .venv
```

Activate the virtual environment:
On Windows: 
```
.\.venv\Scripts\activate
```
On macOS/Linux: source 
```
.venv/bin/activate
```

### Step 4: Install Required Dependencies
Install the required packages from the requirements.txt file.
```
pip install -r requirements.txt
```

### Step 5: Create a .env file in the project root directory
Add the following fields:
- DATABASE_URL
- OpenAI_API_Key
- VISUAL_CROSSING_API_KEY
- EBAY_APP_ID
- FAL_KEY

### Step 6: Launch Your Database Management System (DBMS)
You need to use a SQL-compatible DBMS like PostgreSQL, MySQL, MariaDB, or similar. Open your DBMS and navigate to the query editor.

Popular choices:

pgAdmin (PostgreSQL): For PostgreSQL databases (what we have chosen!)
MySQL Workbench: For MySQL databases.
phpMyAdmin: A web-based tool for managing MySQL databases.

### Step 7: Run the SQL Script to Set Up the Database
In your DBMS query editor:

Locate the provided SQL script named database_setup.sql inside the repository: path/to/LazYdrobe/database_setup.sql.
Copy the entire SQL script content from the database_setup.sql file.
Paste the copied script into your DBMS query editor.
Execute the script (usually by pressing F5, Ctrl+Enter, or clicking the Execute button).
This will create the required tables (such as Users, Wardrobe_Items, Outfits, etc.), set up relationships between them, and insert sample data for testing.

### Step 8: Run Database Migration (if applicable)

If you are using Alembic for migrations, initialize and run migrations:

```
alembic init alembic
# Configure alembic.ini and env.py accordingly
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

```

## Schema Diagram

![LazYdrobe Schema](schema.png)

## Data Model Description

The **LazYdrobe** database is designed using a **SQL relational model**. Below are the key entities and relationships in the system:

### **1. users**
Stores user information, including preferences and their wardrobe.

- **Attributes**:
  - `user_id` (Primary Key): Unique identifier for each user.
  - `username`: User's display name.
  - `email`: User's email address.
  - `password`: Hashed password for user authentication.
  - `location`: User's location for weather-based outfit suggestions.
  - `preferences`: Json of fashion styles preferred by the user.
  - `gender` : User's gender
  - `date_joined`: Date the user registered on the app.

### **2. wardrobe_items**
Represents individual clothing items uploaded by a user which can be connected to an e-commerce product.

- **Attributes**:
  - `item_id` (Primary Key): Unique identifier for each clothing item.
  - `user_id` (Foreign Key): Links to the `Users` table.
  - `clothing_type`: Type of clothing (e.g., jacket, pants).
  - `for_weather`: Suitable weather for the clothing item.
  - `color`: Json of colors for the item.
  - `size`: Size of the clothing item.
  - `tags`: Json of tags related to the clothing item.
  - `image_url`: URL for the image of the clothing.
  - `date_added`: Date the item was added to the wardrobe.

### **3. ecommerce_product**
Represents clothing items that can be purchased online, recommended to users based on wardrobe gaps.

- **Attributes**:
  - `product_id` (Primary Key): Unique identifier for the product.
  - `product_name`: Name of the product.
  - `suggested_item_type`: Type of item the product suggests (e.g., outerwear, footwear).
  - `price`: Price of the product.
  - `product_url`: URL to the product page for purchase.
  - `image_url`: URL for the product's image.
  - `date_suggested`: Date when the product was suggested to a user.

### **4. weather_data**
Stores weather data relevant to a user's location for making weather-appropriate outfit suggestions.

- **Attributes**:
  - `weather_id` (Primary Key): Unique identifier for the weather.
  - `date`: Date when the weather data was recorded.
  - `location`: The location for which the weather data applies.
  - `temp_max`: Maximum temperature.
  - `temp_min`: Minimum temperature.
  - `feels_max`: Feels-like maximum temperature.
  - `feels_min`: Feels-like minimum temperature.
  - `wind_speed`: Wind speed.
  - `humidity`: Humidity percentage.
  - `precipitation`: Amount of precipitation.
  - `precipitation_probability`: Probability of precipitation.
  - `special_condition`: Description of any special weather conditions (e.g., snow, thunderstorms).
  - `weather_icon`: Name of icon to display.

### **5. outfit_suggestions**
Stores information about generated outfit suggestions based on user wardrobe, weather, and trends.

- **Attributes**:
  - `suggestion_id` (Primary Key): Unique identifier for the outfit suggestion.
  - `user_id` (Foreign Key): Links to the `Users` table.
  - `clothings`: Json of clothing item IDs that make up the outfit.
  - `occasion`: Json of occasions the outfit is suitable for.
  - `for_weather`: Weather conditions the outfit is appropriate for.
  - `date_suggested`: Date when the outfit was suggested to the user.
  - `source_url`: URL where the outfit inspiration came from.

### **6. fashion_trends**
Stores fashion trend data that helps inform outfit recommendations.

- **Attributes**:
  - `trend_id` (Primary Key): Unique identifier for each trend.
  - `trend_names`: Name of the fashion trend.
  - `trend_description`: Description of the trend.
  - `outfits`: Json of outfits that fit the trend.
  - `example_url`: URL to an image showcasing the trend.
  - `date_added`: Date when the trend was added.

### **7. outfits**
Stores information about generated outfit suggestions based on user wardrobe, weather, and trends.

- **Attributes**:
  - `outfit_id` (Primary Key): Unique identifier for the outfit.
  - `user_id` (Foreign Key): Links to the `Users` table.
  - `clothings`: Json of clothing item IDs that make up the outfit.
  - `occasion`: Json of occasions the outfit is suitable for.
  - `for_weather`: Weather conditions the outfit is appropriate for.
  - `date_suggested`: Date when the outfit was suggested to the user.
  - `source_url`: URL where the outfit inspiration came from.

### **Relationships**
- **user** to **wardrobe_items**: One-to-Many (a user can have multiple clothing items in their wardrobe).
- **user** to **outfits**: One-to-Many (a user can have multiple outfits saved).
- **user** to **outfit_suggestions**: One-to-Many (a user can have multiple outfits suggestions saved).
- **user** to **weather**: Many-to-Many (users can share the same weather and locations).
- **outfit_suggestions** to **ecommerce_product**: Many-to-One (many outfit suggestions may share a related e-commerce product).
- **wardrobe_items** to **outfits**: Many-to-Many (an outfit consists of multiple wardrobe items, clothing items can suit multiple outfits).

### Why We Chose SQL for LazYdrobe

1. **Structured Data and Relationships**  
   LazYdrobe handles well-defined entities like Users, Wardrobe Items, Outfits, and Weather Data, all with clear relationships. SQL's use of primary and foreign keys helps enforce these connections efficiently ensuring data integrity.

2. **Data Integrity and Consistency**  
   SQL provides ACID properties (Atomicity, Consistency, Isolation, Durability) to maintain strong data integrity. This ensures that operations like adding wardrobe items or generating outfit suggestions are reliable and consistent.

3. **Complex Queries**  
   Generating outfit suggestions requires complex joins between multiple tables (e.g., Users, WardrobeItems, WeatherData). SQL excels at handling such joins and aggregations making it ideal for our application's data retrieval needs.

4. **Scalability**  
   Modern SQL databases support scalability through partitioning and indexing making them capable of handling larger datasets as the app grows.

5. **Data Consistency Over Flexibility**  
   LazYdrobe benefits from the structured schema enforcement SQL provides. While NoSQL offers flexibility, SQL's consistency ensures that wardrobe items, trends, and weather data are always valid and related correctly.


## Database Structure and Key Components

### 1. Users Table
Purpose: Stores basic information about each user.
Key Fields: user_id, username, email, password, location, preferences, gender, date_joined.
Primary Key: user_id (auto-incremented for uniqueness).
Unique Constraints: email must be unique.
### 2. Wardrobe_Items Table
Purpose: Stores information about wardrobe items owned by users.
Key Fields: item_id, user_id, clothing_type, for_weather, color, size, tags, image_url, date_added.
Foreign Key: user_id references Users(user_id), ensuring each wardrobe item belongs to a valid user.
Relationships: If a user is deleted, their wardrobe items are also deleted (ON DELETE CASCADE).
### 3. Outfits Table
Purpose: Stores outfits that are created by users.
Key Fields: outfit_id, clothings, user_id, occasion, for_weather, source_url, date_suggested.
Foreign Key: user_id references Users(user_id), clothings stores Wardrobe_Items(item_id).
### 4. Outfit_Suggestions Table
Purpose: Stores outfits that are suggested for users.
Key Fields: suggestion_id, user_id, outfit_details, gender, image_url, date_suggested.
Foreign Key: user_id references Users(user_id).
### 5. Weather_Data Table
Purpose: Stores weather conditions relevant to a user's location.
Key Fields: weather_id, date, location, temp_min, temp_max, ...
Foreign Key: user_id references Users(user_id).
### 6. Fashion_Trends Table
Purpose: Stores information about fashion trends.
Key Fields: trend_id, trned_names, trend_description, date_added, user_id, tremd_search phrase.
Foreign Key: user_id references Users(user_id).
### 7. E_Commerce_Products Table
Purpose: Stores product suggestions related to wardrobe items, linked to e-commerce platforms.
Key Fields: product_id, user_id, suggested_item_type, product_name, price, product_url, image_url, date_suggested...
Foreign Key: user_id references Users(user_id).

## Testing the Database
Once the tables are set up and sample data is inserted, you can begin testing the database.

1. Run Queries: You can run SELECT statements on each table to view the data, ensuring everything has been created correctly.
SELECT * FROM Users;
SELECT * FROM Wardrobe_Items;
SELECT * FROM Outfits;
2. Modify Sample Data: You can modify, delete, or add new entries to test different aspects of the database, such as the relationships between users and their wardrobe items.
3. Check Data Integrity: Try deleting a user and see how it cascades down to related records in other tables (e.g., their wardrobe items should be deleted).

## Running the API Application

To run the FastAPI application, follow these steps:

1. Open your terminal or command prompt.
2. Navigate to the directory where your `main.py` file is located.
3. Use the following command to start the application:

   ```bash
   uvicorn main:app --reload
   ```

4. Once the server is running, you can access the application locally at: http://127.0.0.1:8000

## Using Postman to Interact with the API

You can use Postman to test the API endpoints. Here’s how to set it up:

### Step 1: Open Postman
Launch the Postman application or access it through the web.

### Step 2: Create a New Collection
1. Click on the **Collections** tab.
2. Create a new collection named **"LazYdrobe API Tests"**.

### Step 3: Add Requests
Follow the structure below for each request:

#### 1. Create a New User
- **Method**: `POST`
- **Endpoint**: `http://127.0.0.1:8000/users/`
- **JSON Input**:
    ```json
    {
      "username": "john_doe",
      "email": "john@example.com",
      "password": "securepassword123",
      "location": "New York, US",
      "preferences": ["casual", "outdoor"],
      "gender": "male"
    }
    ```
- **Expected Output**: JSON object of the created user.

#### 2. Login a User
- **Method**: `POST`
- **Endpoint**: `http://127.0.0.1:8000/login/`
- **JSON Input**:
    ```json
    {
      "email": "john@example.com",
      "password": "securepassword123"
    }
    ```
- **Expected Output**:
    ```json
    {
      "user_id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    }
    ```

#### 3. Retrieve User Information
- **Method**: `GET`
- **Endpoint**: `http://127.0.0.1:8000/users/{user_id}`
- **Input**: 
    ```json
    {
      "user_id": 1
    }
    ```
- **Expected Output**: JSON object of the user.

#### 4. Update User Information
- **Method**: PUT
- **Endpoint**: PUT /users/{user_id}
- **JSON Input**:
    ```json
    {
      "username": "john_doe_updated",
      "email": "johndoe2@example.com",
      "password": "newsecurepassword",
      "location": "Los Angeles, USA",
      "preferences": {"fashion": ["casual", "sportswear"]},
      "gender": "Other",
    }
    ```
- **Expected Output**: JSON object of the updated user.

#### 5. Delete User
- **Method**: `DELETE`
- **Endpoint**: `http://127.0.0.1:8000/users/{user_id}`
- **Input**: 
    ```json
    {
      "user_id": 1
    }
    ```
- **Expected Output**:
    ```json
    {
      "message": "User with ID {user_id} deleted successfully."
    }
    ```

#### 6. Create a Wardrobe Item
- **Method**: `POST`
- **Endpoint**: `http://127.0.0.1:8000/wardrobe_item/`
- **JSON Input**:
    ```json
    {
      "user_id": 1,
      "clothing_type": "jacket",
      "for_weather": ["cold", "rainy"],
      "color": "black",
      "size": "M",
      "tags": ["formal", "winter"],
      "image_url": "https://example.com/image.jpg"
    }
    ```
- **Expected Output**: JSON object of the created wardrobe item.

#### 7. Get Wardrobe Items for User
- **Method**: `GET`
- **Endpoint**: `http://127.0.0.1:8000/wardrobe_item/user/{user_id}`
- **Input**:
    - URL Path Parameter: `{user_id}` (e.g., `1`)
- **Expected Output**: JSON list of wardrobe item objects with the same user_id.

#### 8. Retrieve Wardrobe Item by ID
- **Method**: `GET`
- **Endpoint**: `http://127.0.0.1:8000/wardrobe_item/{item_id}`
- **Input**:
    - URL Path Parameter: `{item_id}` (e.g., `1`)
- **Expected Output**: JSON object of the wardrobe item with {item_id}.

#### 9. Update Wardrobe Item
- **Method**: `PUT`
- **Endpoint**: `http://127.0.0.1:8000/wardrobe_item/{item_id}`
- **JSON Input**:
    ```json
    {
      "clothing_type": "jacket",
      "for_weather": ["cold", "rainy"],
      "color": "navy blue",
      "size": "M",
      "tags": ["formal", "autumn"],
      "image_url": "https://example.com/image.jpg"
    }
    ```
- **Expected Output**: JSON object of the updated wardrobe item.

#### 10. Delete Wardrobe Items
- **Method**: `DELETE`
- **Endpoint**: `http://127.0.0.1:8000/wardrobe_item/`
- **JSON Input**:
    ```json
    {
      "item_ids": [1, 2]
    }
    ```
- **Expected Output**:
    ```json
    {
      "message": "Wardrobe item with IDs {item_ids} deleted successfully."
    }
    ```

#### 11. Get Weather Data
- **Method**: `POST`
- **Endpoint**: `http://127.0.0.1:8000/weather/`
- **JSON Input**:
    ```json
    {
      "user_id": 1
    }
    ```
- **Expected Output**:
    ```json
    [
      {
        "date": "2024-11-11T00:00:00",
        "feels_max": 67.8,
        "feels_min": 55.1,
        "humidity": 65.3,
        "location": "new york,us",
        "precipitation": 0.138,
        "precipitation_probability": 100,
        "special_condition": "Rain, Partially cloudy",
        "temp_max": 67.8,
        "temp_min": 55.1,
        "weather_icon": "showers-day",
        "wind_speed": 16.2
      },
      ...
    ]
    ```

#### 12. Fetch and Update a Fashion Trend
- **Method**: `POST`
- **Endpoint**: `http://127.0.0.1:8000/fashion_trends/update`
- **JSON Input**:
    ```json
    {
        "trend_id": 227,
        "title": "Denim on Denim",
        "description": "This trend involves wearing different denim pieces together. It could be a denim jacket paired with jeans or a denim shirt with a denim skirt.",
        "date_added": "2024-11-17T20:00:56",
        "tags": ["denim jacket", "jeans", "denim shirt"]
    }
    ```
- **Expected Output**: JSON object of fashion trend.

#### 13. Retrieve Latest Fashion Trends
- **Method**: `GET`
- **Endpoint**: `http://127.0.0.1:8000/fashion_trends/`
- **Expected Output**: JSON list of fashion trend objects.

#### 14. Register a New Outfit
- **Method**: `POST`
- **Endpoint**: `http://127.0.0.1:8000/outfit/`
- **JSON Input**:
    ```json
    {
        "user_id": 8,
        "occasion": ["casual"],
        "for_weather": "All Year Around",
        "clothings": [15, 16],
        "date_created": "2024-11-17T23:28:13"
    }
    ```
- **Expected Output**: JSON object of the created outfit.

#### 15. Retrieve Outfits of a User
- **Method**: `GET`
- **Endpoint**: `http://127.0.0.1:8000/outfit/user/{user_id}`
- **Input**:
    - URL Path Parameter: `{user_id}` (e.g., `8`)
- **Expected Output**: JSON list of outfit objects with the same user_id.

#### 16. Update Outfit Information
- **Method**: `PUT`
- **Endpoint**: `http://127.0.0.1:8000/outfit/{outfit_id}`
- **Input**:
    - URL Path Parameter: `{item_id}` (e.g., `6`)
- **JSON Input**:
    ```json
    {
        "user_id": 8,
        "occasion": ["casual", "formal"],
        "for_weather": "Winter",
        "clothings": [15, 16],
        "date_updated": "2024-11-18T10:30:00"
    }
    ```
- **Expected Output**: JSON object of the updated outfit.

#### 17. Delete an Outfit
- **Method**: `DELETE`
- **Endpoint**: `http://127.0.0.1:8000/outfit/{outfit_id}`
- **Input**:
    - URL Path Parameter: `{item_id}` (e.g., `6`)
- **Expected Output**:
  ```json
  {
    "message": "Outfit with ID {outfit_id} deleted successfully."
  }

#### 18. Register a New Outfit Suggestion
- **Method**: `POST`
- **Endpoint**: `http://127.0.0.1:8000/outfits/suggest`
- **JSON Input**:
    ```json
    {
        "outfit_id": 6,
        "suggestions": [
            {
                "gender": "Male",
                "item_id": 1856,
                "eBay_link": ["https://www.ebay.com/itm/John-Raphael-Millenium-Three-Piece-Check-Windowpane-Green-Suit-52L-Pants-42X32-/204184384429"],
                "image_url": "https://i.ebayimg.com/thumbs/images/g/gV0AAOSw8UNjl951/s-l140.jpg"
            }
        ],
        "category": "Unisex",
        "date_added": "2024-11-18T15:39:45"
    }
    ```
- **Expected Output**: JSON object of the suggested outfit.

#### 19. Retrieve Outfit Suggestions of a User
- **Method**: `GET`
- **Endpoint**: `http://127.0.0.1:8000/outfits/suggestions/{user_id}`
- **Input**:
    - URL Path Parameter: `{user_id}` (e.g., `8`)
- **Expected Output**:
    ```json
    [
        {
            "suggestion_id": 40,
            "outfit_id": 6,
            "suggestions": [
                {
                    "gender": "Male",
                    "item_id": 1856,
                    "eBay_link": ["https://www.ebay.com/itm/John-Raphael-Millenium-Three-Piece-Check-Windowpane-Green-Suit-52L-Pants-42X32-/204184384429"],
                    "image_url": "https://i.ebayimg.com/thumbs/images/g/gV0AAOSw8UNjl951/s-l140.jpg"
                }
            ],
            "category": "Unisex",
            "date_added": "2024-11-18T15:39:45"
        }
    ]
    ```

#### 20. Delete all Outfit Suggestion
- **Method**: `DELETE`
- **Endpoint**: `http://127.0.0.1:8000/outfits/suggestions/all`
- **Input**:
    - URL Path Parameter: `{user_id}` (e.g., `40`)
- **Expected Output**:
  ```json
  {
    "message": "Deleted {deleted} outfit suggestion(s) for user_id={user_id}."
  }

#### 21. Delete Outfit Suggestions
- **Method**: `DELETE`
- **Endpoint**: `http://127.0.0.1:8000/outfits/suggestions/`
- **JSON Input**:
    ```json
    {
      "suggestion_ids": [1, 2]
    }
    ```
- **Expected Output**:
    ```json
    {
      "message": "Outfit suggestions with IDs {suggestion_ids} deleted successfully."
    }
    ```

For reference, you can find all the API tests in the [Postman_Tests.txt](Postman_Tests.txt) file. This file contains descriptions of each API endpoint including method types, expected inputs, and outputs.

## Conclusion

The **LazYdrobe API** provides a robust and flexible interface for interacting with the wardrobe management application enabling users to perform essential CRUD operations on clothing items. By following the steps outlined above, you can easily set up, test, and utilize the API to meet your wardrobe management needs. This API is designed for developers looking to integrate personalized outfit suggestions based on user preferences and weather data into their applications.
