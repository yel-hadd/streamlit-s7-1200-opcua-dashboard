import streamlit as st
import random
import time

st.title("IoT Dashboard Prototype")


# Create placeholders for metrics
col1, col2, col3, col4 = st.columns(4)
metric1_placeholder = col1.empty()
metric2_placeholder = col2.empty()
metric3_placeholder = col3.empty()
metric4_placeholder = col4.empty()

col5, col6, col7, col8 = st.columns(4)
col6.button("Refresh")
col7.button("Export to CSV")

while True:
    # Generate random numbers for metrics
    metric1 = random.randint(1, 100)
    metric2 = random.randint(1, 100)
    metric3 = random.randint(1, 100)
    metric4 = random.randint(1, 100)

    # Update metrics
    metric1_placeholder.metric("Metric 1", metric1)
    metric2_placeholder.metric("Metric 2", metric2)
    metric3_placeholder.metric("Metric 3", metric3)
    metric4_placeholder.metric("Metric 4", metric4)

    # Wait for 0.5 seconds
    time.sleep(0.1)
