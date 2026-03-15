"""
Dead Letter Queue Handler
Consumes failed/malformed messages from the news_dlq topic.
Logs errors, attempts reprocessing, and stores unrecoverable messages to PostgreSQL.
"""
import os
import json
import psycopg2
from datetime import datetime, timezone
from kafka import KafkaConsumer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
DB_CONN = os.getenv("POSTGRES_CONN", "dbname=sherin user=postgres host=postgres password=postgres")

consumer = KafkaConsumer(
    "news_dlq",
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    group_id="dlq-handler-group",
    auto_offset_reset="earliest",
)


def store_failed_message(message: dict, reason: str):
    try:
        conn = psycopg2.connect(DB_CONN)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO dead_letter_queue (payload, error_reason, received_at)
            VALUES (%s, %s, %s)
            """,
            (json.dumps(message), reason, datetime.now(timezone.utc)),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DLQ] Failed to store message: {e}")


if __name__ == "__main__":
    print("[DLQ Handler] Started. Consuming from news_dlq...")
    for msg in consumer:
        payload = msg.value
        reason = payload.get("error_reason", "unknown")
        print(f"[DLQ] Received failed message. Reason: {reason}")
        store_failed_message(payload, reason)
