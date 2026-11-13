# Power BI Dashboard Guide

Population for all pages: delivered orders with a delivery date, purchased 2017-01 to 2018-08
(96,203 orders, 6,531 late, 6.79%). Late = delivered on a later calendar date than the estimate.
Data came from PostgreSQL exports (sql/06_exports.sql, sql/07_exports_bi.sql). Key totals match
across pandas, SQL and Power BI.

| Page | Source | Content | Verified against |
|---|---|---|---|
| 1 Overview | orders_window.csv | Cards (orders, late, late rate, median days), monthly volume and late rate |
| 2 Geography | orders_window.csv | State table and late-rate bar chart (24 states with 100+ orders) |
| 3 Stages and reviews | orders_reviews.csv | Review score and stage medians, on time vs late (95,560 reviewed orders) |
| 4 Sellers | seller_orders.csv | Raw late rate beside the late rate outside the 4 spike months (30+ orders) |
| 5 Categories | category_summary.csv | Revenue, share and freight % by category |

Caveats
- Review links are associations, not proof of cause.
- Seller rates are small-sample and not adjusted for destination mix.
- The Sellers table total covers sellers with 30+ orders only.
- Category revenue is item price only.
- Medians use Power BI MEDIAN and match pandas and PostgreSQL to two decimals.