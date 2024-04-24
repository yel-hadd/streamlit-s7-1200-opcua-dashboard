import random
import time
import sqlite3
import pandas as pd
from datetime import datetime
from asyncua import ua, Node
from opc_ua_utils import get_nodes, get_asyncua_client
import asyncio
import concurrent.futures

SQLITE_CONN = sqlite3.connect("data.db")
CURSOR = SQLITE_CONN.cursor()
NODES = asyncio.run(get_nodes(False))
RESET_NODE = NODES[4]

CLIENT = get_asyncua_client()

def get_latest_values_from_db(cursor: sqlite3.Cursor) -> dict:
    cursor.execute("SELECT node_id, value FROM latest_values")
    rows = cursor.fetchall()
    latest_values = {}
    for row in rows:
        node_id, value = row
        latest_values[node_id] = value
    return latest_values


def save_data_changes_as_excel(cursor: sqlite3.Cursor) -> pd.DataFrame:
    cursor.execute("SELECT * FROM data_changes")
    filename = f"data_changes_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=["node_id", "value", "timestamp"])
    df.to_excel(filename, index=False)
    return df


import streamlit as st


st.title("IoT Dashboard Prototype")


# Create placeholders for metrics
col1, col2, col3, col4 = st.columns(4)
secondes_placeholder = col1.empty()
clock_placeholder = col2.empty()
inter_placeholder = col3.empty()
relais_placeholder = col4.empty()

st.markdown("  ")
col5, col6, col7, col8 = st.columns(4)
primary_button = col6.button("Export CSV", use_container_width=True, type="primary")
if primary_button:
    st.markdown("  ")
    df = save_data_changes_as_excel(CURSOR)
    st.dataframe(df, hide_index=True, width=720, height=1080)
refresh = col7.button("Refresh", use_container_width=True, type="secondary")

while True:
    values = get_latest_values_from_db(CURSOR)
    # Generate random numbers for metrics
    secondes = values.get("les seconds", random.randint(0, 100))
    clock = values.get("Clock_5Hz")
    inter = values.get("INTERR_1")
    relais = values.get("RELAIS_2")

    # Update metrics
    secondes_placeholder.markdown(f"#### Seconds: {secondes}")
    clock_placeholder.markdown(f"#### 5 Ghz Clock: {clock}")
    inter_placeholder.markdown(f"#### Inter: {inter}")
    relais_placeholder.markdown(f"#### Relais: {relais}")

    # Wait for 0.5 seconds
    time.sleep(0.5)
