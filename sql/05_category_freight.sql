-- Q6: Revenue and freight by category (items in window-population orders, Step 3.7)
-- Expected: 109,872 items in total; price 13,179,777.95; freight 2,191,963.14;
--           health_beauty revenue share 9.3%, furniture_decor freight 23.7% of price.
-- Category: official translation; 2 untranslated categories get manual names; NULL -> 'unknown'.
WITH items_pop AS (
    SELECT oi.order_id, oi.price, oi.freight_value, p.product_category_name
    FROM order_items oi
    JOIN orders_enriched oe ON oe.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE oe.in_delivery_population
      AND oe.purchase_month BETWEEN DATE '2017-01-01' AND DATE '2018-08-01'
),
named AS (
    SELECT ip.*,
           CASE
               WHEN ip.product_category_name IS NULL THEN 'unknown'
               WHEN ip.product_category_name = 'pc_gamer' THEN 'pc_gamer'
               WHEN ip.product_category_name = 'portateis_cozinha_e_preparadores_de_alimentos'
                    THEN 'portable_kitchen_food_preparers'
               ELSE COALESCE(ct.product_category_name_english, 'unknown')
           END AS category_english
    FROM items_pop ip
    LEFT JOIN category_translation ct ON ct.product_category_name = ip.product_category_name
)
SELECT category_english,
       COUNT(*)                                             AS items,
       ROUND(SUM(price), 2)                                 AS revenue,
       ROUND(SUM(freight_value), 2)                         AS freight,
       ROUND(100.0 * SUM(freight_value) / SUM(price), 1)    AS freight_pct_of_price,
       ROUND(100.0 * SUM(price) / SUM(SUM(price)) OVER (), 1) AS share_of_revenue_pct
FROM named
GROUP BY category_english
ORDER BY revenue DESC;