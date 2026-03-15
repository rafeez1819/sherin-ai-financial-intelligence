"""
NLP Processor
Consumes raw articles from Kafka news_raw topic.
Applies FinBERT sentiment analysis + spaCy entity extraction + event classification.
Publishes structured events to news_processed topic and indexes into Elasticsearch.
"""
import os
import json
from kafka import KafkaConsumer, KafkaProducer
from transformers import pipeline
import spacy
from elasticsearch import Elasticsearch

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
ELASTIC_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
ELASTIC_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))

# Load models once at startup
nlp = spacy.load("en_core_web_sm")
sentiment_analyzer = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

consumer = KafkaConsumer(
    "news_raw",
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    group_id="nlp-processor-group",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5,
)

es = Elasticsearch([f"http://{ELASTIC_HOST}:{ELASTIC_PORT}"])

# Event classification keyword rules
EVENT_RULES = {
    "Monetary Policy": ["fed", "rate", "interest", "central bank", "ecb", "fomc", "hike", "cut"],
    "Commodity Supply": ["oil", "opec", "supply", "crude", "gas", "energy"],
    "Geopolitical Risk": ["war", "conflict", "sanction", "tension", "military"],
    "Fiscal Policy": ["budget", "deficit", "stimulus", "spending", "tax"],
    "Earnings": ["earnings", "revenue", "profit", "quarterly", "eps"],
}


def classify_event(text: str) -> str:
    text_lower = text.lower()
    for event_type, keywords in EVENT_RULES.items():
        if any(kw in text_lower for kw in keywords):
            return event_type
    return "General"


def process_article(article: dict) -> dict:
    title = article.get("title", "")
    summary = article.get("summary", "")
    full_text = f"{title} {summary}"

    # Entity extraction
    doc = nlp(full_text)
    entities = list(set([ent.text for ent in doc.ents if ent.label_ in ["ORG", "GPE", "PRODUCT", "MONEY"]]))

    # Sentiment analysis
    try:
        result = sentiment_analyzer(title[:512])[0]
        score = result["score"] if result["label"] == "Positive" else -result["score"]
    except Exception:
        score = 0.0

    event_type = classify_event(full_text)

    return {
        "id": article.get("link", "").split("/")[-1] or title[:32],
        "title": title,
        "source": article.get("source", "unknown"),
        "published": article.get("published", ""),
        "entities": entities,
        "sentiment": round(score, 4),
        "event_type": event_type,
        "impact_score": round(abs(score) * 100, 2),
    }


if __name__ == "__main__":
    print("[NLP Processor] Started. Consuming from news_raw...")
    for message in consumer:
        try:
            processed = process_article(message.value)
            producer.send("news_processed", processed)
            es.index(index="news_processed", document=processed)
            print(f"[NLP] Processed: {processed['title'][:60]} | {processed['event_type']} | sentiment={processed['sentiment']}")
        except Exception as e:
            print(f"[NLP] Error processing message: {e}")
