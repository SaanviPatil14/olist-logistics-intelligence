-- Q1: Late rate by customer state (window population, as in Step 3.3)
-- Expected: SP 40,399 orders / 1,817 late; RJ 12,310 / 1,495; total 96,203 / 6,531.
SELECT customer_state,
       COUNT(*)                          AS orders,
       COUNT(*) FILTER (WHERE is_late)   AS late_orders,
       ROUND(100.0 * COUNT(*) FILTER (WHERE is_late) / COUNT(*), 2) AS late_rate_pct,
       ROUND(100.0 * COUNT(*) FILTER (WHERE is_late)
             / SUM(COUNT(*) FILTER (WHERE is_late)) OVER (), 1)     AS share_of_late_pct
FROM orders_enriched
WHERE in_delivery_population
  AND purchase_month BETWEEN DATE '2017-01-01' AND DATE '2018-08-01'
GROUP BY customer_state
ORDER BY late_rate_pct DESC;

-- Q2: Same-state vs cross-state (single-seller-state orders, as in Step 3.4)
-- Expected: same state 34,489 orders (4.53% late); cross state 61,207 (8.11%).
WITH order_origin AS (
    SELECT oi.order_id,
           MIN(s.seller_state) AS seller_state
    FROM order_items oi
    JOIN sellers s ON s.seller_id = oi.seller_id
    GROUP BY oi.order_id
    HAVING COUNT(DISTINCT s.seller_state) = 1      -- one origin state only
)
SELECT (oe.customer_state = oo.seller_state)  AS same_state,
       COUNT(*)                               AS orders,
       COUNT(*) FILTER (WHERE oe.is_late)     AS late_orders,
       ROUND(100.0 * COUNT(*) FILTER (WHERE oe.is_late) / COUNT(*), 2) AS late_rate_pct
FROM orders_enriched oe
JOIN order_origin oo ON oo.order_id = oe.order_id   -- one row per order: no fan-out
WHERE oe.in_delivery_population
  AND oe.purchase_month BETWEEN DATE '2017-01-01' AND DATE '2018-08-01'
GROUP BY 1
ORDER BY 1;

-- Q3: Seller late rate, single-seller orders, 30+ orders, with a rank (Step 3.5)
-- Expected: 614 sellers with 30+ orders; top row ad781527... 33 orders, 12 late, 36.36%.
WITH single_seller AS (
    SELECT order_id, MIN(seller_id) AS seller_id
    FROM order_items
    GROUP BY order_id
    HAVING COUNT(DISTINCT seller_id) = 1
),
seller_stats AS (
    SELECT ss.seller_id,
           COUNT(*)                        AS orders,
           COUNT(*) FILTER (WHERE oe.is_late) AS late_orders
    FROM orders_enriched oe
    JOIN single_seller ss ON ss.order_id = oe.order_id
    WHERE oe.in_delivery_population
      AND oe.purchase_month BETWEEN DATE '2017-01-01' AND DATE '2018-08-01'
    GROUP BY ss.seller_id
)
SELECT seller_id, orders, late_orders,
       ROUND(100.0 * late_orders / orders, 2)                       AS late_rate_pct,
       RANK() OVER (ORDER BY 1.0 * late_orders / orders DESC)       AS late_rank
FROM seller_stats
WHERE orders >= 30
ORDER BY late_rank
LIMIT 10;