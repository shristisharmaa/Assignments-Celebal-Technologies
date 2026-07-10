import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker


SEED = 42
CUSTOMER_COUNT = 800
PRODUCT_COUNT = 500
ORDER_COUNT = 1500
ORDER_ITEM_COUNT = 4000

random.seed(SEED)
Faker.seed(SEED)
fake = Faker("en_IN")

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"


def random_datetime(start, end):
    seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, seconds))


def generate_customers():
    customers = []

    for number in range(1, CUSTOMER_COUNT + 1):
        customers.append({
            "customer_id": f"CUST{number:04d}",
            "customer_name": fake.name(),
            "email": fake.unique.email(),
            "registration_date": fake.date_between(
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2025, 12, 31)
            ).strftime("%Y-%m-%d"),
            "customer_type": random.choices(
                ["REGULAR", "PREMIUM", "VIP"],
                weights=[70, 20, 10],
                k=1
            )[0]
        })

    invalid_count = round(CUSTOMER_COUNT * 0.02)
    invalid_indexes = random.sample(range(CUSTOMER_COUNT), invalid_count)

    for position, index in enumerate(invalid_indexes):
        if position % 2 == 0:
            customers[index]["email"] = customers[index]["email"].replace("@", "")
        else:
            username = customers[index]["email"].split("@")[0]
            customers[index]["email"] = username + "@"

    return customers, invalid_count


def generate_products():
    category_map = {
        "Electronics": ["Mobile", "Laptop", "Headphones", "Accessories"],
        "Clothing": ["Men", "Women", "Kids", "Footwear"],
        "Home": ["Kitchen", "Furniture", "Decor", "Bedding"],
        "Books": ["Fiction", "Education", "Business", "Biography"]
    }

    adjectives = [
        "Classic", "Premium", "Smart", "Compact",
        "Modern", "Essential", "Eco", "Comfort"
    ]

    products = []

    for number in range(1, PRODUCT_COUNT + 1):
        category = random.choice(list(category_map))
        subcategory = random.choice(category_map[category])
        product_name = f"{random.choice(adjectives)} {subcategory} {number}"

        products.append({
            "product_id": f"PROD{number:04d}",
            "product_name": product_name,
            "category": category,
            "subcategory": subcategory,
            "cost_price": round(random.uniform(80, 45000), 2)
        })

    inconsistent_count = round(PRODUCT_COUNT * 0.06)
    inconsistent_indexes = random.sample(
        range(PRODUCT_COUNT),
        inconsistent_count
    )

    for position, index in enumerate(inconsistent_indexes):
        name = products[index]["product_name"]

        if position % 3 == 0:
            products[index]["product_name"] = f"  {name}  "
        elif position % 3 == 1:
            products[index]["product_name"] = name.upper()
        else:
            products[index]["product_name"] = name.lower()

    return products, inconsistent_count


def generate_orders(customers):
    customer_registration = {
        row["customer_id"]: datetime.strptime(
            row["registration_date"],
            "%Y-%m-%d"
        )
        for row in customers
    }

    customer_ids = list(customer_registration)
    order_start = datetime(2024, 1, 1)
    order_end = datetime(2026, 6, 30, 23, 59, 59)

    orders = []

    for number in range(1, ORDER_COUNT + 1):
        customer_id = random.choice(customer_ids)
        valid_start = max(
            order_start,
            customer_registration[customer_id]
        )

        order_date = random_datetime(valid_start, order_end)

        orders.append({
            "order_id": f"ORD{number:05d}",
            "customer_id": customer_id,
            "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": random.choices(
                [
                    "PLACED",
                    "SHIPPED",
                    "DELIVERED",
                    "CANCELLED",
                    "RETURNED"
                ],
                weights=[10, 15, 55, 10, 10],
                k=1
            )[0],
            "region_code": random.choice(
                ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]
            )
        })

    missing_count = round(ORDER_COUNT * 0.05)

    for index in random.sample(range(ORDER_COUNT), missing_count):
        orders[index]["customer_id"] = None

    wrong_date_count = round(ORDER_COUNT * 0.03)
    wrong_date_indexes = random.sample(
        range(ORDER_COUNT),
        wrong_date_count
    )

    for index in wrong_date_indexes:
        parsed_date = datetime.strptime(
            orders[index]["order_date"],
            "%Y-%m-%d %H:%M:%S"
        )
        orders[index]["order_date"] = parsed_date.strftime("%d-%m-%Y")

    return orders, missing_count, wrong_date_count


def generate_order_items(orders, products):
    order_ids = [row["order_id"] for row in orders]

    returned_order_ids = {
        row["order_id"]
        for row in orders
        if row["status"] == "RETURNED"
    }

    product_costs = {
        row["product_id"]: row["cost_price"]
        for row in products
    }

    product_ids = list(product_costs)

    selected_orders = order_ids.copy()
    selected_orders.extend(
        random.choices(
            order_ids,
            k=ORDER_ITEM_COUNT - len(selected_orders)
        )
    )
    random.shuffle(selected_orders)

    order_items = []

    for number, order_id in enumerate(selected_orders, start=1):
        product_id = random.choice(product_ids)

        unit_price = (
            product_costs[product_id]
            * random.uniform(1.15, 2.10)
        )

        order_items.append({
            "item_id": f"ITEM{number:05d}",
            "order_id": order_id,
            "product_id": product_id,
            "quantity": random.randint(1, 5),
            "unit_price": round(unit_price, 2),
            "discount_percent": random.choices(
                [0, 5, 10, 15, 20, 25, 30, 40, 50],
                weights=[30, 10, 20, 10, 10, 8, 6, 4, 2],
                k=1
            )[0]
        })

    return_candidates = [
        index
        for index, row in enumerate(order_items)
        if row["order_id"] in returned_order_ids
    ]

    negative_count = round(ORDER_ITEM_COUNT * 0.03)
    negative_indexes = random.sample(
        return_candidates,
        negative_count
    )

    for index in negative_indexes:
        order_items[index]["quantity"] *= -1

    orphan_count = round(ORDER_ITEM_COUNT * 0.01)

    orphan_indexes = random.sample(
        range(ORDER_COUNT, ORDER_ITEM_COUNT),
        orphan_count
    )

    for number, index in enumerate(orphan_indexes, start=1):
        order_items[index]["order_id"] = f"INVALID{number:03d}"

    return order_items, negative_count, orphan_count


def add_duplicates(rows, duplicate_count):
    duplicate_rows = random.sample(rows, duplicate_count)
    copied_rows = [row.copy() for row in duplicate_rows]
    return rows + copied_rows


def save_csv(rows, filename):
    dataframe = pd.DataFrame(rows)
    dataframe.to_csv(RAW_DIR / filename, index=False)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    customers, invalid_emails = generate_customers()
    products, inconsistent_products = generate_products()

    orders, missing_customers, wrong_dates = generate_orders(
        customers
    )

    order_items, negative_quantities, orphan_items = (
        generate_order_items(orders, products)
    )

    customers = add_duplicates(customers, 8)
    products = add_duplicates(products, 5)
    orders = add_duplicates(orders, 15)
    order_items = add_duplicates(order_items, 40)

    save_csv(customers, "customers.csv")
    save_csv(products, "products.csv")
    save_csv(orders, "orders.csv")
    save_csv(order_items, "order_items.csv")

    print("Raw datasets generated successfully")

    print(
        f"Customers: {len(customers)} rows "
        f"({invalid_emails} invalid emails)"
    )

    print(
        f"Products: {len(products)} rows "
        f"({inconsistent_products} inconsistent names)"
    )

    print(
        f"Orders: {len(orders)} rows "
        f"({missing_customers} missing customer IDs, "
        f"{wrong_dates} wrong dates)"
    )

    print(
        f"Order items: {len(order_items)} rows "
        f"({negative_quantities} negative quantities, "
        f"{orphan_items} orphan rows)"
    )

    print(f"Files saved in: {RAW_DIR}")


if __name__ == "__main__":
    main()