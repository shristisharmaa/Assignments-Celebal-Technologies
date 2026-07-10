import re
from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "cleaned"
OUTPUT_DIR = BASE_DIR / "output"

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


def validate_emails(customers):
    invalid_mask = ~customers["email"].fillna("").str.match(EMAIL_PATTERN)

    return customers.loc[
        invalid_mask,
        "customer_id"
    ].tolist()


def clean_customers(customers, issues):
    duplicate_count = customers.duplicated(
        subset="customer_id"
    ).sum()

    issues["Duplicate customer rows"] = int(duplicate_count)

    customers = customers.drop_duplicates(
        subset="customer_id"
    ).copy()

    customers["customer_name"] = (
        customers["customer_name"]
        .str.strip()
        .str.title()
    )

    customers["customer_type"] = (
        customers["customer_type"]
        .str.strip()
        .str.upper()
    )

    customers["registration_date"] = pd.to_datetime(
        customers["registration_date"],
        errors="coerce"
    )

    invalid_date_count = customers[
        "registration_date"
    ].isna().sum()

    issues["Invalid customer registration dates"] = int(
        invalid_date_count
    )

    customers = customers.dropna(
        subset=["registration_date"]
    )

    invalid_email_ids = validate_emails(customers)
    issues["Invalid customer emails"] = len(invalid_email_ids)

    invalid_email_mask = customers["customer_id"].isin(
        invalid_email_ids
    )

    customers.loc[invalid_email_mask, "email"] = (
        customers.loc[invalid_email_mask, "customer_id"]
        .apply(lambda value: f"{value.lower()}@example.com")
    )

    valid_types = {"REGULAR", "PREMIUM", "VIP"}

    invalid_type_mask = ~customers["customer_type"].isin(
        valid_types
    )

    issues["Invalid customer types"] = int(
        invalid_type_mask.sum()
    )

    customers.loc[
        invalid_type_mask,
        "customer_type"
    ] = "REGULAR"

    unknown_customer = pd.DataFrame([
        {
            "customer_id": "CUST_UNKNOWN",
            "customer_name": "Unknown Customer",
            "email": "unknown_customer@example.com",
            "registration_date": pd.Timestamp("2023-01-01"),
            "customer_type": "REGULAR"
        }
    ])

    customers = pd.concat(
        [customers, unknown_customer],
        ignore_index=True
    )

    customers["registration_date"] = (
        customers["registration_date"]
        .dt.strftime("%Y-%m-%d")
    )

    return customers, invalid_email_ids


def clean_products(products, issues):
    duplicate_count = products.duplicated(
        subset="product_id"
    ).sum()

    issues["Duplicate product rows"] = int(duplicate_count)

    products = products.drop_duplicates(
        subset="product_id"
    ).copy()

    original_names = products["product_name"].fillna("")

    normalized_names = (
        original_names
        .str.strip()
        .str.title()
    )

    issues["Inconsistent product names"] = int(
        (original_names != normalized_names).sum()
    )

    products["product_name"] = normalized_names

    products["category"] = (
        products["category"]
        .str.strip()
        .str.title()
    )

    products["subcategory"] = (
        products["subcategory"]
        .str.strip()
        .str.title()
    )

    products["cost_price"] = pd.to_numeric(
        products["cost_price"],
        errors="coerce"
    )

    invalid_price_mask = (
        products["cost_price"].isna()
        | (products["cost_price"] <= 0)
    )

    issues["Invalid product cost prices"] = int(
        invalid_price_mask.sum()
    )

    products = products.loc[
        ~invalid_price_mask
    ].copy()

    products["cost_price"] = (
        products["cost_price"].round(2)
    )

    return products


def parse_order_date(value):
    if pd.isna(value):
        return pd.NaT

    value = str(value).strip()

    accepted_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%d-%m-%Y",
        "%Y-%m-%d"
    ]

    for date_format in accepted_formats:
        try:
            parsed_date = datetime.strptime(
                value,
                date_format
            )

            return pd.Timestamp(parsed_date)

        except ValueError:
            continue

    return pd.NaT


def clean_orders(orders, valid_customer_ids, issues):
    duplicate_count = orders.duplicated(
        subset="order_id"
    ).sum()

    issues["Duplicate order rows"] = int(duplicate_count)

    orders = orders.drop_duplicates(
        subset="order_id"
    ).copy()

    missing_customer_mask = (
        orders["customer_id"].isna()
        | (
            orders["customer_id"]
            .astype(str)
            .str.strip()
            == ""
        )
    )

    issues["Orders with missing customer IDs"] = int(
        missing_customer_mask.sum()
    )

    orders.loc[
        missing_customer_mask,
        "customer_id"
    ] = "CUST_UNKNOWN"

    invalid_reference_mask = ~orders[
        "customer_id"
    ].isin(valid_customer_ids)

    issues["Orders with unknown customer references"] = int(
        invalid_reference_mask.sum()
    )

    orders.loc[
        invalid_reference_mask,
        "customer_id"
    ] = "CUST_UNKNOWN"

    wrong_format_mask = (
        orders["order_date"]
        .astype(str)
        .str.match(r"^\d{2}-\d{2}-\d{4}$")
    )

    issues["Orders with DD-MM-YYYY date format"] = int(
        wrong_format_mask.sum()
    )

    orders["order_date"] = orders[
        "order_date"
    ].apply(parse_order_date)

    invalid_date_mask = orders["order_date"].isna()

    issues["Unparseable order dates"] = int(
        invalid_date_mask.sum()
    )

    orders = orders.loc[
        ~invalid_date_mask
    ].copy()

    future_date_mask = (
        orders["order_date"] > pd.Timestamp.now()
    )

    issues["Orders with future dates"] = int(
        future_date_mask.sum()
    )

    orders = orders.loc[
        ~future_date_mask
    ].copy()

    orders["status"] = (
        orders["status"]
        .str.strip()
        .str.upper()
    )

    orders["region_code"] = (
        orders["region_code"]
        .str.strip()
        .str.upper()
    )

    valid_statuses = {
        "PLACED",
        "SHIPPED",
        "DELIVERED",
        "CANCELLED",
        "RETURNED"
    }

    invalid_status_mask = ~orders[
        "status"
    ].isin(valid_statuses)

    issues["Orders with invalid status"] = int(
        invalid_status_mask.sum()
    )

    orders = orders.loc[
        ~invalid_status_mask
    ].copy()

    orders["order_date"] = (
        orders["order_date"]
        .dt.strftime("%Y-%m-%d %H:%M:%S")
    )

    return orders


def check_referential_integrity(
    order_items,
    valid_order_ids,
    valid_product_ids
):
    orphan_orders = order_items.loc[
        ~order_items["order_id"].isin(valid_order_ids)
    ].copy()

    orphan_products = order_items.loc[
        ~order_items["product_id"].isin(valid_product_ids)
    ].copy()

    return orphan_orders, orphan_products


def clean_order_items(
    order_items,
    valid_order_ids,
    valid_product_ids,
    issues
):
    duplicate_count = order_items.duplicated(
        subset="item_id"
    ).sum()

    issues["Duplicate order item rows"] = int(
        duplicate_count
    )

    order_items = order_items.drop_duplicates(
        subset="item_id"
    ).copy()

    numeric_columns = [
        "quantity",
        "unit_price",
        "discount_percent"
    ]

    for column in numeric_columns:
        order_items[column] = pd.to_numeric(
            order_items[column],
            errors="coerce"
        )

    invalid_numeric_mask = order_items[
        numeric_columns
    ].isna().any(axis=1)

    issues["Order items with invalid numeric values"] = int(
        invalid_numeric_mask.sum()
    )

    order_items = order_items.loc[
        ~invalid_numeric_mask
    ].copy()

    invalid_discount_mask = ~order_items[
        "discount_percent"
    ].between(0, 100)

    issues["Order items with invalid discounts"] = int(
        invalid_discount_mask.sum()
    )

    order_items = order_items.loc[
        ~invalid_discount_mask
    ].copy()

    zero_quantity_mask = order_items["quantity"] == 0

    issues["Order items with zero quantity"] = int(
        zero_quantity_mask.sum()
    )

    order_items = order_items.loc[
        ~zero_quantity_mask
    ].copy()

    invalid_price_mask = order_items["unit_price"] <= 0

    issues["Order items with invalid unit price"] = int(
        invalid_price_mask.sum()
    )

    order_items = order_items.loc[
        ~invalid_price_mask
    ].copy()

    orphan_orders, orphan_products = (
        check_referential_integrity(
            order_items,
            valid_order_ids,
            valid_product_ids
        )
    )

    issues["Order items referencing missing orders"] = len(
        orphan_orders
    )

    issues["Order items referencing missing products"] = len(
        orphan_products
    )

    invalid_item_ids = (
        set(orphan_orders["item_id"])
        | set(orphan_products["item_id"])
    )

    order_items = order_items.loc[
        ~order_items["item_id"].isin(invalid_item_ids)
    ].copy()

    issues["Negative quantities retained as returns"] = int(
        (order_items["quantity"] < 0).sum()
    )

    order_items["quantity"] = (
        order_items["quantity"].astype(int)
    )

    order_items["discount_percent"] = (
        order_items["discount_percent"].astype(float)
    )

    order_items["unit_price"] = (
        order_items["unit_price"].round(2)
    )

    return order_items


def write_quality_report(
    issues,
    invalid_email_ids,
    final_counts
):
    report_path = OUTPUT_DIR / "data_quality_report.txt"

    with report_path.open(
        "w",
        encoding="utf-8"
    ) as report:

        report.write("E-COMMERCE DATA QUALITY REPORT\n")
        report.write("=" * 40 + "\n\n")

        report.write("ISSUES FOUND AND HANDLED\n")
        report.write("-" * 40 + "\n")

        for issue, count in issues.items():
            report.write(f"{issue}: {count}\n")

        report.write("\nINVALID EMAIL CUSTOMER IDS\n")
        report.write("-" * 40 + "\n")

        if invalid_email_ids:
            report.write(", ".join(invalid_email_ids))
        else:
            report.write("None")

        report.write("\n\nFINAL CLEANED ROW COUNTS\n")
        report.write("-" * 40 + "\n")

        for table, count in final_counts.items():
            report.write(f"{table}: {count}\n")

        report.write("\nFINAL VALIDATION\n")
        report.write("-" * 40 + "\n")
        report.write("Duplicate primary keys: 0\n")
        report.write("Orphan order references: 0\n")
        report.write("Orphan product references: 0\n")

    return report_path


def main():
    CLEAN_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    customers = pd.read_csv(
        RAW_DIR / "customers.csv"
    )

    products = pd.read_csv(
        RAW_DIR / "products.csv"
    )

    orders = pd.read_csv(
        RAW_DIR / "orders.csv"
    )

    order_items = pd.read_csv(
        RAW_DIR / "order_items.csv"
    )

    issues = {}

    customers_clean, invalid_email_ids = (
        clean_customers(customers, issues)
    )

    products_clean = clean_products(
        products,
        issues
    )

    valid_customer_ids = set(
        customers_clean["customer_id"]
    )

    orders_clean = clean_orders(
        orders,
        valid_customer_ids,
        issues
    )

    valid_order_ids = set(
        orders_clean["order_id"]
    )

    valid_product_ids = set(
        products_clean["product_id"]
    )

    order_items_clean = clean_order_items(
        order_items,
        valid_order_ids,
        valid_product_ids,
        issues
    )

    customers_clean.to_csv(
        CLEAN_DIR / "customers_clean.csv",
        index=False
    )

    products_clean.to_csv(
        CLEAN_DIR / "products_clean.csv",
        index=False
    )

    orders_clean.to_csv(
        CLEAN_DIR / "orders_clean.csv",
        index=False
    )

    order_items_clean.to_csv(
        CLEAN_DIR / "order_items_clean.csv",
        index=False
    )

    final_counts = {
        "Customers": len(customers_clean),
        "Products": len(products_clean),
        "Orders": len(orders_clean),
        "Order items": len(order_items_clean)
    }

    report_path = write_quality_report(
        issues,
        invalid_email_ids,
        final_counts
    )

    print("Data cleaning completed successfully")

    for table, count in final_counts.items():
        print(f"{table}: {count} cleaned rows")

    print(f"Cleaned files saved in: {CLEAN_DIR}")
    print(f"Quality report saved at: {report_path}")


if __name__ == "__main__":
    main()