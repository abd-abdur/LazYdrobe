-- DELETE statements to clear any existing data from tables
DELETE FROM users;
DELETE FROM clothing;
DELETE FROM outfit;
DELETE FROM eCommerceProduct;
DELETE FROM weatherData;
DELETE FROM fashion;

----------------------------------------

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    wardrobe TEXT[],
    user_ip VARCHAR(255),
    location VARCHAR(255),
    preferences TEXT[],
    date_joined TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Output: Check if the users table is created (structure)
SELECT * FROM users LIMIT 0;

----------------------------------------------------------------
-- Create the clothing table
CREATE TABLE IF NOT EXISTS clothing (
    item_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER,
    type VARCHAR(255) NOT NULL,
    for_weather VARCHAR(255),
    color TEXT[],
    size VARCHAR(50),
    tags TEXT[],
    image_url VARCHAR(255),
    date_added TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_clothing FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Output: Check if the clothing table is created (structure)
SELECT * FROM clothing LIMIT 0;

------------------------------------------------------------------------
-- Create the outfit table
CREATE TABLE IF NOT EXISTS outfit (
    outfit_id SERIAL PRIMARY KEY,
    clothings TEXT[],
    occasion TEXT[],
    for_weather VARCHAR(255),
    date_suggested TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    source_url VARCHAR(255)
);

-- Output: Check if the outfit table is created (structure)
SELECT * FROM outfit LIMIT 0;

-------------------------------------------------------------------------------------
-- Create the weatherData table
CREATE TABLE IF NOT EXISTS weatherData (
    date TIMESTAMPTZ NOT NULL,
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
);

-- Output: Check if the weatherData table is created (structure)
SELECT * FROM weatherData LIMIT 0;

----------------------------------------------------------------------------
-- Create the fashion table
CREATE TABLE IF NOT EXISTS fashion (
    trend_id SERIAL PRIMARY KEY,
    trend_names VARCHAR(255) NOT NULL,
    description TEXT,
    temperature VARCHAR(255),
    occasion VARCHAR(255),
    image_url VARCHAR(255),
    example_fits TEXT[]
);

-- Output: Check if the fashion table is created (structure)
SELECT * FROM fashion LIMIT 0;

---------------------------------------------------------------------------
-- Create the eCommerceProduct table
CREATE TABLE IF NOT EXISTS eCommerceProduct (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    suggested_item_type VARCHAR(255),
    price FLOAT,
    product_url VARCHAR(255),
    image_url VARCHAR(255)
);

-- Output: Check if the eCommerceProduct table is created (structure)
SELECT * FROM eCommerceProduct LIMIT 0;

------------------------------------------------------------------------------------------------
-- Insert sample users based on the provided data
INSERT INTO users (username, email, password, location, preferences)
VALUES 
('user_a', 'user_a@example.com', 'hashed_password_a', 'NY, USA', '{"Black"}'),
('user_b', 'user_b@example.com', 'hashed_password_b', 'London, UK', '{"Long coat"}');

-- Output: Show all users to ensure they were inserted correctly
SELECT * FROM users;

----------------------------------------------------------------------------------------

-- Insert sample users if they don't already exist
INSERT INTO users (username, email, password, location, preferences)
SELECT 'user_a', 'user_a@example.com', 'hashed_password_a', 'NY, USA', '{"Black"}'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'user_a@example.com'
);

INSERT INTO users (username, email, password, location, preferences)
SELECT 'user_b', 'user_b@example.com', 'hashed_password_b', 'London, UK', '{"Long coat"}'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'user_b@example.com'
);

-- Output: Show all users to ensure they were inserted correctly
SELECT * FROM users;

-------------------------------------------------------

-- Verify that users exist in the users table
SELECT user_id, username FROM users;

-- Insert sample outfits based on the provided data, ensuring the correct user_id is used
-- Assuming user_id 1 and 2 exist for 'user_a' and 'user_b'
INSERT INTO outfit (clothings, occasion, for_weather)
VALUES 
('{"shirt", "jeans"}', '{"casual"}', 'sunny'),
('{"dress", "coat"}', '{"formal"}', 'cloudy');

-- Output: Show all outfits
SELECT * FROM outfit;

-----------------------------------------------
-- Insert sample weather data
INSERT INTO weatherData (date, location, temp_max, temp_min, feels_max, feels_min, wind_speed, humidity, precipitation, precipitation_probability, special_condition)
VALUES 
('2024-10-10', 'London, UK', 20.0, 15.0, 18.0, 13.0, 5.0, 80.0, 0.5, 0.2, 'cloudy');

-- Output: Show all weather data
SELECT * FROM weatherData;

-------------------------------------------------------

-- Insert sample fashion trends data
INSERT INTO fashion (trend_names, description, temperature, occasion, image_url, example_fits)
VALUES 
('Summer 2024 Trends', 'Light and airy fabrics dominate', 'warm', 'casual', 'http://example.com/trends2024.jpg', '{"fit1", "fit2"}'),
('Winter 2024 Trends', 'Cozy and oversized are in', 'cold', 'formal', 'http://example.com/trends_winter.jpg', '{"fit3", "fit4"}');

-- Output: Show all fashion trends
SELECT * FROM fashion;

-------------------------------------------------------
-- Insert sample e-commerce products data
INSERT INTO eCommerceProduct (product_name, suggested_item_type, price, product_url, image_url)
VALUES 
('Blue Cotton T-shirt', 'T-shirt', 29.99, 'http://example.com/blue_tshirt', 'http://example.com/blue_tshirt.jpg'),
('Red Silk Dress', 'Dress', 119.99, 'http://example.com/red_silk_dress', 'http://example.com/red_silk_dress.jpg');

-- Output: Show all e-commerce products
SELECT * FROM eCommerceProduct;
