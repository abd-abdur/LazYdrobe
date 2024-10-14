# LazYdrobe

Trouble picking outfits for the upcoming days?  
Too much clothes to keep track of?  
Look no further. Our revolutionary app is here to assist you in keeping up with fashion trends and weather.  
Simply upload items in your wardrobe so that we can suggest future outfits based on the weather conditions and the current fashion trend for you while providing clothing suggestions to fill in the gaps in your wardrobe.

## Features

- **Wardrobe Management**: Users can upload and manage their wardrobe by categorizing items like tops, bottoms, shoes, and accessories.
- **Outfit Suggestions**: Generate personalized outfit recommendations based on the weather, current fashion trends, and user preferences.
- **Weather Integration**: Provides weather-appropriate outfit suggestions based on current and forecasted weather conditions.
- **Fashion Trends**: Keeps users updated with the latest fashion trends ensuring their wardrobe stays trendy.
- **Gap Filling**: Recommends additional clothing items to complete outfits and fill gaps in the user’s wardrobe.
- **E-commerce Integration**: Suggests products from online stores based on wardrobe gaps to help users shop for missing pieces.

## Database Overview

The **LazYdrobe** database is designed to manage user data, wardrobe items, outfit suggestions, weather data, fashion trends, and e-commerce products. The database structure supports efficient retrieval and manipulation of data for various functionalities related to fashion trends and user preferences.
  
## Schema Diagram

![LazYdrobe Schema](schema.png)

## Data Model Description

The **LazYdrobe** database is designed using a **SQL relational model**. Below are the key entities and relationships in the system:

### **1. Users**
Stores user information, including preferences and their wardrobe.

- **Attributes**:
  - `user_id` (Primary Key): Unique identifier for each user.
  - `username`: User's display name.
  - `email`: User's email address.
  - `password`: Hashed password for user authentication.
  - `location`: User's location for weather-based outfit suggestions.
  - `preferences`: List of fashion styles preferred by the user.
  - `date_joined`: Date the user registered on the app.

### **2. Clothing**
Represents individual clothing items uploaded by a user which can be connected to an e-commerce product.

- **Attributes**:
  - `item_id` (Primary Key): Unique identifier for each clothing item.
  - `user_id` (Foreign Key): Links to the `Users` table.
  - `product_id` (Foreign Key): Links to the `eCommerceProduct` table if the item corresponds to a purchasable product.
  - `type`: Type of clothing (e.g., jacket, pants).
  - `for_weather`: Suitable weather for the clothing item.
  - `color` (array): List of colors for the item.
  - `size`: Size of the clothing item.
  - `tags` (array): Tags related to the clothing item.
  - `image_url`: URL for the image of the clothing.
  - `date_added`: Date the item was added to the wardrobe.

### **3. eCommerceProduct**
Represents clothing items that can be purchased online, recommended to users based on wardrobe gaps.

- **Attributes**:
  - `product_id` (Primary Key): Unique identifier for the product.
  - `product_name`: Name of the product.
  - `suggested_item_type`: Type of item the product suggests (e.g., outerwear, footwear).
  - `price`: Price of the product.
  - `product_url`: URL to the product page for purchase.
  - `image_url`: URL for the product's image.
  - `date_suggested`: Date when the product was suggested to a user.

### **4. WeatherData**
Stores weather data relevant to a user's location for making weather-appropriate outfit suggestions.

- **Attributes**:
  - `date` (Primary Key): Date when the weather data was recorded.
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

### **5. Outfit**
Stores information about generated outfit suggestions based on user wardrobe, weather, and trends.

- **Attributes**:
  - `outfit_id` (Primary Key): Unique identifier for the outfit.
  - `clothings` (array): Array of clothing item IDs that make up the outfit.
  - `occasion` (array): Occasions the outfit is suitable for.
  - `for_weather`: Weather conditions the outfit is appropriate for.
  - `date_suggested`: Date when the outfit was suggested to the user.
  - `source_url`: URL where the outfit inspiration came from.

### **6. Fashion**
Stores fashion trend data that helps inform outfit recommendations.

- **Attributes**:
  - `trend_id` (Primary Key): Unique identifier for each trend.
  - `trend_names`: Name of the fashion trend.
  - `description`: Description of the trend.
  - `temperature`: Weather conditions that fit the trend.
  - `occasion`: Occasions or events where the trend is suitable.
  - `image_url`: URL to an image showcasing the trend.
  - `example_fits` (array): Example outfits that fit the trend.

### **Relationships**
- **User** to **Clothing**: One-to-Many (a user can have multiple clothing items in their wardrobe).
- **Clothing** to **eCommerceProduct**: One-to-One (a clothing item may have a related e-commerce product).
- **Outfit** to **Clothing**: One-to-Many (an outfit consists of multiple wardrobe items).
- **Outfit** to **WeatherData**: One-to-One (outfits are suggested based on specific weather conditions).
- **Outfit** to **Fashion**: Many-to-One (outfits may follow a specific fashion trend).
- **WeatherData** to **Outfit**: Many-to-One (outfit suggestions are influenced by weather data).


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
git clone https://github.com/abd-abdur/LazYdrobe.git

### Step 2: Navigate to the Project Directory
After cloning the repository, navigate to the directory containing the project.
cd path/to/LazYdrobe

### Step 3: (Optional) Set Up a Virtual Environment
For Python-based projects, it's recommended to use a virtual environment to isolate project dependencies.
python -m venv .venv

Activate the virtual environment:

On Windows: .\.venv\Scripts\activate
On macOS/Linux: source .venv/bin/activate

### Step 4: Install Required Dependencies (Optional)
Install the required packages from the requirements.txt file.

pip install -r requirements.txt

### Step 5: Launch Your Database Management System (DBMS)
You need to use a SQL-compatible DBMS like PostgreSQL, MySQL, MariaDB, or similar. Open your DBMS and navigate to the query editor.

Popular choices:

pgAdmin (PostgreSQL): For PostgreSQL databases (what we have chosen!)
MySQL Workbench: For MySQL databases.
phpMyAdmin: A web-based tool for managing MySQL databases.

### Step 6: Run the SQL Script to Set Up the Database
In your DBMS query editor:

Locate the provided SQL script named database_setup.sql inside the repository: path/to/LazYdrobe/database_setup.sql.
Copy the entire SQL script content from the database_setup.sql file.
Paste the copied script into your DBMS query editor.
Execute the script (usually by pressing F5, Ctrl+Enter, or clicking the Execute button).
This will create the required tables (such as Users, Wardrobe_Items, Outfits, etc.), set up relationships between them, and insert sample data for testing.

## Database Structure and Key Components

### 1. Users Table
Purpose: Stores basic information about each user.
Key Fields: user_id, username, email, password_hash, location, preferences, date_joined.
Primary Key: user_id (auto-incremented for uniqueness).
Unique Constraints: email must be unique.
### 2. Wardrobe_Items Table
Purpose: Stores information about wardrobe items owned by users.
Key Fields: item_id, user_id, type, season, fabric, color, size, tags, image_url, date_added.
Foreign Key: user_id references Users(user_id), ensuring each wardrobe item belongs to a valid user.
Relationships: If a user is deleted, their wardrobe items are also deleted (ON DELETE CASCADE).
### 3. Outfits Table
Purpose: Stores outfits that are suggested or created for different occasions.
Key Fields: outfit_id, user_id, occasion, weather_condition, trend_score, date_suggested.
Foreign Key: user_id references Users(user_id).
### 4. Outfit_Wardrobe_Items Table
Purpose: A junction table that links outfits to specific wardrobe items (many-to-many relationships).
Key Fields: outfit_id, item_id (composite primary key).
Foreign Keys: Links outfit_id to Outfits(outfit_id) and item_id to Wardrobe_Items(item_id).
### 5. Weather_Data Table
Purpose: Stores weather conditions relevant to a user's location.
Key Fields: weather_id, user_id, location, temperature, precipitation, wind_speed, humidity, date_fetched.
Foreign Key: user_id references Users(user_id).
### 6. Fashion_Trends Table
Purpose: Stores information about fashion trends, including categories and source URLs.
Key Fields: trend_id, title, description, categories, image_url, date_fetched, source_url.
### 7. E_Commerce_Products Table
Purpose: Stores product suggestions related to wardrobe items, linked to e-commerce platforms.
Key Fields: product_id, user_id, suggested_item_type, product_name, price, product_url, image_url, date_suggested.
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

4. Once the server is running, you can access the application locally at:
    ```bash
  http://127.0.0.1:8000

## Using Postman to Interact with the API

You can use Postman to test the API endpoints. Here’s how to set it up:

### Step 1: Open Postman
Launch the Postman application or access it through the web.

### Step 2: Create a New Collection
1. Click on the **Collections** tab.
2. Create a new collection named **"LazYdrobe API Tests"**.

### Step 3: Add Requests
Follow the structure below for each request:

#### 1. Retrieve All Clothing Items
- **Method**: `GET`
- **Endpoint**: `http://127.0.0.1:8000/clothing_items/`
- **Expected Output**: JSON array of clothing items.

#### 2. Retrieve a Specific Clothing Item by ID
- **Method**: `GET`
- **Endpoint**: `http://127.0.0.1:8000/clothing_items/{item_id}`
- **Expected Output**: JSON object of the clothing item.

#### 3. Create a New Clothing Item
- **Method**: `POST`
- **Endpoint**: `http://127.0.0.1:8000/clothing_items/`
- **JSON Input**:
    ```json
    {
      "user_id": 1,
      "type": "T-shirt",
      "season": "Summer",
      "fabric": "Cotton",
      "color": "Blue",
      "size": "L",
      "tags": "casual, summer",
      "image_url": "http://example.com/tshirt.jpg"
    }
    ```
- **Expected Output**: JSON object of the created clothing item.

#### 4. Update an Existing Clothing Item
- **Method**: `PUT`
- **Endpoint**: `http://127.0.0.1:8000/clothing_items/{item_id}`
- **JSON Input**:
    ```json
    {
      "user_id": 1,
      "type": "Updated T-shirt",
      "season": "Summer",
      "fabric": "Cotton",
      "color": "Red",
      "size": "M",
      "tags": "casual, summer",
      "image_url": "http://example.com/updated_tshirt.jpg"
    }
    ```
- **Expected Output**: JSON object of the updated clothing item.

#### 5. Delete a Clothing Item by ID
- **Method**: `DELETE`
- **Endpoint**: `http://127.0.0.1:8000/clothing_items/{item_id}`
- **Expected Output**:
    ```json
    {
      "message": "Item deleted successfully"
    }
    ```
For reference, you can find all the API tests in the [Postman_Tests.txt](Postman%20Tests.txt) file. This file contains descriptions of each API endpoint including method types, expected inputs, and outputs.

## Conclusion

The **LazYdrobe API** provides a robust and flexible interface for interacting with the wardrobe management application enabling users to perform essential CRUD operations on clothing items. By following the steps outlined above, you can easily set up, test, and utilize the API to meet your wardrobe management needs. This API is designed for developers looking to integrate personalized outfit suggestions based on user preferences and weather data into their applications.
