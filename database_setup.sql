
-- =====================================================
-- LazYdrobe Database Setup Script for MySQL
-- =====================================================

-- 1. DROP EXISTING TABLES IF THEY EXIST
DROP TABLE IF EXISTS outfit;
DROP TABLE IF EXISTS wardrobe_items;
DROP TABLE IF EXISTS e_commerce_product;
DROP TABLE IF EXISTS fashion;
DROP TABLE IF EXISTS weather_data;
DROP TABLE IF EXISTS users;

-- 2. CREATE USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_ip VARCHAR(255),
    location VARCHAR(255),
    preferences JSON,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. CREATE E_COMMERCE_PRODUCT TABLE
CREATE TABLE IF NOT EXISTS e_commerce_product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    suggested_item_type VARCHAR(255),
    price FLOAT,
    product_url VARCHAR(255),
    image_url VARCHAR(255),
    date_suggested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_ecommerce FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 4. CREATE WARDROBE_ITEMS TABLE
CREATE TABLE IF NOT EXISTS wardrobe_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT,
    clothing_type VARCHAR(255) NOT NULL,
    for_weather VARCHAR(255),
    color JSON,
    size VARCHAR(50),
    tags JSON,
    image_url VARCHAR(255),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_clothing FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_product_clothing FOREIGN KEY (product_id)
        REFERENCES e_commerce_product(product_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 5. CREATE OUTFIT TABLE
CREATE TABLE IF NOT EXISTS outfit (
    outfit_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    clothings JSON NOT NULL, -- Changed from ARRAY to JSON
    occasion JSON,          -- Changed from ARRAY to JSON
    for_weather VARCHAR(255),
    date_suggested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_url VARCHAR(255),
    CONSTRAINT fk_user_outfit FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 6. CREATE WEATHER_DATA TABLE
CREATE TABLE IF NOT EXISTS weather_data (
    weather_id INT AUTO_INCREMENT PRIMARY KEY,
    weather_date TIMESTAMP NOT NULL,
    location VARCHAR(255) NOT NULL,
    temp_max FLOAT,
    temp_min FLOAT,
    feels_max FLOAT,
    feels_min FLOAT,
    wind_speed FLOAT,
    humidity FLOAT,
    precipitation FLOAT,
    precipitation_probability FLOAT,
    special_condition VARCHAR(255)
) ENGINE=InnoDB;

-- 7. CREATE FASHION TABLE
CREATE TABLE IF NOT EXISTS fashion (
    trend_id INT AUTO_INCREMENT PRIMARY KEY,
    trend_names VARCHAR(255) NOT NULL,
    description TEXT,
    temperature VARCHAR(255),
    occasion VARCHAR(255),
    image_url VARCHAR(255),
    example_fits JSON, -- Changed from ARRAY to JSON
    INDEX idx_trend_names (trend_names)
) ENGINE=InnoDB;

-- 8. CREATE INDEXES FOR FOREIGN KEYS AND FREQUENTLY QUERIED COLUMNS
CREATE INDEX idx_wardrobe_items_user_id ON wardrobe_items(user_id);
CREATE INDEX idx_wardrobe_items_product_id ON wardrobe_items(product_id);
CREATE INDEX idx_ecommerce_user_id ON e_commerce_product(user_id);
CREATE INDEX idx_outfit_user_id ON outfit(user_id);
CREATE INDEX idx_weather_data_location ON weather_data(location);

-- 9. INSERT SAMPLE DATA

-- 9.1 Insert Sample Users
INSERT INTO users (username, email, password, location, preferences)
VALUES 
('user_a', 'user_a@example.com', '$2b$12$e0NRaY5hOvG9aYoGc0VHeuxl25K5qSdeIwx/VEv7HBYe/.n.5bZ0K', 'NY, USA', JSON_ARRAY('Black')),
('user_b', 'user_b@example.com', '$2b$12$e0NRaY5hOvG9aYoGc0VHeuxl25K5qSdeIwx/VEv7HBYe/.n.5bZ0K', 'London, UK', JSON_ARRAY('Long coat'))
ON DUPLICATE KEY UPDATE email=email;

-- 9.2 Insert Sample E-Commerce Products
INSERT INTO e_commerce_product (user_id, product_name, suggested_item_type, price, product_url, image_url)
VALUES 
(1, 'Blue Cotton T-shirt', 'T-shirt', 29.99, 'http://example.com/blue_tshirt', 'http://example.com/blue_tshirt.jpg'),
(2, 'Red Silk Dress', 'Dress', 119.99, 'http://example.com/red_silk_dress', 'http://example.com/red_silk_dress.jpg')
ON DUPLICATE KEY UPDATE product_name=product_name;

-- 9.3 Insert Sample Wardrobe Items
INSERT INTO wardrobe_items (user_id, product_id, clothing_type, for_weather, color, size, tags, image_url)
VALUES 
(1, 1, 'T-shirt', 'Summer', JSON_ARRAY('Blue'), 'M', JSON_ARRAY('casual'), 'https://example.com/tshirt.jpg'),
(2, 2, 'Dress', 'Summer', JSON_ARRAY('Red'), 'L', JSON_ARRAY('formal'), 'https://example.com/dress.jpg')
ON DUPLICATE KEY UPDATE item_id=item_id;

-- 9.4 Insert Sample Outfits
INSERT INTO outfit (user_id, clothings, occasion, for_weather, source_url)
VALUES 
(1, JSON_ARRAY(1), JSON_ARRAY('casual'), 'sunny', 'http://example.com/outfit1'),
(2, JSON_ARRAY(2), JSON_ARRAY('formal'), 'cloudy', 'http://example.com/outfit2')
ON DUPLICATE KEY UPDATE outfit_id=outfit_id;

-- 9.5 Insert Sample Weather Data
INSERT INTO weather_data (weather_date, location, temp_max, temp_min, feels_max, feels_min, wind_speed, humidity, precipitation, precipitation_probability, special_condition)
VALUES 
('2024-10-10 12:00:00', 'London, UK', 20.0, 15.0, 18.0, 13.0, 5.0, 80.0, 0.5, 0.2, 'cloudy')
ON DUPLICATE KEY UPDATE weather_id=weather_id;

-- 9.6 Insert Sample Fashion Trends
INSERT INTO fashion (trend_names, description, temperature, occasion, image_url, example_fits)
VALUES 
('Summer 2024 Trends', 'Light and airy fabrics dominate', 'warm', 'casual', 'http://example.com/trends2024.jpg', JSON_ARRAY('fit1', 'fit2')),
('Winter 2024 Trends', 'Cozy and oversized are in', 'cold', 'formal', 'http://example.com/trends_winter.jpg', JSON_ARRAY('fit3', 'fit4'))
ON DUPLICATE KEY UPDATE trend_id=trend_id;
