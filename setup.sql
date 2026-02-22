CREATE DATABASE IF NOT EXISTS shop_products CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shop_products;
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(100),
    name VARCHAR(500),
    brand VARCHAR(255),
    category VARCHAR(500),
    price VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_product (product_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;