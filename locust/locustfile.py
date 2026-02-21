from locust import HttpUser, task, between
import random
import time

class IoTLatencyUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def send_telemetry(self):
        device_id = f"DEV-{random.randint(1, 1000):04}"
        reading = 15.0 + random.uniform(-2, 2)
        
        # Inject periodic heavy patterns to show on Grafana
        if random.random() < 0.05:
            reading += 10.0
            
        self.client.post("/ingest", json={
            "device_id": device_id,
            "type": "VIBRATION",
            "reading": reading,
            "timestamp": time.time()
        })
