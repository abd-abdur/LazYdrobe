-- Step 1: Create and select the database
CREATE DATABASE IF NOT EXISTS fashion_trend_ecommerce_db;
USE fashion_trend_ecommerce_db;

-- Step 2: Create the Users table
CREATE TABLE IF NOT EXISTS Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,    -- Unique ID for each user
    username VARCHAR(255) NOT NULL,            -- Username
    email VARCHAR(255) UNIQUE NOT NULL,        -- Unique email address
    password_hash VARCHAR(255) NOT NULL,       -- Hashed password for security
    location VARCHAR(255),                     -- Location (city, country)
    preferences JSON,                          -- User preferences stored as JSON
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP -- Auto timestamp when user joins
);

-- Step 3: Create the Wardrobe_Items table
CREATE TABLE IF NOT EXISTS Wardrobe_Items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,    -- Unique ID for each wardrobe item
    user_id INT NOT NULL,                      -- Foreign key to Users table
    type VARCHAR(255) NOT NULL,                -- Type of clothing (e.g., shirt, pants)
    season VARCHAR(255),                       -- Associated season (e.g., summer, winter)
    fabric VARCHAR(255),                       -- Fabric type (e.g., cotton, wool)
    color VARCHAR(255),                        -- Item color (e.g., red, blue)
    size VARCHAR(50),                          -- Size of the item (e.g., M, L, 32)
    tags JSON,                                 -- Tags to categorize items (stored as JSON)
    image_url VARCHAR(255),                    -- URL to the image of the item
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP, -- Auto timestamp when item is added
    CONSTRAINT fk_user_wardrobe FOREIGN KEY (user_id) -- Foreign key reference to Users
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Step 4: Create the Outfits table
CREATE TABLE IF NOT EXISTS Outfits (
    outfit_id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique ID for each outfit
    user_id INT NOT NULL,                      -- Foreign key to Users table
    occasion VARCHAR(255),                     -- Occasion (e.g., casual, formal)
    weather_condition VARCHAR(255),            -- Weather condition when the outfit is suggested
    trend_score DECIMAL(3, 2),                 -- Trend score (0.00 - 10.00 scale)
    date_suggested DATETIME DEFAULT CURRENT_TIMESTAMP, -- Auto timestamp when outfit is suggested
    CONSTRAINT fk_user_outfit FOREIGN KEY (user_id) -- Foreign key reference to Users
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Step 5: Create a junction table Outfit_Wardrobe_Items for many-to-many relationships
CREATE TABLE IF NOT EXISTS Outfit_Wardrobe_Items (
    outfit_id INT NOT NULL,                    -- Foreign key to Outfits
    item_id INT NOT NULL,                      -- Foreign key to Wardrobe_Items
    PRIMARY KEY (outfit_id, item_id),          -- Composite primary key
    CONSTRAINT fk_outfit FOREIGN KEY (outfit_id) -- Foreign key to Outfits table
        REFERENCES Outfits(outfit_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_wardrobe_item FOREIGN KEY (item_id) -- Foreign key to Wardrobe_Items table
        REFERENCES Wardrobe_Items(item_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Step 6: Create the Weather_Data table
CREATE TABLE IF NOT EXISTS Weather_Data (
    weather_id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique weather record ID
    user_id INT NOT NULL,                       -- Foreign key to Users table
    location VARCHAR(255) NOT NULL,             -- Location (city, country)
    temperature DECIMAL(5, 2),                  -- Temperature in °C or °F
    precipitation DECIMAL(5, 2),                -- Precipitation in mm
    wind_speed DECIMAL(5, 2),                   -- Wind speed in km/h or mph
    humidity DECIMAL(5, 2),                     -- Humidity percentage
    date_fetched DATETIME DEFAULT CURRENT_TIMESTAMP, -- Auto timestamp for data fetch
    CONSTRAINT fk_user_weather FOREIGN KEY (user_id) -- Foreign key reference to Users
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Step 7: Create the Fashion_Trends table
CREATE TABLE IF NOT EXISTS Fashion_Trends (
    trend_id INT PRIMARY KEY AUTO_INCREMENT,    -- Unique ID for each trend
    title VARCHAR(255) NOT NULL,                -- Trend title
    description TEXT,                           -- Detailed description of the trend
    categories VARCHAR(255),                    -- Trend categories (comma-separated)
    image_url VARCHAR(255),                     -- URL to an image representing the trend
    date_fetched DATETIME DEFAULT CURRENT_TIMESTAMP, -- Auto timestamp for when trend was fetched
    source_url VARCHAR(255)                     -- Source URL from where the trend was fetched
);

-- Step 8: Create the E_Commerce_Products table
CREATE TABLE IF NOT EXISTS E_Commerce_Products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique product ID
    user_id INT NOT NULL,                       -- Foreign key to Users table
    suggested_item_type VARCHAR(255),           -- Suggested item type (e.g., shirt, shoes)
    product_name VARCHAR(255) NOT NULL,         -- Product name
    price DECIMAL(10, 2),                       -- Product price
    product_url VARCHAR(255),                   -- URL to the product on the e-commerce platform
    image_url VARCHAR(255),                     -- URL to the product image
    date_suggested DATETIME DEFAULT CURRENT_TIMESTAMP, -- Auto timestamp when product is suggested
    CONSTRAINT fk_user_ecommerce FOREIGN KEY (user_id) -- Foreign key reference to Users
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Step 9: Sample Data Insertion

-- Insert sample users
INSERT INTO Users (username, email, password_hash, location, preferences)
VALUES 
('a', 'user_a@example.com', 'hashed_password_a', 'NY, USA', JSON_ARRAY('Black')),
('b', 'user_b@example.com', 'hashed_password_b', 'London, UK', JSON_ARRAY('Long coat'));

-- Insert sample wardrobe items
INSERT INTO Wardrobe_Items (user_id, type, season, fabric, color, size, tags, image_url)
VALUES 
(1, 'T-shirt', 'summer', 'cotton', 'blue', 'M', JSON_ARRAY('casual', 'light'), 'http://example.com/tshirt.jpg'),
(1, 'Jeans', 'all_season', 'denim', 'black', '32', JSON_ARRAY('casual'), 'http://example.com/jeans.jpg'),
(2, 'Dress', 'summer', 'silk', 'red', 'M', JSON_ARRAY('formal', 'evening'), 'http://example.com/dress.jpg');

-- Insert sample outfits
INSERT INTO Outfits (user_id, occasion, weather_condition, trend_score)
VALUES 
(1, 'casual', 'sunny', 7.5),
(2, 'formal', 'cloudy', 8.0);

-- Insert sample data into Outfit_Wardrobe_Items (junction table)
INSERT INTO Outfit_Wardrobe_Items (outfit_id, item_id)
VALUES 
(1, 1),
(1, 2),
(2, 3);

-- Insert sample weather data
INSERT INTO Weather_Data (user_id, location, temperature, precipitation, wind_speed, humidity)
VALUES 
(1, 'London, UK', 63.1, 0.11, 12.1, 85),
(2, 'London, UK', 61.8, 0.01, 8.9, 80.4);

-- Insert sample fashion trends
INSERT INTO Fashion_Trends (title, description, categories, image_url, source_url)
VALUES 
('Country house chic', 'Fall’s most alluring trend... English countryside.', 'fall', 'https://media.glamour.com/photos/66ccdbd14397358d42cb7841/master/w_1600,c_limit/fall%20fashion%20trends%20%E2%80%94%20country%20house%20chic.png', 'http://glamour.com/country-house-chic'),
('Boho 3.0', 'Shabby chic! While the word boho... feel fresher.', 'fall', 'https://media.glamour.com/photos/66ccdc324397358d42cb7843/master/w_1600,c_limit/fall%20fashion%20trends%20%E2%80%94%20boho.png', 'http://glamour.com/boho-3.0');

-- Insert sample e-commerce products
INSERT INTO E_Commerce_Products (user_id, suggested_item_type, product_name, price, product_url, image_url)
VALUES 
(1, 'Jacket', 'Classic Leather Biker Jacket', 199.99, 'https://www.ebay.com/itm/Classic-Leather-Biker-Jacket-64b1f1a2e3f4a5b6c7d8e900', 'https://i.ebayimg.com/images/g/Leather-Biker-Jacket.jpg'),
(2, 'Boots', 'Waterproof Ankle Boots', 89.99, 'https://www.ebay.com/itm/Waterproof-Ankle-Boots-abc123', 'https://i.ebayimg.com/images/g/Waterproof-Ankle-Boots.jpg'),
(1, 'Shirt', 'Casual White Shirt', 29.99, 'https://www.ebay.com/itm/Casual-White-Shirt-xyz789', 'https://i.ebayimg.com/images/g/Casual-White-Shirt.jpg'),
(2, 'Dress', 'Summer Floral Dress', 49.99, 'https://www.ebay.com/itm/Summer-Floral-Dress-456xyz', 'https://i.ebayimg.com/images/g/Summer-Floral-Dress.jpg');
