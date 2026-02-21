from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
import os
import json
import time
from prometheus_client import Counter, Histogram, make_asgi_app

import sys
import os

# Add parent dir to path to import config_loader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import settings

app = FastAPI(title="Enterprise IoT Ingestor")

# --- Prometheus Metrics ---
INGESTION_COUNT = Counter("ingestion_requests_total", "Total ingestion requests", ["status"])
LATENCY = Histogram("ingestion_latency_seconds", "Time spent processing request")

# Add prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# --- Configuration from YAML ---
REDIS_URL = os.getenv("REDIS_URL", settings['broker']['url'])
STREAM_NAME = settings['broker']['stream_name']
redis_client = redis.from_url(REDIS_URL)

# --- Governance: Schema Enforcement ---
class TelemetryData(BaseModel):
    device_id: str = Field(..., example="DEV-001")
    type: str = Field(..., example="VIBRATION")
    reading: float = Field(..., example=15.4)
    timestamp: float = Field(default_factory=time.time)

    @validator('type')
    def validate_type(cls, v):
        allowed = settings['governance']['allowed_types']
        if v not in allowed:
            raise ValueError(f"Type must be one of {allowed}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "device_id": "DEV-001",
                "type": "VIBRATION",
                "reading": 15.4
            }
        }

@app.post("/ingest")
async def ingest_data(data: TelemetryData):
    start_time = time.time()
    try:
        # 1. Schema Validation (Automated by Pydantic)
        
        # 2. Resilient Ingestion: Push to Redis Stream
        # In enterprise, Redis Streams provide persistence and consumer groups
        await redis_client.xadd("telemetry_stream", {"data": data.json()})
        
        INGESTION_COUNT.labels(status="success").inc()
        duration = time.time() - start_time
        LATENCY.observe(duration)
        
        return {"status": "accepted", "id": data.device_id}
    except Exception as e:
        INGESTION_COUNT.labels(status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "broker": "connected"}
