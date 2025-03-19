-- drop existing functions, procedures, and triggers
-- setup passwords needs to be run before this
DROP FUNCTION IF EXISTS get_contact_email;
DROP FUNCTION IF EXISTS get_sale_price; 
DROP FUNCTION IF EXISTS store_count; 
DROP FUNCTION IF EXISTS store_score; 
DROP TABLE IF EXISTS mv_store_sales_stats;
DROP PROCEDURE IF EXISTS sp_store_stat_new_sale;
DROP TRIGGER trg_store_sale_insert; 
DROP PROCEDURE IF EXISTS update_inventory;

-- Returns a VARCHAR email address for an administrator and a client 
-- If the user is an administrator, it adds a fixed domain @retail_stats.com 
-- to the username
-- If the user is a client, returns users contact email 
DELIMITER !
CREATE FUNCTION get_contact_email(
    -- input: user's username 
    username VARCHAR(30)
    -- input: flag whether user is admin or client
    -- is_admin TINYINT
) RETURNS VARCHAR(254) DETERMINISTIC -- email adddress can't exceed 254 char
BEGIN
    -- store resulting email 
    DECLARE user_email VARCHAR(254);
    SET user_email = CONCAT(username, '@retail_stats.com');
    -- IF is_admin = 1 THEN
    --     -- in case of admin, append fixed domain to username to 
    --     -- get employee email 
    --     SET user_email = CONCAT(username, '@retail_stats.com');
    -- ELSE
    --     -- in case of client, query email
    --     SELECT contact_email INTO user_email
    --     FROM client 
    --     WHERE client.username = username;
    -- END IF;

    RETURN user_email;
END !

DELIMITER ;

-- test FUNCTION get_contact_email for an admin user
-- expected output: jwoodwell@retail_stats.com
SELECT get_contact_email('jwoodwell') AS email;

-- test FUNCTION get_contact_email for a client user
-- expected output: cbrown@gmail.com
SELECT get_contact_email('cbrown') AS email;


-- Calculates the numbers of stores that a store chain (defined by store_id)
-- has open 
-- Returns INT 
DELIMITER ! 
CREATE FUNCTION store_count(
    -- input: store chain id (e.g id corresponding to Target)
    store_id INT 
) RETURNS INT DETERMINISTIC
BEGIN
    -- store resulting store chain count
    DECLARE store_count INT; 
    -- count number of opened stores 
    SELECT COUNT(*) INTO store_count FROM store 
    WHERE store.store_id = store_id;
    RETURN store_count; 
END !
DELIMITER ; 

-- test FUNCTION store_count test case with store chain id 25 
-- expected output: 5
SELECT store_count(25) AS store_count;

-- Calculates the sale price of a retailed object after applying 
-- the discount percentage to the original price for a specific
-- product for a specific purchase for a specifc customer at a specific store 
-- Returns type DECIMAL(10,2)
-- Upperbound on sale price is $99,999,999.99
DELIMITER ! 
CREATE FUNCTION get_sale_price(
    purchase_id CHAR(7),
    product_id  CHAR(7),
    store_id    INT, 
    customer_id INT
) RETURNS DECIMAL(10,2) DETERMINISTIC
BEGIN
    -- store the resulting sale price
    DECLARE sale_price DECIMAL(10,2);

    -- apply discount to the orignal price to calculate sale price
    SELECT 
    purchase.purchased_product_price_usd 
    * (1 - (purchase.discount_percent / 100.0))
    INTO sale_price FROM purchase
    WHERE purchase.purchase_id = purchase_id
    AND purchase.product_id = product_id
    AND purchase.store_id = store_id
    AND purchase.customer_id = customer_id;

    RETURN sale_price;
END !
DELIMITER ; 

-- test FUNCTION get_sale_price in case where discount is present
-- expected output: 131.61 
SELECT get_sale_price(10, 227, 39, 625) AS sale_price;
-- test FUNCTION get_sale_price in case where discount is not present (or 0)
-- expected output: 205.49
SELECT get_sale_price(1, 88, 47, 693) AS sale_price;


-- view summarizes the total sales 
-- grouped by product category and customer age range.
CREATE VIEW sales_summary_by_age_group AS
SELECT
    -- product category
    product.product_category,
    -- sort customer age into specific group
    CASE
    WHEN customer.age BETWEEN 0 AND 9 THEN '0-9'
    WHEN customer.age BETWEEN 10 AND 20 THEN '10-20'
    WHEN customer.age BETWEEN 20 AND 29 THEN '20-29'
    WHEN customer.age BETWEEN 30 AND 39 THEN '30-39'
    WHEN customer.age BETWEEN 40 AND 49 THEN '40-49'
    WHEN customer.age BETWEEN 50 AND 59 THEN '50-59'
    WHEN customer.age BETWEEN 60 AND 69 THEN '60-69'
    WHEN customer.age BETWEEN 70 AND 79 THEN '70-79'
    WHEN customer.age BETWEEN 80 AND 89 THEN '80-89'
    ELSE '90+'
    END AS age_range,
    
    -- Calculate total sales by summing the sale price for each purchase
    SUM(
    get_sale_price
    (purchase.purchase_id, purchase.product_id, 
    purchase.store_id, purchase.customer_id)) AS total_sales
FROM purchase 
JOIN product ON purchase.product_id = product.product_id
JOIN customer ON purchase.customer_id = customer.customer_id
GROUP BY product.product_category, age_range
ORDER BY product.product_category, age_range;

-- Calculates a store score which examines foot_traffic in relation 
-- store sales. This score will helps determine how successful a store is 
-- in relation to foot_traffic, transactions, and scores. 
-- Formula followed: 
-- store_score = w1 * transactions/foot_traffic + w2 * profit/transactions 
-- The first term is a conversion rate explaining how well a store transforms
-- visitors into customers. The second term is average profit per transaction 
-- which shows how valuable/lucrative a transaction was. 
-- RETURNS DOUBLE
DELIMITER !
CREATE FUNCTION store_score(store_id INT)
RETURNS DOUBLE
DETERMINISTIC
BEGIN
    -- store useful values for store score calculation
    DECLARE total_transactions INT;
    DECLARE total_foot_traffic INT;
    DECLARE total_profit DOUBLE DEFAULT 0;
    DECLARE w1 DOUBLE DEFAULT 0.5;
    DECLARE w2 DOUBLE DEFAULT 0.5;
    DECLARE score DOUBLE;

    -- count the total number of transactions that occurred at a store
    SELECT COUNT(purchase_id) INTO total_transactions
    FROM purchase WHERE purchase.store_id = store_id;

    -- calculate store popularity by summing store foot traffic
    SELECT SUM(foot_traffic) INTO total_foot_traffic
    FROM popularity WHERE popularity.store_id = store_id;

    -- find profit for a product by computing difference between the 
    -- actual sale price of the product and the amount the product cost 
    -- to the store 
    SELECT 
    SUM(get_sale_price(
        purchase.purchase_id, purchase.product_id, 
        purchase.store_id, purchase.customer_id) 
        - inventory.product_cost_usd) 
    INTO total_profit FROM purchase
    -- related to the cost of specific product 
    LEFT JOIN inventory
    ON purchase.product_id = inventory.product_id 
    AND purchase.store_id = inventory.store_id 
    AND purchase.store_location = inventory.store_location  
    WHERE purchase.store_id = store_id 
    AND purchase.store_location = inventory.store_location;  

    -- store score computation
    IF total_transactions = 0 THEN SET score = 0;
    ELSE
    SET score = w1 * (total_transactions / total_foot_traffic) 
    + w2 * (total_profit / total_transactions);

    END IF;

    RETURN score;
END !

DELIMITER ;

-- test FUNCTION store_score
-- Expect Output: small number since store profit is low 
SELECT store_score(33) AS store_evaluation;

-- create materialized view of store sale statistics
-- including statistics about the amount of transactions occuring at 
-- a store, the number of sales, the average discount, minimum product 
-- sale price (after discount is applied), and maximum product sale price
-- (after discount is applied)
CREATE TABLE mv_store_sales_stats (
    store_id        INT,
    total_sales     NUMERIC(15, 2) NOT NULL,
    num_purchases   INT NOT NULL,
    avg_discount    NUMERIC(5, 2) NOT NULL,
    min_price       NUMERIC(12, 2) NOT NULL,
    max_price       NUMERIC(12, 2) NOT NULL,
    PRIMARY KEY(store_id)
);

-- populate the materialized view 
INSERT INTO mv_store_sales_stats 
(store_id, total_sales, num_purchases, avg_discount, min_price, max_price)
-- use the get_sale_price function to apply discount to the original price
SELECT 
    store_id, 
    SUM(get_sale_price(purchase_id, product_id, store_id, customer_id)) 
    AS total_sales,
    COUNT(*) AS num_purchases,
    CAST(AVG(discount_percent) 
    AS DECIMAL(5,2)) AS avg_discount,
    MIN(get_sale_price(purchase_id, product_id, store_id, customer_id)) 
    AS min_price,
    MAX(get_sale_price(purchase_id, product_id, store_id, customer_id)) 
    AS max_price
FROM purchase
GROUP BY store_id;

-- A procedure to execute when inserting new purchase to the 
-- to the store stats materialized view (mv_store_sales_stats).
-- If a store chain is already in view, its average discount is 
-- recompted with the additional purchase, the number of 
-- purchases increases by 1, and the sales prices are 
-- adjusted accordingly
DELIMITER !
CREATE PROCEDURE sp_store_stat_new_sale(
    new_store_id    INT,
    -- price before discount
    new_price       NUMERIC(12, 2),
    new_discount    NUMERIC(5, 2)
)
BEGIN
    DECLARE actual_sale_price NUMERIC(12, 2);
    
    -- calculates actual sale price after applying the discount
    SET actual_sale_price = new_price * (1 - (new_discount / 100));

    -- if store chain not already in view; add row
    INSERT INTO mv_store_sales_stats 
    (store_id, total_sales, num_purchases, avg_discount, min_price, max_price)
    VALUES 
        (new_store_id, actual_sale_price, 1, new_discount, actual_sale_price, actual_sale_price)
     -- if store chain in view; update row accordingly
    ON DUPLICATE KEY UPDATE 
        avg_discount = CAST(((avg_discount * num_purchases + new_discount) / (num_purchases + 1)) AS DECIMAL(5,2)),
        num_purchases = num_purchases + 1,
        total_sales = total_sales + actual_sale_price,
        min_price = LEAST(min_price, actual_sale_price),
        max_price = GREATEST(max_price, actual_sale_price);
END !

DELIMITER ;

-- test PROCEDURE sp_store_stat_new_sale to see if store_chain 1 
-- sales statistics update accordingly
CALL sp_store_stat_new_sale(1, 5.00, 0.00);

-- A procedure to execute when updating the store inventory 
-- Inputs: specific product quantity being change and the quantity change
-- at a store at a specific location
DELIMITER !
CREATE PROCEDURE update_inventory(product_id INT, qty_change INT, 
store_id INT, store_location VARCHAR(255))
BEGIN
    DECLARE curr_qty INT;

    SELECT qty INTO curr_qty
    FROM inventory
    WHERE inventory.product_id = product_id
    AND inventory.store_id = store_id
    AND inventory.store_location = store_location;

    -- do not update inventory if inventory becomes negative
    IF (curr_qty + qty_change) < 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Cannot update inventory';
    ELSE
        -- update inventory table to reflect quantity change
        UPDATE inventory
        SET qty = curr_qty + qty_change
        WHERE inventory.product_id = product_id
        AND inventory.store_id = store_id
        AND inventory.store_location = store_location;
    END IF;
END !
DELIMITER ;

-- test procedure 
-- output should have a net gain of 5 in quanitity
CALL update_inventory(1, 20, 15, 'Philadelphia');
CALL update_inventory(1, -15, 15, 'Philadelphia');

-- Handles new rows added to purchase table, updates stats accordingly
-- in the materialized view and the inventory table
DELIMITER !
CREATE TRIGGER trg_store_sale_insert
AFTER INSERT ON purchase
FOR EACH ROW
BEGIN
    -- Example of calling helper procedure, 
    -- passing in the new row's information
    CALL sp_store_stat_new_sale(
    NEW.store_id,  
    -- original price before discount
    NEW.purchased_product_price_usd, 
    -- discount percent
    NEW.discount_percent
    );

    CALL update_inventory(
    NEW.product_id, -1, NEW.store_id, NEW.store_location 
    ); 
END !

DELIMITER ;

-- -- Insert data into tables to test trigger 
-- INSERT INTO store (store_id, store_location, year_opened)
-- VALUES (101, 'San Jose', 2015);
-- INSERT INTO product (product_id, product_category)
-- VALUES ('P12345', 'Health & Beauty');
-- INSERT INTO customer (age, gender, annual_income_usd, full_name)
-- VALUES (30, 'M', 50000.00, 'John Doe');
-- INSERT INTO inventory (product_id, store_id, store_location, qty, 
-- product_price_usd, product_cost_usd, competitor_price_usd)
-- VALUES ('P12345', 101, 'San Jose', 50, 25.00, 15.00, 22.00);
-- INSERT INTO popularity (store_id, store_location, visit_date, foot_traffic)
-- VALUES (101, 'San Jose', '2023-06-01', 200);
-- INSERT INTO purchase 
-- (purchase_id, product_id, store_id, customer_id, store_location, 
-- payment_method, discount_percent, txn_date, purchased_product_price_usd) 
-- VALUES 
-- ('P000123', 'P12345', 101, 1, 'San Jose', 'Credit Card', 20, 
-- '2023-06-01', 100.00);
-- INSERT INTO customer_visits (customer_id, store_id, store_location, is_favorite)
-- VALUES (1, 101, 'San Jose', 1);
