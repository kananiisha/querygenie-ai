"""
Streamlit frontend for QueryGenie AI.
Mokshi owns this file.
"""

import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="QueryGenie AI", page_icon="🔍", layout="wide")
st.title("🔍 QueryGenie AI")
st.caption("Ask your business database questions in plain English.")

# ─── Query Input ─────────────────────────────────────────────────────────────
question = st.text_input("Your question:", placeholder="e.g. Which customers are from Mumbai?")

if st.button("Ask", type="primary") and question:
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/query",
                json={"question": question},
                timeout=30,
            )
            data = response.json()

            if response.status_code == 200:
                st.success("Answer ready!")
                st.subheader("Generated SQL")
                st.code(data["sql"], language="sql")
            else:
                st.error(f"Error: {data.get('detail', 'Something went wrong.')}")

        except Exception as e:
            st.error(f"Could not connect to backend: {e}")

# ─── Query History ───────────────────────────────────────────────────────────
st.divider()
st.subheader("Recent Queries")

if st.button("Refresh history"):
    try:
        hist = requests.get(f"{BACKEND_URL}/query/history", timeout=10).json()
        for item in hist:
            status_icon = "✅" if item["status"] == "success" else "❌"
            with st.expander(f"{status_icon} {item['question']}"):
                if item["sql"]:
                    st.code(item["sql"], language="sql")
                st.caption(item["created_at"])
    except Exception as e:
        st.error(f"Could not load history: {e}")
