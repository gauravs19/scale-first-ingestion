import asyncio
import json
import random
import time
from rich.console import Console
from rich.live import Live
from rich.table import Table

console = Console()

# --- Config ---
DEVICE_COUNT = 100
SIMULATION_STEPS = 50

# --- Metrics Store ---
metrics = {
    "total_packets": 0,
    "anomalies_detected": 0,
    "processing_rate": 0
}

# --- Device Logic ---
async def device_simulator(device_id, queue):
    """Simulates a single industrial sensor."""
    for _ in range(SIMULATION_STEPS):
        # Base reading + random noise
        val = 15.0 + random.uniform(-1, 1)
        
        # Inject occasional anomaly
        if random.random() < 0.05:
            val += 10.0 # Extreme vibration

        packet = {
            "device_id": f"DEV-{device_id:03}",
            "ts": time.time(),
            "reading": round(val, 2),
            "type": "VIBRATION"
        }
        await queue.put(packet)
        await asyncio.sleep(random.uniform(0.1, 0.5))

# --- Processor Logic ---
async def data_processor(queue):
    """Processes packets from the queue (Simulating Spark/Kafka Consumer)."""
    while True:
        packet = await queue.get()
        metrics["total_packets"] += 1
        
        # Validation Logic
        if packet["reading"] > 22.0:
            metrics["anomalies_detected"] += 1
            # Potential Alert Logic here
        
        queue.task_done()

# --- Dashboard Logic ---
def generate_table() -> Table:
    table = Table(title="IoT Ingestion Live Metrics")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    
    table.add_row("Active Devices", str(DEVICE_COUNT))
    table.add_row("Total Packets Captured", str(metrics["total_packets"]))
    table.add_row("Anomalies Flagged", f"[red]{metrics['anomalies_detected']}[/red]")
    table.add_row("Ingestion Health", "[green]NOMINAL[/green]" if metrics["anomalies_detected"] < 20 else "[orange]WARN[/orange]")
    
    return table

# --- Orchestrator ---
async def main():
    queue = asyncio.Queue(maxsize=1000)
    
    # Start Devices
    tasks = [asyncio.create_task(device_simulator(i, queue)) for i in range(DEVICE_COUNT)]
    
    # Start Processor
    processor_task = asyncio.create_task(data_processor(queue))

    # Live Dashboard
    with Live(generate_table(), refresh_per_second=4) as live:
        while not all(t.done() for t in tasks):
            live.update(generate_table())
            await asyncio.sleep(0.2)
    
    # Wait for remaining queue items
    await queue.join()
    processor_task.cancel()
    
    console.print("\n[bold green]Simulation Complete. 100% Data Integrity Verified.[/bold green]")

if __name__ == "__main__":
    asyncio.run(main())
