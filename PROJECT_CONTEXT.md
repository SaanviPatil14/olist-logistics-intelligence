# PROJECT CONTEXT: E-commerce Operations & Logistics Intelligence

Last updated: 2026-11-10 (end of Phase 3)
Repo: https://github.com/SaanviPatil14/olist-logistics-intelligence
Last commit I saw confirmed: a8bb901. Later commits (notebooks, docs, figures) were
reported as done but not seen. Check `git status` and `git log --oneline -5`.

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
- Run commands from the project root after `source .venv/bin/activate`.
- Notebooks run from notebooks/, so they use `../data/...` relative paths.
- Power BI Desktop is a Windows app and may hit the same local Application
  Control block (test in Phase 5; Power BI Service on the web is a fallback).

## 3. Working Rules
- One phase and one step at a time (exception: Phase 2 was consolidated into
  src/clean_data.py after every rule was decided).
- Explain why each operation is needed.
- Readable, commented code; minimal libraries.
- Never fabricate data, results, or insights; every number comes from code.
- Always check for incorrect joins (fan-out) and data leakage.
- Relative paths only; reproducible code.
- Every file comes with how-to-run and how-to-verify instructions.
- Every chart and table states which population it uses.
- Causes are hypotheses until tested. Associations are not causes.

## 4. Phases
1. Dataset understanding & setup        [DONE]
2. Data cleaning & preprocessing        [DONE]
3. Exploratory Data Analysis            [DONE]
4. SQL business analysis                [IN PROGRESS, not started]
5. Power BI dashboards                  [ ]
6. Late-delivery prediction (ML)        [ ]
7. Business recommendations & report    [ ]
8. GitHub documentation & portfolio     [ ]

## 5. Folder Structure
```
olist-logistics-intelligence/
├── data/raw/          # 9 original CSVs, never edited, not in Git
├── data/processed/    # outputs of src/clean_data.py, not in Git
├── notebooks/         # 01_data_understanding, 02_data_cleaning, 03_eda
├── src/clean_data.py  # reproducible cleaning script
├── sql/  powerbi/  models/
├── reports/figures/   # 5 PNGs from Phase 3 (tracked in Git)
├── docs/data_dictionary.md
├── docs/phase2_cleaning_checklist.md
├── docs/eda_findings.md
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
  93,099 people ordered once; 2,997 more than once. Count customers with customer_unique_id.
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
  estimated delivery up to 2018-11-12. All estimated dates are at midnight.
- Date logic violations: purchase<approved 0; purchase<customer delivery 0;
  purchase<estimated 0; carrier pickup before approval 1,359; customer delivery
  before carrier pickup 23 (all 23 delivered).
- Carrier-before-approval gaps: median 17.2 h, p75 26.0 h, max 4,109 h (~171 days);
  458 over 1 day, 14 over 7 days, 1 over 30 days.
- Delivery population (full): delivered AND delivery date present = 96,470 orders
  (2,971 excluded).
- Full-population metrics: delivery_days median 10.22, p95 29.27, p99 46.05, max 209.63;
  estimated_days median 23.23; delay_days median -11.95, p95 +3.82, max +188.98.
- Late rate (full population): 6.77% calendar-day rule (6,534 late) vs 8.11% timestamp
  rule (7,826); the rules differ on 1,292 orders.
- Reload of orders_clean.csv across all 96,476 orders with a delivery date shows
  6,535 late; the population has 6,534 (one of the 6 canceled is late).

### 7.5 Items
- price: min 0.85, median 74.99, p99 890, max 6,735; no zero/negative values.
- freight_value: median 16.26, p99 84.52, max 409.68; 383 items with freight 0.
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
- Impact: null category 1,603 items (1.42%, price revenue 179,535.28, 1.32%);
  untranslated 24 items (0.02%, 5,514.48, 0.04%). Total 1,627 items (1.44%), ~1.36% of item revenue.
- category_english has 74 distinct values (71 + 2 manual + 'unknown').
- 4 products have weight 0 g (impossible), affecting 8 items. No zero dimensions.
  Weight median 700 g, p99 22,538 g, max 40,425 g.

### 7.7 Locations
- Customers: 27 states, all valid; 4,119 cities, no accent/case variants.
- Sellers: 23 states, all valid; 611 raw city strings; seller_city_clean has 584.

### 7.8 EDA: scope and time (Phase 3)
- Monthly orders: 2016-09: 4, 2016-10: 324, 2016-11: none, 2016-12: 1; 2017-01: 800,
  rising to ~6,000-7,500 a month in 2018; 2018-09: 16, 2018-10: 4 (0 in population).
- ANALYSIS WINDOW: purchases 2017-01 to 2018-08. Window population = 96,203 delivered
  orders, 6,531 late (6.79%). Excluded months: 3 late orders.
- Late rate by purchase month (full population): mostly 1-7%; 2017-11 12.40%,
  2018-02 14.13%, 2018-03 18.96%. Feb+Mar 2018 = 2,254 of 6,534 late orders (~34.5%).
- Spike months (2017-11, 2017-12, 2018-02, 2018-03) hold 27.5% of single-seller orders.
- Spikes are system-wide: Other states 13.0/6.5/14.3/23.7%, SP 7.0/3.1/7.3/9.4%,
  RJ 26.0/24.0/34.0/34.5%. RJ is roughly double Other in Nov and Dec 2017, and still
  24.0% in Dec 2017 when Other was 6.5%. All groups normalize by Apr 2018.
  SP rises to 9.0% in Aug 2018 (cause unknown). Cause of the spikes not determined.

### 7.9 EDA: geography
- Window population by customer state: SP 40,399 orders (42.0%, 4.50% late, 27.8% of late);
  RJ 12,310 (12.8%, 12.14% late, 22.9% of late); MG 11,319 (4.59%); BA 3,253 (12.17%).
  SP+RJ = ~50.7% of late orders.
- Highest late rates: AL 21.46%, MA 17.53%, SE 15.36%, PI 13.89%, CE 13.83% (small volumes).
  Median delivery: SP 7.20 d; AM 25.88, RR 25.13, AP 24.35, AL 22.33.
  AM/AP/RO: long delivery, low late rate (estimates likely generous; unverified).
- Multi-seller orders: 1,278 (1,272 in window). Route analysis uses orders with a single
  seller state: 95,696 of 96,203 (507 excluded).
- Same-state (34,489): median 6.53 d, p90 14.23, late 4.53%. Cross-state (61,207): median
  12.81 d, p90 26.29, late 8.11%.
- SP-origin orders (68,052): median delivery rises with distance (MG 10.79 d, RJ 12.84,
  BA 17.69) but late rate does not (MG 5.30%, PR 4.45%, RS 6.67%; RJ 14.20%, ES 12.35%,
  BA 12.91%). SP-to-RJ late rate by month is 2-8% normally, 32.0/29.9/39.2/42.2% in the
  four spike months.

### 7.10 EDA: sellers
- Single-seller orders in window: 94,931 (overall late 6.87%); 2,925 sellers;
  614 with 30+ orders cover 83.2% of orders.
- Top 10 sellers by late count: 1,019 of 6,518 late orders (~15.6%). Lateness is
  not concentrated in a few sellers.
- Worst 10 sellers by late rate (30+ orders): 20-36% late. Spike-month check:
  54965b and ede0c0 had 0% late outside spike months, 712e6e 6.5% (timing artifacts);
  2a1348, ef990a, beadbe, 835f0f, ad7815 stayed at 19-30% (candidates for review);
  71039d 23.1% on ~13 orders (inconclusive); a49928 10.3%. Samples are small and
  destination mix is not tested.

### 7.11 EDA: reviews and stages (analysis only, leakage for ML)
- 95,560 orders in window have a review; 643 do not.
- On time: mean 4.29, 1-star 6.60%, 5-star 62.28%. Late: mean 2.27, 1-star 53.76%, 5-star 16.54%.
- Mean score by delay: early 4.29, on date 4.03, 1-3 d 3.29, 4-7 d 2.10, 8-14 d 1.67,
  15+ d 1.72 (flattens after ~8 days). Association only.
- Stages (window): median approval->carrier 1.84 d (p90 5.99), carrier->customer 7.10 d
  (p90 18.91), total 10.21 d. Late orders: carrier->customer 26.20 d vs 6.95 on time;
  approval->carrier 3.07 vs 1.79. Most lateness is in carrier transit.

### 7.12 EDA: categories, freight, weight
- Items in window population: 109,872 (96,203 orders); price 13,179,777.95;
  freight 2,191,963.14 (~16.6% of price).
- Top 12 of 74 categories = 69.0% of item revenue (health_beauty 9.3%, watches_gifts 8.8%,
  bed_bath_table 7.8%). 'unknown' = 1.3%.
- Freight as % of price: furniture_decor 23.7, housewares 23.2, garden_tools 20.6,
  bed_bath_table 19.7; watches_gifts 8.4.
- Single-category orders: 95,425 of 96,203; overall late 6.83%; 32 categories with 300+
  orders range ~4.28% (luggage_accessories) to 12.06% (audio, 340 orders).
  office_furniture has median delivery 18.87 d but late 8.19%.
- Weight (96,181 orders with all weights known): median delivery 9.43 d (<=250 g) to
  11.19 d (>2,800 g); late rate 6.10, 7.04, 6.25, 7.05, 7.56% (not monotonic). Weak signal.

## 8. Decision Log

| Step | Decision | Reason |
|---|---|---|
| 1.2 | Environment: GitHub Codespaces | Local Windows Application Control policy blocks compiled packages (pandas, jupyter.exe); Python 3.15 also lacked wheels |
| 2.1 | Date-order violations: keep rows, add flags, null only the invalid stage durations | Total delivery time stays valid; dropping would lose data and may bias seller analysis. 1,359 and 23 rows |
| 2.2 | Delivery population = delivered AND delivery date present (96,470) | Excludes 8 delivered with no date and 6 canceled with a date |
| 2.3 | is_late = delivery DATE > estimated DATE (calendar-day rule); null if no delivery date | Estimate is a date at midnight, so same-day delivery meets the promise. Timestamp rule kept as is_late_timestamp_rule (report both in README) |
| 2.4 | Long shipping deadlines: keep rows, flag_long_shipping_limit (>30 days, 239 items); do not use shipping_limit_date as a feature until its timing is confirmed | ~0.2% of items. The 30-day threshold is a judgment |
| 2.5 | Category gaps: keep all items; manual English names for 2 untranslated categories; null -> 'unknown'; keep category_status | 1.44% of items; imputing would be fabrication. The two manual translations are my reading of the Portuguese, still to be checked by the owner |
| 2.6 | One review per order: latest review_answer_timestamp; add n_reviews; 768 no-review orders stay null | Answer timestamp never ties. Accepted by default. 202 orders' scores depend on it |
| 2.7 | Cleaning consolidated in src/clean_data.py with asserts | Reproducibility |
| 2.8 | seller_city_clean: normalize, cut at / , \, five unusable values -> 'unknown'; strip a trailing state code only when it equals seller_state (8 sellers) | Avoids guessing. 'aguas claras df' (state SP) conflicts and is unchanged. Prefer seller_state for regional analysis |
| 2.8 | product_weight_g_clean = weight with 0 -> null | A physical product cannot weigh 0 g |
| 3.1 | Load processed CSVs with date_format="mixed" and nullable boolean for is_late | review_creation_date mixes date-only and datetime strings. Cause unconfirmed, data valid |
| 3.2 | Trend window = purchases 2017-01 to 2018-08; 2016 and 2018-09/10 excluded from trend charts, kept in totals | Months with 0-324 orders give unreliable rates; Nov 2016 has no data |
| 3.4 | Route and seller analyses use single-seller(-state) orders only | An order with several sellers cannot be attributed to one origin |
| 3.5 | Seller rankings need 30+ orders and a spike-month check | Small samples and timing artifacts mislead. 30 is a judgment |
| 3.7 | Category late rates use single-category orders, 300+ orders | Avoids double counting. 300 is a judgment |

## 9. Open Items and Unverified Claims
- Not done by design: geolocation reduction (do when a phase needs it; zip prefixes are
  int, so leading zeros are lost, keep types consistent); rename of "lenght" columns (optional).
- Not verified: whether the 209.6-day delivery and 171-day timestamp gap are the same
  order; how the 239 long-deadline items split across the 45 sellers; why 6 canceled
  orders have a delivery date; why Nov 2016 has no orders; cause of the review_creation_date
  mixed format; the two manual category translations.
- Not tested in Phase 3: estimated delivery days by state and category; destination and
  month adjustment for seller and category rates; cause of the spike months; why RJ
  stays high in Dec 2017; the SP rise in Aug 2018.
- Known gap: seller 'aguas claras df' with state SP (1 row).
- Anomaly to exclude from item-level analysis: 1 shipped order with no items.
- Step 3.8 outputs (5 PNGs in reports/figures, docs/eda_findings.md commit) not seen.

## 10. Outputs of src/clean_data.py (data/processed/, not in Git)
- orders_clean.csv: 99,441 rows x 29 columns (flags, delivery metrics, is_late,
  in_delivery_population, customer_unique_id, one review per order, item and payment aggregates)
- order_items_clean.csv: 112,650 rows x 11 columns (category_english, category_status,
  flag_long_shipping_limit, product_weight_g_clean)
- sellers_clean.csv: 3,095 rows x 5 columns (seller_city_clean)
- customer_state is not in orders_clean.csv; notebooks join it from the raw customers
  table (many_to_one, row count asserted).

## 11. Leakage Rules for Phase 6
- Define the prediction time first. Features must be known at that time.
- Never use as features: actual delivery dates, delivery_days, delay_days, is_late
  variants, review_score and review dates, stage durations after the prediction time.
- order_estimated_delivery_date and shipping_limit_date: check when they are set before use.
- Target: is_late (calendar-day rule) on delivered orders with a delivery date.
- Split by time, not randomly, unless justified. The spike months make this important.
- Candidate features (hypotheses): same_state, customer state, seller state, order weight,
  category, purchase month.

## 12. Progress Log
- [x] 1.1 to 1.6 Concepts, environment, data load, keys, dictionary
- [x] 2.1 to 2.8 Cleaning decisions and src/clean_data.py
- [x] 3.1 Reload verified (17 number checks, dates fixed)
- [x] 3.2 Monthly volume and late rate
- [x] 3.3 State analysis
- [x] 3.4 Route (same-state vs cross-state), RJ by month
- [x] 3.5 Sellers and spike-month check
- [x] 3.6 Reviews and delivery stages
- [x] 3.7 Categories, freight, weight
- [x] 3.8 Findings summary (docs/eda_findings.md) and charts
- [ ] 4.1 Choose the database: SQLite or PostgreSQL (next)