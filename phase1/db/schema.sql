-- ============================================================
-- Sherin AI Financial Intelligence Platform
-- Phase 1 Database Schema
-- ============================================================

-- TimescaleDB: Market OHLCV candles
CREATE TABLE IF NOT EXISTS candles_1m (
    time        TIMESTAMPTZ     NOT NULL,
    symbol      TEXT            NOT NULL,
    open        DOUBLE PRECISION,
    high        DOUBLE PRECISION,
    low         DOUBLE PRECISION,
    close       DOUBLE PRECISION,
    volume      DOUBLE PRECISION,
    PRIMARY KEY (time, symbol)
);

SELECT create_hypertable('candles_1m', 'time', if_not_exists => TRUE);

-- Index for fast symbol lookups
CREATE INDEX IF NOT EXISTS idx_candles_symbol ON candles_1m (symbol, time DESC);

-- ============================================================
-- PostgreSQL: Macro Economic Data
-- ============================================================
CREATE TABLE IF NOT EXISTS macro_data (
    indicator   TEXT            NOT NULL,
    value       DOUBLE PRECISION,
    date        DATE            NOT NULL,
    PRIMARY KEY (indicator, date)
);

CREATE INDEX IF NOT EXISTS idx_macro_indicator ON macro_data (indicator, date DESC);

-- ============================================================
-- PostgreSQL: Dead Letter Queue
-- ============================================================
CREATE TABLE IF NOT EXISTS dead_letter_queue (
    id              SERIAL PRIMARY KEY,
    payload         JSONB           NOT NULL,
    error_reason    TEXT,
    received_at     TIMESTAMPTZ     DEFAULT NOW(),
    resolved        BOOLEAN         DEFAULT FALSE
);

-- ============================================================
-- PostgreSQL: Pipeline Monitoring
-- ============================================================
CREATE TABLE IF NOT EXISTS pipeline_metrics (
    id              SERIAL PRIMARY KEY,
    pipeline_name   TEXT            NOT NULL,
    metric_name     TEXT            NOT NULL,
    metric_value    DOUBLE PRECISION,
    recorded_at     TIMESTAMPTZ     DEFAULT NOW()
);
