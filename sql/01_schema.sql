-- Schema for the raw Olist tables (PostgreSQL).
-- category_translation: 623 products have no match (610 null + 13 untranslated).
-- Zip prefixes are INTEGER to match the pandas load (leading zeros not kept).

DROP TABLE IF EXISTS order_reviews, order_payments, order_items, orders,
    geolocation, products, sellers, customers, category_translation CASCADE;

CREATE TABLE customers (
    customer_id               TEXT PRIMARY KEY,
    customer_unique_id        TEXT NOT NULL,
    customer_zip_code_prefix  INTEGER,
    customer_city             TEXT,
    customer_state            CHAR(2)
);

CREATE TABLE sellers (
    seller_id               TEXT PRIMARY KEY,
    seller_zip_code_prefix  INTEGER,
    seller_city             TEXT,
    seller_state            CHAR(2)
);

CREATE TABLE category_translation (
    product_category_name          TEXT PRIMARY KEY,
    product_category_name_english  TEXT NOT NULL
);

CREATE TABLE products (
    product_id                  TEXT PRIMARY KEY,
    product_category_name       TEXT,
    product_name_lenght         NUMERIC,   -- spelling kept from the source
    product_description_lenght  NUMERIC,
    product_photos_qty          NUMERIC,
    product_weight_g            NUMERIC,
    product_length_cm           NUMERIC,
    product_height_cm           NUMERIC,
    product_width_cm            NUMERIC
);

CREATE TABLE orders (
    order_id                       TEXT PRIMARY KEY,
    customer_id                    TEXT NOT NULL REFERENCES customers(customer_id),
    order_status                   TEXT NOT NULL,
    order_purchase_timestamp       TIMESTAMP,
    order_approved_at              TIMESTAMP,
    order_delivered_carrier_date   TIMESTAMP,
    order_delivered_customer_date  TIMESTAMP,
    order_estimated_delivery_date  TIMESTAMP
);

CREATE TABLE order_items (
    order_id             TEXT NOT NULL REFERENCES orders(order_id),
    order_item_id        INTEGER NOT NULL,
    product_id           TEXT NOT NULL REFERENCES products(product_id),
    seller_id            TEXT NOT NULL REFERENCES sellers(seller_id),
    shipping_limit_date  TIMESTAMP,
    price                NUMERIC(10,2),
    freight_value        NUMERIC(10,2),
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE order_payments (
    order_id              TEXT NOT NULL REFERENCES orders(order_id),
    payment_sequential    INTEGER NOT NULL,
    payment_type          TEXT,
    payment_installments  INTEGER,
    payment_value         NUMERIC(12,2),
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE TABLE order_reviews (
    review_id                TEXT NOT NULL,
    order_id                 TEXT NOT NULL REFERENCES orders(order_id),
    review_score             INTEGER,
    review_comment_title     TEXT,
    review_comment_message   TEXT,
    review_creation_date     TIMESTAMP,
    review_answer_timestamp  TIMESTAMP,
    PRIMARY KEY (review_id, order_id)   -- review_id alone is NOT unique
);

CREATE TABLE geolocation (
    geolocation_zip_code_prefix  INTEGER,
    geolocation_lat              DOUBLE PRECISION,
    geolocation_lng              DOUBLE PRECISION,
    geolocation_city             TEXT,
    geolocation_state            CHAR(2)
);