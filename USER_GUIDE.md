# User Guide: Enterprise IoT Ingestion Engine

This guide walks you through the operation, monitoring, and stress-testing of the Distributed Ingestion system.

## 🛠️ Getting Started

### 1. Launch the Stack
Ensure you have Podman (or Docker) installed.
```bash
podman compose up -d
```
All services are now active in the background.

---

## 🚦 System Interfaces

| Service | URL | Description |
| :--- | :--- | :--- |
| **Ingestion API** | `http://localhost:8000/docs` | Interactive Swagger UI for individual telemetry ingest. |
| **Load Control** | `http://localhost:8089` | Locust dashboard to simulate thousands of devices. |
| **Metrics Engine** | `http://localhost:9090` | Prometheus dashboard for SRE-level alerting. |
| **Live Dashboards** | `http://localhost:3000` | Grafana visual command center (admin/admin). |

---

## 🧪 Testing Scenarios

### Scenario A: Contract Enforcement
How to prove the system rejects invalid data:
1.  Navigate to the **Ingestion API** (`/docs`).
2.  Try a POST request with an invalid `type` (e.g., `"COFFEE"`).
3.  Observe the `422` error—this prevents garbage data from entering your message broker.

### Scenario B: High-Throughput Stress
How to prove the system scales:
1.  Open the **Load Control** dashboard.
2.  The system is pre-configured to autostart with 10 users.
3.  Increase to **1000 users** and watch the RPS (Requests Per Second) climb.
4.  Observe the **CPU/Memory metrics** in the processor logs; the system handles the load via async non-blocking queues.

### Scenario C: Resilience (The DLQ Junk Yard)
How the system handles "Poison Pills":
1.  Send a request with a vibration reading of `999.9`.
2.  The system identifies this as a "Physical Impossibility."
3.  The message is shunted to the **Dead Letter Queue (`telemetry_dlq`)** for manual audit.
4.  Inspect the DLQ:
    ```bash
    podman exec ingestion_broker redis-cli xread streams telemetry_dlq 0
    ```

---

## 📁 Key File Locations
-   **Configuration:** `config/settings.yaml` (Tweak thresholds here).
-   **Architecture:** `ARCHITECTURE.md` (Deep dive into design patterns).
-   **Scaling:** `docker-compose.yml` (Orchestration blueprint).

---
*Created by Gaurav Sharma — Solutions Architect*
