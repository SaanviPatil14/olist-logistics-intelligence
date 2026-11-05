# PROJECT CONTEXT: E-commerce Operations & Logistics Intelligence

## 1. Objective
Analyze the Olist Brazilian E-commerce dataset (~100k orders) to identify
operational inefficiencies, delivery bottlenecks, underperforming sellers,
and logistics optimization opportunities. Portfolio project targeting
Data Analyst / Business Analyst roles.

## 2. Tech Stack
Python (Pandas, NumPy), SQL (PostgreSQL preferred, SQLite fallback),
Jupyter Notebook, Power BI, Scikit-learn, XGBoost, Git/GitHub.

## 3. Working Rules
- One phase and one step at a time; no full-project dumps.
- Explain why each operation is needed.
- Readable, commented, production-quality code; minimal libraries.
- Never fabricate data, results, or insights; every number must come from code.
- Always check for incorrect joins (fan-out) and data leakage.
- Relative paths only; reproducible code.
- Every file comes with how-to-run and how-to-verify instructions.

## 4. Phases
1. Dataset understanding & setup        [IN PROGRESS]
2. Data cleaning & preprocessing        [ ]
3. Exploratory Data Analysis            [ ]
4. SQL business analysis                [ ]
5. Power BI dashboards                  [ ]
6. Late-delivery prediction (ML)        [ ]
7. Business recommendations & report    [ ]
8. GitHub documentation & portfolio     [ ]

## 5. Dataset (source: Kaggle "Brazilian E-Commerce Public Dataset by Olist")
Raw files live in data/raw/ and are never modified.

| Table | Grain | Primary Key | Foreign Keys |
|---|---|---|---|
| customers | one customer_id (per order) | customer_id | none |
| orders | one order | order_id | customer_id |
| order_items | one item in an order | (order_id, order_item_id) | order_id, product_id, seller_id |
| order_payments | one payment part | (order_id, payment_sequential) | order_id |
| order_reviews | one review | review_id (verify uniqueness) | order_id |
| products | one product | product_id | product_category_name |
| sellers | one seller | seller_id | none |
| geolocation | coordinate samples | none | joins by zip_code_prefix |
| category_translation | one category | product_category_name | none |

## 6. Key Decisions & Known Pitfalls
- customer_id is per-order; customer_unique_id identifies the real customer.
- Aggregate order_items and order_payments to order level BEFORE joining
  to orders, to avoid row fan-out and inflated revenue.
- Geolocation must be reduced to one row per zip prefix before joining.
- Delivery-time analysis uses only orders with status = 'delivered'.
- Delivery metrics = order grain; revenue/seller metrics = item grain.
- ML leakage rule (Phase 6): features must be available at prediction time.
  Actual delivery date and review data are post-outcome and must be excluded.
- Row counts and key uniqueness are VERIFIED IN CODE, not assumed.

## 7. Decision Log
| Date | Decision | Reason |
|---|---|---|
| (fill in) | Database: PostgreSQL or SQLite | (decide in Phase 4) |

## 8. Progress Log
- [x] Step 1.1 Concepts, folder structure, requirements
- [x] Step 1.2 Environment setup (Codespaces) + dataset download
- [x] Step 1.3 Raw files in data/raw/ (9 CSVs verified present)
- [x] Step 1.4 Notebook loads all 9 tables; row counts verified
- [ ] Step 1.5 Key uniqueness, nulls, join checks