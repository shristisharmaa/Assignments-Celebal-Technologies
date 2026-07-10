-- 15. Registration-month cohort and retention analysis

WITH customer_cohorts AS (
    SELECT
        customer_id,
        STRFTIME(
            '%Y-%m',
            registration_date
        ) AS cohort_month
    FROM customers
    WHERE customer_id <> 'CUST_UNKNOWN'
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
),

customer_activity AS (
    SELECT DISTINCT
        cohort.customer_id,
        cohort.cohort_month,
        STRFTIME(
            '%Y-%m',
            o.order_date
        ) AS order_month
    FROM customer_cohorts AS cohort
    JOIN orders AS o
        ON cohort.customer_id = o.customer_id
    WHERE o.status <> 'CANCELLED'
),

activity_by_month AS (
    SELECT
        customer_id,
        cohort_month,
        order_month,

        (
            (
                CAST(
                    SUBSTR(order_month, 1, 4)
                    AS INTEGER
                )
                -
                CAST(
                    SUBSTR(cohort_month, 1, 4)
                    AS INTEGER
                )
            ) * 12

            +

            (
                CAST(
                    SUBSTR(order_month, 6, 2)
                    AS INTEGER
                )
                -
                CAST(
                    SUBSTR(cohort_month, 6, 2)
                    AS INTEGER
                )
            )
        ) AS month_number

    FROM customer_activity
),

cohort_orders AS (
    SELECT
        cohort_month,

        COUNT(
            DISTINCT CASE
                WHEN month_number = 0
                    THEN customer_id
            END
        ) AS month_0_customers,

        COUNT(
            DISTINCT CASE
                WHEN month_number = 1
                    THEN customer_id
            END
        ) AS month_1_customers,

        COUNT(
            DISTINCT CASE
                WHEN month_number = 2
                    THEN customer_id
            END
        ) AS month_2_customers,

        COUNT(
            DISTINCT CASE
                WHEN month_number = 3
                    THEN customer_id
            END
        ) AS month_3_customers

    FROM activity_by_month
    WHERE month_number BETWEEN 0 AND 3
    GROUP BY cohort_month
)

SELECT
    size.cohort_month,
    size.cohort_size,

    COALESCE(
        activity.month_0_customers,
        0
    ) AS month_0_customers,

    COALESCE(
        activity.month_1_customers,
        0
    ) AS month_1_customers,

    COALESCE(
        activity.month_2_customers,
        0
    ) AS month_2_customers,

    COALESCE(
        activity.month_3_customers,
        0
    ) AS month_3_customers,

    ROUND(
        100.0
        * COALESCE(activity.month_0_customers, 0)
        / size.cohort_size,
        2
    ) AS month_0_retention,

    ROUND(
        100.0
        * COALESCE(activity.month_1_customers, 0)
        / size.cohort_size,
        2
    ) AS month_1_retention,

    ROUND(
        100.0
        * COALESCE(activity.month_2_customers, 0)
        / size.cohort_size,
        2
    ) AS month_2_retention,

    ROUND(
        100.0
        * COALESCE(activity.month_3_customers, 0)
        / size.cohort_size,
        2
    ) AS month_3_retention

FROM cohort_sizes AS size

LEFT JOIN cohort_orders AS activity
    ON size.cohort_month = activity.cohort_month

ORDER BY size.cohort_month;


-- 16. Products frequently purchased together

WITH product_pairs AS (
    SELECT
        product_a.product_name AS product_a,
        product_b.product_name AS product_b,

        COUNT(
            DISTINCT item_a.order_id
        ) AS times_bought_together

    FROM order_items AS item_a

    JOIN order_items AS item_b
        ON item_a.order_id = item_b.order_id
       AND item_a.product_id < item_b.product_id

    JOIN orders AS o
        ON item_a.order_id = o.order_id

    JOIN products AS product_a
        ON item_a.product_id = product_a.product_id

    JOIN products AS product_b
        ON item_b.product_id = product_b.product_id

    WHERE item_a.quantity > 0
      AND item_b.quantity > 0
      AND o.status <> 'CANCELLED'

    GROUP BY
        item_a.product_id,
        item_b.product_id,
        product_a.product_name,
        product_b.product_name
),

ranked_pairs AS (
    SELECT
        product_a,
        product_b,
        times_bought_together,

        DENSE_RANK() OVER (
            ORDER BY times_bought_together DESC
        ) AS pair_rank

    FROM product_pairs
)

SELECT
    product_a,
    product_b,
    times_bought_together

FROM ranked_pairs

ORDER BY
    pair_rank,
    product_a,
    product_b

LIMIT 20;