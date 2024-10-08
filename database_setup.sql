DELETE FROM Users;
DELETE FROM Wardrobe_Items;
DELETE FROM Outfits;
DELETE FROM Outfit_Wardrobe_Items;
DELETE FROM Weather_Data;
DELETE FROM Fashion_Trends;
DELETE FROM E_Commerce_Products;
----------------------------------------

-- Create the Users table
CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    location TEXT,
    preferences TEXT,
    date_joined TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Output: Check if the Users table is created (structure)
SELECT * FROM Users LIMIT 0;
----------------------------------------------------------------
-- Create the Wardrobe_Items table
CREATE TABLE IF NOT EXISTS Wardrobe_Items (
    item_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    season TEXT,
    fabric TEXT,
    color TEXT,
    size TEXT,
    tags TEXT,
    image_url TEXT,
    date_added TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_wardrobe FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Output: Check if the Wardrobe_Items table is created (structure)
SELECT * FROM Wardrobe_Items LIMIT 0;
------------------------------------------------------------------------
-- Create the Outfits table
CREATE TABLE IF NOT EXISTS Outfits (
    outfit_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    occasion TEXT,
    weather_condition TEXT,
    trend_score REAL,
    date_suggested TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_outfit FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Output: Check if the Outfits table is created (structure)
SELECT * FROM Outfits LIMIT 0;
-----------------------------------------------------------------------
-- Create the Outfit_Wardrobe_Items table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS Outfit_Wardrobe_Items (
    outfit_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    PRIMARY KEY (outfit_id, item_id),
    CONSTRAINT fk_outfit FOREIGN KEY (outfit_id)
        REFERENCES Outfits(outfit_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_wardrobe_item FOREIGN KEY (item_id)
        REFERENCES Wardrobe_Items(item_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Output: Check if the Outfit_Wardrobe_Items table is created (structure)
SELECT * FROM Outfit_Wardrobe_Items LIMIT 0;
-------------------------------------------------------------------------------------
-- Create the Weather_Data table
CREATE TABLE IF NOT EXISTS Weather_Data (
    weather_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    location TEXT NOT NULL,
    temperature REAL,
    precipitation REAL,
    wind_speed REAL,
    humidity REAL,
    date_fetched TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_weather FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Output: Check if the Weather_Data table is created (structure)
SELECT * FROM Weather_Data LIMIT 0;
----------------------------------------------------------------------------
-- Create the Fashion_Trends table
CREATE TABLE IF NOT EXISTS Fashion_Trends (
    trend_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    categories TEXT,
    image_url TEXT,
    date_fetched TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    source_url TEXT
);

-- Output: Check if the Fashion_Trends table is created (structure)
SELECT * FROM Fashion_Trends LIMIT 0;
---------------------------------------------------------------------------
-- Create the E_Commerce_Products table
CREATE TABLE IF NOT EXISTS E_Commerce_Products (
    product_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    suggested_item_type TEXT,
    product_name TEXT NOT NULL,
    price REAL,
    product_url TEXT,
    image_url TEXT,
    date_suggested TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_ecommerce FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Output: Check if the E_Commerce_Products table is created (structure)
SELECT * FROM E_Commerce_Products LIMIT 0;
------------------------------------------------------------------------------------------------
-- Insert sample users if they don't already exist
INSERT INTO Users (username, email, password_hash, location, preferences)
SELECT 'a', 'user_a@example.com', 'hashed_password_a', 'NY, USA', '["Black"]'
WHERE NOT EXISTS (
    SELECT 1 FROM Users WHERE email = 'user_a@example.com'
);

INSERT INTO Users (username, email, password_hash, location, preferences)
SELECT 'b', 'user_b@example.com', 'hashed_password_b', 'London, UK', '["Long coat"]'
WHERE NOT EXISTS (
    SELECT 1 FROM Users WHERE email = 'user_b@example.com'
);

-- Output: Show all users to ensure they were inserted correctly
SELECT * FROM Users;
----------------------------------------------------------------------------------------
-- Insert sample wardrobe items (ensure user_id exists in Users table)
INSERT INTO Wardrobe_Items (user_id, type, season, fabric, color, size, tags, image_url)
SELECT 1, 'T-shirt', 'summer', 'cotton', 'blue', 'M', '["casual", "light"]', 'http://example.com/tshirt.jpg'
WHERE EXISTS (
    SELECT 1 FROM Users WHERE user_id = 1
);

INSERT INTO Wardrobe_Items (user_id, type, season, fabric, color, size, tags, image_url)
SELECT 1, 'Jeans', 'all_season', 'denim', 'black', '32', '["casual"]', 'http://example.com/jeans.jpg'
WHERE EXISTS (
    SELECT 1 FROM Users WHERE user_id = 1
);

INSERT INTO Wardrobe_Items (user_id, type, season, fabric, color, size, tags, image_url)
SELECT 2, 'Dress', 'summer', 'silk', 'red', 'M', '["formal", "evening"]', 'http://example.com/dress.jpg'
WHERE EXISTS (
    SELECT 1 FROM Users WHERE user_id = 2
);

-- Output: Show all wardrobe items
SELECT * FROM Wardrobe_Items;
-------------------------------------------------------

-- Insert sample outfits
INSERT INTO Outfits (user_id, occasion, weather_condition, trend_score)
SELECT 1, 'casual', 'sunny', 7.5
WHERE EXISTS (
    SELECT 1 FROM Users WHERE user_id = 1
);

INSERT INTO Outfits (user_id, occasion, weather_condition, trend_score)
SELECT 2, 'formal', 'cloudy', 8.0
WHERE EXISTS (
    SELECT 1 FROM Users WHERE user_id = 2
);

-- Output: Show all outfits
SELECT * FROM Outfits;
-----------------------------------------------
-- Insert sample data into the Outfit_Wardrobe_Items junction table
INSERT INTO Outfit_Wardrobe_Items (outfit_id, item_id)
SELECT 1, 1
WHERE EXISTS (
    SELECT 1 FROM Outfits WHERE outfit_id = 1
) AND EXISTS (
    SELECT 1 FROM Wardrobe_Items WHERE item_id = 1
);

INSERT INTO Outfit_Wardrobe_Items (outfit_id, item_id)
SELECT 1, 2
WHERE EXISTS (
    SELECT 1 FROM Outfits WHERE outfit_id = 1
) AND EXISTS (
    SELECT 1 FROM Wardrobe_Items WHERE item_id = 2
);

INSERT INTO Outfit_Wardrobe_Items (outfit_id, item_id)
SELECT 2, 3
WHERE EXISTS (
    SELECT 1 FROM Outfits WHERE outfit_id = 2
) AND EXISTS (
    SELECT 1 FROM Wardrobe_Items WHERE item_id = 3
);

-- Output: Show all outfit-wardrobe item relationships
SELECT * FROM Outfit_Wardrobe_Items;
---------------------------------------------------------

-- Insert sample weather data
INSERT INTO Weather_Data (user_id, location, temperature, precipitation, wind_speed, humidity)
SELECT 1, 'London, UK', 63.1, 0.11, 12.1, 85
WHERE EXISTS (
    SELECT 1 FROM Users WHERE user_id = 1
);

-- Repeat for the second weather data entry:
INSERT INTO Weather_Data (user_id, location, temperature, precipitation, wind_speed, humidity)
SELECT 2, 'London, UK', 61.8, 0.01, 8.9, 80.4
WHERE EXISTS (
    SELECT 1 FROM Users WHERE user_id = 2
);

-- Output: Show all weather data
SELECT * FROM Weather_Data;
