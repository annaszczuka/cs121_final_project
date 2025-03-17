DROP TABLE IF EXISTS staging_data;

-- Temporary table to hold raw csv data before inserting into actual database tables
CREATE TABLE staging_data (
    customer_id INT,
    age INT,
    annual_income_usd FLOAT,
    product_category VARCHAR(255),
    product_price_usd FLOAT,
    purchase_date DATE, 
    store_id INT, 
    store_location VARCHAR(255),
    payment_method VARCHAR(255),
    discount_percent INT,
    product_cost_usd FLOAT,
    foot_traffic INT,
    qty INT,
    competitor_price_usd FLOAT,
    full_name VARCHAR(255),
    gender CHAR(1),
    year_opened INT,  
    is_favorite INT,  
    purchase_id VARCHAR(7), 
    product_id VARCHAR(7), 
    visit_date DATE, 
    purchased_product_price_usd NUMERIC(6,2)
);

SET SESSION sql_mode = '';
SET GLOBAL local_infile=1;

LOAD DATA LOCAL INFILE 'data.csv'
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
FROM staging_data
WHERE customer_id IS NOT NULL;

-- ensure no duplicate store entries in staging_data before inserting (deduplicated)
CREATE TEMPORARY TABLE distinct_store_staging_data AS
SELECT DISTINCT store_id, store_location, year_opened
FROM staging_data;

-- Insert into store
INSERT INTO store (store_id, store_location, year_opened)
SELECT store_id, store_location, year_opened FROM distinct_store_staging_data;

DROP TEMPORARY TABLE distinct_store_staging_data;

-- Insert into product
INSERT INTO product (product_id, product_category)
SELECT DISTINCT
    product_id,
    product_category
FROM staging_data;

-- Insert into inventory
INSERT INTO inventory (product_id, store_id, store_location, 
qty, product_price_usd, product_cost_usd, competitor_price_usd)
SELECT DISTINCT
    product_id,
    store_id,
    store_location,
    qty,
    COALESCE(CAST(product_price_usd AS DECIMAL(8,2)), 0.00),
    COALESCE(CAST(product_cost_usd AS DECIMAL(6,2)), 0.00),
    COALESCE(CAST(competitor_price_usd AS DECIMAL(8,2)), NULL)
FROM staging_data;

-- Insert into popularity
INSERT INTO popularity (store_id, store_location, visit_date, foot_traffic)
SELECT DISTINCT
    store_id,
    store_location,
    visit_date,
    foot_traffic
FROM staging_data;

-- Insert into purchase 
INSERT INTO purchase (purchase_id, product_id, store_id, 
customer_id, payment_method, discount_percent, txn_date, store_location,
purchased_product_price_usd)
SELECT DISTINCT
    purchase_id,
    product_id,
    store_id,
    customer_id,
    payment_method,
    discount_percent,
    purchase_date,
    store_location,
    purchased_product_price_usd
FROM staging_data
WHERE purchase_id IS NOT NULL;

INSERT INTO customer_visits (customer_id, store_id, store_location, is_favorite)
SELECT DISTINCT
    customer_id,
    store_id,
    store_location,
    CASE WHEN is_favorite > 0 THEN 1 ELSE 0 END
FROM staging_data;

DROP TABLE staging_data;