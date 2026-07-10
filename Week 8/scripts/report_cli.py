import argparse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = BASE_DIR / "database" / "ecommerce.db"
DATE_FORMAT = "%Y-%m-%d"

PERIODS = {"daily", "weekly", "monthly"}

REPORTS = PERIODS | {
    "summary",
    "revenue",
    "top_customers",
    "retention"
}


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Generate reports from the "
            "e-commerce order database."
        )
    )

    parser.add_argument(
        "--report",
        required=True,
        choices=sorted(REPORTS),
        help=(
            "Report name or daily/weekly/monthly "
            "summary type."
        )
    )

    parser.add_argument(
        "--period",
        choices=sorted(PERIODS),
        default="monthly",
        help=(
            "Grouping period for revenue reports "
            "(default: monthly)."
        )
    )

    parser.add_argument(
        "--start-date",
        required=True,
        help="Start date in YYYY-MM-DD format."
    )

    parser.add_argument(
        "--end-date",
        required=True,
        help="End date in YYYY-MM-DD format."
    )

    return parser.parse_args()


def validate_dates(start_value, end_value):
    try:
        start_date = datetime.strptime(
            start_value,
            DATE_FORMAT
        ).date()

        end_date = datetime.strptime(
            end_value,
            DATE_FORMAT
        ).date()

    except ValueError as error:
        raise ValueError(
            "Dates must use YYYY-MM-DD format."
        ) from error

    if start_date > end_date:
        raise ValueError(
            "Start date cannot be after end date."
        )

    return start_date, end_date


def previous_period(start_date, end_date):
    period_length = (end_date - start_date).days

    previous_end = start_date - timedelta(days=1)

    previous_start = (
        previous_end - timedelta(days=period_length)
    )

    return previous_start, previous_end


def percentage_change(current_value, previous_value):
    if previous_value == 0:
        return "N/A"

    change = (
        100.0
        * (current_value - previous_value)
        / previous_value
    )

    return f"{change:.2f}%"


def get_summary(connection, start_date, end_date):
    query = """
        SELECT
            COUNT(
                DISTINCT o.order_id
            ) AS total_orders,

            COALESCE(
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (
                        1
                        - oi.discount_percent / 100.0
                    )
                ),
                0
            ) AS revenue,

            COUNT(
                DISTINCT CASE
                    WHEN o.customer_id <> 'CUST_UNKNOWN'
                        THEN o.customer_id
                END
            ) AS unique_customers

        FROM orders AS o

        JOIN order_items AS oi
            ON o.order_id = oi.order_id

        WHERE DATE(o.order_date) BETWEEN ? AND ?
          AND o.status <> 'CANCELLED'
    """

    row = connection.execute(
        query,
        (str(start_date), str(end_date))
    ).fetchone()

    return {
        "total_orders": row["total_orders"],
        "revenue": row["revenue"],
        "unique_customers": row["unique_customers"]
    }


def get_top_products(
    connection,
    start_date,
    end_date,
    limit=3
):
    query = """
        SELECT
            p.product_name,

            SUM(
                oi.quantity
            ) AS net_quantity,

            ROUND(
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (
                        1
                        - oi.discount_percent / 100.0
                    )
                ),
                2
            ) AS revenue

        FROM products AS p

        JOIN order_items AS oi
            ON p.product_id = oi.product_id

        JOIN orders AS o
            ON oi.order_id = o.order_id

        WHERE DATE(o.order_date) BETWEEN ? AND ?
          AND o.status <> 'CANCELLED'

        GROUP BY
            p.product_id,
            p.product_name

        ORDER BY revenue DESC

        LIMIT ?
    """

    return connection.execute(
        query,
        (
            str(start_date),
            str(end_date),
            limit
        )
    ).fetchall()


def get_revenue_breakdown(
    connection,
    start_date,
    end_date,
    period
):
    period_expressions = {
        "daily": "DATE(o.order_date)",

        "weekly": (
            "STRFTIME('%Y-W%W', o.order_date)"
        ),

        "monthly": (
            "STRFTIME('%Y-%m', o.order_date)"
        )
    }

    period_expression = period_expressions[period]

    query = f"""
        SELECT
            {period_expression} AS report_period,

            COUNT(
                DISTINCT o.order_id
            ) AS total_orders,

            ROUND(
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (
                        1
                        - oi.discount_percent / 100.0
                    )
                ),
                2
            ) AS revenue,

            COUNT(
                DISTINCT CASE
                    WHEN o.customer_id <> 'CUST_UNKNOWN'
                        THEN o.customer_id
                END
            ) AS unique_customers

        FROM orders AS o

        JOIN order_items AS oi
            ON o.order_id = oi.order_id

        WHERE DATE(o.order_date) BETWEEN ? AND ?
          AND o.status <> 'CANCELLED'

        GROUP BY {period_expression}

        ORDER BY report_period
    """

    return connection.execute(
        query,
        (str(start_date), str(end_date))
    ).fetchall()


def get_top_customers(
    connection,
    start_date,
    end_date
):
    query = """
        SELECT
            c.customer_id,
            c.customer_name,

            COUNT(
                DISTINCT o.order_id
            ) AS total_orders,

            ROUND(
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (
                        1
                        - oi.discount_percent / 100.0
                    )
                ),
                2
            ) AS total_value

        FROM customers AS c

        JOIN orders AS o
            ON c.customer_id = o.customer_id

        JOIN order_items AS oi
            ON o.order_id = oi.order_id

        WHERE DATE(o.order_date) BETWEEN ? AND ?
          AND o.status <> 'CANCELLED'
          AND c.customer_id <> 'CUST_UNKNOWN'

        GROUP BY
            c.customer_id,
            c.customer_name

        ORDER BY total_value DESC

        LIMIT 10
    """

    return connection.execute(
        query,
        (str(start_date), str(end_date))
    ).fetchall()


def get_retention_summary(
    connection,
    start_date,
    end_date
):
    query = """
        WITH customer_orders AS (
            SELECT
                customer_id,

                COUNT(
                    DISTINCT order_id
                ) AS total_orders

            FROM orders

            WHERE DATE(order_date) BETWEEN ? AND ?
              AND status <> 'CANCELLED'
              AND customer_id <> 'CUST_UNKNOWN'

            GROUP BY customer_id
        )

        SELECT
            COUNT(*) AS purchasing_customers,

            SUM(
                CASE
                    WHEN total_orders = 1 THEN 1
                    ELSE 0
                END
            ) AS one_time_customers,

            SUM(
                CASE
                    WHEN total_orders > 1 THEN 1
                    ELSE 0
                END
            ) AS repeat_customers,

            ROUND(
                100.0
                * SUM(
                    CASE
                        WHEN total_orders > 1 THEN 1
                        ELSE 0
                    END
                )
                / NULLIF(COUNT(*), 0),
                2
            ) AS repeat_customer_rate

        FROM customer_orders
    """

    return connection.execute(
        query,
        (str(start_date), str(end_date))
    ).fetchone()


def print_table(headers, rows):
    rows = [list(row) for row in rows]

    if not rows:
        print(
            "No records found for the "
            "selected date range."
        )
        return

    display_rows = []

    for row in rows:
        display_rows.append([
            "" if value is None else str(value)
            for value in row
        ])

    widths = [
        len(header)
        for header in headers
    ]

    for row in display_rows:
        for index, value in enumerate(row):
            widths[index] = max(
                widths[index],
                len(value)
            )

    separator = (
        "+-"
        + "-+-".join(
            "-" * width
            for width in widths
        )
        + "-+"
    )

    header_line = (
        "| "
        + " | ".join(
            header.ljust(widths[index])
            for index, header in enumerate(headers)
        )
        + " |"
    )

    print(separator)
    print(header_line)
    print(separator)

    for row in display_rows:
        print(
            "| "
            + " | ".join(
                value.ljust(widths[index])
                for index, value in enumerate(row)
            )
            + " |"
        )

    print(separator)


def print_summary(
    connection,
    start_date,
    end_date,
    period
):
    current = get_summary(
        connection,
        start_date,
        end_date
    )

    previous_start, previous_end = previous_period(
        start_date,
        end_date
    )

    previous = get_summary(
        connection,
        previous_start,
        previous_end
    )

    print(
        "\nSUMMARY AND PREVIOUS-PERIOD COMPARISON"
    )

    summary_rows = [
        (
            "Total orders",
            current["total_orders"],
            previous["total_orders"],

            percentage_change(
                current["total_orders"],
                previous["total_orders"]
            )
        ),

        (
            "Revenue",
            f"{current['revenue']:,.2f}",
            f"{previous['revenue']:,.2f}",

            percentage_change(
                current["revenue"],
                previous["revenue"]
            )
        ),

        (
            "Unique customers",
            current["unique_customers"],
            previous["unique_customers"],

            percentage_change(
                current["unique_customers"],
                previous["unique_customers"]
            )
        )
    ]

    print_table(
        [
            "Metric",
            "Current",
            "Previous",
            "Change"
        ],
        summary_rows
    )

    if current["total_orders"] == 0:
        print(
            "No orders found for the "
            "selected date range."
        )
        return

    print("\nTOP 3 PRODUCTS")

    top_products = get_top_products(
        connection,
        start_date,
        end_date
    )

    product_rows = [
        (
            row["product_name"],
            row["net_quantity"],
            f"{row['revenue']:,.2f}"
        )
        for row in top_products
    ]

    print_table(
        [
            "Product",
            "Net quantity",
            "Revenue"
        ],
        product_rows
    )

    print(f"\n{period.upper()} BREAKDOWN")

    breakdown = get_revenue_breakdown(
        connection,
        start_date,
        end_date,
        period
    )

    breakdown_rows = [
        (
            row["report_period"],
            row["total_orders"],
            f"{row['revenue']:,.2f}",
            row["unique_customers"]
        )
        for row in breakdown
    ]

    print_table(
        [
            "Period",
            "Orders",
            "Revenue",
            "Customers"
        ],
        breakdown_rows
    )


def main():
    arguments = parse_arguments()

    try:
        start_date, end_date = validate_dates(
            arguments.start_date,
            arguments.end_date
        )

        if not DATABASE_PATH.exists():
            raise FileNotFoundError(
                "Database not found. Run "
                "scripts/load_database.py first."
            )

        if arguments.report in PERIODS:
            report_name = "summary"
            period = arguments.report
        else:
            report_name = arguments.report
            period = arguments.period

        with sqlite3.connect(
            DATABASE_PATH
        ) as connection:

            connection.row_factory = sqlite3.Row

            print("=" * 65)
            print(
                "E-COMMERCE ORDER ANALYTICS REPORT"
            )
            print(
                "Report: "
                f"{report_name.replace('_', ' ').title()}"
            )
            print(f"Period: {period.title()}")
            print(
                f"Date range: {start_date} to {end_date}"
            )
            print("=" * 65)

            if report_name == "summary":
                print_summary(
                    connection,
                    start_date,
                    end_date,
                    period
                )

            elif report_name == "revenue":
                rows = get_revenue_breakdown(
                    connection,
                    start_date,
                    end_date,
                    period
                )

                formatted_rows = [
                    (
                        row["report_period"],
                        row["total_orders"],
                        f"{row['revenue']:,.2f}",
                        row["unique_customers"]
                    )
                    for row in rows
                ]

                print_table(
                    [
                        "Period",
                        "Orders",
                        "Revenue",
                        "Customers"
                    ],
                    formatted_rows
                )

            elif report_name == "top_customers":
                rows = get_top_customers(
                    connection,
                    start_date,
                    end_date
                )

                formatted_rows = [
                    (
                        row["customer_id"],
                        row["customer_name"],
                        row["total_orders"],
                        f"{row['total_value']:,.2f}"
                    )
                    for row in rows
                ]

                print_table(
                    [
                        "Customer ID",
                        "Name",
                        "Orders",
                        "Total value"
                    ],
                    formatted_rows
                )

            elif report_name == "retention":
                row = get_retention_summary(
                    connection,
                    start_date,
                    end_date
                )

                retention_rows = [
                    (
                        row["purchasing_customers"] or 0,
                        row["one_time_customers"] or 0,
                        row["repeat_customers"] or 0,
                        row["repeat_customer_rate"] or 0
                    )
                ]

                print_table(
                    [
                        "Customers",
                        "One-time",
                        "Repeat",
                        "Repeat rate %"
                    ],
                    retention_rows
                )

    except ValueError as error:
        print(f"Input error: {error}")

    except FileNotFoundError as error:
        print(f"File error: {error}")

    except sqlite3.Error as error:
        print(f"Database error: {error}")


if __name__ == "__main__":
    main()