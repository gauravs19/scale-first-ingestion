import asyncio
import os
import json
import redis.asyncio as redis
from prometheus_client import Counter, start_http_server

import sys
import os

# Add parent dir to path to import config_loader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import settings

# --- Consumer Metrics ---
PROCESSED_COUNT = Counter("worker_processed_total", "Total packets processed by worker", ["status"])
ANOMALY_COUNT = Counter("worker_anomalies_total", "Anomalies detected")

# --- Configuration from YAML ---
REDIS_URL = os.getenv("REDIS_URL", settings['broker']['url'])
STREAM_NAME = settings['broker']['stream_name']
VIBRATION_THRESHOLD = settings['processor']['vibration_threshold']
BATCH_SIZE = settings['processor']['batch_size']
READ_BLOCK_MS = settings['processor']['read_block_ms']

async def main():
    # Start Prometheus metrics server
    start_http_server(settings['processor']['metrics_port'])
    
    redis_client = redis.from_url(REDIS_URL)
    print("Worker started: Listening to telemetry_stream...")

    while True:
        try:
            # Read from Redis Stream (Blocking Read)
            # 0 means "read new messages only"
            messages = await redis_client.xread({"telemetry_stream": "$"}, count=10, block=1000)
            
            for stream_name, stream_msgs in messages:
                for msg_id, payload in stream_msgs:
                    data = json.loads(payload[b'data'])
                    
                    # 1. Resilience: Idempotency check could happen here
                    
                    # 2. Logic: Anomaly Detection
                    if data['reading'] > VIBRATION_THRESHOLD:
                        ANOMALY_COUNT.inc()
                        # Dead Letter Logic: Shunt to error stream if parsing fails
                    
                    PROCESSED_COUNT.labels(status="success").inc()
                    
        except Exception as e:
            print(f"Worker Error: {e}")
            PROCESSED_COUNT.labels(status="error").inc()
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
