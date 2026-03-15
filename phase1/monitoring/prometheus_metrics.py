"""
Prometheus Metrics Exporter
Exposes pipeline health metrics for Grafana dashboards.
Tracks: news ingestion rate, market data latency, macro data freshness, feature store cache hits.
"""
import os
import time
import psycopg2
from prometheus_client import start_http_server, Gauge, Counter

METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))
DB_CONN = os.getenv("POSTGRES_CONN", "dbname=sherin user=postgres host=postgres password=postgres")
TIMESCALE_CONN = os.getenv("TIMESCALE_CONN", "dbname=sherin user=postgres host=timescaledb password=postgres")

# Define metrics
news_ingestion_rate = Gauge("sherin_news_ingestion_rate", "Articles ingested per minute")
market_data_latency_ms = Gauge("sherin_market_data_latency_ms", "Market data ingestion latency in ms")
macro_data_freshness_hours = Gauge("sherin_macro_data_freshness_hours", "Hours since last macro data update")
feature_store_cache_hits = Counter("sherin_feature_store_cache_hits_total", "Total feature store cache hits")
pipeline_errors = Counter("sherin_pipeline_errors_total", "Total pipeline errors", ["pipeline"])


def collect_macro_freshness():
    try:
        conn = psycopg2.connect(DB_CONN)
        cur = conn.cursor()
        cur.execute("SELECT MAX(date) FROM macro_data")
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result and result[0]:
            from datetime import date
            delta = (date.today() - result[0]).total_seconds() / 3600
            macro_data_freshness_hours.set(delta)
    except Exception as e:
        print(f"[Metrics] Macro freshness error: {e}")


def collect_market_candle_count():
    try:
        conn = psycopg2.connect(TIMESCALE_CONN)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM candles_1m WHERE time > NOW() - INTERVAL '1 minute'")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        news_ingestion_rate.set(count)
    except Exception as e:
        print(f"[Metrics] Market candle count error: {e}")


if __name__ == "__main__":
    print(f"[Metrics] Starting Prometheus exporter on port {METRICS_PORT}...")
    start_http_server(METRICS_PORT)
    while True:
        collect_macro_freshness()
        collect_market_candle_count()
        time.sleep(30)
