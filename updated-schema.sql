/*
Changes and Justifications
	1.	Removed the transaction table since the schema now integrates purchases within purchase, and the discount logic is handled directly within that table.
	2.	Replaced transaction_id with purchase_id in purchase to ensure proper tracking of individual purchases.
	3.	Reworked the product table to have a separate inventory table that links products to store locations while keeping prices, costs, and competitor prices flexible across stores.
	4.	Reorganized store to use a composite primary key (store_id, store_location), allowing differentiation between locations of the same store chain.
	5.	Added proper foreign key relationships and cascading updates/deletes to maintain referential integrity.
*/

-- Clean up old tables
-- Must drop tables with foreign keys first due to referential integrity constraints
DROP TABLE IF EXISTS customer_visits;
DROP TABLE IF EXISTS purchase;
DROP TABLE IF EXISTS popularity;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS store;

-- Represents customers uniquely identified by customer_id
CREATE TABLE customer (
    customer_id         CHAR(7) PRIMARY KEY, 
    age                INT NOT NULL,
    gender             CHAR(1) NOT NULL CHECK (gender IN ('M', 'F', 'X')),
    annual_income_usd  NUMERIC(8, 2) NOT NULL,
    full_name          VARCHAR(255) NOT NULL
);

-- Represents stores uniquely identified by store_id and store_location
CREATE TABLE store (
    store_id         CHAR(7),
    store_location   VARCHAR(255),
    year_opened      YEAR NOT NULL, 
    PRIMARY KEY (store_id, store_location)
);

-- Represents products uniquely identified by product_id and store_id
CREATE TABLE product (
    product_id       CHAR(7),
    store_id         CHAR(7),
    product_category VARCHAR(255) NOT NULL,
    PRIMARY KEY (product_id, store_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- Represents inventory at a store, uniquely identified by store_id, store_location, and product_id
CREATE TABLE inventory (
    store_id               CHAR(7),
    store_location         VARCHAR(255),
    product_id             CHAR(7),
    qty                    INT NOT NULL,
    product_price_usd      NUMERIC(8, 2) NOT NULL,
    product_cost_usd       NUMERIC(6, 2) NOT NULL,
    competitor_price_usd   NUMERIC(8, 2),
    PRIMARY KEY (store_id, store_location, product_id),
    FOREIGN KEY (store_id, store_location) REFERENCES store(store_id, store_location)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- Represents store popularity tracking foot traffic by store and date
CREATE TABLE popularity (
    store_id         CHAR(7),
    store_location   VARCHAR(255),
    visit_date       DATE NOT NULL,
    foot_traffic     INT NOT NULL,
    PRIMARY KEY (store_id, store_location, visit_date),
    FOREIGN KEY (store_id, store_location) REFERENCES store(store_id, store_location)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- Represents individual purchases uniquely identified by purchase_id
CREATE TABLE purchase (
    purchase_id       CHAR(7) PRIMARY KEY,
    product_id        CHAR(7),
    store_id         CHAR(7),
    customer_id      CHAR(7),
    payment_method   VARCHAR(255) NOT NULL,
    discount_percent INT NOT NULL,
    txn_date        DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES store(store_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- Tracks individual customer visits to stores and favorites
CREATE TABLE customer_visits (
    store_id        CHAR(7),
    store_location  VARCHAR(255),
    customer_id     CHAR(7),
    is_favorite     BOOLEAN NOT NULL,
    PRIMARY KEY (store_id, store_location, customer_id),
    FOREIGN KEY (store_id, store_location) REFERENCES store(store_id, store_location)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);
