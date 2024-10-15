-- DELETE statements to clear any existing data from tables
DELETE FROM users;
DELETE FROM clothing;
DELETE FROM outfit;
DELETE FROM weatherData;
DELETE FROM fashion;
DELETE FROM eCommerceProduct;

----------------------------------------

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    wardrobe TEXT[],
    user_ip VARCHAR,
    location VARCHAR,
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
    type VARCHAR NOT NULL,
    for_weather VARCHAR,
    color TEXT[],
    size VARCHAR,
    tags TEXT[],
    image_url TEXT,
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
    occasion TEXT,
    for_weather VARCHAR,
    date_suggested TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    source_url TEXT
);

-- Output: Check if the outfit table is created (structure)
SELECT * FROM outfit LIMIT 0;

-------------------------------------------------------------------------------------
-- Create the weatherData table
CREATE TABLE IF NOT EXISTS weatherData (
    date TIMESTAMPTZ NOT NULL,
    location VARCHAR NOT NULL,
    temp_max FLOAT,
    temp_min FLOAT,
    feels_max FLOAT,
    feels_min FLOAT,
    wind_speed FLOAT,
    humidity FLOAT,
    precipitation FLOAT,
    precipitation_probability FLOAT,
    special_condition VARCHAR
);

-- Output: Check if the weatherData table is created (structure)
SELECT * FROM weatherData LIMIT 0;

----------------------------------------------------------------------------
-- Create the fashion table
CREATE TABLE IF NOT EXISTS fashion (
    trend_id SERIAL PRIMARY KEY,
    trend_names VARCHAR NOT NULL,
    description TEXT,
    temperature VARCHAR,
    occasion VARCHAR,
    image_url TEXT,
    example_fits TEXT[]
);

-- Output: Check if the fashion table is created (structure)
SELECT * FROM fashion LIMIT 0;

---------------------------------------------------------------------------
-- Create the eCommerceProduct table
CREATE TABLE IF NOT EXISTS eCommerceProduct (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR NOT NULL,
    suggested_item_type VARCHAR,
    price FLOAT,
    product_url TEXT,
    image_url TEXT
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

-- Insert sample clothing items based on the provided data
INSERT INTO clothing (user_id, product_id, type, for_weather, color, size, tags, image_url)
VALUES 
(1, 101, 'Jacket', 'Winter', '{"Black"}', 'M', '{"Formal"}', 'http://example.com/jacket.jpg'),
(2, 102, 'T-shirt', 'Summer', '{"White"}', 'L', '{"Casual"}', 'http://example.com/tshirt.jpg');

-- Output: Show all clothing items to ensure they were inserted correctly
SELECT * FROM clothing;

----------------------------------------------------------------------------------------

-- Insert sample outfits based on the provided data
INSERT INTO outfit (clothings, occasion, for_weather, source_url)
VALUES 
('{"Jacket", "T-shirt"}', 'casual', 'sunny', 'http://example.com/outfit1.jpg'),
('{"T-shirt"}', 'formal', 'cloudy', 'http://example.com/outfit2.jpg');

-- Output: Show all outfits
SELECT * FROM outfit;

----------------------------------------------------------------------------------------

-- Insert sample weather data
INSERT INTO weatherData (date, location, temp_max, temp_min, feels_max, feels_min, wind_speed, humidity, precipitation, precipitation_probability, special_condition)
VALUES 
('2024-10-15', 'NY, USA', 80.5, 65.3, 82.0, 64.0, 10.5, 60.2, 0.1, 0.2, 'Clear'),
('2024-10-15', 'London, UK', 60.3, 45.6, 58.2, 44.5, 15.1, 70.0, 0.3, 0.4, 'Cloudy');

-- Output: Show all weather data
SELECT * FROM weatherData;

----------------------------------------------------------------------------------------

-- Insert sample fashion trends based on the provided data
INSERT INTO fashion (trend_names, description, temperature, occasion, image_url, example_fits)
VALUES 
('Summer 2024 Trends', 'Light fabrics and bright colors.', 'Summer', 'Casual', 'http://example.com/summer2024.jpg', '{"Shirt", "Shorts"}'),
('Winter 2024 Trends', 'Cozy oversized clothes.', 'Winter', 'Formal', 'http://example.com/winter2024.jpg', '{"Coat", "Scarf"}');

-- Output: Show all fashion trends
SELECT * FROM fashion;

----------------------------------------------------------------------------------------

-- Insert sample e-commerce products
INSERT INTO eCommerceProduct (product_name, suggested_item_type, price, product_url, image_url)
VALUES 
('Blue Cotton T-shirt', 'T-shirt', 29.99, 'http://example.com/blue_tshirt', 'http://example.com/images/blue_tshirt.jpg'),
('Red Silk Dress', 'Dress', 119.99, 'http://example.com/red_silk_dress', 'http://example.com/images/red_silk_dress.jpg');

-- Output: Show all e-commerce products
SELECT * FROM eCommerceProduct;

