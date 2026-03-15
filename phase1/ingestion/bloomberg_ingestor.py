"""
Bloomberg News Ingestor
Fetches financial news from Bloomberg API every 5 minutes and publishes to Kafka news_raw topic.
"""
import os
import time
import json
import requests
from kafka import KafkaProducer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
API_KEY = os.getenv("BLOOMBERG_API_KEY")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5,
)


def fetch_bloomberg_news():
    url = f"https://api.bloomberg.com/news?apiKey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        for article in articles:
            producer.send("news_raw", article)
            print(f"[Bloomberg] Sent: {article.get('title', 'N/A')}")
        producer.flush()
    except Exception as e:
        print(f"[Bloomberg] Error: {e}")


if __name__ == "__main__":
    print("[Bloomberg] Ingestor started.")
    while True:
        fetch_bloomberg_news()
        time.sleep(300)
