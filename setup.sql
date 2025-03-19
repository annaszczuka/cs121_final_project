-- clean up old tables
-- must drop tables with foreign keys first 
-- due to referential integrity constraints
DROP TABLE IF EXISTS customer_visits;
DROP TABLE IF EXISTS purchase;
DROP TABLE IF EXISTS popularity;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS store;

-- represents customers uniquely identified by customer_id
-- requires all non-null values
CREATE TABLE customer (
    -- unique identifier for each customer
    customer_id        INT AUTO_INCREMENT, 
    -- age of customer at the time of transaction
    age                INT NOT NULL,
    -- gender of client, M/F/X (X for nonbinary)
    gender             CHAR(1) NOT NULL,
    -- annual income of client, capped at 1 mil, in usd
    annual_income_usd  NUMERIC(8, 2) NOT NULL,
    -- first and last name of client 
    full_name          VARCHAR(255) NOT NULL, 
    PRIMARY KEY(customer_id),
    CHECK(gender IN ('M', 'F', 'X')), 
    CHECK(age >= 0 AND age < 100)
);

-- represents stores uniquely identified by store_id and store_location
-- requires all non-null values
CREATE TABLE store (
    -- unique identifier for each store with store_location
    store_id         INT,
    -- city store is located in, all stores are located in U.S.A
    store_location   VARCHAR(255),
    -- compamy name of the store chain
    store_chain_name VARCHAR(50),
    -- year the specific store had grand opening
    year_opened      YEAR NOT NULL, 
    PRIMARY KEY(store_id, store_location)
);

-- represents products uniquely identified by product_id and store_id
-- requires all non-null values
CREATE TABLE product (
    -- unique identifier for each product with store_id 
    product_id          CHAR(7),
    -- category of item involved in transaction
    -- e.g Health & Beauty, Electronics, Groceries, Books 
    product_category    VARCHAR(255) NOT NULL,
    PRIMARY KEY(product_id)
);

-- represents inventory at a store, 
-- uniquely identified by store_id, store_location, and product_id
CREATE TABLE inventory (
    product_id             CHAR(7),
    store_id               INT,
    store_location         VARCHAR(255),
    -- number of units of such product at said store available for sale
    qty                    INT NOT NULL,
    -- price product retails for, capped at 1 million, in usd
    product_price_usd      NUMERIC(8, 2) NOT NULL,
    -- cost to produce product, capped at 10k, in usd
    product_cost_usd       NUMERIC(6, 2) NOT NULL,
    -- price product retails for at different store, capped at 1 mil, in usd
    -- it is the store’s most common competitor 
    -- if that competitor exists in the current location, else this can be null
    competitor_price_usd   NUMERIC(8, 2),
    PRIMARY KEY(product_id, store_id, store_location),
    FOREIGN KEY(store_id, store_location) 
    REFERENCES store(store_id, store_location)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(product_id) REFERENCES product(product_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- represents store popularity tracking foot traffic
-- requires all non-null values
-- uniquely identified by store_id, store_location, and visit_date
CREATE TABLE popularity (
    -- (store_id, store_location, visit_date) 
    -- is unique identifer for popoularity
    store_id         INT,
    store_location   VARCHAR(255),
    visit_date       DATE NOT NULL,
    -- number of customers who have visited the store on visit_date
    foot_traffic     INT NOT NULL,
    PRIMARY KEY(store_id, store_location, visit_date),
    FOREIGN KEY(store_id, store_location) 
    REFERENCES store(store_id, store_location)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- represents individual purchases uniquely identified by purchase_id
-- requires all non-null values
-- uniquely identified by purchase_id, product_id, store_id, customer_id
CREATE TABLE purchase (
    -- (purchase_id, product_id, store_id, customer_id)
    -- is unique identifier for purchase 
    purchase_id       CHAR(7),
    product_id        CHAR(7),
    store_id          INT,
    customer_id       INT AUTO_INCREMENT,
    -- method of payment
    -- e.g. debit, credit, cash, mobile payment
    payment_method    VARCHAR(255) NOT NULL,
    -- percentage of product price that is discounted
    -- there can not be discount percent by 0.5%
    discount_percent  INT NOT NULL,
    -- date a transaction has occurred 
    txn_date          DATE NOT NULL,
    -- city store is located in, all stores are located in U.S.A
    store_location   VARCHAR(255),
    -- price of the purchased product before the discount
    purchased_product_price_usd NUMERIC(6, 2) NOT NULL, 
    PRIMARY KEY(purchase_id), 
    FOREIGN KEY(product_id) 
    REFERENCES product(product_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(store_id, store_location) 
    REFERENCES store(store_id, store_location)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(customer_id) 
    REFERENCES customer(customer_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- tracks individual customer visits to stores and favorites
CREATE TABLE customer_visits (
    -- (customer_id, store_id, store_location)
    -- is unique identifier for customer_visits
    customer_id     INT AUTO_INCREMENT,
    store_id        INT,
    store_location  VARCHAR(255),
    -- indicates if a particular store is a customer's favorite store 
    is_favorite     BOOLEAN NOT NULL,
    PRIMARY KEY(customer_id, store_id, store_location),
    FOREIGN KEY(store_id, store_location) 
    REFERENCES store(store_id, store_location)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(customer_id) REFERENCES customer(customer_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- create index on the product_price_usd of inventory table
CREATE INDEX idx_store_inventory_price ON inventory(product_price_usd);


SET FOREIGN_KEY_CHECKS = 1;
