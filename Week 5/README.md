# Spark Assignment - Data Cleaning, Transformation and Aggregation using PySpark

## Objective

The objective of this assignment is to understand Apache Spark fundamentals and perform data cleaning, transformation, filtering, aggregation, and grouping operations using Spark DataFrames.

---

## Dataset Used

**Sample Superstore Dataset**

The dataset contains sales information including orders, customers, products, regions, sales, discounts, quantity, and profit.

---

## Why Spark?

### Limitations of MapReduce
- Processes data using disk I/O, making it slower.
- Requires multiple stages for complex operations.
- High latency for iterative processing.

### Advantages of Apache Spark
- In-memory processing provides faster execution.
- Supports DataFrames and SQL-like operations.
- Suitable for large-scale data processing.
- Easy to perform transformations and aggregations.

---

## Spark DataFrame Immutability

Spark DataFrames are immutable. Operations such as `filter()`, `select()`, `withColumn()`, and `dropDuplicates()` do not modify the original DataFrame. Instead, Spark creates a new DataFrame containing the transformed data.

---

## Operations Performed

1. Created a Spark Session.
2. Loaded the CSV dataset into a Spark DataFrame.
3. Displayed sample records using `show()`.
4. Inspected column names and schema.
5. Removed duplicate records.
6. Handled missing values using `na.drop()`.
7. Applied filtering conditions on Category, Region, Sales, and Quantity.
8. Renamed the `Sales` column to `TotalSales`.
9. Converted columns to appropriate numeric data types.
10. Performed aggregations using:
    - Count
    - Sum
    - Average
    - Minimum
    - Maximum
11. Used `groupBy()` for category-wise and region-wise analysis.
12. Built a complete data processing pipeline.

---

## Aggregation Operations

The following aggregation functions were performed:

- `count()`
- `sum()`
- `avg()`
- `min()`
- `max()`

These functions were used to summarize and analyze the sales data.

---

## GroupBy Analysis

The following grouping operations were performed:

- Category-wise Total Sales
- Region-wise Average Profit
- Sub-Category-wise Record Count

---

## Wide Transformations and Shuffle

### Wide Transformations
Wide transformations require data movement across partitions. Examples include:

- `groupBy()`
- `join()`
- `reduceByKey()`

### Shuffle
Shuffle is the process of redistributing data across partitions during wide transformations. Excessive shuffling can increase execution time and resource consumption.

---

## Data Processing Pipeline

The complete pipeline followed:

1. Load Dataset
2. Clean Data
3. Filter Records
4. Apply Transformations
5. Perform Aggregations
6. Analyze Results using GroupBy

---

## Steps Performed

1. Loaded the Superstore dataset into a Spark DataFrame.
2. Explored the dataset using `show()`, columns, and schema.
3. Removed duplicate records.
4. Handled missing values.
5. Applied filtering conditions on the dataset.
6. Renamed and transformed columns.
7. Converted data types using casting.
8. Performed aggregation operations.
9. Grouped data using `groupBy()`.
10. Built a complete Spark processing pipeline.

---

## Observations

1. Data cleaning improved data quality and consistency.
2. Filtering helped focus analysis on specific records.
3. Aggregation functions provided summarized business insights.
4. GroupBy operations helped identify sales and profit trends.
5. Spark DataFrames simplified large-scale data processing.
6. Wide transformations involve shuffling and can impact performance.

---

## Technologies Used

- Python
- PySpark
- Jupyter Notebook
- Apache Spark

---

## Project Structure

```text
spark-assignment/
│
├── data/
│   └── dataset.csv
│
├── notebook/
│   └── spark_basics.ipynb
│
├── output/
│   └── results.csv
│
└── README.md
```

## Conclusion

This assignment demonstrated how Apache Spark can be used for data cleaning, transformation, filtering, aggregation, and analytical processing using DataFrames. Spark's in-memory processing and DataFrame API make it efficient for handling large datasets and performing data analysis.
