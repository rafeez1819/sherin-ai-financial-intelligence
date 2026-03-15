"""
Data Validator (Great Expectations)
Validates market data and news data quality.
Checks for null values, price ranges, volume integrity, and schema compliance.
"""
import os
import json
import great_expectations as ge
import pandas as pd
import psycopg2

DB_CONN = os.getenv("TIMESCALE_CONN", "dbname=sherin user=postgres host=timescaledb password=postgres")
REPORT_PATH = os.getenv("VALIDATION_REPORT_PATH", "/app/reports/validation_results.json")


def validate_market_data() -> dict:
    conn = psycopg2.connect(DB_CONN)
    df = pd.read_sql("SELECT * FROM candles_1m ORDER BY time DESC LIMIT 10000", conn)
    conn.close()

    gdf = ge.from_pandas(df)

    results = {}

    # Price must be positive
    r1 = gdf.expect_column_values_to_be_between("close", min_value=0.0001, max_value=None)
    results["close_price_positive"] = r1["success"]

    # Volume must not be null
    r2 = gdf.expect_column_values_to_not_be_null("volume")
    results["volume_not_null"] = r2["success"]

    # Symbol must not be null
    r3 = gdf.expect_column_values_to_not_be_null("symbol")
    results["symbol_not_null"] = r3["success"]

    # Time must be unique per symbol
    r4 = gdf.expect_compound_columns_to_be_unique(["time", "symbol"])
    results["time_symbol_unique"] = r4["success"]

    passed = all(results.values())
    print(f"[Validator] Market data validation: {'PASSED' if passed else 'FAILED'}")
    print(json.dumps(results, indent=2))

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump({"market_data": results, "passed": passed}, f, indent=2)

    return results


def validate_news_data(articles: list) -> dict:
    df = pd.DataFrame(articles)
    gdf = ge.from_pandas(df)

    results = {}

    r1 = gdf.expect_column_values_to_not_be_null("title")
    results["title_not_null"] = r1["success"]

    r2 = gdf.expect_column_values_to_not_be_null("source")
    results["source_not_null"] = r2["success"]

    r3 = gdf.expect_column_values_to_be_between("sentiment", min_value=-1.0, max_value=1.0)
    results["sentiment_range_valid"] = r3["success"]

    passed = all(results.values())
    print(f"[Validator] News data validation: {'PASSED' if passed else 'FAILED'}")
    return results


if __name__ == "__main__":
    validate_market_data()
