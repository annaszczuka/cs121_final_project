-- Admin queries:

-- This query requires user input to run, so we choose an arbitrary id
-- This query retrieves the store chain name for each store_id
SELECT store_id_to_store_chain(1);

-- This query selects the maximum value of purchase_id in all purchases. 
-- This is helpful for the user to know what the next available purchase_id is
SELECT MAX(CAST(purchase_id AS UNSIGNED)) FROM purchase;

-- This query selects the maximum value of customer_id in all customers. 
-- This is helpful to get a range of possible customer_ids to use
SELECT MAX(customer_id) FROM purchase;

-- Retrieves product id, store id, and store location from a previously made
-- purchase 
SELECT product_id, store_id, store_location FROM purchase;

-- The following queries all require user input.
-- These ensure that the info entered by the user exist in 
-- the database
SELECT COUNT(*) FROM customer WHERE customer_id = 1;
SELECT COUNT(*) FROM store WHERE store_id = 1;
SELECT COUNT(*) FROM purchase WHERE purchase_id = 1;
SELECT COUNT(*) FROM store WHERE store_id = 13 AND store_location = "San Jose";
SELECT COUNT(*)
FROM inventory i
WHERE i.product_id = 1 AND i.store_id = 13 AND i.store_location = "San Jose";

-- This query requires user input. Essentially adds a new purchase
-- based on information provided by the user. 
-- This query will fail if the user provides a purchase id that is already 
-- taken, and the purchase id availability depends on whether the user 
-- has made new purchases in the application, so we comment it out here. 
-- INSERT INTO purchase 
--             (purchase_id, product_id, store_id, customer_id, store_location, 
--              payment_method, discount_percent, txn_date, 
--              purchased_product_price_usd)
--             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);

-- For each store location, we get information such as revenue, 
-- total transactions, and average foot traffic per store.
WITH purchase_summary AS (
    SELECT store_id,
        store_location,
        COUNT(*) AS total_transactions,
        SUM(purchased_product_price_usd) AS total_revenue
    FROM purchase
    GROUP BY store_id, store_location
),
popularity_summary AS (
    SELECT store_id,
        store_location,
        AVG(foot_traffic) AS avg_foot_traffic
    FROM popularity
    GROUP BY store_id, store_location
)
SELECT s.store_id, 
    s.store_location,
    COALESCE(p.total_transactions, 0) AS total_transactions,
    COALESCE(p.total_revenue, 0)      AS total_revenue,
    COALESCE(pop.avg_foot_traffic, 0) AS avg_foot_traffic
FROM store s
LEFT JOIN purchase_summary p 
    ON s.store_id = p.store_id 
    AND s.store_location = p.store_location
LEFT JOIN popularity_summary pop
    ON s.store_id = pop.store_id
    AND s.store_location = pop.store_location;

-- Uses a materialized view. Allows the reader to see the view
SELECT store_id, total_sales, 
        num_purchases, 
        avg_discount, 
        min_price, max_price
FROM mv_store_sales_stats;

-- Client queries: 

-- Gets usage counts of each payment method at each store
SELECT p.store_id, 
    p.store_location, 
    p.payment_method, 
    COUNT(*) AS usage_count
FROM purchase p
GROUP BY p.store_id, p.store_location, p.payment_method
ORDER BY p.store_id, p.store_location, usage_count DESC;

-- Retrieves total number of purchases made by age group 
SELECT
    age_range,
    SUM(total_sales) AS total_sales
FROM sales_summary_by_age_group
GROUP BY age_range
ORDER BY total_sales DESC;

-- Equivalent Query A*
-- Retrieves total number of purchases and average purchase price by gender
-- Equivalent to RA expression 2) in Part G.
SELECT c.gender, 
        COUNT(p.purchase_id) AS total_purchases,
        ROUND(AVG(p.purchased_product_price_usd), 2) AS avg_spent_per_transaction
FROM customer c
JOIN purchase p 
    ON c.customer_id = p.customer_id
GROUP BY c.gender;

-- retail statistics by store, including total transactions, total revenue, 
-- and average foot traffic
WITH purchase_summary AS (
    SELECT store_id,
        store_location,
        COUNT(*) AS total_transactions,
        SUM(purchased_product_price_usd) AS total_revenue
    FROM purchase
    GROUP BY store_id, store_location
),
popularity_summary AS (
    SELECT store_id,
        store_location,
        AVG(foot_traffic) AS avg_foot_traffic
    FROM popularity
    GROUP BY store_id, store_location
)
SELECT s.store_id, 
    s.store_location,
    COALESCE(p.total_transactions, 0) AS total_transactions,
    COALESCE(p.total_revenue, 0)      AS total_revenue,
    COALESCE(pop.avg_foot_traffic, 0) AS avg_foot_traffic
FROM store s
LEFT JOIN purchase_summary p 
    ON s.store_id = p.store_id 
    AND s.store_location = p.store_location
LEFT JOIN popularity_summary pop
    ON s.store_id = pop.store_id
    AND s.store_location = pop.store_location;


-- Retrieves total number of purchases for each gender for a specific 
-- product category. In the application, the client would specify the 
-- product category through input, but for running purposes here we set 
-- an arbitrary product category to be Health & Beauty. 
SELECT c.gender, 
            COUNT(*) AS purchase_count
        FROM customer c
        JOIN purchase p 
            ON c.customer_id = p.customer_id
        JOIN product pr 
            ON p.product_id = pr.product_id
        WHERE pr.product_category = 'Health & Beauty'
        GROUP BY c.gender;

-- Retrieves the youngest and oldest buyer age group for each product category
SELECT product_category, 
        MIN(age_range) AS youngest_buyers,
        MAX(age_range) AS oldest_buyers
FROM sales_summary_by_age_group
GROUP BY product_category;

-- Retrives the total amount spent per age group on products classified as 
-- necessities versus products not classified as necessities
SELECT age_range, 
        ROUND(CAST(SUM(CASE WHEN 
            product_category IN ('Groceries', 'Health & Beauty') 
            THEN total_sales ELSE 0 END) AS DECIMAL(10,2)), 2)
        AS necessities,
        ROUND(CAST(SUM(CASE WHEN 
            product_category NOT IN ('Groceries', 'Health & Beauty') 
            THEN total_sales ELSE 0 END) AS DECIMAL(10,2)), 2)
        AS non_necessities
FROM sales_summary_by_age_group
GROUP BY age_range
ORDER BY age_range;

-- For each age group, this query retrieves the most popular store chain and 
-- number of customer visits 
SELECT 
    age_group, 
    store_chain, 
    total_purchases
FROM (
    SELECT 
        CASE 
            WHEN c.age BETWEEN 18 AND 25 THEN '18-25'
            WHEN c.age BETWEEN 26 AND 35 THEN '26-35'
            WHEN c.age BETWEEN 36 AND 50 THEN '36-50'
            WHEN c.age BETWEEN 40 AND 49 THEN '40-49'
            WHEN c.age BETWEEN 50 AND 59 THEN '50-59'
            WHEN c.age BETWEEN 60 AND 69 THEN '60-69'
            WHEN c.age BETWEEN 70 AND 79 THEN '70-79'
            WHEN c.age BETWEEN 80 AND 89 THEN '80-89'
            ELSE '90+'
        END AS age_group,
        s.store_chain_name AS store_chain,
        COUNT(*) AS total_purchases
    FROM customer_visits cv
    JOIN customer c ON cv.customer_id = c.customer_id
    JOIN store s ON cv.store_id = s.store_id
    GROUP BY age_group, s.store_chain_name, s.store_id
) ranked_stores
WHERE total_purchases = (
    SELECT MAX(total_purchases)
    FROM (
        SELECT 
            CASE 
                WHEN c.age BETWEEN 18 AND 25 THEN '18-25'
                WHEN c.age BETWEEN 26 AND 35 THEN '26-35'
                WHEN c.age BETWEEN 36 AND 50 THEN '36-50'
                WHEN c.age BETWEEN 40 AND 49 THEN '40-49'
                WHEN c.age BETWEEN 50 AND 59 THEN '50-59'
                WHEN c.age BETWEEN 60 AND 69 THEN '60-69'
                WHEN c.age BETWEEN 70 AND 79 THEN '70-79'
                WHEN c.age BETWEEN 80 AND 89 THEN '80-89'
                ELSE '90+'
            END AS age_group,
            s.store_chain_name,
            COUNT(*) AS total_purchases
        FROM customer_visits cv
        JOIN customer c ON cv.customer_id = c.customer_id
        JOIN store s ON cv.store_id = s.store_id
        GROUP BY age_group, s.store_chain_name, s.store_id
    ) max_counts
    WHERE max_counts.age_group = ranked_stores.age_group
)
ORDER BY age_group;


-- Retrieves the 10 most expensive items stored in inventory at each 
-- store location 
SELECT 
    inventory.product_id, 
    store.store_chain_name,
    inventory.store_location, 
    inventory.product_price_usd
FROM inventory JOIN store 
ON inventory.store_id = store.store_id 
AND inventory.store_location = store.store_location
ORDER BY inventory.product_price_usd DESC
LIMIT 10;

-- Uses the materialized view and allows the user to see the view
SELECT store_id, total_sales, 
    num_purchases, 
    avg_discount, 
    min_price, max_price
FROM mv_store_sales_stats;


-- Equivalent Query B*
-- Calculates the profit for each store chain location using the amount of money the product was purchased for
-- for each purchased product at that store chain and location for each store, subtracted from the cost
-- it took to make the product. In short, we get the store locations and total profit for each store based on
-- all the products sold at the store. This query is equivalent to RA expression 4) in part G.
SELECT
    s.store_chain_name,
    i.store_location,
    SUM(p.purchased_product_price_usd - i.product_cost_usd) AS total_profit
FROM inventory i
JOIN purchase p
    ON i.product_id = p.product_id
    AND i.store_id = p.store_id
    AND i.store_location = p.store_location
JOIN store s
    ON i.store_id = s.store_id
    AND i.store_location = s.store_location
GROUP BY
    s.store_chain_name,
    i.store_location;


-- The following queries require user input. We could theoretically input 
-- arbitrary values, but this will result in users being created before 
-- the application runs, which is not necessary.
-- If want to test this, can test by running the application.  
-- CALL sp_add_user(%s, %s, %s, %s, %s, %s, %s, %s)
-- SELECT get_contact_email(%s)
-- SELECT authenticate(%s, %s) also requires user input

