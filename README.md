# Sherin AI Financial Intelligence

AI-driven financial platform with live news map, knowledge graph, and probabilistic trading signals.

Phase 1 – Data Foundation in progress.
# Sherin AI Financial Intelligence Platform

**AI-driven financial intelligence system**  
Combining **live global news map**, **knowledge graph**, **probabilistic trading signals**, **sector forecasting**, **macro radar**, and **semi-autonomous trading**.

> From raw news & market data → structured events → explainable predictions → actionable trading intelligence.

Current focus: **Phase 1 – Data Foundation** (real-time ingestion pipelines)

[![GitHub license](https://img.shields.io/github/license/rafeez1819/sherin-ai-financial-intelligence)](https://github.com/rafeez1819/sherin-ai-financial-intelligence/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/rafeez1819/sherin-ai-financial-intelligence?style=social)](https://github.com/rafeez1819/sherin-ai-financial-intelligence)

## System Architecture

```mermaid
graph TD
    A[Global News Sources<br>Reuters • Bloomberg • CNBC • FT • RSS] -->|Kafka Streaming| B[News Ingestion & NLP<br>FinBERT • Entity Extraction • Sentiment]
    C[Market Data<br>Binance • Polygon • Twelve Data • Alpha Vantage] -->|WebSocket + Kafka| D[Market Aggregation<br>OHLC • Indicators • TimescaleDB]
    E[Macro Data<br>FRED • ECB • World Bank] -->|Airflow ETL| F[PostgreSQL Macro Store]

    B --> G[Elasticsearch + Schema Registry]
    D --> G
    F --> G

    G --> H[Feature Store<br>Feast]
    H --> I[AI Engines<br>LSTM • Transformers • GNN • PPO RL]

    I --> J[Probability & Explainable Engine<br>SHAP • Confidence Bands]
    J --> K[Sherin Trading UI<br>Signals • Heatmap • Forecast Charts]

    K --> L[Macro Radar<br>Geopolitical • Economic Events Map]
    K --> M[Broker Integrations<br>Binance • IBKR • MT5]

    style A fill:#f9f,stroke:#333
    style C fill:#bbf,stroke:#333
    style E fill:#bfb,stroke:#333
    style L fill:#ff9,stroke:#333
```

# Development Roadmap – Phases 1 to 6
```
gantt
    title Sherin AI Financial Intelligence Roadmap
    dateFormat  YYYY-MM
    axisFormat  %Y-%m
    section Phase 1
    Data Foundation<br>(Ingestion + Storage)     :done, p1, 2026-03, 3m
    section Phase 2
    Intelligence Layer<br>(Knowledge Graph + Events) :active, p2, after p1, 3m
    section Phase 3
    Prediction Engine<br>(Sector + Regime + Probability) : p3, after p2, 6m
    section Phase 4
    Autonomous Agent<br>(RL Trading + Broker Execution) : p4, after p3, 6m
    section Phase 5
    Explainable AI + Macro Radar<br>(SHAP + Counterfactuals + Visualization) : p5, after p4, 3m
    section Phase 6
    Portfolio & Governance<br>(Dynamic Allocation + Model Monitoring + Scaling) : p6, after p5, 3m
```
# Folder Structure (Phases 1–6)
```
sherin-ai-financial-intelligence/
├── .github/workflows/                # CI/CD pipelines
├── docs/                             # Documentation & architecture drawings
│   ├── architecture.md
│   └── phase-plans/
├── infrastructure/                   # Deployment & infra-as-code
│   ├── docker-compose.yml
│   ├── terraform/
│   └── feast-feature-store/
├── src/
│   ├── common/                       # Shared utilities & config
│   ├── phase1-data-foundation/       # Real-time ingestion pipelines (current focus)
│   │   ├── ingestion/                # Reuters, Bloomberg, RSS, Binance, Polygon, FRED...
│   │   ├── processing/               # NLP, aggregation, dead-letter
│   │   ├── validation/
│   │   ├── monitoring/
│   │   ├── feature_store/
│   │   └── docker/
│   ├── phase2-intelligence-layer/    # Knowledge Graph + Event Engine
│   ├── phase3-prediction-engine/     # Sector forecast, regime detection, probability
│   ├── phase4-autonomous-agent/      # RL trading agent + broker connectors
│   ├── phase5-explainable-ai-radar/  # SHAP explanations + macro radar UI
│   └── phase6-portfolio-governance/  # Portfolio optimization + model governance
├── models/                           # Model checkpoints (gitignored large files)
├── notebooks/                        # Exploratory & backtesting notebooks
├── configs/                          # YAML configs, schemas, API keys templates
├── tests/                            # Unit + integration tests per phase
├── data/                             # Small samples only (gitignore large/raw data)
├── .gitignore
├── LICENSE
├── README.md                         # ← this file
└── requirements.txt
```

# Competitive Comparison
```
Feature,Sherin,Freqtrade,FinRL,QLib,Bloomberg Terminal
Live global news ingestion,✓ (multi-source),✗,✗,✗,✓ (very expensive)
Knowledge Graph,✓ (Neo4j planned),✗,✗,Partial,Partial
Probabilistic signals,✓ (with confidence),Partial,RL-focused,✓,✓
Macro event radar / map,✓ (Phase 5),✗,✗,✗,✓
Explainable AI (SHAP etc.),✓ (Phase 5),✗,Limited,Limited,✓
Semi-autonomous execution,✓ (Phase 4),✓,✓,Partial,✗ (manual heavy)
Affordable & open-source base,✓,✓,✓,✓,✗ ($24k+/year)
```
