# Enterprise Scale-First IoT Ingestion Blueprint

A production-grade reference architecture for high-throughput telemetric data ingestion, processing, and observability.

## 🏛️ Project Vision
This repository demonstrates a **Distributed Ingestion Pipeline** designed to handle 100K+ concurrent industrial assets. It moves beyond simple prototypes by implementing industry-standard patterns for resilience, scale, and "Zero Trust" data governance.

### Architectural Pillars (Enterprise Standard)
1.  **Decoupled Orchestration:** Uses **Redis Streams** as a high-performance message broker (Mini-Kafka) to decouple ingestion from processing.
2.  **Schema Governance:** Strict enforcement of data contracts using **Pydantic** models and custom validators.
3.  **Observability-First:** Every component is instrumented with **Prometheus** metrics for real-time health tracking.
4.  **Externalized Configuration:** Centralized YAML-based configuration management for zero-code environmental tuning.

---

## 🛠️ Technical Stack
- **Ingestor:** FastAPI (Asynchronous API Gateway).
- **Broker:** Redis 7.0 (Streams for persistence and consumer groups).
- **Processor:** Async Python Workers (Stateless transformation and anomaly detection).
- **Observability:** Prometheus (Metrics Scaping) & Grafana (Visual Dashboards).
- **Stress Testing:** Locust (Distributed Load Generation).
- **Infrastructure:** Docker Compose (Orchestrated Microservices).

---

## 📂 Repository Structure
```bash
├── ingestor/           # FastAPI gateway with schema enforcement
├── processor/          # Decoupled stream consumers
├── config/             # Centralized settings.yaml
├── prometheus/         # Metrics scraping configuration
├── locust/             # Stress-testing scripts
└── docker-compose.yml  # Full distributed stack orchestration
```

---

## 🚀 Enterprise Launch (Docker)
Experience the full distributed system locally:
```bash
docker-compose up --build
```
- **API Docs:** `http://localhost:8000/docs`
- **Metrics:** `http://localhost:9090`
- **Load Test:** `http://localhost:8089`

---
*Created by [Gaurav Sharma](https://gauravs19.github.io/portfolio/) — Solutions Architect*
