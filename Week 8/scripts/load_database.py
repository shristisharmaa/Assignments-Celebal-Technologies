import csv
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_DIR = BASE_DIR / "data" / "cleaned"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "ecommerce.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def read_csv(filename):
    file_path = CLEAN_DIR / filename

    with file_path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        return list(csv.DictReader(file))


def load_customers(connection):
    rows = read_csv("customers_clean.csv")

    values = [
        (
            row["customer_id"],
            row["customer_name"],
            row["email"],
            row["registration_date"],
            row["customer_type"]
        )
        for row in rows
    ]

    connection.executemany(
        """
        INSERT INTO customers (
            customer_id,
            customer_name,
            email,
            registration_date,
            customer_type
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        values
    )


def load_products(connection):
    rows = read_csv("products_clean.csv")

    values = [
        (
            row["product_id"],
            row["product_name"],
            row["category"],
            row["subcategory"],
            float(row["cost_price"])
        )
        for row in rows
    ]

    connection.executemany(
        """
        INSERT INTO products (
            product_id,
            product_name,
            category,
            subcategory,
            cost_price
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        values
    )


def load_orders(connection):
    rows = read_csv("orders_clean.csv")

    values = [
        (
            row["order_id"],
            row["customer_id"],
            row["order_date"],
            row["status"],
            row["region_code"]
        )
        for row in rows
    ]

    connection.executemany(
        """
        INSERT INTO orders (
            order_id,
            customer_id,
            order_date,
            status,
            region_code
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        values
    )


def load_order_items(connection):
    rows = read_csv("order_items_clean.csv")

    values = [
        (
            row["item_id"],
            row["order_id"],
            row["product_id"],
            int(float(row["quantity"])),
            float(row["unit_price"]),
            float(row["discount_percent"])
        )
        for row in rows
    ]

    connection.executemany(
        """
        INSERT INTO order_items (
            item_id,
            order_id,
            product_id,
            quantity,
            unit_price,
            discount_percent
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        values
    )


def verify_database(connection):
    table_names = [
        "customers",
        "products",
        "orders",
        "order_items"
    ]

    print("Database row counts")
    print("-" * 30)

    for table_name in table_names:
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

        print(f"{table_name}: {count}")

    foreign_key_errors = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    if foreign_key_errors:
        print(
            f"Foreign key errors found: "
            f"{len(foreign_key_errors)}"
        )
    else:
        print("Foreign key validation: Passed")


def main():
    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    schema = SCHEMA_PATH.read_text(
        encoding="utf-8"
    )

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute(
                "PRAGMA foreign_keys = ON"
            )

            connection.executescript(schema)

            load_customers(connection)
            load_products(connection)
            load_orders(connection)
            load_order_items(connection)

            verify_database(connection)

        print(
            f"Database created successfully: "
            f"{DATABASE_PATH}"
        )

    except FileNotFoundError as error:
        print(
            f"Required file not found: "
            f"{error.filename}"
        )

    except sqlite3.Error as error:
        print(f"Database error: {error}")

    except ValueError as error:
        print(
            f"Invalid value found while loading data: "
            f"{error}"
        )


if __name__ == "__main__":
    main()