import sqlite3
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = BASE_DIR / "scripts"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"

sys.path.insert(0, str(SCRIPTS_DIR))

from clean_data import clean_orders
from report_cli import get_summary, validate_dates


class EcommerceEdgeCaseTests(unittest.TestCase):

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")

        self.connection.row_factory = sqlite3.Row

        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        schema = SCHEMA_PATH.read_text(
            encoding="utf-8"
        )

        self.connection.executescript(schema)

        self.connection.execute(
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
            (
                "CUST0001",
                "Test Customer",
                "test@example.com",
                "2025-01-01",
                "REGULAR"
            )
        )

        self.connection.execute(
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
            (
                "PROD0001",
                "Test Product",
                "Electronics",
                "Accessories",
                500.0
            )
        )

        self.connection.execute(
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
            (
                "ORD00001",
                "CUST0001",
                "2026-01-15 10:00:00",
                "DELIVERED",
                "NORTH"
            )
        )

    def tearDown(self):
        self.connection.close()

    def test_order_item_with_missing_order_id(self):
        with self.assertRaises(
            sqlite3.IntegrityError
        ):
            self.connection.execute(
                """
                INSERT INTO order_items
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "ITEM00001",
                    "ORD_NOT_FOUND",
                    "PROD0001",
                    1,
                    700.0,
                    10.0
                )
            )

    def test_discount_above_100(self):
        with self.assertRaises(
            sqlite3.IntegrityError
        ):
            self.connection.execute(
                """
                INSERT INTO order_items
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "ITEM00002",
                    "ORD00001",
                    "PROD0001",
                    1,
                    700.0,
                    120.0
                )
            )

    def test_zero_quantity(self):
        with self.assertRaises(
            sqlite3.IntegrityError
        ):
            self.connection.execute(
                """
                INSERT INTO order_items
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "ITEM00003",
                    "ORD00001",
                    "PROD0001",
                    0,
                    700.0,
                    10.0
                )
            )

    def test_future_order_date_is_removed(self):
        future_date = (
            date.today() + timedelta(days=10)
        )

        orders = pd.DataFrame([
            {
                "order_id": "ORD_FUTURE",
                "customer_id": "CUST0001",
                "order_date": future_date.strftime(
                    "%Y-%m-%d"
                ),
                "status": "PLACED",
                "region_code": "NORTH"
            }
        ])

        issues = {}

        cleaned_orders = clean_orders(
            orders,
            {"CUST0001"},
            issues
        )

        self.assertTrue(
            cleaned_orders.empty
        )

        self.assertEqual(
            issues["Orders with future dates"],
            1
        )

    def test_empty_order_result(self):
        self.connection.execute(
            "DELETE FROM orders"
        )

        summary = get_summary(
            self.connection,
            date(2026, 1, 1),
            date(2026, 1, 31)
        )

        self.assertEqual(
            summary["total_orders"],
            0
        )

        self.assertEqual(
            summary["revenue"],
            0
        )

        self.assertEqual(
            summary["unique_customers"],
            0
        )

    def test_single_customer_summary(self):
        self.connection.execute(
            """
            INSERT INTO order_items
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "ITEM00004",
                "ORD00001",
                "PROD0001",
                2,
                700.0,
                10.0
            )
        )

        summary = get_summary(
            self.connection,
            date(2026, 1, 1),
            date(2026, 1, 31)
        )

        self.assertEqual(
            summary["total_orders"],
            1
        )

        self.assertEqual(
            summary["unique_customers"],
            1
        )

        self.assertEqual(
            summary["revenue"],
            1260.0
        )

    def test_invalid_date_range(self):
        with self.assertRaises(ValueError):
            validate_dates(
                "2026-06-30",
                "2026-01-01"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)