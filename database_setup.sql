-- DELETE statements to clear any existing data from tables
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
-- Insert sample users based on the provided data
INSERT INTO Users (username, email, password_hash, location, preferences)
VALUES 
('user_a', 'user_a@example.com', 'hashed_password_a', 'NY, USA', '["Black"]'),
('user_b', 'user_b@example.com', 'hashed_password_b', 'London, UK', '["Long coat"]');

-- Output: Show all users to ensure they were inserted correctly
SELECT * FROM Users;

----------------------------------------------------------------------------------------

-- Insert sample users if they don't already exist
INSERT INTO Users (username, email, password_hash, location, preferences)
SELECT 'user_a', 'user_a@example.com', 'hashed_password_a', 'NY, USA', '["Black"]'
WHERE NOT EXISTS (
    SELECT 1 FROM Users WHERE email = 'user_a@example.com'
);

INSERT INTO Users (username, email, password_hash, location, preferences)
SELECT 'user_b', 'user_b@example.com', 'hashed_password_b', 'London, UK', '["Long coat"]'
WHERE NOT EXISTS (
    SELECT 1 FROM Users WHERE email = 'user_b@example.com'
);

-- Output: Show all users to ensure they were inserted correctly
SELECT * FROM Users;



-------------------------------------------------------

-- Verify that users exist in the Users table
SELECT user_id, username FROM Users;
-- Insert sample outfits based on the provided data, ensuring the correct user_id is used
-- Assuming user_id 1 and 2 exist for 'user_a' and 'user_b'
INSERT INTO Outfits (user_id, occasion, weather_condition, trend_score)
SELECT user_id, 'casual', 'sunny', 7.5
FROM Users
WHERE username = 'user_a';

INSERT INTO Outfits (user_id, occasion, weather_condition, trend_score)
SELECT user_id, 'formal', 'cloudy', 8.0
FROM Users
WHERE username = 'user_b';

-- Output: Show all outfits
SELECT * FROM Outfits;
-- Insert sample data into the Outfit_Wardrobe_Items junction table
-- Ensure the outfit_id and item_id are correct and exist in the respective tables
INSERT INTO Outfit_Wardrobe_Items (outfit_id, item_id)
SELECT 1, 1
WHERE EXISTS (SELECT 1 FROM Outfits WHERE outfit_id = 1)
  AND EXISTS (SELECT 1 FROM Wardrobe_Items WHERE item_id = 1);

INSERT INTO Outfit_Wardrobe_Items (outfit_id, item_id)
SELECT 1, 2
WHERE EXISTS (SELECT 1 FROM Outfits WHERE outfit_id = 1)
  AND EXISTS (SELECT 1 FROM Wardrobe_Items WHERE item_id = 2);

INSERT INTO Outfit_Wardrobe_Items (outfit_id, item_id)
SELECT 2, 3
WHERE EXISTS (SELECT 1 FROM Outfits WHERE outfit_id = 2)
  AND EXISTS (SELECT 1 FROM Wardrobe_Items WHERE item_id = 3);

-- Output: Show all outfit-wardrobe item relationships
SELECT * FROM Outfit_Wardrobe_Items;


-----------------------------------------------
-- Insert sample outfits based on the provided data
-- Using a SELECT to retrieve the correct user_id from the Users table
INSERT INTO Outfits (user_id, occasion, weather_condition, trend_score)
SELECT user_id, 'casual', 'sunny', 7.5
FROM Users
WHERE username = 'user_a';

INSERT INTO Outfits (user_id, occasion, weather_condition, trend_score)
SELECT user_id, 'formal', 'cloudy', 8.0
FROM Users
WHERE username = 'user_b';

-- Output: Show all outfits and their corresponding outfit_id to use in the next step
SELECT * FROM Outfits;

-- Retrieve the outfit_id values
SELECT outfit_id, user_id, occasion FROM Outfits;

-- Insert sample data into the Outfit_Wardrobe_Items junction table
-- Use the correct outfit_id and item_id values from the previous SELECT query
INSERT INTO Outfit_Wardrobe_Items (outfit_id, item_id)
VALUES 
(1, 1),  -- Assuming outfit_id 1 corresponds to the first outfit
(1, 2),
(2, 3);  -- Assuming outfit_id 2 corresponds to the second outfit

-- Output: Show all outfit-wardrobe item relationships
SELECT * FROM Outfit_Wardrobe_Items;

-- Insert sample weather data based on the provided data
-- Ensure the correct user_id exists in the Users table
INSERT INTO Weather_Data (user_id, location, temperature, precipitation, wind_speed, humidity)
SELECT user_id, 'London, UK', 63.1, 0.11, 12.1, 85.0
FROM Users
WHERE username = 'user_a';

INSERT INTO Weather_Data (user_id, location, temperature, precipitation, wind_speed, humidity)
SELECT user_id, 'London, UK', 61.8, 0.01, 8.9, 80.4
FROM Users
WHERE username = 'user_b';

-- Output: Show all weather data
SELECT * FROM Weather_Data;


---------------------------------------------------------

-- Insert sample weather data based on the provided data
INSERT INTO Weather_Data (user_id, location, temperature, precipitation, wind_speed, humidity)
VALUES 
(1, 'London, UK', 63.1, 0.11, 12.1, 85.0),
(2, 'London, UK', 61.8, 0.01, 8.9, 80.4);

-- Output: Show all weather data
SELECT * FROM Weather_Data;

-------------------------------------------------------
-- Insert sample fashion trends data
INSERT INTO Fashion_Trends (title, description, categories, image_url, source_url)
VALUES 
('Summer 2024 Trends', 'Light and airy fabrics dominate', '["summer", "light"]', 'http://example.com/trends2024.jpg', 'http://example.com/source'),
('Winter 2024 Trends', 'Cozy and oversized are in', '["winter", "oversized"]', 'http://example.com/trends_winter.jpg', 'http://example.com/source_winter');

-- Output: Show all fashion trends
SELECT * FROM Fashion_Trends;

-------------------------------------------------------
-- Insert sample e-commerce products data based on the provided data
INSERT INTO E_Commerce_Products (user_id, suggested_item_type, product_name, price, product_url, image_url)
VALUES 
(1, 'T-shirt', 'Blue Cotton T-shirt', 29.99, 'http://example.com/blue_tshirt', 'http://example.com/blue_tshirt.jpg'),
(2, 'Dress', 'Red Silk Dress', 119.99, 'http://example.com/red_silk_dress', 'http://example.com/red_silk_dress.jpg');

-- Output: Show all e-commerce products
SELECT * FROM E_Commerce_Products;
