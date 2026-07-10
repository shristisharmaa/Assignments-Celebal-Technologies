-- 1. Total revenue per category

SELECT
    p.category,
    ROUND(
        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ),
        2
    ) AS total_revenue
FROM order_items AS oi
JOIN orders AS o
    ON oi.order_id = o.order_id
JOIN products AS p
    ON oi.product_id = p.product_id
WHERE o.status <> 'CANCELLED'
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 2. Top 10 customers by total order value

SELECT
    c.customer_id,
    c.customer_name,
    c.customer_type,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(
        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ),
        2
    ) AS total_order_value
FROM customers AS c
JOIN orders AS o
    ON c.customer_id = o.customer_id
JOIN order_items AS oi
    ON o.order_id = oi.order_id
WHERE o.status <> 'CANCELLED'
  AND c.customer_id <> 'CUST_UNKNOWN'
GROUP BY
    c.customer_id,
    c.customer_name,
    c.customer_type
ORDER BY total_order_value DESC
LIMIT 10;


-- 3. Month-wise order count for latest 12 months

WITH latest_order_date AS (
    SELECT MAX(DATE(order_date)) AS max_date
    FROM orders
)
SELECT
    STRFTIME('%Y-%m', o.order_date) AS order_month,
    COUNT(DISTINCT o.order_id) AS order_count
FROM orders AS o
CROSS JOIN latest_order_date AS latest
WHERE DATE(o.order_date) >= DATE(
    latest.max_date,
    'start of month',
    '-11 months'
)
GROUP BY STRFTIME('%Y-%m', o.order_date)
ORDER BY order_month;


-- 4. Customers who ordered but never received a delivered order

SELECT
    c.customer_id,
    c.customer_name,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM customers AS c
JOIN orders AS o
    ON c.customer_id = o.customer_id
WHERE c.customer_id <> 'CUST_UNKNOWN'
GROUP BY
    c.customer_id,
    c.customer_name
HAVING SUM(
    CASE
        WHEN o.status = 'DELIVERED' THEN 1
        ELSE 0
    END
) = 0
ORDER BY total_orders DESC;


-- 5. Products with more returned units than purchased units

SELECT
    p.product_id,
    p.product_name,

    SUM(
        CASE
            WHEN oi.quantity > 0
                THEN oi.quantity
            ELSE 0
        END
    ) AS purchased_units,

    SUM(
        CASE
            WHEN oi.quantity < 0
                THEN ABS(oi.quantity)
            ELSE 0
        END
    ) AS returned_units

FROM products AS p
JOIN order_items AS oi
    ON p.product_id = oi.product_id

GROUP BY
    p.product_id,
    p.product_name

HAVING returned_units > purchased_units
ORDER BY returned_units DESC;


-- 6. Return rate per category

SELECT
    p.category,

    SUM(
        CASE
            WHEN oi.quantity > 0
                THEN oi.quantity
            ELSE 0
        END
    ) AS purchased_units,

    SUM(
        CASE
            WHEN oi.quantity < 0
                THEN ABS(oi.quantity)
            ELSE 0
        END
    ) AS returned_units,

    ROUND(
        100.0
        * SUM(
            CASE
                WHEN oi.quantity < 0
                    THEN ABS(oi.quantity)
                ELSE 0
            END
        )
        / NULLIF(
            SUM(
                CASE
                    WHEN oi.quantity > 0
                        THEN oi.quantity
                    ELSE 0
                END
            ),
            0
        ),
        2
    ) AS return_rate_percent

FROM products AS p
JOIN order_items AS oi
    ON p.product_id = oi.product_id

GROUP BY p.category
ORDER BY return_rate_percent DESC;


-- Extra: Top 10 products by quantity and revenue

SELECT
    p.product_id,
    p.product_name,
    SUM(oi.quantity) AS net_quantity_sold,

    ROUND(
        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ),
        2
    ) AS total_revenue

FROM products AS p
JOIN order_items AS oi
    ON p.product_id = oi.product_id
JOIN orders AS o
    ON oi.order_id = o.order_id

WHERE o.status <> 'CANCELLED'

GROUP BY
    p.product_id,
    p.product_name

ORDER BY total_revenue DESC
LIMIT 10;


-- Extra: Average order value by customer type

WITH order_values AS (
    SELECT
        o.order_id,
        c.customer_type,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS order_value

    FROM orders AS o

    JOIN customers AS c
        ON o.customer_id = c.customer_id

    JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE o.status <> 'CANCELLED'
      AND c.customer_id <> 'CUST_UNKNOWN'

    GROUP BY
        o.order_id,
        c.customer_type
)

SELECT
    customer_type,
    COUNT(*) AS total_orders,
    ROUND(
        AVG(order_value),
        2
    ) AS average_order_value

FROM order_values
GROUP BY customer_type
ORDER BY average_order_value DESC;