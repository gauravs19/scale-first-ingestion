# Testing & Validation Guide: Scale-First IoT Ingestion

This guide outlines how to verify the resilience, data integrity, and performance of the Distributed Ingestion system.

## 1. Environment Verification
Ensure the full stack is running via Podman or Docker:
```bash
podman compose up -d
podman compose ps
```
All 6 services (`ingestor`, `processor`, `redis`, `prometheus`, `grafana`, `locust`) should show a status of `Up`.

---

## 2. Functional & Contract Testing (The "Happy Path")
Validate that the API enforces the enterprise data schema using the built-in Swagger UI.

1.  **Open:** [http://localhost:8000/docs](http://localhost:8000/docs)
2.  **Test Case 1 (Valid Data):** 
    - Click **POST /ingest** -> **Try it out**.
    - Use the default JSON. Click **Execute**.
    - **Expected Result:** `200 OK` with `status: accepted`.
3.  **Test Case 2 (Invalid Contract):**
    - Change `"type": "VIBRATION"` to `"type": "COFFEE"`.
    - **Expected Result:** `422 Unprocessable Entity`. (Proves Schema Governance).

---

## 3. Load & Stress Testing (The "Scalability" Proof)
This test proves the system can handle concurrent ingestion without memory leaks or packet loss.

1.  **Open:** [http://localhost:8089](http://localhost:8089)
2.  **Configuration:** (Pre-configured for Autostart).
    - If stopped, set **Number of users: 100** and **Spawn rate: 10**.
3.  **Validation:** 
    - Watch the **Total Requests per Second (RPS)**.
    - Check the **Failures** tab. It should remain at 0% even as load increases.
    - This demonstrates the **Non-blocking async ingestion** logic.

---

## 4. Observability Testing (The "Operations" View)
Verify that the system is properly instrumented for SRE (Site Reliability Engineering) teams.

### A. Raw Metrics (Prometheus)
- **Open:** [http://localhost:9090](http://localhost:9090).
- **Query:** `worker_processed_total`
- **Goal:** Verify that the background worker is successfully consuming and processing messages from the Redis Stream.

### B. Live Logs (CLI)
- **Anomaly Detection Check:** Monitoring the processor for vibration spikes.
```bash
podman logs -f ingestion_worker
```
- **Ingestion Log Check:**
```bash
podman logs -f ingestion_api
```

---

## 5. Resilience Testing (The "Chaos" Component)
Prove that the system survives component failure and data anomalies.

### A. Consumer Failure Logic
1.  **Step:** Stop the worker container while Locust is running:
    ```bash
    podman stop ingestion_worker
    ```
2.  **Observation:** The API continues to accept requests (caching them in the Redis Stream).
3.  **Step:** Restart the worker:
    ```bash
    podman start ingestion_worker
    ```
4.  **Result:** The worker will drain the "Backlog" accumulated during the downtime.

### B. Poison Pill / DLQ Verification
1.  **Step:** Send a "Malformed" manual request (e.g., physically impossible reading):
    ```bash
    curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d '{"device_id": "STRESS-TEST", "type": "VIBRATION", "reading": 999.9}'
    ```
2.  **Observation:** Watch the worker logs:
    ```bash
    podman logs -f ingestion_worker
    ```
    You should see: `[🛡️ DLQ] Shunting message ... Reason: PHYSICAL_IMPOSSIBILITY_THRESHOLD`.
3.  **Validation:** Check the Redis Stream directly (if Redis CLI is available):
    ```bash
    podman exec -it ingestion_broker redis-cli xread streams telemetry_dlq 0
    ```

---
*Created by Gaurav Sharma — Solutions Architect*
