# PROJECT CONTEXT: E-commerce Operations & Logistics Intelligence

Last updated: 2026-11-10 (end of Phase 2)
Repo: https://github.com/SaanviPatil14/olist-logistics-intelligence
Latest commit when written: a8bb901 (the notebook 02_data_cleaning.ipynb may still be uncommitted)

## 1. Objective
Analyze the Olist Brazilian E-commerce dataset (~100k orders) to identify
operational inefficiencies, delivery bottlenecks, underperforming sellers,
and logistics optimization opportunities. Portfolio project targeting
Data Analyst / Business Analyst roles.

## 2. Tech Stack and Environment
- Python, Pandas, NumPy, Jupyter, SQL (PostgreSQL preferred, SQLite fallback),
  Power BI, Scikit-learn, XGBoost, Git/GitHub.
- Environment: GitHub Codespaces (Linux). Python in the Codespace venv is 3.14
  (seen in tracebacks). Exact package versions: requirements-lock.txt.
- Run commands from the project root with `source .venv/bin/activate`.
- Notebooks run from notebooks/, so they use `../data/...` relative paths.
- Power BI Desktop is a Windows app and may hit the same local Application
  Control block (to be tested in Phase 5; Power BI Service on the web is a fallback).

## 3. Working Rules
- One phase and one step at a time; no full-project dumps (exception: Phase 2
  was consolidated into src/clean_data.py after every rule was decided).
- Explain why each operation is needed.
- Readable, commented code; minimal libraries.
- Never fabricate data, results, or insights; every number comes from code.
- Always check for incorrect joins (fan-out) and data leakage.
- Relative paths only; reproducible code.
- Every file comes with how-to-run and how-to-verify instructions.
- Every chart must state which population it uses.

## 4. Phases
1. Dataset understanding & setup        [DONE]
2. Data cleaning & preprocessing        [DONE]
3. Exploratory Data Analysis            [IN PROGRESS, not started]
4. SQL business analysis                [ ]
5. Power BI dashboards                  [ ]
6. Late-delivery prediction (ML)        [ ]
7. Business recommendations & report    [ ]
8. GitHub documentation & portfolio     [ ]

## 5. Folder Structure
```
olist-logistics-intelligence/
├── data/raw/          # 9 original CSVs, never edited, not in Git
├── data/processed/    # outputs of src/clean_data.py, not in Git
├── notebooks/         # 01_data_understanding, 02_data_cleaning (03_eda next)
├── src/clean_data.py  # reproducible cleaning script
├── sql/  powerbi/  reports/figures/  models/  docs/
├── docs/data_dictionary.md
├── docs/phase2_cleaning_checklist.md
├── PROJECT_CONTEXT.md  README.md  requirements.txt  requirements-lock.txt  .gitignore
```
Rebuild processed data with: `python src/clean_data.py` (prints "All checks passed.").

## 6. Dataset (Kaggle: "Brazilian E-Commerce Public Dataset by Olist")

| Table | Rows (verified) | Grain | Primary key (verified) | Foreign keys |
|---|---|---|---|---|
| customers | 99,441 | one customer_id (one per order) | customer_id | none |
| orders | 99,441 | one order | order_id | customer_id |
| order_items | 112,650 | one item in an order | (order_id, order_item_id) | order_id, product_id, seller_id |
| order_payments | 103,886 | one payment part | (order_id, payment_sequential) | order_id |
| order_reviews | 99,224 | one review | (review_id, order_id); review_id alone NOT unique | order_id |
| products | 32,951 | one product | product_id | product_category_name |
| sellers | 3,095 | one seller | seller_id | none |
| geolocation | 1,000,163 | coordinate sample | none | joins by zip prefix (untested) |
| category_translation | 71 | one category | product_category_name | none |

FK integrity: 0 orphans everywhere except products -> category_translation (623, see 7.6).

## 7. Verified Findings

### 7.1 Keys, customers, reviews
- customer_id is per order: 99,441 customer_id vs 96,096 customer_unique_id.
  93,099 people ordered once; 2,997 ordered more than once. Count customers with customer_unique_id.
- review_id repeats: 1,603 rows share a review_id. 547 orders have 2-3 reviews
  (543 with 2, 4 with 3); 768 orders have no review.
- Of the 547 multi-review orders: scores differ in 202; creation dates tie in 155;
  answer timestamps never tie.

### 7.2 Fan-out (proof for the "aggregate before joining" rule)
- Naive join orders+items+payments: 118,434 rows, payment_value 20,470,726.66.
- True payments total: 16,008,872.12 (+27.9% inflation from the bad join).
- Pre-aggregated payments join: 99,441 rows, total 16,008,872.12.

### 7.3 Order status and missing values
- order_status: delivered 96,478 (97.0%), shipped 1,107, canceled 625,
  unavailable 609, invoiced 314, processing 301, created 5, approved 2.
- Nulls in orders: approved 160, carrier date 1,783, customer delivery 2,965.
- 775 orders have no items: 603 unavailable, 164 canceled, 5 created, 2 invoiced,
  1 shipped (anomaly). 1 order has no payment.
- 8 delivered orders have no customer delivery date.
- 6 canceled orders DO have a customer delivery date (anomaly, cause unknown).

### 7.4 Dates and delivery metrics
- Timestamps parse cleanly. Range: purchase 2016-09-04 to 2018-10-17;
  estimated delivery up to 2018-11-12. Monthly volume not yet examined.
- Date logic violations: purchase<approved 0; purchase<customer delivery 0;
  purchase<estimated 0; carrier pickup before approval 1,359; customer delivery
  before carrier pickup 23 (all 23 status delivered).
- Carrier-before-approval gaps: median 17.2 h, p75 26.0 h, max 4,109 h (~171 days);
  458 over 1 day, 14 over 7 days, 1 over 30 days.
- Delivery population: delivered AND delivery date present = 96,470 orders
  (2,971 excluded).
- Population metrics: delivery_days median 10.22, p95 29.27, p99 46.05, max 209.63;
  estimated_days median 23.23; delay_days median -11.95, p95 +3.82, max +188.98.
- All estimated delivery dates are at midnight.
- Late rate (population): 6.77% calendar-day rule (6,534 late) vs 8.11% timestamp
  rule (7,826). The rules differ on 1,292 orders.
- On reload of orders_clean.csv across all 96,476 orders with a delivery date,
  is_late shows 6,535 True; the population has 6,534 (one of the 6 canceled is late).

### 7.5 Items
- price: min 0.85, median 74.99, p99 890, max 6,735; no zero/negative values.
- freight_value: median 16.26, p99 84.52, max 409.68; 383 items with freight 0; none negative.
- Top prices are in plausible categories (housewares, computers, art, small appliances).
- shipping_limit_date minus purchase: min 2.00, median 6.01, p99 19.01 days;
  0 before purchase; 239 items over 30 days, 4 over 365 days (max 1,056 days;
  raw max date 2020-04-09). The 239 items are in 209 orders and 45 sellers;
  187 of those orders are delivered.

### 7.6 Products and categories
- 610 products have null category AND null name length, description length, photo count
  (same rows). 2 products lack weight/dimensions.
- 13 products have 2 categories missing from the translation table
  (portateis_cozinha_e_preparadores_de_alimentos: 10, pc_gamer: 3).
- Impact on items: null category 1,603 items (1.42%, price revenue 179,535.28, 1.32%);
  untranslated 24 items (0.02%, 5,514.48, 0.04%). Total 1,627 items (1.44%), ~1.36% of item revenue.
- category_english has 74 distinct values (71 + 2 manual + 'unknown').
- 4 products have weight 0 g (impossible), affecting 8 items. No zero dimensions.
  Weight median 700 g, p99 22,538 g, max 40,425 g.

### 7.7 Locations
- Customers: 27 states, all valid; 4,119 cities, no accent/case variants.
- Sellers: 23 states, all valid; 611 raw city strings. 21 values with unusual
  characters, 1 seller each (state/country attached, a zip-like number, an email).
- seller_city_clean: 584 distinct values (see decision log).

## 8. Decision Log

| Step | Decision | Reason |
|---|---|---|
| 1.2 | Environment: GitHub Codespaces | Local Windows Application Control policy blocks compiled packages (pandas, jupyter.exe); Python 3.15 also lacked wheels |
| 2.1 | Date-order violations: keep rows, add flags, null only the invalid stage durations | Total delivery time stays valid; dropping would lose data and may bias seller analysis. 1,359 and 23 rows |
| 2.2 | Delivery population = delivered AND delivery date present (96,470) | Excludes 8 delivered with no date and 6 canceled with a date |
| 2.3 | is_late = delivery DATE > estimated DATE (calendar-day rule); null if no delivery date | Estimate is a date at midnight, so same-day delivery meets the promise. Timestamp rule kept as is_late_timestamp_rule (sensitivity check, report both in README) |
| 2.4 | Long shipping deadlines: keep rows, flag_long_shipping_limit (>30 days, 239 items); do not use shipping_limit_date as a feature until its timing is confirmed | ~0.2% of items; 99% fall within 2-19 days. The 30-day threshold is a judgment |
| 2.5 | Category gaps: keep all items; manual English names for 2 untranslated categories; null -> 'unknown'; keep category_status | 1.44% of items; imputing would be fabrication. The two manual translations are my reading of the Portuguese, still to be checked by the owner |
| 2.6 | One review per order: latest review_answer_timestamp; add n_reviews; keep 768 no-review orders as null | Answer timestamp never ties. Accepted by default (owner did not object). 202 orders' scores depend on this choice |
| 2.7 | Cleaning consolidated in src/clean_data.py with asserts against verified numbers | Reproducibility |
| 2.8 | seller_city_clean: normalize, cut at / , \, five unusable values -> 'unknown' (04482255, vendas@creditparts.com.br, sp / sp, sbc/sp, arraial d'ajuda (porto seguro)); strip a trailing state code only when it equals seller_state (8 sellers) | Avoids guessing. 'aguas claras df' (state SP) conflicts and is left unchanged. Prefer seller_state for regional analysis |
| 2.8 | product_weight_g_clean = weight with 0 -> null | A physical product cannot weigh 0 g |

## 9. Open Items and Unverified Claims
- Not done by design: geolocation reduction (do when a phase needs it; zip prefixes
  are int, so leading zeros are lost, keep types consistent in joins); rename of "lenght" columns (optional).
- Not verified: the full list of the 29 orders_clean.csv columns (29 matches my count
  of 8+2+5+3+1+4+4+2, not seen in output); whether the 209.6-day delivery and the
  171-day timestamp gap are the same orders; how the 239 long-deadline items split across the 45 sellers;
  how many items have null product_weight_g_clean (assert is >= 8); monthly order volume
  (early 2016 may not be comparable to 2017-2018); why 6 canceled orders have a delivery date.
- Known gap: seller 'aguas claras df' with state SP (conflict, 1 row).
- On reload of the processed CSVs, set dtypes explicitly (parse dates; is_late as nullable boolean).
- Anomalies to exclude from item-level analysis: 1 shipped order with no items.

## 10. Outputs of src/clean_data.py (data/processed/, not in Git)
- orders_clean.csv: 99,441 rows x 29 columns (flags, delivery metrics, is_late,
  in_delivery_population, customer_unique_id, one review per order, item and payment aggregates)
- order_items_clean.csv: 112,650 rows x 11 columns (category_english, category_status,
  flag_long_shipping_limit, product_weight_g_clean)
- sellers_clean.csv: 3,095 rows (seller_city_clean)

## 11. Leakage Rules for Phase 6
- Features must be available at the chosen prediction time (define it first).
- Never use as features: actual delivery dates, delivery_days, delay_days, is_late
  variants, review_score and review dates, stage durations after the prediction time.
- order_estimated_delivery_date and shipping_limit_date: check when they are set before using.
- The target is is_late (calendar-day rule) on the 96,470-order population.
- Split by time, not randomly, unless justified.

## 12. Progress Log
- [x] 1.1 Concepts, folder structure, requirements
- [x] 1.2 Environment (Codespaces) and repo setup
- [x] 1.3 Raw files in data/raw/
- [x] 1.4 Notebook loads all 9 tables
- [x] 1.5 Keys, nulls, orphans, fan-out
- [x] 1.6 Data dictionary and Phase 2 checklist
- [x] 2.1 Timestamp conversion and date logic
- [x] 2.2 Delivery metrics and flags
- [x] 2.3 Population, distributions, late definitions
- [x] 2.4 Final is_late, items, shipping deadlines
- [x] 2.5 Category gap impact
- [x] 2.6 category_english and review duplicates
- [x] 2.7 Consolidated cleaning script
- [x] 2.8 Seller city and weight cleaning
- [ ] 3.1 Reload cleaned CSVs with explicit dtypes and verify key numbers (next)