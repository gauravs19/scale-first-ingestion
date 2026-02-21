import streamlit as st
import pandas as pd
import numpy as np
import time
import queue
import threading
import random

# --- Page Config ---
st.set_page_config(page_title="IoT Ingestion Live", layout="wide")
st.title("🛰️ Enterprise IoT Ingestion - Live Session")
st.markdown("---")

# --- Initialize Session State ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['ts', 'device_id', 'reading', 'status'])
if 'packet_count' not in st.session_state:
    st.session_state.packet_count = 0
if 'anomalies' not in st.session_state:
    st.session_state.anomalies = 0

# --- Metrics Header ---
col1, col2, col3, col4 = st.columns(4)
m1 = col1.metric("Packets Processed", st.session_state.packet_count)
m2 = col2.metric("Active Streams", "100")
m3 = col3.metric("Anomalies Detected", st.session_state.anomalies, delta_color="inverse")
m4 = col4.metric("Ingestion Health", "NOMINAL", delta="98.2%")

# --- Charts ---
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.subheader("Real-time Vibration (mm/s)")
    line_chart = st.empty()

with chart_col2:
    st.subheader("Ingestion Latency (ms)")
    latency_chart = st.empty()

# --- Simulation Background ---
def run_simulation():
    while True:
        ts = pd.Timestamp.now()
        device_id = f"DEV-{random.randint(1, 100):03}"
        reading = 15.0 + (np.sin(time.time() * 0.5) * 2) + random.uniform(-0.5, 0.5)
        
        status = "NORMAL"
        if random.random() < 0.03: # 3% anomaly rate
            reading += 10.0
            status = "CRITICAL"
            st.session_state.anomalies += 1
        
        new_row = {'ts': ts, 'device_id': device_id, 'reading': reading, 'status': status}
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])]).tail(50)
        st.session_state.packet_count += 1
        
        # Update Charts
        line_chart.line_chart(st.session_state.data.set_index('ts')['reading'])
        
        # Performance/Metrics Update
        m1.metric("Packets Processed", st.session_state.packet_count)
        m3.metric("Anomalies Detected", st.session_state.anomalies)
        
        time.sleep(0.1)

# Start simulation
if st.button("Start Live Session"):
    run_simulation()
