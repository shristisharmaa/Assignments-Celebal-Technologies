-- 7. Running total of revenue per region and date

WITH daily_revenue AS (
    SELECT
        o.region_code,
        DATE(o.order_date) AS order_date,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS daily_revenue

    FROM orders AS o

    JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE o.status <> 'CANCELLED'

    GROUP BY
        o.region_code,
        DATE(o.order_date)
)

SELECT
    region_code,
    order_date,
    ROUND(daily_revenue, 2) AS daily_revenue,

    ROUND(
        SUM(daily_revenue) OVER (
            PARTITION BY region_code
            ORDER BY order_date
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ),
        2
    ) AS running_total

FROM daily_revenue
ORDER BY region_code, order_date;


-- 8. Rank products by revenue within each category

WITH product_revenue AS (
    SELECT
        p.category,
        p.product_id,
        p.product_name,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS total_revenue

    FROM products AS p

    JOIN order_items AS oi
        ON p.product_id = oi.product_id

    JOIN orders AS o
        ON oi.order_id = o.order_id

    WHERE o.status <> 'CANCELLED'

    GROUP BY
        p.category,
        p.product_id,
        p.product_name
)

SELECT
    category,
    product_name,
    ROUND(total_revenue, 2) AS total_revenue,

    DENSE_RANK() OVER (
        PARTITION BY category
        ORDER BY total_revenue DESC
    ) AS rank_in_category

FROM product_revenue

ORDER BY
    category,
    rank_in_category,
    product_name;


-- 9. Gap between consecutive orders and risk status

WITH ordered_customer_orders AS (
    SELECT
        customer_id,
        order_id,
        DATE(order_date) AS order_date,

        LAG(DATE(order_date)) OVER (
            PARTITION BY customer_id
            ORDER BY order_date, order_id
        ) AS previous_order_date

    FROM orders

    WHERE customer_id <> 'CUST_UNKNOWN'
),

order_gaps AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        previous_order_date,

        CAST(
            JULIANDAY(order_date)
            - JULIANDAY(previous_order_date)
            AS INTEGER
        ) AS days_gap

    FROM ordered_customer_orders
),

average_gaps AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        previous_order_date,
        days_gap,

        AVG(days_gap) OVER (
            PARTITION BY customer_id
        ) AS average_days_gap

    FROM order_gaps
)

SELECT
    customer_id,
    order_date,
    previous_order_date,
    days_gap,
    ROUND(average_days_gap, 2) AS average_days_gap,

    CASE
        WHEN average_days_gap > 30
            THEN 'At Risk'
        ELSE 'Active'
    END AS customer_status

FROM average_gaps

ORDER BY
    customer_id,
    order_date;


-- 10. Monthly customer revenue categories using CTEs

WITH monthly_customer_revenue AS (
    SELECT
        STRFTIME(
            '%Y-%m',
            o.order_date
        ) AS revenue_month,

        o.customer_id,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS monthly_revenue

    FROM orders AS o

    JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE o.status <> 'CANCELLED'
      AND o.customer_id <> 'CUST_UNKNOWN'

    GROUP BY
        STRFTIME('%Y-%m', o.order_date),
        o.customer_id
),

customer_value_groups AS (
    SELECT
        revenue_month,
        customer_id,
        monthly_revenue,

        CASE
            WHEN monthly_revenue > 10000
                THEN 'High'
            WHEN monthly_revenue >= 5000
                THEN 'Medium'
            ELSE 'Low'
        END AS value_category

    FROM monthly_customer_revenue
)

SELECT
    revenue_month,
    value_category,
    COUNT(*) AS customer_count

FROM customer_value_groups

GROUP BY
    revenue_month,
    value_category

ORDER BY
    revenue_month,

    CASE value_category
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        ELSE 3
    END;


-- 11. Customer lifetime-value quartiles using NTILE

WITH customer_lifetime_value AS (
    SELECT
        c.customer_id,

        ROUND(
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_percent / 100.0)
            ),
            2
        ) AS total_value

    FROM customers AS c

    JOIN orders AS o
        ON c.customer_id = o.customer_id

    JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE o.status <> 'CANCELLED'
      AND c.customer_id <> 'CUST_UNKNOWN'

    GROUP BY c.customer_id
),

customer_quartiles AS (
    SELECT
        customer_id,
        total_value,

        NTILE(4) OVER (
            ORDER BY total_value DESC
        ) AS quartile

    FROM customer_lifetime_value
)

SELECT
    customer_id,
    total_value,
    quartile,

    CASE quartile
        WHEN 1 THEN 'Platinum'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        ELSE 'Bronze'
    END AS quartile_label

FROM customer_quartiles

ORDER BY
    quartile,
    total_value DESC;


-- 12. Year-over-year monthly revenue comparison

WITH monthly_revenue AS (
    SELECT
        CAST(
            STRFTIME('%Y', o.order_date)
            AS INTEGER
        ) AS revenue_year,

        CAST(
            STRFTIME('%m', o.order_date)
            AS INTEGER
        ) AS revenue_month,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS revenue

    FROM orders AS o

    JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE o.status <> 'CANCELLED'

    GROUP BY
        STRFTIME('%Y', o.order_date),
        STRFTIME('%m', o.order_date)
)

SELECT
    current.revenue_year AS year,
    current.revenue_month AS month,
    ROUND(current.revenue, 2) AS revenue,

    ROUND(
        previous.revenue,
        2
    ) AS previous_year_revenue,

    CASE
        WHEN previous.revenue IS NULL
          OR previous.revenue = 0
            THEN NULL

        ELSE ROUND(
            100.0
            * (current.revenue - previous.revenue)
            / previous.revenue,
            2
        )
    END AS yoy_growth_percent

FROM monthly_revenue AS current

LEFT JOIN monthly_revenue AS previous
    ON previous.revenue_year
        = current.revenue_year - 1

   AND previous.revenue_month
        = current.revenue_month

ORDER BY
    current.revenue_year,
    current.revenue_month;


-- 13. First and recent purchased category

WITH purchase_events AS (
    SELECT DISTINCT
        o.customer_id,
        o.order_id,
        o.order_date,
        p.category

    FROM orders AS o

    JOIN order_items AS oi
        ON o.order_id = oi.order_id

    JOIN products AS p
        ON oi.product_id = p.product_id

    WHERE o.status <> 'CANCELLED'
      AND o.customer_id <> 'CUST_UNKNOWN'
),

category_history AS (
    SELECT
        customer_id,

        FIRST_VALUE(category) OVER (
            PARTITION BY customer_id
            ORDER BY
                order_date,
                order_id,
                category
        ) AS first_category,

        LAST_VALUE(category) OVER (
            PARTITION BY customer_id
            ORDER BY
                order_date,
                order_id,
                category

            ROWS BETWEEN UNBOUNDED PRECEDING
            AND UNBOUNDED FOLLOWING
        ) AS recent_category

    FROM purchase_events
)

SELECT DISTINCT
    customer_id,
    first_category,
    recent_category,

    CASE
        WHEN first_category <> recent_category
            THEN 'Yes'
        ELSE 'No'
    END AS category_shift

FROM category_history

ORDER BY customer_id;


-- 14. Cumulative customer revenue distribution

WITH customer_revenue AS (
    SELECT
        o.customer_id,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS revenue

    FROM orders AS o

    JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE o.status <> 'CANCELLED'
      AND o.customer_id <> 'CUST_UNKNOWN'

    GROUP BY o.customer_id
),

cumulative_values AS (
    SELECT
        customer_id,
        revenue,

        SUM(revenue) OVER (
            ORDER BY revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ) AS cumulative_revenue,

        SUM(revenue) OVER () AS overall_revenue

    FROM customer_revenue
)

SELECT
    customer_id,
    ROUND(revenue, 2) AS revenue,

    ROUND(
        cumulative_revenue,
        2
    ) AS cumulative_revenue,

    ROUND(
        100.0
        * cumulative_revenue
        / overall_revenue,
        2
    ) AS cumulative_percent

FROM cumulative_values

ORDER BY revenue DESC;


-- Extra: Three-month moving average

WITH monthly_totals AS (
    SELECT
        STRFTIME(
            '%Y-%m',
            o.order_date
        ) AS revenue_month,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS monthly_revenue

    FROM orders AS o

    JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE o.status <> 'CANCELLED'

    GROUP BY
        STRFTIME('%Y-%m', o.order_date)
)

SELECT
    revenue_month,

    ROUND(
        monthly_revenue,
        2
    ) AS monthly_revenue,

    ROUND(
        AVG(monthly_revenue) OVER (
            ORDER BY revenue_month
            ROWS BETWEEN 2 PRECEDING
            AND CURRENT ROW
        ),
        2
    ) AS three_month_moving_average

FROM monthly_totals

ORDER BY revenue_month;


-- Extra: Month-over-month revenue growth

WITH monthly_totals AS (
    SELECT
        STRFTIME(
            '%Y-%m',
            o.order_date
        ) AS revenue_month,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS monthly_revenue

    FROM orders AS o

    JOIN order_items AS oi
        ON o.order_id = oi.order_id

    WHERE o.status <> 'CANCELLED'

    GROUP BY
        STRFTIME('%Y-%m', o.order_date)
),

revenue_comparison AS (
    SELECT
        revenue_month,
        monthly_revenue,

        LAG(monthly_revenue) OVER (
            ORDER BY revenue_month
        ) AS previous_month_revenue

    FROM monthly_totals
)

SELECT
    revenue_month,

    ROUND(
        monthly_revenue,
        2
    ) AS monthly_revenue,

    ROUND(
        previous_month_revenue,
        2
    ) AS previous_month_revenue,

    CASE
        WHEN previous_month_revenue IS NULL
          OR previous_month_revenue = 0
            THEN NULL

        ELSE ROUND(
            100.0
            * (
                monthly_revenue
                - previous_month_revenue
            )
            / previous_month_revenue,
            2
        )
    END AS monthly_growth_percent

FROM revenue_comparison

ORDER BY revenue_month;