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
    product_id BIGINT AUTO_INCREMENT PRIMARY KEY,  -- Changed to BIGINT
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
    product_id BIGINT,  -- Changed to BIGINT to match ecommerce_products
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
