"""
Binance Market Data Ingestor
Streams real-time BTC/USDT trade ticks via WebSocket and publishes to Kafka market_data topic.
"""
import os
import json
import websocket
from kafka import KafkaProducer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
SYMBOL = os.getenv("BINANCE_SYMBOL", "btcusdt")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5,
)


def on_message(ws, message):
    data = json.loads(message)
    payload = {
        "symbol": data.get("s", SYMBOL.upper()),
        "price": float(data.get("p", 0)),
        "volume": float(data.get("q", 0)),
        "timestamp": data.get("T"),
        "source": "binance",
    }
    producer.send("market_data", payload)
    print(f"[Binance] {payload['symbol']} @ {payload['price']}")


def on_error(ws, error):
    print(f"[Binance] WebSocket error: {error}")


def on_close(ws, close_status_code, close_msg):
    print("[Binance] WebSocket closed. Reconnecting...")
    start()


def on_open(ws):
    print("[Binance] WebSocket connected.")


def start():
    url = f"wss://stream.binance.com:9443/ws/{SYMBOL}@trade"
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    ws.run_forever()


if __name__ == "__main__":
    start()
