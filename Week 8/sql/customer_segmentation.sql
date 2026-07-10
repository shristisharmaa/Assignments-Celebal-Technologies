-- Customer segmentation by frequency and spending

WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.customer_type,

        COUNT(
            DISTINCT o.order_id
        ) AS total_orders,

        COALESCE(
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_percent / 100.0)
            ),
            0
        ) AS total_spend

    FROM customers AS c

    LEFT JOIN orders AS o
        ON c.customer_id = o.customer_id
       AND o.status <> 'CANCELLED'

    LEFT JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE c.customer_id <> 'CUST_UNKNOWN'

    GROUP BY
        c.customer_id,
        c.customer_name,
        c.customer_type
)

SELECT
    customer_id,
    customer_name,
    customer_type,
    total_orders,

    ROUND(
        total_spend,
        2
    ) AS total_spend,

    CASE
        WHEN total_orders = 0
            THEN 'Never Purchased'
        WHEN total_orders = 1
            THEN 'One-Time'
        WHEN total_orders BETWEEN 2 AND 4
            THEN 'Occasional'
        ELSE 'Loyal'
    END AS frequency_segment,

    CASE
        WHEN total_spend < 250000
            THEN 'Low'
        WHEN total_spend < 750000
            THEN 'Medium'
        ELSE 'High'
    END AS spend_tier

FROM customer_metrics

ORDER BY total_spend DESC;


-- RFM-style customer analysis

WITH latest_date AS (
    SELECT
        MAX(DATE(order_date)) AS analysis_date
    FROM orders
    WHERE status <> 'CANCELLED'
),

rfm_metrics AS (
    SELECT
        c.customer_id,

        CAST(
            JULIANDAY(latest.analysis_date)
            - JULIANDAY(MAX(DATE(o.order_date)))
            AS INTEGER
        ) AS recency_days,

        COUNT(
            DISTINCT o.order_id
        ) AS frequency,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS monetary

    FROM customers AS c

    JOIN orders AS o
        ON c.customer_id = o.customer_id
       AND o.status <> 'CANCELLED'

    JOIN order_items AS oi
        ON o.order_id = oi.order_id

    CROSS JOIN latest_date AS latest

    WHERE c.customer_id <> 'CUST_UNKNOWN'

    GROUP BY
        c.customer_id,
        latest.analysis_date
),

rfm_scores AS (
    SELECT
        customer_id,
        recency_days,
        frequency,
        monetary,

        NTILE(4) OVER (
            ORDER BY recency_days DESC
        ) AS recency_score,

        NTILE(4) OVER (
            ORDER BY frequency
        ) AS frequency_score,

        NTILE(4) OVER (
            ORDER BY monetary
        ) AS monetary_score

    FROM rfm_metrics
)

SELECT
    customer_id,
    recency_days,
    frequency,

    ROUND(
        monetary,
        2
    ) AS monetary,

    recency_score,
    frequency_score,
    monetary_score,

    CAST(recency_score AS TEXT)
        || CAST(frequency_score AS TEXT)
        || CAST(monetary_score AS TEXT)
        AS rfm_code,

    CASE
        WHEN recency_score >= 3
         AND frequency_score >= 3
         AND monetary_score >= 3
            THEN 'Champion'

        WHEN frequency_score >= 3
         AND monetary_score >= 2
            THEN 'Loyal'

        WHEN recency_score = 1
         AND frequency_score >= 2
            THEN 'At Risk'

        WHEN frequency = 1
         AND recency_score >= 3
            THEN 'New Customer'

        ELSE 'Regular'
    END AS rfm_segment

FROM rfm_scores

ORDER BY monetary DESC;


-- Churned, active and repeat-customer identification

WITH latest_date AS (
    SELECT
        MAX(DATE(order_date)) AS analysis_date
    FROM orders
    WHERE status <> 'CANCELLED'
),

customer_orders AS (
    SELECT
        c.customer_id,
        c.customer_name,

        COUNT(
            DISTINCT o.order_id
        ) AS total_orders,

        MAX(
            DATE(o.order_date)
        ) AS last_order_date

    FROM customers AS c

    LEFT JOIN orders AS o
        ON c.customer_id = o.customer_id
       AND o.status <> 'CANCELLED'

    WHERE c.customer_id <> 'CUST_UNKNOWN'

    GROUP BY
        c.customer_id,
        c.customer_name
)

SELECT
    customer.customer_id,
    customer.customer_name,
    customer.total_orders,
    customer.last_order_date,

    CASE
        WHEN customer.total_orders = 0
            THEN 'Never Purchased'
        WHEN customer.total_orders = 1
            THEN 'One-Time'
        ELSE 'Repeat'
    END AS purchase_behavior,

    CASE
        WHEN customer.total_orders = 0
            THEN 'Inactive'

        WHEN JULIANDAY(latest.analysis_date)
             - JULIANDAY(customer.last_order_date) > 90
            THEN 'Churned'

        ELSE 'Active'
    END AS activity_status

FROM customer_orders AS customer

CROSS JOIN latest_date AS latest

ORDER BY
    customer.total_orders DESC,
    customer.customer_id;