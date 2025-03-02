-- clean up old tables
-- must drop tables with foreign keys first 
-- due to referential integrity constraints
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS store;
DROP TABLE IF EXISTS transaction;

-- Represents commerce transactions uniquely identified by transaction_id
-- Requires all non-null values
CREATE TABLE transaction (
    -- unique identifier for each transaction
    transaction_id     CHAR(7), 
    -- method of payment
    -- e.g. debit, credit, cash, mobile payment
    payment_method     VARCHAR(255) NOT NULL,
    -- boolean indicator of if discount was used
    discount_applied   BOOLEAN NOT NULL, 
    -- percentage of product price that is discounted
    discount_percent   INT NOT NULL, 
    PRIMARY KEY (transaction_id)
);

-- Represents stores uniquely identified by store_id
-- Requires all non-null values
CREATE TABLE store (
    -- unique identifier for each store 
    store_id         CHAR(7), 
    -- city store is located in, all stores are located in U.S.A
    store_location   VARCHAR(255) NOT NULL,
    -- number of customers who have visited the store 
    -- on day of purchase of transaction
    foot_traffic     INT NOT NULL,      
    PRIMARY KEY (store_id)
);

-- Represents products uniquely identified by transaction_id
-- Requires all non-null values
CREATE TABLE product (
    -- unique identifier for each transaction
    transaction_id         CHAR(7), 
    -- category of item involved in transaction
    -- e.g Health & Beauty, Electronics, Groceries, Books 
    product_category       VARCHAR(255) NOT NULL,
    -- price product retails for, capped at 1 million, in usd
    product_price_usd      NUMERIC(8, 2) NOT NULL, 
    -- cost to produce product, capped at 1k, in usd
    product_cost_usd       NUMERIC(5, 2) NOT NULL, 
    -- money made from selling such product, capped at 1 mil, in usd
    profit_usd             NUMERIC(8, 2) NOT NULL,
    -- price product retails for at different store, capped at 1 mil, in usd
    competitor_price_usd   NUMERIC(8, 2) NOT NULL,
    -- number of units of such product at said store
    inventory_level        INT NOT NULL, 
    --  uniquely defines store
    store_id               CHAR(7) NOT NULL, 
    PRIMARY KEY (transaction_id),
    FOREIGN KEY (transaction_id) REFERENCES transaction(transaction_id)
     -- cascaded update & delete on transaction_id
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES store(store_id)
     -- cascaded update & delete on store_id
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- Represents customers uniquely identified by (transaction_id, customer_id)
-- Requires all non-null values
CREATE TABLE customer (
    -- unique identifier for each transaction
    transaction_id         CHAR(7), 
    -- unique identifier for each customer 
    customer_id            CHAR(7), 
    -- age of customer at the time of transaction
    age                    INT NOT NULL,
    -- gender of client, M/F/X (X for nonbinary)
    gender                 CHAR(1) NOT NULL, 
    -- annual income of client, capped at 1 mil, in usd
    annual_income_usd      NUMERIC(8, 2) NOT NULL,
    -- first and last name of client 
    full_name              VARCHAR(255) NOT NULL, 
    PRIMARY KEY (transaction_id, customer_id),
    FOREIGN KEY (transaction_id) REFERENCES transaction(transaction_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);
