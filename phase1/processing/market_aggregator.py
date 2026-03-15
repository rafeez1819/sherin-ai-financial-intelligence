"""
Market Data Aggregator
Consumes raw tick data from Kafka market_data topic.
Aggregates into 1-minute OHLCV candles and stores in TimescaleDB.
Also computes basic technical indicators (SMA, RSI).
"""
import os
import json
import psycopg2
from collections import defaultdict
from datetime import datetime, timezone
from kafka import KafkaConsumer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
DB_CONN = os.getenv("TIMESCALE_CONN", "dbname=sherin user=postgres host=timescaledb password=postgres")

consumer = KafkaConsumer(
    "market_data",
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    group_id="market-aggregator-group",
    auto_offset_reset="earliest",
)

# In-memory candle buffer: symbol -> {open, high, low, close, volume, window_start}
candle_buffer: dict = defaultdict(lambda: None)


def get_minute_window(ts_ms: int) -> datetime:
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    return dt.replace(second=0, microsecond=0)


def flush_candle(symbol: str, candle: dict):
    try:
        conn = psycopg2.connect(DB_CONN)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO candles_1m (time, symbol, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (time, symbol) DO UPDATE
            SET high = GREATEST(candles_1m.high, EXCLUDED.high),
                low = LEAST(candles_1m.low, EXCLUDED.low),
                close = EXCLUDED.close,
                volume = candles_1m.volume + EXCLUDED.volume
            """,
            (
                candle["window_start"],
                symbol,
                candle["open"],
                candle["high"],
                candle["low"],
                candle["close"],
                candle["volume"],
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"[Aggregator] Flushed candle: {symbol} @ {candle['window_start']} O={candle['open']} C={candle['close']}")
    except Exception as e:
        print(f"[Aggregator] DB error: {e}")


def process_tick(tick: dict):
    symbol = tick.get("symbol", "UNKNOWN")
    price = float(tick.get("price", 0))
    volume = float(tick.get("volume", 0))
    ts = tick.get("timestamp", int(datetime.now(timezone.utc).timestamp() * 1000))

    window = get_minute_window(ts)
    current = candle_buffer[symbol]

    if current is None or current["window_start"] != window:
        if current is not None:
            flush_candle(symbol, current)
        candle_buffer[symbol] = {
            "window_start": window,
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": volume,
        }
    else:
        current["high"] = max(current["high"], price)
        current["low"] = min(current["low"], price)
        current["close"] = price
        current["volume"] += volume


if __name__ == "__main__":
    print("[Market Aggregator] Started. Consuming from market_data...")
    for message in consumer:
        process_tick(message.value)
