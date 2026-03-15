"""
Feast Feature Store Definitions
Defines feature views for news sentiment, market indicators, and macro data.
Used by downstream ML models in Phase 2 and Phase 3.
"""
from datetime import timedelta
from feast import FeatureStore, FeatureView, Field, Entity
from feast.types import Float32, String
from feast.infra.offline_stores.file_source import FileSource

# Entities
asset_entity = Entity(name="asset", join_keys=["asset_id"])

# Feature sources (batch)
news_source = FileSource(
    path="data/news_features.parquet",
    timestamp_field="event_timestamp",
)

market_source = FileSource(
    path="data/market_features.parquet",
    timestamp_field="event_timestamp",
)

macro_source = FileSource(
    path="data/macro_features.parquet",
    timestamp_field="event_timestamp",
)

# Feature views
news_sentiment_fv = FeatureView(
    name="news_sentiment",
    entities=[asset_entity],
    ttl=timedelta(days=1),
    schema=[
        Field(name="sentiment_score", dtype=Float32),
        Field(name="impact_score", dtype=Float32),
        Field(name="event_type", dtype=String),
    ],
    online=True,
    source=news_source,
    tags={"phase": "1", "module": "news_intelligence"},
)

market_indicators_fv = FeatureView(
    name="market_indicators",
    entities=[asset_entity],
    ttl=timedelta(hours=1),
    schema=[
        Field(name="rsi_14", dtype=Float32),
        Field(name="sma_20", dtype=Float32),
        Field(name="macd", dtype=Float32),
        Field(name="volume_24h", dtype=Float32),
    ],
    online=True,
    source=market_source,
    tags={"phase": "1", "module": "market_data"},
)

macro_indicators_fv = FeatureView(
    name="macro_indicators",
    entities=[asset_entity],
    ttl=timedelta(days=30),
    schema=[
        Field(name="inflation_rate", dtype=Float32),
        Field(name="fed_rate", dtype=Float32),
        Field(name="gdp_growth", dtype=Float32),
        Field(name="unemployment_rate", dtype=Float32),
    ],
    online=True,
    source=macro_source,
    tags={"phase": "1", "module": "macro_economic"},
)


def get_features_for_asset(asset_id: str) -> dict:
    """Retrieve all online features for a given asset."""
    fs = FeatureStore(repo_path=".")
    features = fs.get_online_features(
        features=[
            "news_sentiment:sentiment_score",
            "news_sentiment:impact_score",
            "market_indicators:rsi_14",
            "market_indicators:sma_20",
            "macro_indicators:inflation_rate",
            "macro_indicators:fed_rate",
        ],
        entity_rows=[{"asset_id": asset_id}],
    ).to_dict()
    return features
