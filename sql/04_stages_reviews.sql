-- Q4: Median and p90 days per stage (window population, as in Step 3.6)
-- Expected: approval->carrier 94,838 orders, median 1.84, p90 5.99;
--           carrier->customer 96,183, median 7.10, p90 18.91;
--           total delivery 96,203, median 10.21, p90 23.06.
SELECT 'approval_to_carrier' AS stage,
       COUNT(approval_to_carrier_days) AS orders,
       ROUND((percentile_cont(0.5) WITHIN GROUP (ORDER BY approval_to_carrier_days))::numeric, 2) AS median_days,
       ROUND((percentile_cont(0.9) WITHIN GROUP (ORDER BY approval_to_carrier_days))::numeric, 2) AS p90_days
FROM orders_enriched
WHERE in_delivery_population AND purchase_month BETWEEN DATE '2017-01-01' AND DATE '2018-08-01'
UNION ALL
SELECT 'carrier_to_customer', COUNT(carrier_to_customer_days),
       ROUND((percentile_cont(0.5) WITHIN GROUP (ORDER BY carrier_to_customer_days))::numeric, 2),
       ROUND((percentile_cont(0.9) WITHIN GROUP (ORDER BY carrier_to_customer_days))::numeric, 2)
FROM orders_enriched
WHERE in_delivery_population AND purchase_month BETWEEN DATE '2017-01-01' AND DATE '2018-08-01'
UNION ALL
SELECT 'total_delivery', COUNT(delivery_days),
       ROUND((percentile_cont(0.5) WITHIN GROUP (ORDER BY delivery_days))::numeric, 2),
       ROUND((percentile_cont(0.9) WITHIN GROUP (ORDER BY delivery_days))::numeric, 2)
FROM orders_enriched
WHERE in_delivery_population AND purchase_month BETWEEN DATE '2017-01-01' AND DATE '2018-08-01';

-- Q5: Review score, late vs on time (one review per order: latest answer timestamp)
-- Expected: 95,560 orders with a review. On time 89,182 / mean 4.29 / 1-star 6.60%;
--           late 6,378 / mean 2.27 / 1-star 53.76%.
WITH latest_review AS (
    SELECT order_id, review_score
    FROM (
        SELECT order_id, review_score,
               ROW_NUMBER() OVER (PARTITION BY order_id
                                  ORDER BY review_answer_timestamp DESC) AS rn
        FROM order_reviews
    ) r
    WHERE rn = 1                                     -- one row per order: no fan-out
)
SELECT oe.is_late,
       COUNT(*)                                             AS orders,
       ROUND(AVG(lr.review_score), 2)                       AS mean_score,
       ROUND(100.0 * AVG((lr.review_score = 1)::int), 2)    AS pct_1_star,
       ROUND(100.0 * AVG((lr.review_score = 5)::int), 2)    AS pct_5_star
FROM orders_enriched oe
JOIN latest_review lr ON lr.order_id = oe.order_id
WHERE oe.in_delivery_population
  AND oe.purchase_month BETWEEN DATE '2017-01-01' AND DATE '2018-08-01'
GROUP BY oe.is_late
ORDER BY oe.is_late;