# PROJECT CONTEXT: E-commerce Operations & Logistics Intelligence

## 1. Objective

Analyze the Olist Brazilian E-commerce dataset (~100k orders) to identify operational inefficiencies, delivery bottlenecks, underperforming sellers, and logistics optimization opportunities.

Portfolio project targeting Data Analyst / Business Analyst roles.

## 2. Tech Stack

- **Programming:** Python (Pandas, NumPy)
- **Database:** SQL (PostgreSQL preferred, SQLite fallback)
- **Development:** Jupyter Notebook, VS Code, Git/GitHub, GitHub Codespaces
- **Visualization:** Matplotlib, Seaborn, Power BI
- **Machine Learning:** Scikit-learn, XGBoost

## 3. Working Rules

- One phase and one step at a time; no full-project dumps.
- Explain why each operation is needed.
- Write readable, commented, production-quality code.
- Use minimal libraries.
- Never fabricate data, results, or insights. Every number must come from code.
- Always check for incorrect joins (fan-out) and data leakage.
- Use relative paths only and ensure reproducible code.
- Raw data in `data/raw/` must never be modified.
- Every file comes with how-to-run and how-to-verify instructions.
- Verify row counts, primary keys, and relationships through code rather than assumptions.
- Distinguish verified findings from hypotheses and pending investigations.

## 4. Phases

1. Dataset understanding & setup       [COMPLETED]
2. Data cleaning & preprocessing       [ ]
3. Exploratory Data Analysis            [ ]
4. SQL business analysis                [ ]
5. Power BI dashboards                  [ ]
6. Late-delivery prediction (ML)        [ ]
7. Business recommendations & report   [ ]
8. GitHub documentation & portfolio    [ ]

## 5. Dataset

**Source:** Kaggle - Brazilian E-Commerce Public Dataset by Olist.

Raw files are stored in `data/raw/` and must never be modified.

The dataset contains 9 CSV tables.

| Table | Grain | Primary Key | Foreign Keys |
|---|---|---|---|
| customers | One customer_id (per order) | customer_id | None |
| orders | One order | order_id | customer_id |
| order_items | One item in an order | (order_id, order_item_id) | order_id, product_id, seller_id |
| order_payments | One payment part | (order_id, payment_sequential) | order_id |
| order_reviews | One review | (review_id, order_id) | order_id |
| products | One product | product_id | product_category_name |
| sellers | One seller | seller_id | None |
| geolocation | Coordinate samples | No unique primary key established | Joins by zip_code_prefix |
| category_translation | One category | product_category_name | None |

### Primary Key Validation

- All listed primary keys passed the uniqueness checks performed in Step 1.5.
- `review_id` alone is NOT unique.
- 1,603 rows share a `review_id`.
- `(review_id, order_id)` is a valid composite primary key.
- Geolocation has no established unique primary key and must be aggregated before joining.

## 6. Key Decisions & Known Pitfalls

### 6.1 Customer Identification

- `customer_id` is an order-level customer record identifier.
- `customer_unique_id` identifies the actual customer across multiple orders.
- Use `customer_unique_id` for unique customer counts and customer-level analysis.
- Never interpret `customer_id` as the count of distinct real customers.

### 6.2 Join Integrity and Fan-out

- `order_items` and `order_payments` are one-to-many relationships with orders.
- Aggregate `order_items` and `order_payments` to the required grain BEFORE joining to orders when creating order-level analytical tables.
- Never directly join multiple one-to-many tables and calculate revenue without validating row multiplication.
- Geolocation must be reduced to one row per zip prefix before joining.
- Validate row counts, key uniqueness, and payment totals after every major join.
- Foreign-key integrity has been validated. Six of seven checks showed zero orphan records.
- The exception is `products.product_category_name` against `category_translation`, with 623 unmatched products.

### 6.3 Analytical Grain

- Delivery-time analysis: order grain.
- Revenue analysis: payment or order grain, depending on the metric.
- Product and seller performance: item grain.
- Customer analysis: customer_unique_id grain.
- Review analysis: review grain unless explicitly aggregated to order level.

### 6.4 Delivery Analysis

- Delivery-time analysis uses only orders with `order_status = 'delivered'`.
- 96,478 delivered orders represent approximately 97.0% of all orders.
- Eight delivered orders have missing customer delivery timestamps.
- Exclude these eight records from delivery-time calculations and document the exclusion.
- Do not automatically replace missing delivery dates with estimated values.
- The other 2,957 missing customer delivery dates belong to non-delivered orders.

### 6.5 Review Handling

- `review_id` alone is not a valid primary key.
- Use `(review_id, order_id)` as the composite key.
- 547 orders have multiple reviews.
- 768 orders have no reviews.
- A review selection or aggregation rule must be established before order-level review analysis.

### 6.6 Missing Values

Potentially legitimate missing values:

- `order_delivered_customer_date`: 2,965 missing (2.98%).
- `order_delivered_carrier_date`: 1,783 missing.
- `order_approved_at`: 160 missing.
- Review title: 88.34% missing.
- Review comment: 58.70% missing.

Product data-quality gaps:

- 610 products have a null category.
- 623 products have no matching category translation.
- This implies approximately 13 additional products have non-null categories absent from the translation table. Their category values still need inspection.
- 2 products have missing weight and dimensions.
- The missing-value pattern across the 610 products requires final confirmation.

Do not treat all missing values as errors. Investigate their business context first.

### 6.7 Orders Without Items or Payments

- 775 orders have no associated order items.
- Their status distribution:
  - Unavailable: 603
  - Canceled: 164
  - Created: 5
  - Invoiced: 2
  - Shipped: 1

- The 603 unavailable and 164 canceled orders generally did not reach fulfilment.
- One shipped order has no associated items. Treat this as an anomaly and exclude it from item-level analysis.
- One order has no associated payment. Its business context requires investigation.

### 6.8 Category Translation

- 623 products do not match a category in the translation table.
- 610 have a null category.
- Approximately 13 have non-null categories that are not present in the translation table.
- A category handling strategy must be decided during Phase 2.
- Potential approaches include retaining Portuguese category names or assigning an `unknown` label.
- Do not silently drop unmatched products through inner joins.

### 6.9 Machine Learning Leakage Rules (Phase 6)

- Features must be available at the actual prediction time.
- Actual delivery dates and post-delivery review information must be excluded from prediction features.
- Use a clearly defined prediction point.
- Avoid target leakage through derived features.
- Use appropriate train/test splitting and evaluation metrics.

## 7. Verified Findings (Step 1.5)

### 7.1 Customer Identity

| Metric | Verified Value |
|---|---:|
| Total customer records | 99,441 |
| Distinct customer_id | 99,441 |
| Distinct customer_unique_id | 96,096 |
| Customers with exactly one order | 93,099 |
| Customers with multiple orders | Approximately 2,997 |

- `customer_unique_id` is the correct identifier for customer-level analysis.
- The customer-to-orders join preserved 99,441 rows.
- `validate="many_to_one"` passed.
- No fan-out occurred in this relationship.

### 7.2 Review Distribution

| Metric | Verified Value |
|---|---:|
| Orders with exactly one review | 98,126 |
| Orders with two reviews | 543 |
| Orders with three reviews | 4 |
| Orders with multiple reviews | 547 |
| Orders without reviews | 768 |
| Orders with at least one review | 98,673 |

The review distribution reconciles with the total of 99,441 orders.

### 7.3 Order Status Distribution

| Order Status | Number of Orders |
|---|---:|
| Delivered | 96,478 |
| Shipped | 1,107 |
| Canceled | 625 |
| Unavailable | 609 |
| Invoiced | 314 |
| Processing | 301 |
| Created | 5 |
| Approved | 2 |
| **Total** | **99,441** |

- Delivered orders account for approximately 97.0% of all orders.
- 2,963 orders have not reached delivered status.
- The delivered population is the base population for delivery-time analysis.

### 7.4 Foreign Key Integrity

- Six of seven foreign-key checks returned zero orphan records.
- All orders have valid customer references.
- Order items, payments and reviews reference existing parent records.
- Product references to sellers and products were validated.
- Exception: 623 products do not match the category translation table.
- The 610 null-category products are the same rows missing name length,
  description length and photo count (verified: all four missing in 610 rows).

Breakdown:

| Category Matching Issue | Count |
|---|---:|
| Products with null category | 610 |
| Additional non-null unmatched categories | Approximately 13 |
| Total unmatched products | 623 |

The 13 non-null unmatched categories are inferred from the difference and require direct inspection.

### 7.5 Orders Without Items

| Order Status | Orders Without Items |
|---|---:|
| Unavailable | 603 |
| Canceled | 164 |
| Created | 5 |
| Invoiced | 2 |
| Shipped | 1 |
| **Total** | **775** |

- 774 orders without items have statuses consistent with not reaching normal fulfilment.
- One shipped order without items is an anomaly requiring documentation.
- These orders cannot contribute to item-level product and seller analysis.

### 7.6 Delivered Orders With Missing Delivery Dates

- Total missing `order_delivered_customer_date`: 2,965.
- Delivered orders missing the date: 8.
- Non-delivered orders missing the date: 2,957.
- The eight delivered orders with missing timestamps must be excluded from delivery-time calculations.

### 7.7 Join Fan-out Validation

| Scenario | Rows | Payment Value |
|---|---:|---:|
| Orders | 99,441 | - |
| Orders + Items | 113,425 | - |
| Orders + Items + Payments (naive join) | 118,434 | 20,470,726.66 |
| Payments table alone | - | 16,008,872.12 |
| Safe join with pre-aggregated payments | 99,441 | 16,008,872.12 |

- Naive join inflates payment value by 4,461,854.54.
- This represents approximately 27.9% overstatement.
- Pre-aggregating payments at order level preserves the correct total.

### 7.8 Additional Missing Values

- 1,783 missing carrier delivery timestamps.
- 160 missing approval timestamps.
- 88.34% missing review titles.
- 58.70% missing review comments.
- 610 products with null categories and associated descriptive gaps.
- 2 products with missing physical dimensions and weight.

## 8. Decision Log

| Date | Decision | Reason |
|---|---|---|
| 05-Nov-2026 | Use customer_unique_id for customer-level analysis | customer_id is order-specific |
| 05-Nov-2026 | Use (review_id, order_id) as review primary key | review_id alone is not unique |
| 05-Nov-2026 | Pre-aggregate payment records before joining | Prevents 27.9% payment inflation observed in validation |
| 05-Nov-2026 | Preserve raw CSV files without modification | Ensures reproducibility and traceability |
| 05-Nov-2026 | Exclude 8 delivered orders with missing customer delivery dates from delivery-time calculations | Delivery duration cannot be calculated reliably |
| 05-Nov-2026 | Flag 1 shipped order without items as an anomaly | Shipped order has no associated item records |
| TBD | Database: PostgreSQL or SQLite | To be decided in Phase 4 |
| TBD | Multiple-review handling strategy | Requires business justification |
| TBD | Missing category translation strategy | Requires inspection of unmatched category values |
| TBD | Missing-value treatment strategy | Depends on business context and Phase 2 analysis |

## 9. Progress Log

- [x] Step 1.1 Concepts, folder structure, requirements.
- [x] Step 1.2 Environment setup (Codespaces) + dataset download.
- [x] Step 1.3 Raw files in data/raw/ (9 CSVs verified present).
- [x] Step 1.4 Notebook loads all 9 tables; row counts verified.
- [x] Step 1.5 Primary key uniqueness, nulls, foreign keys, orphan records, order status and join fan-out checks.
- [ ] Step 1.6 Data dictionary and prioritized Phase 2 cleaning plan.

## 10. Pending Investigations (Step 1.6)

1. Inspect the 13 non-null product categories that do not match the translation table.
2. Confirm whether the same 610 product rows are missing category, name length, description length and photo count.
3. Investigate the 2 products missing weight and dimensions.
4. Inspect the one shipped order without order items.
5. Investigate the one order without payment information.
6. Define a strategy for multiple reviews per order.
7. Document missing-value treatment based on business context.
8. Prepare a data dictionary for all nine tables.
9. Create a prioritized list of Phase 2 data-cleaning tasks.

## 11. Phase 1 Completion Criteria

Phase 1 is complete when:

- All nine datasets have been loaded and inspected.
- Primary keys and composite keys have been validated.
- Foreign-key integrity has been checked.
- Missing-value patterns have been documented.
- Order status distribution has been verified.
- Unmatched and orphan records have been investigated.
- Join fan-out risks have been demonstrated and documented.
- A data dictionary has been prepared.
- Phase 2 cleaning requirements have been prioritized.

**Current Status:** Step 1.5 is complete. Step 1.6 (data dictionary and prioritized cleaning plan) is the final remaining step before beginning Phase 2: Data Cleaning & Preprocessing.