import asyncio
import os
import json
import time
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
DLQ_STREAM_NAME = settings['broker']['dlq_stream_name'] if 'dlq_stream_name' in settings['broker'] else "telemetry_dlq"
VIBRATION_THRESHOLD = settings['processor']['vibration_threshold']
RETRY_LIMIT = settings['processor'].get('retry_limit', 3)

async def shunt_to_dlq(redis_client, msg_id, payload, error_reason):
    """Shunts a 'poison pill' message to the Dead Letter Queue."""
    print(f"[🛡️ DLQ] Shunting message {msg_id} to {DLQ_STREAM_NAME}. Reason: {error_reason}")
    await redis_client.xadd(DLQ_STREAM_NAME, {
        "original_id": str(msg_id),
        "data": payload[b'data'],
        "error": error_reason,
        "ts": str(time.time())
    })
    # Acknowledge in original stream so it's not retried there
    # Note: Using xdel or just letting the group offset move forward
    await redis_client.xack(STREAM_NAME, settings['broker']['group_name'], msg_id)

async def main():
    # Start Prometheus metrics server
    start_http_server(settings['processor']['metrics_port'])
    
    redis_client = redis.from_url(REDIS_URL)
    print(f"Worker started: Listening to {STREAM_NAME} (DLQ: {DLQ_STREAM_NAME})...")

    # In a real app, we'd initialize the consumer group here
    # await redis_client.xgroup_create(STREAM_NAME, settings['broker']['group_name'], id='0', mkstream=True)

    while True:
        try:
            # Read from Redis Stream (Blocking Read)
            messages = await redis_client.xread({STREAM_NAME: "$"}, count=10, block=1000)
            
            for stream_name, stream_msgs in messages:
                for msg_id, payload in stream_msgs:
                    try:
                        data = json.loads(payload[b'data'])
                        
                        # Logic: Anomaly Detection
                        if data['reading'] > VIBRATION_THRESHOLD:
                            ANOMALY_COUNT.inc()
                            
                            # Example of 'Complex' business rule failure shunting to DLQ
                            if data['reading'] > 500.0: # Physical Impossibility
                                await shunt_to_dlq(redis_client, msg_id, payload, "PHYSICAL_IMPOSSIBILITY_THRESHOLD")
                                continue

                        PROCESSED_COUNT.labels(status="success").inc()
                        
                    except json.JSONDecodeError:
                        await shunt_to_dlq(redis_client, msg_id, payload, "MALFORMED_JSON")
                    except Exception as e:
                        print(f"Processing Error: {data['device_id'] if 'data' in locals() else 'unknown'} - {e}")
                        await shunt_to_dlq(redis_client, msg_id, payload, str(e))
                    
        except Exception as e:
            print(f"Critical Worker Error: {e}")
            PROCESSED_COUNT.labels(status="error").inc()
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
