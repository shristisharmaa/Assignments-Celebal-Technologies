# Retail E-Commerce Sales Analytics Pipeline

An end-to-end Retail E-Commerce Data Engineering project built using Databricks, PySpark, and Delta Lake following the Medallion Architecture (Bronze → Silver → Gold).

This project processes historical batch data and daily incremental data, performs data quality checks, implements Slowly Changing Dimension (SCD Type 2) tracking, and creates analytics-ready Gold tables for business reporting.

---

## Project Objective

Build a production-style retail analytics pipeline capable of:

- Ingesting historical and incremental retail data
- Handling dirty and inconsistent records
- Managing schema evolution
- Implementing Customer and Product SCD Type 2 dimensions
- Creating a conformed fact table
- Generating business-ready analytics tables
- Demonstrating Delta Lake features

---

## Tech Stack

- Databricks
- PySpark
- Delta Lake
- SQL
- Unity Catalog

---

## Architecture

```text
Raw CSV Files
      │
      ▼
Bronze Layer
(Raw Delta Tables)
      │
      ▼
Silver Stage 1
(Data Cleaning, Casting,
Deduplication, Quarantine)
      │
      ▼
Silver Stage 2
(SCD Type 2 Dimensions)
      │
      ▼
Fact Orders Table
      │
      ▼
Gold Layer
(Daily Sales, Category Sales,
Segment Sales, Region Sales)
```

---

## Dataset Overview

### Historical Batch Files

- orders_batch.csv
- customers_batch.csv
- products_batch.csv
- stores_batch.csv

### Incremental Files

- orders_incremental_YYYY-MM-DD.csv
- customers_cdc_YYYY-MM-DD.csv
- products_cdc_YYYY-MM-DD.csv

### Data Quality Challenges

- Null IDs
- Duplicate records
- Invalid dates
- Invalid numeric values
- Late arriving data
- Schema evolution (coupon_code)

---

# Bronze Layer

Raw ingestion layer that stores source data exactly as received.

### Tables Created

- bronze_orders
- bronze_customers
- bronze_products
- bronze_stores
- bronze_orders_incremental
- bronze_customers_cdc
- bronze_products_cdc

### Features

- Raw Delta storage
- Metadata columns

```text
source_file
ingestion_ts
load_type
```

- Historical auditability

---

# Silver Stage 1

Data quality enforcement layer.

### Operations Performed

### Orders

- Timestamp conversion
- Numeric casting
- Invalid record detection
- Deduplication
- Quarantine handling

### Customers

- Date parsing
- Null handling
- Deduplication

### Products

- Price cleaning
- Date validation
- Deduplication

### Stores

- Duplicate removal

### Tables Created

- silver1_orders_clean
- silver1_customers_clean
- silver1_products_clean

### Quarantine Tables

- quarantine_orders
- quarantine_customers
- quarantine_products

---

# Silver Stage 2 - SCD Type 2

Implemented historical tracking for Customer and Product dimensions.

### SCD2 Columns

- surrogate_key
- effective_start_date
- effective_end_date
- is_current
- hash_value

### Features

- Change detection using hash comparison
- Historical version tracking
- Current record identification
- CDC processing

### Tables Created

- dim_customer_scd2
- dim_product_scd2
- dim_store

---

# Fact Table

### fact_orders

Conformed fact table built using:

- Customer Dimension
- Product Dimension
- Store Dimension

### Features

- Surrogate keys
- Point-in-time joins
- Historical accuracy
- Delta storage

Columns include:

- customer_sk
- product_sk
- store_sk
- quantity
- unit_price
- gross_amount
- order_status

---

# Gold Layer

Business-ready analytics tables.

## 1. Daily Sales

Metrics:

- Total Orders
- Total Revenue
- Total Quantity

Table:

```text
gold_daily_sales
```

---

## 2. Category Sales

Metrics:

- Orders by Category
- Revenue by Category
- Units Sold

Table:

```text
gold_category_sales
```

---

## 3. Segment Sales

Metrics:

- Unique Customers
- Orders
- Revenue

Table:

```text
gold_segment_sales
```

---

## 4. Region Sales

Metrics:

- Orders
- Revenue
- Units Sold

Table:

```text
gold_region_sales
```

---

# Delta Lake Features Demonstrated

### Delta History

```sql
DESCRIBE HISTORY retail_gold.fact_orders
```

### Time Travel

```sql
VERSION AS OF
```

### Schema Evolution

New column introduced:

```text
coupon_code
```

Pipeline successfully handled schema changes without failure.

---

# Final Tables

## Bronze

- bronze_orders
- bronze_customers
- bronze_products
- bronze_stores
- bronze_orders_incremental
- bronze_customers_cdc
- bronze_products_cdc

## Silver

- silver1_orders_clean
- silver1_customers_clean
- silver1_products_clean
- dim_customer_scd2
- dim_product_scd2
- dim_store

## Gold

- fact_orders
- gold_daily_sales
- gold_category_sales
- gold_segment_sales
- gold_region_sales

---

# Key Learnings

- Medallion Architecture
- Delta Lake
- Incremental Processing
- Change Data Capture (CDC)
- Slowly Changing Dimensions (SCD Type 2)
- Data Quality Validation
- Point-in-Time Joins
- Fact and Dimension Modeling
- Business Analytics Engineering

---

# Project Outcome

Successfully built a scalable Retail E-Commerce Analytics Pipeline capable of processing historical and incremental retail data while maintaining data quality, historical accuracy, and analytics-ready reporting using Databricks, PySpark, and Delta Lake.
