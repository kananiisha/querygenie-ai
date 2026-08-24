"""
QueryGenie AI — Upgraded Frontend with File Upload + Demo Mode
"""

import streamlit as st
import requests
import pandas as pd
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="QueryGenie AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    #MainMenu, footer { visibility: hidden; }
    .stApp { background-color: #f8fafc; }

    .hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 16px;
        padding: 36px 40px;
        margin-bottom: 28px;
        color: white;
    }
    .hero h1 { font-size: 2.4rem; font-weight: 800; margin: 0 0 6px 0; color: white; }
    .hero p { font-size: 1.05rem; opacity: 0.9; margin: 0; color: white; }

    .mode-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    .mode-card.active { border-color: #6366f1; background: #f5f3ff; }

    .answer-card {
        background: white;
        border-left: 4px solid #6366f1;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    .answer-label { color: #6366f1; font-size: 0.75rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; }
    .answer-text { color: #1e293b; font-size: 1.05rem; line-height: 1.75; }

    .upload-zone {
        background: #f8fafc;
        border: 2px dashed #c7d2fe;
        border-radius: 12px;
        padding: 32px;
        text-align: center;
        margin: 16px 0;
    }

    .schema-pill {
        display: inline-block;
        background: #ede9fe;
        color: #6366f1;
        border-radius: 6px;
        padding: 3px 10px;
        font-size: 0.78rem;
        font-weight: 500;
        margin: 2px;
    }

    .stTextInput > div > div > input {
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        font-size: 1rem !important;
        padding: 12px !important;
        background: white !important;
        color: #1e293b !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 12px !important;
        width: 100% !important;
    }

    .pill {
        display: inline-block;
        background: #ede9fe;
        color: #6366f1;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 3px;
    }

    [data-testid="stSidebar"] { background: white !important; border-right: 1px solid #e2e8f0 !important; }

    .step-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; color: #475569; font-size: 0.9rem; border-bottom: 1px solid #f1f5f9; }
    .step-num { background: #ede9fe; color: #6366f1; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem; flex-shrink: 0; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
if "mode" not in st.session_state:
    st.session_state.mode = "demo"
if "uploaded_table" not in st.session_state:
    st.session_state.uploaded_table = None
if "uploaded_columns" not in st.session_state:
    st.session_state.uploaded_columns = []
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🔍 QueryGenie AI</h1>
    <p>Ask your database anything in plain English — works with your own CSV, Excel files, or our demo dataset.</p>
</div>
""", unsafe_allow_html=True)

# ─── Mode Selector ────────────────────────────────────────────────────────────
st.markdown("#### Choose your data source:")
col_demo, col_upload = st.columns(2)
with col_demo:
    if st.button("🏪 Demo Dataset (E-Commerce)", use_container_width=True):
        st.session_state.mode = "demo"
with col_upload:
    if st.button("📁 Upload Your Own File (CSV/Excel)", use_container_width=True):
        st.session_state.mode = "upload"

st.markdown(f"**Current mode:** {'🏪 Demo Dataset' if st.session_state.mode == 'demo' else '📁 Upload Mode'}")
st.divider()

# ─── Upload Mode ──────────────────────────────────────────────────────────────
if st.session_state.mode == "upload":
    st.markdown("### 📁 Upload Your Dataset")
    st.markdown("Supports CSV and Excel files up to 50MB.")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        if st.button("⚡ Process File", type="primary"):
            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/upload",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                        timeout=120,
                    )
                    data = res.json()
                    if res.status_code == 200:
                        st.session_state.uploaded_table = data["table_name"]
                        st.session_state.uploaded_columns = data["columns"]
                        st.session_state.uploaded_filename = data["filename"]
                        st.success(f"✅ **{data['filename']}** uploaded successfully! {data['rows']:,} rows, {len(data['columns'])} columns.")
                        st.markdown("**Columns found:**")
                        cols_html = " ".join([f'<span class="schema-pill">{c}</span>' for c in data["columns"]])
                        st.markdown(cols_html, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ {data.get('detail', 'Upload failed.')}")
                except Exception as e:
                    st.error(f"❌ {e}")

    if st.session_state.uploaded_filename:
        st.info(f"📊 Active dataset: **{st.session_state.uploaded_filename}** — {len(st.session_state.uploaded_columns)} columns")

    st.divider()

# ─── Query Input ──────────────────────────────────────────────────────────────
if st.session_state.mode == "demo":
    st.markdown("""
    <div style="margin-bottom: 8px;">
    <span class="pill">Which customers are from Mumbai?</span>
    <span class="pill">Total revenue from payments?</span>
    <span class="pill">How many orders delivered?</span>
    <span class="pill">Top selling category?</span>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1:
    placeholder = "Ask about your uploaded data..." if st.session_state.mode == "upload" else "e.g. Which customers are from Mumbai?"
    question = st.text_input("q", placeholder=placeholder, label_visibility="collapsed")
with col2:
    ask = st.button("⚡ Ask", type="primary", use_container_width=True)

# ─── Pipeline ─────────────────────────────────────────────────────────────────
if ask and question:
    if st.session_state.mode == "upload" and not st.session_state.uploaded_table:
        st.warning("⚠️ Please upload a file first before asking questions.")
    else:
        with st.spinner("🤖 Running AI agents..."):
            try:
                payload = {"question": question}
                if st.session_state.mode == "upload" and st.session_state.uploaded_table:
                    payload["table_hint"] = st.session_state.uploaded_table

                res = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=120)
                data = res.json()

                if res.status_code == 200:
                    st.markdown(f"""
                    <div class="answer-card">
                        <div class="answer-label">💬 Answer</div>
                        <div class="answer-text">{data['answer']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("📊 Rows Returned", len(data.get("results", [])))
                    with c2:
                        st.metric("🤖 Agents Used", 5)
                    with c3:
                        st.metric("✅ Status", "Success")

                    with st.expander("🔍 View Generated SQL"):
                        st.code(data["sql"], language="sql")

                    if data.get("results"):
                        with st.expander(f"📋 Raw Data — {len(data['results'])} row(s)"):
                            df = pd.DataFrame(data["results"])
                            st.dataframe(df, use_container_width=True, hide_index=True)

                            # Export CSV
                            csv = df.to_csv(index=False)
                            st.download_button(
                                "⬇️ Download as CSV",
                                csv,
                                "query_results.csv",
                                "text/csv",
                            )
                else:
                    st.error(f"❌ {data.get('detail', 'Something went wrong.')}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Backend not running. Start it with: `python -m uvicorn backend.main:app --reload`")
            except requests.exceptions.Timeout:
                st.error("⏱️ Timed out — please try again.")
            except Exception as e:
                st.error(f"❌ {e}")

elif ask:
    st.warning("⚠️ Please type a question first.")

st.divider()

# ─── History ──────────────────────────────────────────────────────────────────
st.subheader("📜 Recent Queries")
if st.button("🔄 Refresh"):
    try:
        hist = requests.get(f"{BACKEND_URL}/query/history", timeout=10).json()
        if hist:
            for item in hist:
                icon = "✅" if item["status"] == "success" else "❌"
                with st.expander(f"{icon} {item['question']}"):
                    if item["sql"]:
                        st.code(item["sql"], language="sql")
                    st.caption(f"🕐 {item['created_at']}")
        else:
            st.info("No queries yet!")
    except Exception as e:
        st.error(str(e))

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 QueryGenie AI")
    st.markdown("---")

    if st.session_state.mode == "demo":
        st.markdown("### 💡 Sample Questions")
        for q in [
            "Which customers are from Mumbai?",
            "Total revenue from successful payments?",
            "How many orders were delivered?",
            "Which product category has most orders?",
            "Show all customers from Bangalore",
            "How many orders were cancelled?",
        ]:
            st.markdown(f"▸ {q}")
    else:
        st.markdown("### 📊 Your Dataset")
        if st.session_state.uploaded_filename:
            st.markdown(f"**File:** {st.session_state.uploaded_filename}")
            st.markdown(f"**Columns ({len(st.session_state.uploaded_columns)}):**")
            for col in st.session_state.uploaded_columns[:15]:
                st.markdown(f"▸ `{col}`")
            if len(st.session_state.uploaded_columns) > 15:
                st.markdown(f"*...and {len(st.session_state.uploaded_columns) - 15} more*")
        else:
            st.info("Upload a file to see columns here.")

    st.markdown("---")
    st.markdown("### 🏗️ How it works")
    steps = [
        ("1", "Schema Retriever — finds relevant tables"),
        ("2", "SQL Generator — writes the query"),
        ("3", "Validator — checks it's safe"),
        ("4", "Executor — runs against DB"),
        ("5", "Explainer — plain English answer"),
    ]
    for num, label in steps:
        st.markdown(f"""
        <div class="step-item">
            <div class="step-num">{num}</div>
            <span>{label}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ Tech Stack")
    st.markdown("""
| | |
|---|---|
| LLM | Groq LLaMA 3.3 |
| Embeddings | sentence-transformers |
| Vector DB | Qdrant |
| Backend | FastAPI |
| DB | SQLite / PostgreSQL |
| UI | Streamlit |
    """)
