-- SQL Assignment: SQL-based Data Analysis using Filtering, Aggregation, and Business Queries

-- Step 1: Setup Environment

CREATE DATABASE IF NOT EXISTS SuperstoreDB;
USE SuperstoreDB;

-- =====================================================
-- Section A: Data Exploration
-- =====================================================

-- Explore table structure and sample data

SELECT COUNT(*) AS total_records
FROM superstore;

SELECT *
FROM superstore
LIMIT 10;

DESCRIBE superstore;

-- =====================================================
-- Section B: Data Filtering
-- =====================================================

-- Filter by Region

SELECT *
FROM superstore
WHERE region = 'West';

-- Filter by Category

SELECT *
FROM superstore
WHERE category = 'Furniture';

-- Filter by Sales

SELECT *
FROM superstore
WHERE sales > 500;

-- Filter by Order Year

SELECT *
FROM superstore
WHERE YEAR(order_date) = 2017;

-- =====================================================
-- Section C: Aggregation
-- =====================================================

-- Total Sales by Region

SELECT
    region,
    SUM(sales) AS total_sales
FROM superstore
GROUP BY region;

-- Total Profit by Category

SELECT
    category,
    SUM(profit) AS total_profit
FROM superstore
GROUP BY category;

-- Average Discount by Sub-Category

SELECT
    sub_category,
    AVG(discount) AS avg_discount
FROM superstore
GROUP BY sub_category;

-- Total Quantity by Segment

SELECT
    segment,
    SUM(quantity) AS total_quantity
FROM superstore
GROUP BY segment;

-- =====================================================
-- Section D: Business Queries
-- =====================================================

-- Top Sales Records

SELECT *
FROM superstore
ORDER BY sales DESC
LIMIT 10;

-- Top Products by Profit

SELECT
    product_name,
    SUM(profit) AS total_profit
FROM superstore
GROUP BY product_name
ORDER BY total_profit DESC
LIMIT 10;

-- Top Products by Quantity Sold

SELECT
    product_name,
    SUM(quantity) AS total_quantity
FROM superstore
GROUP BY product_name
ORDER BY total_quantity DESC
LIMIT 10;

-- Monthly Sales Trend

SELECT
    DATE_FORMAT(
        STR_TO_DATE(order_date,'%m/%d/%Y'),
        '%Y-%m'
    ) AS month,
    SUM(sales) AS total_sales
FROM superstore
GROUP BY month
ORDER BY month;

-- Top Customers

SELECT
    customer_name,
    SUM(sales) AS total_spent
FROM superstore
GROUP BY customer_name
ORDER BY total_spent DESC
LIMIT 10;

-- Orders with Negative Profit

SELECT *
FROM superstore
WHERE profit < 0;

-- City-wise Sales Analysis

SELECT
    city,
    SUM(sales) AS total_sales
FROM superstore
GROUP BY city
ORDER BY total_sales DESC;

-- Discount vs Average Profit

SELECT
    discount,
    AVG(profit) AS avg_profit
FROM superstore
GROUP BY discount
ORDER BY discount;

-- =====================================================
-- Section E: Data Validation
-- =====================================================

-- Check Missing Values

SELECT *
FROM superstore
WHERE sales IS NULL
OR profit IS NULL;

-- Check Duplicate Orders

SELECT
    order_id,
    COUNT(*) AS order_count
FROM superstore
GROUP BY order_id
HAVING order_count > 1;

-- Check Invalid Sales Values

SELECT *
FROM superstore
WHERE sales < 0;
