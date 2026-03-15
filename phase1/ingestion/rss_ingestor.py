"""
RSS News Ingestor
Fetches news from CNBC and Financial Times RSS feeds every 5 minutes.
Publishes raw articles to Kafka news_raw topic.
"""
import os
import time
import json
import feedparser
from kafka import KafkaProducer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
CNBC_RSS = os.getenv("CNBC_RSS_URL", "https://www.cnbc.com/id/100003114/device/rss/rss.html")
FT_RSS = os.getenv("FT_RSS_URL", "https://www.ft.com/?format=rss")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5,
)


def fetch_rss_feed(url: str, source: str):
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            article = {
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "source": source,
            }
            producer.send("news_raw", article)
            print(f"[{source}] Sent: {entry.get('title', 'N/A')}")
        producer.flush()
    except Exception as e:
        print(f"[{source}] Error: {e}")


if __name__ == "__main__":
    print("[RSS Ingestor] Started.")
    while True:
        fetch_rss_feed(CNBC_RSS, "CNBC")
        fetch_rss_feed(FT_RSS, "Financial Times")
        time.sleep(300)
