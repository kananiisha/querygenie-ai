"""
QueryGenie AI — Clean Professional Light Theme
"""

import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://localhost:8000"

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
    .hero h1 {
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0 0 6px 0;
        color: white;
    }
    .hero p {
        font-size: 1.05rem;
        opacity: 0.9;
        margin: 0;
        color: white;
    }

    .answer-card {
        background: white;
        border-left: 4px solid #6366f1;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    .answer-label {
        color: #6366f1;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .answer-text {
        color: #1e293b;
        font-size: 1.05rem;
        line-height: 1.75;
    }

    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
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

    .history-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 8px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    [data-testid="stSidebar"] {
        background: white !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    .step-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        color: #475569;
        font-size: 0.9rem;
        border-bottom: 1px solid #f1f5f9;
    }
    .step-num {
        background: #ede9fe;
        color: #6366f1;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        flex-shrink: 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🔍 QueryGenie AI</h1>
    <p>Ask your business database anything in plain English — no SQL knowledge needed.</p>
</div>
""", unsafe_allow_html=True)

# ─── Input ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    question = st.text_input("q", placeholder="e.g. Which customers are from Mumbai?", label_visibility="collapsed")
with col2:
    ask = st.button("⚡ Ask", type="primary", use_container_width=True)

st.markdown("""
<div style="margin: 4px 0 20px 0;">
<span style="color:#94a3b8; font-size:0.82rem;">Try: </span>
<span class="pill">Which customers are from Mumbai?</span>
<span class="pill">Total revenue from payments?</span>
<span class="pill">How many orders delivered?</span>
<span class="pill">Top selling category?</span>
</div>
""", unsafe_allow_html=True)

# ─── Pipeline ─────────────────────────────────────────────────────────────────
if ask and question:
    with st.spinner("🤖 Running AI agents..."):
        try:
            res = requests.post(f"{BACKEND_URL}/query", json={"question": question}, timeout=60)
            data = res.json()

            if res.status_code == 200:
                # Answer
                st.markdown(f"""
                <div class="answer-card">
                    <div class="answer-label">💬 Answer</div>
                    <div class="answer-text">{data['answer']}</div>
                </div>
                """, unsafe_allow_html=True)

                # Metrics
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("📊 Rows Returned", len(data.get("results", [])))
                with c2:
                    st.metric("🤖 Agents Used", 4)
                with c3:
                    st.metric("✅ Status", "Success")

                # SQL
                with st.expander("🔍 View Generated SQL"):
                    st.code(data["sql"], language="sql")

                # Results table
                if data.get("results"):
                    with st.expander(f"📋 Raw Data — {len(data['results'])} row(s)"):
                        st.dataframe(pd.DataFrame(data["results"]), use_container_width=True, hide_index=True)

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
hc1, hc2 = st.columns([4, 1])
with hc1:
    st.subheader("📜 Recent Queries")
with hc2:
    if st.button("🔄 Refresh", use_container_width=True):
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
| Agents | LangChain |
| Vector DB | Qdrant |
| Backend | FastAPI |
| DB | SQLite |
| UI | Streamlit |
    """)
