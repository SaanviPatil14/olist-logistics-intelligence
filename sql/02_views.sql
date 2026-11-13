-- One row per order, with the Phase 2 rules rebuilt in SQL.
-- The join to customers is many-to-one on a primary key, so rows cannot multiply.
CREATE OR REPLACE VIEW orders_enriched AS
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    DATE_TRUNC('month', o.order_purchase_timestamp)::date AS purchase_month,

    -- Flags for illogical stage order. In SQL a comparison with NULL is NULL,
    -- so COALESCE makes it FALSE, matching the pandas flags.
    COALESCE(o.order_delivered_carrier_date < o.order_approved_at, FALSE)
        AS flag_carrier_before_approval,
    COALESCE(o.order_delivered_customer_date < o.order_delivered_carrier_date, FALSE)
        AS flag_delivered_before_carrier,

    -- Durations in days (NULL if either timestamp is missing).
    EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400.0
        AS delivery_days,
    EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_estimated_delivery_date)) / 86400.0
        AS delay_days,

    -- Stage durations, set to NULL only on the flagged rows (Phase 2 rule).
    CASE WHEN o.order_delivered_carrier_date < o.order_approved_at THEN NULL
         ELSE EXTRACT(EPOCH FROM (o.order_delivered_carrier_date - o.order_approved_at)) / 86400.0
    END AS approval_to_carrier_days,
    CASE WHEN o.order_delivered_customer_date < o.order_delivered_carrier_date THEN NULL
         ELSE EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_delivered_carrier_date)) / 86400.0
    END AS carrier_to_customer_days,

    -- Late label, calendar-day rule: delivery DATE after estimated DATE.
    -- NULL (unknown) when there is no delivery date.
    CASE WHEN o.order_delivered_customer_date IS NULL THEN NULL
         ELSE o.order_delivered_customer_date::date > o.order_estimated_delivery_date::date
    END AS is_late,

    -- Sensitivity rule: delivered after midnight of the estimated day.
    CASE WHEN o.order_delivered_customer_date IS NULL THEN NULL
         ELSE o.order_delivered_customer_date > o.order_estimated_delivery_date
    END AS is_late_timestamp_rule,

    -- Delivery population: delivered AND a delivery date exists.
    (o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL)
        AS in_delivery_population
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id;