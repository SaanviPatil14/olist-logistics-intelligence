# E-commerce Operations & Logistics Intelligence

**Analyzing operational efficiency, customer behaviour, delivery performance, and logistics bottlenecks using the Olist Brazilian E-commerce Dataset.**

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20%7C%20SQLite-336791?logo=postgresql)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi)
![Status](https://img.shields.io/badge/Project-In%20Progress-orange)

## 1. Project Overview

E-commerce businesses depend on efficient logistics operations to deliver orders on time, maintain customer satisfaction, and optimize operational costs.

This project analyzes the **Brazilian E-Commerce Public Dataset by Olist**, containing approximately 100,000 orders, to uncover operational inefficiencies and identify opportunities for logistics optimization.

The objective is to transform raw transactional data into actionable business insights through data analysis, SQL, visualization, and predictive modelling.

### Business Questions

- What factors contribute to late deliveries?
- Which sellers and product categories experience delivery inefficiencies?
- How does delivery performance vary across regions?
- What are the purchasing patterns of repeat customers?
- Which operational bottlenecks affect order fulfilment?
- Can machine learning help predict late deliveries before they happen?

## 2. Dataset

**Source:** [Brazilian E-Commerce Public Dataset by Olist - Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

The dataset contains nine interconnected CSV files:

| Dataset | Description |
|---|---|
| Customers | Customer identifiers and geographical information |
| Orders | Order timestamps and order status |
| Order Items | Products, sellers, quantities and prices |
| Order Payments | Payment methods and payment values |
| Order Reviews | Customer ratings and feedback |
| Products | Product attributes and categories |
| Sellers | Seller identifiers and geographical information |
| Geolocation | Brazilian ZIP code coordinates |
| Category Translation | Portuguese-to-English product category mapping |

**Data handling:** Raw CSV files are stored in `data/raw/` and are never modified. Processed datasets and analytical outputs are maintained separately.

## 3. Tech Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| Data Manipulation | Pandas, NumPy |
| Data Visualization | Matplotlib, Seaborn |
| Database | SQL, PostgreSQL / SQLite |
| Machine Learning | Scikit-learn, XGBoost |
| Business Intelligence | Power BI |
| Development | Jupyter Notebook, VS Code, Git, GitHub Codespaces |

## 4. Project Workflow

The project follows an end-to-end analytics workflow.

| Phase | Activities | Status |
|---|---|---|
| 1. Dataset Understanding | Schema inspection, key validation, missing values, relationship and join checks | Completed |
| 2. Data Cleaning | Missing values, anomalies, duplicate records and preprocessing | Upcoming |
| 3. Exploratory Data Analysis | Customer, seller, product, revenue and delivery analysis | Upcoming |
| 4. SQL Business Analysis | Business queries, aggregations and KPI calculations | Upcoming |
| 5. Power BI Dashboards | Interactive operational and logistics dashboards | Upcoming |
| 6. Predictive Analytics | Late-delivery prediction using ML models | Upcoming |
| 7. Business Recommendations | Findings, operational improvements and recommendations | Upcoming |
| 8. Documentation | Final report and portfolio documentation | Upcoming |

## 5. Data Quality & Validation

Before beginning exploratory analysis, data integrity checks were performed across the nine datasets.

### 5.1 Primary Key Validation

Primary keys and composite keys were checked for uniqueness.

| Table | Validated Primary Key |
|---|---|
| Customers | customer_id |
| Orders | order_id |
| Order Items | (order_id, order_item_id) |
| Order Payments | (order_id, payment_sequential) |
| Order Reviews | (review_id, order_id) |
| Products | product_id |
| Sellers | seller_id |
| Category Translation | product_category_name |

**Important finding:** `review_id` alone is not unique. A composite key of `(review_id, order_id)` is required.

### 5.2 Customer Identity Validation

The dataset contains:

| Metric | Count |
|---|---:|
| Customer records | 99,441 |
| Distinct customer_id | 99,441 |
| Distinct customer_unique_id | 96,096 |
| Customers with exactly one order | 93,099 |
| Customers with multiple orders | 2,997 |

`customer_id` represents an order-level customer record, whereas `customer_unique_id` identifies the actual customer across multiple orders.

Therefore, `customer_unique_id` is used for customer-level analysis to avoid overcounting.

### 5.3 Order Status Distribution

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

Approximately 97% of orders have delivered status.

This establishes the initial population for delivery-performance analysis. Eight delivered orders have missing customer delivery timestamps and will be excluded from delivery-time calculations.

### 5.4 Foreign Key Integrity

Six of the seven foreign-key validation checks returned zero orphan records.

The exception was the relationship between products and category translations.

- 623 products do not match the category translation table.
- 610 products have a missing category.
- Approximately 13 additional products may have non-null categories absent from the translation table. These require direct inspection.

Unmatched categories will be handled explicitly during data cleaning rather than silently discarded.

### 5.5 Orders Without Items

A total of 775 orders have no associated order items.

| Order Status | Orders Without Items |
|---|---:|
| Unavailable | 603 |
| Canceled | 164 |
| Created | 5 |
| Invoiced | 2 |
| Shipped | 1 |
| **Total** | **775** |

One shipped order without associated items has been flagged as an anomaly.

### 5.6 Join Integrity & Payment Inflation

A join validation exercise revealed a significant issue when combining multiple one-to-many tables.

| Scenario | Rows | Payment Value |
|---|---:|---:|
| Orders | 99,441 | - |
| Orders + Items | 113,425 | - |
| Orders + Items + Payments (naive join) | 118,434 | 20,470,726.66 |
| Payments table alone | - | 16,008,872.12 |
| Safe join with pre-aggregated payments | 99,441 | 16,008,872.12 |

**Key finding:** A naive multi-table join inflates payment value by 4,461,854.54, approximately 27.9%.

To prevent this, payment records must be aggregated at the order level before joining them with other one-to-many datasets.

This validation ensures that subsequent revenue and payment-related metrics remain accurate.

## 6. Analytical Approach

The project will focus on the following analytical areas:

**Customer Analytics**
- Unique and repeat customer analysis.
- Customer purchasing behaviour.
- Geographic distribution of customers.

**Sales & Product Analytics**
- Revenue and order trends.
- Product category performance.
- Average order value.
- Seller contribution and performance.

**Logistics & Operations Analytics**
- Delivery time and delay analysis.
- Regional delivery performance.
- Seller-related fulfilment patterns.
- Order status and cancellation analysis.
- Identification of logistics bottlenecks.

**Predictive Analytics**
- Late-delivery prediction.
- Feature engineering using information available at prediction time.
- Model comparison using Scikit-learn and XGBoost.
- Model evaluation using appropriate classification metrics.

## 7. Machine Learning Strategy

The predictive modelling phase will focus on identifying orders at risk of late delivery.

Potential modelling steps:

1. Define a late-delivery target.
2. Establish a prediction point and eligible order population.
3. Engineer features available at prediction time.
4. Split data into training and testing sets.
5. Train baseline classification models.
6. Evaluate and compare model performance.
7. Identify important factors influencing late deliveries.

**Data leakage prevention:** Actual delivery dates and post-delivery review information will not be used as predictive features.

## 8. Repository Structure

```text
olist-logistics-intelligence/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   └── 03_exploratory_data_analysis.ipynb
│
├── src/
│
├── sql/
│
├── dashboards/
│
├── models/
│
├── outputs/
│
├── docs/
│
├── PROJECT_CONTEXT.md
├── README.md
├── requirements.txt
└── .gitignore
```

## 9. Setup & Installation

### Prerequisites

- Python 3.12 or a compatible supported Python version.
- Git.
- Jupyter Notebook or VS Code with the Python and Jupyter extensions.

### Clone the Repository

```bash
git clone <your-github-repository-url>
cd olist-logistics-intelligence
```

### Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

**Windows:**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux / GitHub Codespaces:**
```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Download the Dataset

Download the Olist dataset from Kaggle and extract the nine CSV files into:

```text
data/raw/
```

Do not modify the original raw files.

### Run the Notebooks

Open the repository in VS Code or GitHub Codespaces.

Select the project's Python virtual environment as the Jupyter kernel and execute the notebooks in numerical order.

## 10. Current Progress

- [x] Project setup and folder structure.
- [x] Python environment and dependencies setup.
- [x] Olist dataset downloaded and raw files verified.
- [x] All nine datasets loaded into Pandas.
- [x] Primary key and composite key validation.
- [x] Customer identity validation.
- [x] Missing-value analysis.
- [x] Order status distribution.
- [x] Foreign-key integrity and orphan checks.
- [x] Join fan-out validation.
- [ ] Data dictionary and Phase 2 cleaning plan.
- [ ] Data cleaning and preprocessing.
- [ ] Exploratory Data Analysis.
- [ ] SQL business analysis.
- [ ] Power BI dashboards.
- [ ] Late-delivery prediction.
- [ ] Business recommendations and final report.

## 11. Project Documentation

- `PROJECT_CONTEXT.md`: Detailed project decisions, verified findings, analytical rules and progress tracking.
- `docs/data_dictionary.md`: Dataset definitions, columns, keys and relationships (planned).
- `docs/phase_2_cleaning_plan.md`: Prioritized data-cleaning tasks (planned).

## 12. Expected Deliverables

- Reproducible Python data analysis notebooks.
- Cleaned and validated analytical datasets.
- SQL queries answering business questions.
- Interactive Power BI dashboards.
- A machine learning model for late-delivery prediction.
- Business recommendations supported by analytical evidence.
- Complete project documentation.

---

**Project Status:** Phase 1 completed through Step 1.5. Step 1.6 (data dictionary and Phase 2 cleaning plan) is in progress.

*This repository is an ongoing portfolio project. Findings and deliverables will be updated as the analysis progresses.*