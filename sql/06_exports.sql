-- Exports for Power BI. Run from the project root with psql.
-- \copy writes the files on the client side, into data/exports/.

\copy (SELECT * FROM orders_enriched WHERE in_delivery_population AND purchase_month BETWEEN DATE '2017-01-01' AND DATE '2018-08-01') TO 'data/exports/orders_window.csv' WITH (FORMAT csv, HEADER true)

\copy (SELECT purchase_month, COUNT(*) AS delivered_orders, COUNT(*) FILTER (WHERE is_late) AS late_orders FROM orders_enriched WHERE in_delivery_population GROUP BY purchase_month ORDER BY purchase_month) TO 'data/exports/monthly_late.csv' WITH (FORMAT csv, HEADER true)