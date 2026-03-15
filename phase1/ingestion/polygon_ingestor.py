"""
Polygon.io Stock Market Data Ingestor
Streams real-time stock trades via WebSocket and publishes to Kafka market_data topic.
"""
import os
import json
import websocket
from kafka import KafkaProducer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
SYMBOLS = os.getenv("POLYGON_SYMBOLS", "AAPL,MSFT,TSLA").split(",")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5,
)


def on_message(ws, message):
    events = json.loads(message)
    for event in events:
        if event.get("ev") == "T":  # Trade event
            payload = {
                "symbol": event.get("sym"),
                "price": event.get("p"),
                "volume": event.get("s"),
                "timestamp": event.get("t"),
                "source": "polygon",
            }
            producer.send("market_data", payload)
            print(f"[Polygon] {payload['symbol']} @ {payload['price']}")


def on_open(ws):
    print("[Polygon] Connected. Authenticating...")
    ws.send(json.dumps({"action": "auth", "params": POLYGON_API_KEY}))
    subscribe_msg = {"action": "subscribe", "params": ",".join([f"T.{s}" for s in SYMBOLS])}
    ws.send(json.dumps(subscribe_msg))


def on_error(ws, error):
    print(f"[Polygon] Error: {error}")


def on_close(ws, *args):
    print("[Polygon] Connection closed.")


if __name__ == "__main__":
    url = "wss://socket.polygon.io/stocks"
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_open=on_open,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever()
