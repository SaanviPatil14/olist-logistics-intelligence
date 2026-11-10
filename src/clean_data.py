"""Phase 2: clean the Olist tables and write them to data/processed/.

Run from the project root:   python src/clean_data.py

Every rule here was decided in the Phase 2 steps. The asserts compare results
with numbers verified earlier, so a failure means something changed.
"""
from pathlib import Path
import pandas as pd
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
SECONDS_PER_DAY = 86400

# Values that are not usable city names; deliberately left unmapped.
UNKNOWN_SELLER_CITIES = {"04482255", "vendas@creditparts.com.br", "sp / sp",
                         "sbc/sp", "arraial d'ajuda (porto seguro)"}

def clean_city(text):
    """Lowercase, strip accents, unify apostrophes, drop trailing state/country."""
    t = unicodedata.normalize("NFKD", str(text).strip().lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.replace("´", "'").replace("'", " ").strip()
    if t in UNKNOWN_SELLER_CITIES or t.replace(" ", "") in {c.replace(" ", "").replace("'", "") for c in UNKNOWN_SELLER_CITIES}:
        return "unknown"
    return re.split(r"[/,\\]", t)[0].strip()

def clean_sellers():
    sellers = pd.read_csv(RAW / "olist_sellers_dataset.csv")
    sellers["seller_city_clean"] = sellers["seller_city"].map(clean_city)

    # Remove a trailing state code only if it matches the seller's own state.
    def strip_state_suffix(row):
        city, state = row["seller_city_clean"], row["seller_state"].lower()
        for suffix in (f" - {state}", f" {state}"):
            if city.endswith(suffix) and len(city) > len(suffix):
                return city[: -len(suffix)].strip()
        return city

    sellers["seller_city_clean"] = sellers.apply(strip_state_suffix, axis=1)
    return sellers

def days_between(start, end):
    """Elapsed days from start to end (NaN if either is missing)."""
    return (end - start).dt.total_seconds() / SECONDS_PER_DAY


def clean_orders():
    orders = pd.read_csv(RAW / "olist_orders_dataset.csv")
    date_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col])  # raises on unparseable values
    oc = orders

    # Flags for illogical stage order (rows are kept, see Decision Log).
    oc["flag_carrier_before_approval"] = (
        oc["order_delivered_carrier_date"] < oc["order_approved_at"])
    oc["flag_delivered_before_carrier"] = (
        oc["order_delivered_customer_date"] < oc["order_delivered_carrier_date"])

    # Delivery metrics.
    oc["delivery_days"] = days_between(
        oc["order_purchase_timestamp"], oc["order_delivered_customer_date"])
    oc["estimated_days"] = days_between(
        oc["order_purchase_timestamp"], oc["order_estimated_delivery_date"])
    oc["delay_days"] = days_between(
        oc["order_estimated_delivery_date"], oc["order_delivered_customer_date"])
    # Stage durations are nulled only on the rows flagged above.
    oc["approval_to_carrier_days"] = days_between(
        oc["order_approved_at"], oc["order_delivered_carrier_date"]
    ).mask(oc["flag_carrier_before_approval"])
    oc["carrier_to_customer_days"] = days_between(
        oc["order_delivered_carrier_date"], oc["order_delivered_customer_date"]
    ).mask(oc["flag_delivered_before_carrier"])

    # Late label: calendar-day rule; unknown (null) when there is no delivery date.
    has_delivery = oc["order_delivered_customer_date"].notna()
    delivered_date = oc["order_delivered_customer_date"].dt.normalize()
    oc["is_late"] = (
        (delivered_date > oc["order_estimated_delivery_date"])
        .astype("boolean").where(has_delivery))
    # Sensitivity check: late if delivered after midnight of the estimated day.
    oc["is_late_timestamp_rule"] = (
        (oc["delay_days"] > 0).astype("boolean").where(has_delivery))

    # Delivery analysis population: delivered AND a delivery date exists.
    oc["in_delivery_population"] = (oc["order_status"] == "delivered") & has_delivery
    return oc


def one_review_per_order():
    """Keep the review with the latest answer timestamp (never ties)."""
    rev = pd.read_csv(RAW / "olist_order_reviews_dataset.csv")
    for col in ["review_creation_date", "review_answer_timestamp"]:
        rev[col] = pd.to_datetime(rev[col])
    n_reviews = rev.groupby("order_id").size().rename("n_reviews")
    latest = (rev.sort_values("review_answer_timestamp")
                 .drop_duplicates("order_id", keep="last")
                 [["order_id", "review_score", "review_creation_date",
                   "review_answer_timestamp"]])
    out = latest.merge(n_reviews, on="order_id", validate="one_to_one")
    assert out["order_id"].is_unique
    return out


def clean_items():
    items = pd.read_csv(RAW / "olist_order_items_dataset.csv")
    items["shipping_limit_date"] = pd.to_datetime(items["shipping_limit_date"])

    # Flag deadlines more than 30 days after purchase (date itself unchanged).
    purchase = pd.read_csv(
        RAW / "olist_orders_dataset.csv",
        usecols=["order_id", "order_purchase_timestamp"],
        parse_dates=["order_purchase_timestamp"])
    chk = items[["order_id"]].merge(purchase, on="order_id", how="left",
                                    validate="many_to_one")
    limit_days = days_between(chk["order_purchase_timestamp"],
                              items["shipping_limit_date"])
    items["flag_long_shipping_limit"] = (limit_days > 30).to_numpy()

    # Category: official translation + 2 manual names; null -> 'unknown'.
    products = pd.read_csv(RAW / "olist_products_dataset.csv")
    products["product_weight_g_clean"] = products["product_weight_g"].where(products["product_weight_g"] > 0)
    trans = pd.read_csv(RAW / "product_category_name_translation.csv")
    mapping = dict(zip(trans["product_category_name"],
                       trans["product_category_name_english"]))
    mapping.update({
        "pc_gamer": "pc_gamer",
        "portateis_cozinha_e_preparadores_de_alimentos":
            "portable_kitchen_food_preparers",  # my reading: check it
    })
    is_null = products["product_category_name"].isna()
    products["category_english"] = (
        products["product_category_name"].map(mapping).fillna("unknown"))
    products["category_status"] = "translated"
    products.loc[is_null, "category_status"] = "null_category"
    products.loc[~is_null & ~products["product_category_name"]
                 .isin(trans["product_category_name"]),
                 "category_status"] = "missing_from_translation"

    n = len(items)
    items = items.merge(
        products[["product_id", "category_english", "category_status","product_weight_g_clean"]],
        on="product_id", how="left", validate="many_to_one")
    assert len(items) == n
    return items


def order_level_money(items):
    """Collapse items and payments to ONE row per order before any join."""
    from_items = items.groupby("order_id").agg(
        n_items=("order_item_id", "size"),
        n_sellers=("seller_id", "nunique"),
        items_price=("price", "sum"),
        items_freight=("freight_value", "sum"))
    pay = pd.read_csv(RAW / "olist_order_payments_dataset.csv")
    from_pay = pay.groupby("order_id").agg(
        n_payments=("payment_sequential", "size"),
        payment_total=("payment_value", "sum"))
    return from_items, from_pay


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    oc = clean_orders()
    items = clean_items()
    reviews = one_review_per_order()
    from_items, from_pay = order_level_money(items)
    customers = pd.read_csv(RAW / "olist_customers_dataset.csv",
                            usecols=["customer_id", "customer_unique_id"])
    sellers = clean_sellers()
    assert len(sellers) == 3095
    assert (sellers["seller_city_clean"] == "unknown").sum() == 5
    assert items["product_weight_g_clean"].isna().sum() >= 8
    assert "brasilia df" not in set(sellers["seller_city_clean"])
    sellers.to_csv(OUT / "sellers_clean.csv", index=False)

    n_orders = len(oc)
    orders_final = (
        oc.merge(customers, on="customer_id", how="left", validate="many_to_one")
          .merge(reviews, on="order_id", how="left", validate="one_to_one")
          .merge(from_items, on="order_id", how="left", validate="one_to_one")
          .merge(from_pay, on="order_id", how="left", validate="one_to_one"))
    assert len(orders_final) == n_orders  # no fan-out

    # Checks against numbers verified in Phase 1 and 2.
    pop = orders_final[orders_final["in_delivery_population"]]
    assert n_orders == 99441
    assert len(items) == 112650
    assert orders_final["flag_carrier_before_approval"].sum() == 1359
    assert orders_final["flag_delivered_before_carrier"].sum() == 23
    assert len(pop) == 96470
    assert int(pop["is_late"].sum()) == 6534
    assert int(pop["is_late_timestamp_rule"].sum()) == 7826
    assert int(items["flag_long_shipping_limit"].sum()) == 239
    assert (items["category_english"] == "unknown").sum() == 1603
    assert round(orders_final["payment_total"].sum(), 2) == 16008872.12
    assert (orders_final["n_reviews"] > 1).sum() == 547
    assert orders_final["review_score"].isna().sum() == 768

    orders_final.to_csv(OUT / "orders_clean.csv", index=False)
    items.to_csv(OUT / "order_items_clean.csv", index=False)
    print("All checks passed.")
    print("orders_clean.csv:     ", orders_final.shape)
    print("order_items_clean.csv:", items.shape)
    print(f"late rate (population): {pop['is_late'].mean():.4f}")


if __name__ == "__main__":
    main()