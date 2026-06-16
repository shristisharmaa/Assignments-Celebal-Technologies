##Tasks 
##Step 1: Setup Data
## 1. Import the Superstore dataset into a table named superstore.
USE SuperstoreDB;
SELECT * FROM superstore
LIMIT 5;

## 2.Create these 3 tables from it:  customers , orders , products 
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(100)
);

CREATE TABLE products (
    product_id VARCHAR(50),
    product_name VARCHAR(255),
    category VARCHAR(50),
    sub_category VARCHAR(50)
);

CREATE TABLE orders (
    row_id INT,
    order_id VARCHAR(50),
    order_date VARCHAR(20),
    ship_date VARCHAR(20),
    customer_id VARCHAR(20),
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(5,2),
    profit DECIMAL(10,4)
);

## 3. Insert data into these tables using SELECT DISTINCT.
INSERT INTO customers (customer_id, customer_name)
SELECT DISTINCT
    `Customer ID`,
    `Customer Name`
FROM superstore;

INSERT INTO products (product_id , product_name, category , sub_category)
SELECT DISTINCT
    `Product ID`,
    `Product Name`,
    `Category`,
    `Sub-Category`
FROM superstore;

INSERT INTO orders
SELECT
    `Row ID`,
    `Order ID`,
    `Order Date`,
    `Ship Date`,
    `Customer ID`,
    `Sales`,
    `Quantity`,
    `Discount`,
    `Profit`
FROM superstore;

/*Step 2: Perform Required Queries 

Write and execute SQL queries for each of the following: */

## Query 1 : Find all orders where sales are greater than the average sales. (Subquery) 
SELECT *
FROM orders
WHERE sales >
(
    SELECT AVG(sales)
    FROM orders
); 

## Query 2 : Find the highest sales order for each customer. (Subquery)  
SELECT *
FROM orders o
WHERE sales =
(
    SELECT MAX(sales)
    FROM orders
    WHERE customer_id = o.customer_id
);

## Query 3 : Calculate total sales for each customer. (CTE)  
WITH customer_sales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_sales;

## Query 4 : Find customers whose total sales are above average. (CTE + Subquery)  
WITH customer_sales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_sales
WHERE total_sales >
(
    SELECT AVG(total_sales)
    FROM customer_sales
);

## Query 5: Rank all customers based on total sales. (Window Function)  
WITH customer_sales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT
    customer_id,
    total_sales,
    RANK() OVER (ORDER BY total_sales DESC) AS customer_rank
FROM customer_sales;

##  Query 6: Assign row numbers to each order within a customer. (Window Function + PARTITION BY)  
SELECT
    customer_id,
    order_id,
    sales,
    ROW_NUMBER() OVER
    (
        PARTITION BY customer_id
        ORDER BY sales DESC
    ) AS row_num
FROM orders;

## Query 7: Display top 3 customers based on total sales. (Window Function)  
WITH customer_sales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM
(
    SELECT
        customer_id,
        total_sales,
        RANK() OVER (ORDER BY total_sales DESC) AS customer_rank
    FROM customer_sales
) t
WHERE customer_rank <= 3;

/*Step 3: Final Combined Query 

Write one final query that shows: 

Customer Name  

Total Sales  

Rank  

(Use JOIN + CTE + Window Function together)*/

WITH customer_sales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    cs.total_sales,
    RANK() OVER (ORDER BY cs.total_sales DESC) AS customer_rank
FROM customer_sales cs
JOIN customers c
ON cs.customer_id = c.customer_id;

/*Mini Project: Customer Sales Insights 

Answer the following using SQL:*/

## 1. Who are the top 5 customers?  
WITH customer_sales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    cs.total_sales
FROM customer_sales cs
JOIN customers c
ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales DESC
LIMIT 5;

## 2. Who are the bottom 5 customers?  
WITH customer_sales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    cs.total_sales
FROM customer_sales cs
JOIN customers c
ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales ASC
LIMIT 5;

## 3. Which customers made only one order?  
SELECT
    customer_id,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders
GROUP BY customer_id
HAVING COUNT(DISTINCT order_id) = 1;

## 4. Which customers have above-average sales?
WITH customer_sales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_sales
WHERE total_sales >
(
    SELECT AVG(total_sales)
    FROM customer_sales
);

## 5. What is the highest order value per customer?
SELECT
    customer_id,
    MAX(sales) AS highest_order_value
FROM orders
GROUP BY customer_id;