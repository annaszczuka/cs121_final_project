DROP TABLE IF EXISTS staging_data;

CREATE TABLE staging_data (
    customer_id INT,  
    age INT,
    annual_income_usd FLOAT,
    product_category TEXT,
    product_price_usd FLOAT,
    purchase_date DATE,  -- Fixed: Changed from TEXT to DATE
    store_id INT,  -- Fixed: Changed from FLOAT to INT
    store_location TEXT,
    payment_method TEXT,
    discount_percent INT,  -- Fixed: Changed from FLOAT to INT
    product_cost_usd FLOAT,
    foot_traffic INT,
    quantity INT,
    competitor_price_usd FLOAT,
    full_name TEXT,
    gender TEXT,
    year_opened INT,  -- Fixed: Changed from FLOAT to INT
    is_favorite INT,  -- Fixed: Changed from BOOLEAN to INT (0/1)
    purchase_id VARCHAR(7),  -- Fixed: Matches CHAR(7)
    product_id VARCHAR(7),  -- Fixed: Matches CHAR(7)
    visit_date DATE  -- Fixed: Changed from TEXT to DATE
);

-- COPY staging_data FROM '/var/lib/mysql-files/cleaned_data.csv' DELIMITER ',' CSV HEADER;
SET SESSION sql_mode = '';

LOAD DATA INFILE '/var/lib/mysql-files/data.csv'
INTO TABLE staging_data
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Insert into customer
INSERT INTO customer (customer_id, age, gender, annual_income_usd, full_name)
SELECT DISTINCT 
    customer_id,  
    age,  
    gender,  
    annual_income_usd,  
    full_name
FROM staging_data;

-- Insert into store
INSERT IGNORE INTO store (store_id, store_location, year_opened)
SELECT DISTINCT 
    store_id,  
    store_location,  
    year_opened
FROM staging_data;

-- Insert into product (Fixed: Removed store_id)
INSERT IGNORE INTO product (product_id, product_category)
SELECT DISTINCT 
    product_id,  
    product_category
FROM staging_data;

-- Insert into inventory
INSERT INTO inventory (product_id, store_id, store_location, qty, product_price_usd, product_cost_usd, competitor_price_usd)
SELECT DISTINCT 
    product_id,  
    store_id,  
    store_location,  
    quantity,  
    product_price_usd,  
    product_cost_usd,  
    competitor_price_usd
FROM staging_data;

-- Insert into popularity
INSERT INTO popularity (store_id, store_location, visit_date, foot_traffic)
SELECT DISTINCT 
    store_id,  
    store_location,  
    visit_date,  
    foot_traffic
FROM staging_data;

-- Insert into purchase (Fixed: Added store_location)
INSERT INTO purchase (purchase_id, product_id, store_id, store_location, customer_id, payment_method, discount_percent, txn_date, purchased_product_price_usd)
SELECT DISTINCT 
    purchase_id,  
    product_id,  
    store_id,  
    store_location,  
    customer_id,  
    payment_method,  
    discount_percent,  
    purchase_date,  
    product_price_usd
FROM staging_data;

-- Insert into customer_visits (Fixed: Handled BOOLEAN properly)
INSERT INTO customer_visits (customer_id, store_id, store_location, is_favorite)
SELECT DISTINCT 
    customer_id,  
    store_id,  
    store_location,  
    CASE WHEN is_favorite > 0 THEN TRUE ELSE FALSE END
FROM staging_data;
