# SQL Analysis Summary

Database: PostgreSQL 16 (Codespace). Rebuild with `python src/build_db.py`, which creates
the tables from sql/01_schema.sql, loads the raw CSVs, builds the view in sql/02_views.sql,
and asserts the results against the Phase 1-3 pandas numbers.

| File | Content | Reconciled with |
|---|---|---|
| sql/01_schema.sql | 9 tables, primary keys, foreign keys | Phase 1 key checks |
| sql/02_views.sql | orders_enriched: flags, durations, calendar-day is_late, population | Phase 2 (96,470 population, 6,534 late) |
| sql/03_analysis.sql | State, same-state vs cross-state, top sellers (CTE, RANK, FILTER) |
| sql/04_stages_reviews.sql | Stage medians/p90 (percentile_cont), review score by lateness (ROW_NUMBER) |
| sql/05_category_freight.sql | Revenue and freight by category | Step 3.7 |
| sql/06_exports.sql | CSV exports for Power BI | row counts |

Join safety: items are aggregated to one row per order (CTEs with HAVING COUNT(DISTINCT))
before joining to orders; reviews are reduced with ROW_NUMBER; category_translation joins
on its primary key.

Not done: weight analysis in SQL, per-seller spike-month check, PostgreSQL index tuning.
PostgreSQL features used: percentile_cont, FILTER, window functions, DATE_TRUNC.