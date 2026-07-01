# Delta Lake Assignment - Incremental Data Processing using PySpark

## Objective

The objective of this assignment is to understand incremental data processing using Delta Lake by performing data loading, cleaning, transformation, and MERGE (upsert) operations.

This simulates real-world data engineering scenarios where new data continuously arrives and must be merged with existing datasets efficiently.

---

## Dataset Used

### Sample Superstore Dataset (`sample-superstore.csv`)

The dataset used in this assignment is the Sample Superstore dataset, which contains retail sales transaction data.

It includes:
- Order and shipping details
- Customer information
- Product categories and sub-categories
- Region and segment
- Sales, Profit, Quantity, and Discount

Additionally, an incremental dataset was created from the original dataset to simulate real-time incoming data for MERGE operations.

---

## Why Delta Lake?

### Limitations of Traditional Data Processing
- No built-in support for incremental updates
- Difficult handling of insert and update logic separately
- Risk of data inconsistency in batch processing

### Advantages of Delta Lake
- Supports ACID transactions
- Enables MERGE (upsert) operations
- Provides data versioning (time travel)
- Efficient for large-scale incremental pipelines

---

## Data Processing Pipeline

Load Dataset → Clean Data → Create Incremental Dataset → MERGE into Delta Table → Validate Results → Display Final Output

---

## Operations Performed

- Loaded the Sample Superstore dataset into a Spark DataFrame
- Created a Delta table for storage
- Performed data cleaning (handled null values and removed duplicates)
- Created an incremental dataset to simulate new incoming data
- Applied transformations to modify existing records and add new ones
- Executed MERGE operation using Row_ID as the key
- Updated existing records and inserted new records
- Validated results using row count and duplicate checks
- Displayed final merged dataset

---

## Incremental Data Simulation

A second dataset was created to simulate real-world incremental data:

- Existing records were updated (update scenario)
- New records were introduced (insert scenario)

This represents real-time data ingestion in modern data pipelines.

---

## MERGE Operation (Upsert Logic)

The MERGE operation performs:

- WHEN MATCHED → UPDATE existing records
- WHEN NOT MATCHED → INSERT new records

This ensures:
- Data consistency
- No duplicate records
- Efficient incremental processing

---

## Validation

- Verified total row count after MERGE
- Checked for duplicate Row_ID values
- Confirmed successful updates and inserts in final dataset

---

## Technologies Used

- Python
- PySpark
- Apache Spark
- Delta Lake
- Databricks

---

## Project Structure
Week 7/
│
├── data/
│ ├── sample-superstore.csv
│
├── notebooks/
│ └── Assignment 7 Celebal.ipynb
│
├── screenshots/
│ ├── data_loading/
│ ├── data_cleaning/
│ ├── scd1/
│ ├── scd2/
│ ├── validation/
│ └── final_output/
│
└── README.md


---

## Conclusion

This assignment demonstrates incremental data processing using Delta Lake.

The MERGE operation enables efficient handling of both updates and inserts, making it highly suitable for real-world data engineering pipelines.

Delta Lake ensures reliability, consistency, and scalability in modern big data systems.
