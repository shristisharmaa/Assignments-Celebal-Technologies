# Spark Assignment - Data Cleaning, Transformation and Aggregation using PySpark

---

## Objective

The objective of this assignment is to understand Apache Spark fundamentals and perform data cleaning, transformation, filtering, aggregation, and grouping operations using Spark DataFrames.

---

## Dataset Used

### Sample Superstore Dataset
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

- Created a Spark Session.
- Loaded the CSV dataset into a Spark DataFrame.
- Displayed sample records using `show()`.
- Inspected column names and schema.
- Removed duplicate records.
- Handled missing values using `na.drop()`.
- Applied filtering conditions on Category, Region, Sales, and Quantity.
- Renamed the Sales column to TotalSales.
- Converted columns to appropriate numeric data types.
- Performed aggregations using Count, Sum, Average, Minimum, and Maximum.
- Used `groupBy()` for category-wise and region-wise analysis.
- Built a complete data processing pipeline.

---

## Aggregation Operations

The following aggregation functions were used:

- `count()`
- `sum()`
- `avg()`
- `min()`
- `max()`

These functions help summarize and analyze the dataset efficiently.

---

## GroupBy Analysis

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

Shuffle is the process of redistributing data across partitions during wide transformations. It can impact performance due to data movement across the cluster.

---

## Data Processing Pipeline
