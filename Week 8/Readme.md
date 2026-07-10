# E-Commerce Order Analytics System

## Overview

This project is an end-to-end e-commerce order analytics system developed using Python, Pandas, SQLite, and SQL.

The system generates realistic but intentionally inconsistent order data, performs data cleaning and integrity validation, loads the cleaned data into a relational database, and generates business reports using SQL and a command-line interface.

## Objectives

- Generate realistic e-commerce datasets
- Introduce and identify common data-quality issues
- Clean and validate data using Pandas
- Maintain referential integrity between tables
- Load cleaned data into SQLite
- Perform business analysis using SQL
- Implement CTEs and window functions
- Analyze customer cohorts, retention, and RFM segments
- Generate dynamic reports using a Python CLI
- Handle invalid inputs and critical edge cases

## Data Pipeline

```text
Raw CSV Files
      ↓
Pandas Cleaning and Validation
      ↓
Cleaned CSV Files
      ↓
SQLite Database
      ↓
SQL Analytics and CLI Reports
```

## Datasets

Four related datasets are generated:

| Dataset | Description | Raw Rows | Cleaned Rows |
|---|---|---:|---:|
| Customers | Customer details and registration information | 808 | 801 |
| Products | Product catalogue and pricing details | 505 | 500 |
| Orders | Order, customer, date, status, and region data | 1,515 | 1,500 |
| Order Items | Products and quantities included in orders | 4,040 | 3,960 |

## Dataset Relationships

- One customer can place multiple orders.
- One order can contain multiple order items.
- One product can appear in multiple order items.
- `order_items` connects the `orders` and `products` tables.

## Intentional Data-Quality Issues

The raw datasets contain controlled inconsistencies:

- 5% of orders have missing customer IDs
- 3% of order items have negative quantities
- 2% of customers have invalid email addresses
- Some order dates use the `DD-MM-YYYY` format
- Some product names contain extra spaces or inconsistent case
- Duplicate records are included
- Some order items reference non-existent orders

These issues are included to demonstrate data cleaning and validation.

## Data Cleaning

The `clean_data.py` script performs the following operations:

- Removes duplicate primary-key records
- Standardizes customer and product text fields
- Converts order dates into `YYYY-MM-DD HH:MM:SS`
- Validates and repairs invalid email addresses
- Converts numeric columns into correct data types
- Validates discount, quantity, and price values
- Detects future and unparseable dates
- Checks customer, order, and product references
- Removes orphan order-item records
- Generates a data-quality report

Orders with missing customer IDs are mapped to a controlled `CUST_UNKNOWN` record. Negative quantities are retained because they represent product returns.

The complete issue summary is available in:

```text
output/data_quality_report.txt
```

## Database Design

SQLite is used as the local relational database.

The schema implements:

- Primary keys
- Foreign keys
- `NOT NULL` constraints
- `UNIQUE` email constraint
- `CHECK` constraints
- Indexes on common join and filtering columns

Database tables:

- `customers`
- `products`
- `orders`
- `order_items`

The generated database is stored at:

```text
database/ecommerce.db
```

## SQL Analytics

### Basic and Intermediate Analysis

1. Total revenue per product category
2. Top 10 customers by total order value
3. Month-wise order count for the latest 12 months
4. Customers who ordered but never received a delivered order
5. Products with more returned units than purchased units
6. Return rate per category
7. Top products by quantity and revenue
8. Average order value by customer type

### Advanced SQL Analysis

1. Region-wise running revenue using `SUM() OVER`
2. Category-wise product ranking using `DENSE_RANK()`
3. Consecutive order gap using `LAG()`
4. Customer risk identification using average order gap
5. Monthly customer revenue groups using multiple CTEs
6. Customer lifetime-value quartiles using `NTILE()`
7. Year-over-year monthly revenue comparison
8. First and recent purchased category analysis
9. Cumulative customer revenue distribution
10. Three-month moving average
11. Month-over-month revenue growth

### Cohort and Customer Analysis

- Registration-month cohorts
- Month 0 to Month 3 retention
- Frequently purchased product pairs
- Frequency-based customer segmentation
- Spend-tier segmentation
- Recency, Frequency, and Monetary analysis
- RFM customer scores
- Churned, active, one-time, and repeat customers

## CLI Reporting Tool

The command-line reporting tool supports:

- Daily reports
- Weekly reports
- Monthly reports
- Revenue reports
- Top-customer reports
- Retention summaries
- Custom date ranges
- Previous-period comparisons
- Empty-result handling
- Invalid-input handling
- Database-error handling

The CLI uses only Python standard-library modules, including `sqlite3`, `argparse`, `datetime`, and `pathlib`.

### Monthly Summary

```bash
python scripts/report_cli.py --report monthly --start-date 2026-01-01 --end-date 2026-06-30
```

### Weekly Revenue

```bash
python scripts/report_cli.py --report revenue --period weekly --start-date 2026-06-01 --end-date 2026-06-30
```

### Top Customers

```bash
python scripts/report_cli.py --report top_customers --start-date 2026-01-01 --end-date 2026-06-30
```

### Retention Summary

```bash
python scripts/report_cli.py --report retention --start-date 2026-01-01 --end-date 2026-06-30
```

## Edge-Case Testing

The test suite verifies:

1. Order item referencing a non-existent order
2. Discount percentage greater than 100
3. Quantity equal to zero
4. Order date in the future
5. Empty order result
6. Single-customer summary
7. Invalid date range

Run the tests using:

```bash
python tests/test_edge_cases.py
```

Expected result:

```text
Ran 7 tests
OK
```

## Project Structure

```text
ecommerce-analytics-system/
│
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   └── order_items.csv
│   │
│   └── cleaned/
│       ├── customers_clean.csv
│       ├── products_clean.csv
│       ├── orders_clean.csv
│       └── order_items_clean.csv
│
├── database/
│   └── ecommerce.db
│
├── scripts/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── load_database.py
│   └── report_cli.py
│
├── sql/
│   ├── schema.sql
│   ├── aggregations.sql
│   ├── window_functions.sql
│   ├── cohort_analysis.sql
│   └── customer_segmentation.sql
│
├── tests/
│   └── test_edge_cases.py
│
├── output/
│   ├── data_quality_report.txt
│   └── sample_reports/
│       ├── monthly_summary.txt
│       ├── weekly_revenue.txt
│       ├── top_customers.txt
│       └── retention_summary.txt
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Execution

### 1. Create the virtual environment

```bash
py -3.12 -m venv .venv
```

### 2. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Generate raw datasets

```bash
python scripts/generate_data.py
```

### 5. Clean and validate the data

```bash
python scripts/clean_data.py
```

### 6. Create and load the database

```bash
python scripts/load_database.py
```

### 7. Generate a report

```bash
python scripts/report_cli.py --report monthly --start-date 2026-01-01 --end-date 2026-06-30
```

### 8. Run edge-case tests

```bash
python tests/test_edge_cases.py
```

## Sample Reports

- [Monthly summary](output/sample_reports/monthly_summary.txt)
- [Weekly revenue](output/sample_reports/weekly_revenue.txt)
- [Top customers](output/sample_reports/top_customers.txt)
- [Retention summary](output/sample_reports/retention_summary.txt)

## Assumptions

- Cancelled orders are excluded from revenue calculations.
- Negative quantities represent returned units and reduce net revenue.
- Since item-level delivery status is unavailable, delivery analysis uses `orders.status`.
- Missing customer IDs are mapped to `CUST_UNKNOWN`.
- Cohort retention is calculated against the total registered cohort size.
- Return rate is calculated as returned units divided by purchased units.
- Revenue is calculated as:

```text
quantity × unit_price × (1 - discount_percent / 100)
```

## Technologies Used

- Python
- Pandas
- Faker
- SQLite
- SQL
- Git and GitHub

### Monthly CLI Report

![Monthly CLI Report](output/sample_reports/monthly_summary.png)

### Edge-Case Test Results

![Edge-Case Test Results](output/sample_reports/edge_case_tests.png)