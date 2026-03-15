"""
FRED Macro Economic Data Ingestor (Airflow DAG)
Fetches GDP, inflation, interest rate, and employment data from FRED API daily.
Stores structured records into PostgreSQL macro_data table.
"""
import os
import requests
import psycopg2
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

FRED_API_KEY = os.getenv("FRED_API_KEY")
DB_CONN = os.getenv("POSTGRES_CONN", "dbname=sherin user=postgres host=postgres password=postgres")

# FRED series to ingest
SERIES = {
    "GDP": "GDP",
    "INFLATION": "CPIAUCSL",
    "FED_RATE": "FEDFUNDS",
    "UNEMPLOYMENT": "UNRATE",
}


def fetch_series(series_id: str, indicator: str):
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
    )
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    observations = response.json().get("observations", [])

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    for obs in observations:
        if obs["value"] == ".":
            continue
        cur.execute(
            """
            INSERT INTO macro_data (indicator, value, date)
            VALUES (%s, %s, %s)
            ON CONFLICT (indicator, date) DO UPDATE SET value = EXCLUDED.value
            """,
            (indicator, float(obs["value"]), obs["date"]),
        )
    conn.commit()
    cur.close()
    conn.close()
    print(f"[FRED] Ingested {indicator} ({len(observations)} records)")


def ingest_all_series():
    for series_id, indicator in SERIES.items():
        fetch_series(series_id, indicator)


# Airflow DAG definition
dag = DAG(
    "fred_macro_ingestion",
    schedule_interval="@daily",
    start_date=datetime(2026, 3, 15),
    catchup=False,
    tags=["phase1", "macro"],
)

task = PythonOperator(
    task_id="fetch_fred_macro_data",
    python_callable=ingest_all_series,
    dag=dag,
)
