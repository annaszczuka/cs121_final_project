-- Get all customer's general retails
SELECT * FROM customer;

-- Get the total number of stores the database has
SELECT COUNT(*) AS total_stores FROM store;

-- Get the average age of all customers
SELECT AVG(age) as avg_age FROM customer;

-- Determine the most common payment method across all purchases
SELECT payment_method, COUNT(*) AS usg_count
FROM purchase
GROUP BY payment_method
ORDER BY usg_count DESC LIMIT 1;

-- Get the total revenue of each store by adding the product prices sold and considering discounts
-- We are assuming that the price never changes in this ideal model of the world.
SELECT
    s.store_id,
    s.store_location,
    SUM(p.purchased_product_price_usd * ((1 - (p.discount_percent / 100.0)))) AS total_revenue
FROM purchase p
JOIN store s ON p.store_id = s.store_id
GROUP BY s.store_id, s.store_location
ORDER BY total_revenue DESC;

