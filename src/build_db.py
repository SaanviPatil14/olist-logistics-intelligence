
import os
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SCHEMA = ROOT / "sql" / "01_schema.sql"
VIEWS = ROOT / "sql" / "02_views.sql"

CONN = dict(
    host=os.environ.get("PGHOST", "localhost"),
    dbname=os.environ.get("PGDATABASE", "olist"),
    user=os.environ.get("PGUSER", "olist"),
    password=os.environ.get("PGPASSWORD", "olist_dev"),
)

# Load order matters: parents before children (foreign keys).
LOAD_ORDER = [
    ("customers",            "olist_customers_dataset.csv"),
    ("sellers",              "olist_sellers_dataset.csv"),
    ("category_translation", "product_category_name_translation.csv"),
    ("products",             "olist_products_dataset.csv"),
    ("orders",               "olist_orders_dataset.csv"),
    ("order_items",          "olist_order_items_dataset.csv"),
    ("order_payments",       "olist_order_payments_dataset.csv"),
    ("order_reviews",        "olist_order_reviews_dataset.csv"),
    ("geolocation",          "olist_geolocation_dataset.csv"),
]

EXPECTED_ROWS = {
    "customers": 99441, "sellers": 3095, "category_translation": 71,
    "products": 32951, "orders": 99441, "order_items": 112650,
    "order_payments": 103886, "order_reviews": 99224, "geolocation": 1000163,
}


def load_table(cur, table, filename):
    """Bulk-load one CSV with COPY, mapping columns by the file's header names."""
    path = RAW / filename
    with open(path, encoding="utf-8-sig") as f:
        columns = f.readline().strip().split(",")
        f.seek(0)
        cur.copy_expert(
            f"COPY {table} ({', '.join(columns)}) FROM STDIN WITH (FORMAT csv, HEADER true)",
            f,
        )


def scalar(cur, sql):
    cur.execute(sql)
    return cur.fetchone()[0]


def main():
    missing = [f for _, f in LOAD_ORDER if not (RAW / f).exists()]
    assert not missing, f"Missing raw files: {missing}"

    conn = psycopg2.connect(**CONN)
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA.read_text())
            for table, filename in LOAD_ORDER:
                load_table(cur, table, filename)
                print(f"loaded {table}")

            # Checks against numbers verified in Phase 1.
            for table, expected in EXPECTED_ROWS.items():
                actual = scalar(cur, f"SELECT COUNT(*) FROM {table}")
                assert actual == expected, f"{table}: {actual} rows, expected {expected}"

            assert scalar(cur, "SELECT SUM(payment_value) FROM order_payments") \
                == __import__("decimal").Decimal("16008872.12")
            assert scalar(cur, "SELECT COUNT(*) FROM orders WHERE order_approved_at IS NULL") == 160
            assert scalar(cur, "SELECT COUNT(*) FROM orders WHERE order_delivered_carrier_date IS NULL") == 1783
            assert scalar(cur, "SELECT COUNT(*) FROM orders WHERE order_delivered_customer_date IS NULL") == 2965
            assert scalar(cur, "SELECT COUNT(*) FROM order_reviews WHERE review_comment_title IS NULL") == 87656
            assert scalar(cur, "SELECT COUNT(*) FROM order_reviews WHERE review_comment_message IS NULL") == 58247
            assert scalar(cur, "SELECT COUNT(DISTINCT customer_unique_id) FROM customers") == 96096

            #create the view, then check it.
            cur.execute(VIEWS.read_text())
            window = ("in_delivery_population AND purchase_month "
                      "BETWEEN DATE '2017-01-01' AND DATE '2018-08-01'")
            view_checks = {
                "orders_enriched rows":        ("SELECT COUNT(*) FROM orders_enriched", 99441),
                "delivery population":         ("SELECT COUNT(*) FROM orders_enriched WHERE in_delivery_population", 96470),
                "late (calendar-day), pop":    ("SELECT COUNT(*) FROM orders_enriched WHERE in_delivery_population AND is_late", 6534),
                "late (timestamp), pop":       ("SELECT COUNT(*) FROM orders_enriched WHERE in_delivery_population AND is_late_timestamp_rule", 7826),
                "flag carrier before approval":("SELECT COUNT(*) FROM orders_enriched WHERE flag_carrier_before_approval", 1359),
                "flag delivered before carrier":("SELECT COUNT(*) FROM orders_enriched WHERE flag_delivered_before_carrier", 23),
                "delivery_days non-null":      ("SELECT COUNT(delivery_days) FROM orders_enriched", 96476),
                "approval_to_carrier non-null":("SELECT COUNT(approval_to_carrier_days) FROM orders_enriched", 96285),
                "carrier_to_customer non-null":("SELECT COUNT(carrier_to_customer_days) FROM orders_enriched", 96452),
                "window population":           (f"SELECT COUNT(*) FROM orders_enriched WHERE {window}", 96203),
                "late in window":              (f"SELECT COUNT(*) FROM orders_enriched WHERE {window} AND is_late", 6531),
            }
            for label, (sql, expected) in view_checks.items():
                actual = scalar(cur, sql)
                assert actual == expected, f"{label}: {actual}, expected {expected}"
            print("All view checks passed.")
        conn.commit()
        print("All database checks passed.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()