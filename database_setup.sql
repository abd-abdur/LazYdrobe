-- Create users table
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

-- Create ecommerce_products table
CREATE TABLE IF NOT EXISTS ecommerce_products (
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

-- Create wardrobe_items table
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
        REFERENCES ecommerce_products(product_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Create outfits table
CREATE TABLE IF NOT EXISTS outfits (
    outfit_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    clothings JSON NOT NULL,
    occasion JSON,
    for_weather VARCHAR(255),
    source_url VARCHAR(255),
    date_suggested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_outfit FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Insert sample data into users table
INSERT INTO users (username, email, password, user_ip, location, preferences)
VALUES 
('user1', 'user1@example.com', '$2b$12$e0NRaY5hOvG9aYoGc0VHeuxl25K5qSdeIwx/VEv7HBYe/.n.5bZ0K', '192.168.1.1', 'New York, USA', JSON_ARRAY('casual', 'black')),
('user2', 'user2@example.com', '$2b$12$e0NRaY5hOvG9aYoGc0VHeuxl25K5qSdeIwx/VEv7HBYe/.n.5bZ0K', '192.168.1.2', 'London, UK', JSON_ARRAY('formal', 'blue'));

-- Insert sample data into ecommerce_products table
INSERT INTO ecommerce_products (user_id, product_name, suggested_item_type, price, product_url, image_url)
VALUES 
(1, 'Black T-shirt', 'T-shirt', 19.99, 'http://example.com/black-tshirt', 'http://example.com/images/black-tshirt.jpg'),
(1, 'Blue Jeans', 'Jeans', 39.99, 'http://example.com/blue-jeans', 'http://example.com/images/blue-jeans.jpg'),
(2, 'Formal Shirt', 'Shirt', 29.99, 'http://example.com/formal-shirt', 'http://example.com/images/formal-shirt.jpg');

-- Insert sample data into wardrobe_items table
INSERT INTO wardrobe_items (user_id, product_id, clothing_type, for_weather, color, size, tags, image_url)
VALUES 
(1, 1, 'T-shirt', 'summer', JSON_ARRAY('black'), 'M', JSON_ARRAY('casual', 'cotton'), 'http://example.com/images/black-tshirt.jpg'),
(1, 2, 'Jeans', 'all-weather', JSON_ARRAY('blue'), '32', JSON_ARRAY('casual', 'denim'), 'http://example.com/images/blue-jeans.jpg'),
(2, 3, 'Shirt', 'all-weather', JSON_ARRAY('white'), 'L', JSON_ARRAY('formal', 'long-sleeve'), 'http://example.com/images/formal-shirt.jpg');

-- Insert sample data into outfits table
INSERT INTO outfits (user_id, clothings, occasion, for_weather, source_url)
VALUES 
(1, JSON_ARRAY('Black T-shirt', 'Blue Jeans'), JSON_ARRAY('casual', 'weekend'), 'summer', 'http://example.com/outfits/casual1'),
(2, JSON_ARRAY('Formal Shirt'), JSON_ARRAY('business', 'meeting'), 'all-weather', 'http://example.com/outfits/formal1');
