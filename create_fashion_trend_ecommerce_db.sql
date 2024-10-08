-- Creating the database and selecting it
CREATE DATABASE IF NOT EXISTS fashion_trend_ecommerce_db;
USE fashion_trend_ecommerce_db;

-- Script for Fashion Trend, E-Commerce Products, and other key entities (Users, Wardrobe, Outfits, Weather Data)
-- Homework: Write SQL scripts to create tables, define constraints, and establish relationships

-- TABLE: Users
CREATE TABLE IF NOT EXISTS Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique ID for each user
    username VARCHAR(255) NOT NULL,          -- Username
    email VARCHAR(255) UNIQUE NOT NULL,      -- Email address
    password_hash VARCHAR(255) NOT NULL,     -- Hashed password
    location VARCHAR(255),                   -- User's location
    preferences TEXT,                        -- User's preferences, stored as JSON or TEXT
    date_joined DATETIME                     -- Date when the user joined
);

-- TABLE: Wardrobe Items
CREATE TABLE IF NOT EXISTS Wardrobe_Items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique ID for each wardrobe item
    user_id INT,                             -- Foreign key referencing Users
    type VARCHAR(255) NOT NULL,              -- Type of clothing (e.g., shirt, pants)
    season VARCHAR(255),                     -- Season (e.g., summer, winter)
    fabric VARCHAR(255),                     -- Fabric type
    color VARCHAR(255),                      -- Color of the item
    size VARCHAR(255),                       -- Size of the item
    tags TEXT,                               -- Tags (e.g., casual, formal)
    image_url VARCHAR(255),                  -- URL to the item's image
    date_added DATETIME,                     -- Date when the item was added
    CONSTRAINT fk_user_wardrobe FOREIGN KEY (user_id) -- Foreign key linking to Users
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- TABLE: Outfits
CREATE TABLE IF NOT EXISTS Outfits (
    outfit_id INT PRIMARY KEY AUTO_INCREMENT, -- Unique ID for each outfit
    user_id INT,                              -- Foreign key referencing Users
    occasion VARCHAR(255),                    -- Occasion (e.g., casual, formal)
    weather_condition VARCHAR(255),           -- Weather condition for the outfit
    trend_score DECIMAL(3, 2),                -- Trend score for the outfit
    date_suggested DATETIME,                  -- Date when the outfit was suggested
    CONSTRAINT fk_user_outfit FOREIGN KEY (user_id) -- Foreign key linking to Users
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- TABLE: Outfit_Wardrobe_Items (Junction table for outfits and wardrobe items)
CREATE TABLE IF NOT EXISTS Outfit_Wardrobe_Items (
    outfit_id INT,                             -- Foreign key referencing Outfits
    item_id INT,                               -- Foreign key referencing Wardrobe Items
    PRIMARY KEY (outfit_id, item_id),          -- Composite primary key (outfit_id, item_id)
    CONSTRAINT fk_outfit FOREIGN KEY (outfit_id) -- Foreign key linking to Outfits
        REFERENCES Outfits(outfit_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_wardrobe_item FOREIGN KEY (item_id) -- Foreign key linking to Wardrobe Items
        REFERENCES Wardrobe_Items(item_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- TABLE: Weather Data
CREATE TABLE IF NOT EXISTS Weather_Data (
    weather_id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique weather ID
    user_id INT,                                -- Foreign key referencing Users
    location VARCHAR(255),                      -- Location
    temperature DECIMAL(5, 2),                  -- Temperature in Celsius or Fahrenheit
    precipitation DECIMAL(5, 2),                -- Precipitation in mm
    wind_speed DECIMAL(5, 2),                   -- Wind speed in km/h or mph
    humidity DECIMAL(5, 2),                     -- Humidity percentage
    date_fetched DATETIME,                      -- Date when weather data was fetched
    CONSTRAINT fk_user_weather FOREIGN KEY (user_id) -- Foreign key linking to Users
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- TABLE: Fashion Trends
CREATE TABLE IF NOT EXISTS Fashion_Trends (
    trend_id INT PRIMARY KEY AUTO_INCREMENT,    -- Unique ID for each fashion trend
    title VARCHAR(255) NOT NULL,                -- Trend title
    description TEXT,                           -- Trend description
    categories VARCHAR(255),                    -- Categories for the trend (comma-separated)
    image_url VARCHAR(255),                     -- URL to the trend's image
    date_fetched DATETIME,                      -- Date when the trend data was fetched
    source_url VARCHAR(255)                     -- Source URL from where the trend data was fetched
);

-- TABLE: E-Commerce Products
CREATE TABLE IF NOT EXISTS E_Commerce_Products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique product ID
    user_id INT,                                -- Foreign key referencing the user
    suggested_item_type VARCHAR(255),           -- Suggested item type (e.g., shirt, shoes)
    product_name VARCHAR(255) NOT NULL,         -- Product name
    price DECIMAL(10, 2),                       -- Price of the product
    product_url VARCHAR(255),                   -- URL to the product
    image_url VARCHAR(255),                     -- URL to the product image
    date_suggested DATETIME,                    -- Date when the product was suggested
    CONSTRAINT fk_user_ecommerce FOREIGN KEY (user_id) -- Foreign key linking to Users
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Sample Data Population

-- Insert sample users
INSERT INTO Users (username, email, password_hash, location, preferences, date_joined)
VALUES 
('john_doe', 'john@example.com', 'hashed_password_1', 'New York', '{"style": "casual"}', NOW()),
('jane_smith', 'jane@example.com', 'hashed_password_2', 'Los Angeles', '{"style": "formal"}', NOW());

-- Insert sample wardrobe items
INSERT INTO Wardrobe_Items (user_id, type, season, fabric, color, size, tags, image_url, date_added)
VALUES 
(1, 'T-shirt', 'summer', 'cotton', 'blue', 'M', 'casual, light', 'http://example.com/tshirt.jpg', NOW()),
(1, 'Jeans', 'all_season', 'denim', 'black', '32', 'casual', 'http://example.com/jeans.jpg', NOW()),
(2, 'Dress', 'summer', 'silk', 'red', 'M', 'formal, evening', 'http://example.com/dress.jpg', NOW());

-- Insert sample outfits
INSERT INTO Outfits (user_id, occasion, weather_condition, trend_score, date_suggested)
VALUES 
(1, 'casual', 'sunny', 7.5, NOW()),
(2, 'formal', 'cloudy', 8.0, NOW());

-- Insert sample outfit-wardrobe items (junction table)
INSERT INTO Outfit_Wardrobe_Items (outfit_id, item_id)
VALUES 
(1, 1),
(1, 2),
(2, 3);

-- Insert sample weather data
INSERT INTO Weather_Data (user_id, location, temperature, precipitation, wind_speed, humidity, date_fetched)
VALUES 
(1, 'New York', 25.5, 0.0, 5.2, 60.0, NOW()),
(2, 'Los Angeles', 22.3, 0.0, 3.4, 50.0, NOW());

-- Insert sample fashion trends
INSERT INTO Fashion_Trends (title, description, categories, image_url, date_fetched, source_url)
VALUES 
('Summer Florals', 'Floral patterns are in this summer.', 'summer, floral', 'http://example.com/florals.jpg', NOW(), 'http://fashionwebsite.com/floral-trend'),
('Bold Colors', 'Bright, bold colors are trending this season.', 'bold, colors', 'http://example.com/colors.jpg', NOW(), 'http://fashionwebsite.com/bold-colors');

-- Insert sample e-commerce products
INSERT INTO E_Commerce_Products (user_id, suggested_item_type, product_name, price, product_url, image_url, date_suggested)
VALUES 
(1, 'shirt', 'Blue Casual Shirt', 25.99, 'http://ecommerce.com/product/blue-shirt', 'http://example.com/blue-shirt.jpg', NOW()),
(2, 'dress', 'Elegant Red Dress', 79.99, 'http://ecommerce.com/product/red-dress', 'http://example.com/red-dress.jpg', NOW());
