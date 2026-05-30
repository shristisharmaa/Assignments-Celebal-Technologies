-- Steps: 1.Load dataset into a SQL database.

CREATE DATABASE IF NOT EXISTS SuperstoreDB;
USE SuperstoreDB;

-- 2.Explore table (schema, sample data). 

SELECT COUNT(*) FROM superstore;
SELECT * FROM superstore LIMIT 10;
DESCRIBE superstore;

-- 3.Apply WHERE filters (region, category, date, sales).

SELECT * FROM superstore WHERE region = 'West';
SELECT * FROM superstore WHERE category = 'Furniture';
SELECT * FROM superstore WHERE sales > 500;
SELECT * FROM superstore WHERE YEAR(order_date) = 2017;

-- 4.Use GROUP BY for aggregations (sales, quantity, averages).

SELECT region, SUM(sales) AS total_sales FROM superstore GROUP BY region;
SELECT category, SUM(profit) AS total_profit FROM superstore GROUP BY category;
SELECT sub_category, AVG(discount) AS avg_discount FROM superstore GROUP BY sub_category;
SELECT segment, SUM(quantity) AS total_qty FROM superstore GROUP BY segment;

-- 5.Sort and limit results (top products, top categories).

SELECT * FROM superstore ORDER BY sales DESC LIMIT 10;
SELECT product_name, SUM(profit) AS total_profit FROM superstore GROUP BY product_name ORDER BY total_profit DESC LIMIT 10;
SELECT product_name, SUM(quantity) AS total_qty FROM superstore GROUP BY product_name ORDER BY total_qty DESC LIMIT 10;

-- 6.Solve use cases (monthly trends, top customers, duplicates). 

SELECT DATE_FORMAT(STR_TO_DATE(order_date, '%m/%d/%Y'), '%Y-%m') AS month, SUM(sales) AS total_sales FROM superstore GROUP BY month ORDER BY month;
SELECT customer_name, SUM(sales) AS total_spent FROM superstore GROUP BY customer_name ORDER BY total_spent DESC LIMIT 10;
SELECT * FROM superstore WHERE profit < 0;
SELECT city, SUM(sales) AS total_sales FROM superstore GROUP BY city ORDER BY total_sales DESC;
SELECT discount, AVG(profit) AS avg_profit FROM superstore GROUP BY discount ORDER BY discount;

-- 7.Validate results (row counts, data quality). 

SELECT * FROM superstore WHERE sales IS NULL OR profit IS NULL;
SELECT order_id, COUNT(*) AS order_count FROM superstore GROUP BY order_id HAVING order_count > 1;
SELECT * FROM superstore WHERE sales < 0;
