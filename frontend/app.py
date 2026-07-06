"""
QueryGenie AI — Upgraded Streamlit Frontend
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

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Hide default header */
    #MainMenu, header, footer { visibility: hidden; }

    /* Hero section */
    .hero-container {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 40px;
        margin-bottom: 24px;
        border: 1px solid #2d3748;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-top: 8px;
    }

    /* Answer card */
    .answer-card {
        background: linear-gradient(135deg, #1e293b, #1a2744);
        border: 1px solid #6366f1;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
    }
    .answer-label {
        color: #6366f1;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .answer-text {
        color: #e2e8f0;
        font-size: 1.1rem;
        line-height: 1.7;
    }

    /* SQL card */
    .sql-card {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
    }
    .sql-label {
        color: #58a6ff;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 16px;
        margin: 16px 0;
    }
    .metric-card {
        background: #1e293b;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 16px 24px;
        flex: 1;
        text-align: center;
    }
    .metric-value {
        color: #6366f1;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-label {
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 4px;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        background-color: #1e293b !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-size: 1rem !important;
        padding: 14px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
    }

    /* History item */
    .history-item {
        background: #1e293b;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 16px;
        margin: 8px 0;
        cursor: pointer;
    }
    .history-question {
        color: #e2e8f0;
        font-weight: 500;
    }
    .history-meta {
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 4px;
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #21262d !important;
    }

    /* Sample question pill */
    .sample-pill {
        background: #1e293b;
        border: 1px solid #374151;
        border-radius: 20px;
        padding: 6px 14px;
        color: #94a3b8;
        font-size: 0.85rem;
        display: inline-block;
        margin: 4px 2px;
        cursor: pointer;
    }

    /* Divider */
    hr { border-color: #21262d !important; }

    /* Dataframe */
    .dataframe { background: #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# ─── Hero Section ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <p class="hero-title">🔍 QueryGenie AI</p>
    <p class="hero-subtitle">Ask your business database anything in plain English — no SQL knowledge needed.</p>
</div>
""", unsafe_allow_html=True)

# ─── Query Input ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    question = st.text_input(
        "question",
        placeholder="e.g. Which customers are from Mumbai? | What is total revenue?",
        label_visibility="collapsed",
        key="main_question"
    )
with col2:
    ask_button = st.button("⚡ Ask", type="primary", use_container_width=True)

# Sample question pills
st.markdown("""
<div style="margin: -8px 0 16px 0;">
    <span style="color: #64748b; font-size: 0.8rem;">Try: </span>
    <span class="sample-pill">Which customers are from Mumbai?</span>
    <span class="sample-pill">Total revenue from successful payments?</span>
    <span class="sample-pill">How many orders were delivered?</span>
</div>
""", unsafe_allow_html=True)

# ─── Run Pipeline ─────────────────────────────────────────────────────────────
if ask_button and question:
    with st.spinner("🤖 AI agents working..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/query",
                json={"question": question},
                timeout=60,
            )
            data = response.json()

            if response.status_code == 200:
                # Answer Card
                st.markdown(f"""
                <div class="answer-card">
                    <div class="answer-label">💬 Answer</div>
                    <div class="answer-text">{data['answer']}</div>
                </div>
                """, unsafe_allow_html=True)

                # Metrics row
                result_count = len(data.get("results", []))
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Rows Returned", result_count)
                with col2:
                    st.metric("🤖 Agents Used", "4")
                with col3:
                    st.metric("✅ Status", "Success")

                # SQL expander
                with st.expander("🔍 View Generated SQL Query"):
                    st.code(data["sql"], language="sql")

                # Results table
                if data.get("results"):
                    with st.expander(f"📋 Raw Results — {result_count} row(s)"):
                        df = pd.DataFrame(data["results"])
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True,
                        )
            else:
                st.error(f"❌ {data.get('detail', 'Something went wrong.')}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Make sure the server is running:\n`python -m uvicorn backend.main:app --reload`")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out — the pipeline is taking longer than expected. Try again.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

elif ask_button and not question:
    st.warning("⚠️ Please type a question first.")

st.divider()

# ─── Query History ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("📜 Recent Queries")
with col2:
    refresh = st.button("🔄 Refresh", use_container_width=True)

if refresh:
    try:
        hist = requests.get(f"{BACKEND_URL}/query/history", timeout=10).json()
        if hist:
            for item in hist:
                status_icon = "✅" if item["status"] == "success" else "❌"
                with st.expander(f"{status_icon} {item['question']}"):
                    if item["sql"]:
                        st.code(item["sql"], language="sql")
                    st.caption(f"🕐 {item['created_at']}")
        else:
            st.info("No queries yet — ask something above!")
    except Exception as e:
        st.error(f"Could not load history: {e}")

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 QueryGenie AI")
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("#### 💡 Sample Questions")
    samples = [
        "Which customers are from Mumbai?",
        "What is total revenue from successful payments?",
        "How many orders were delivered?",
        "Which product category has the most orders?",
        "Show all customers from Bangalore",
        "How many orders were cancelled?",
    ]
    for s in samples:
        st.markdown(f"▸ *{s}*")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("#### ⚙️ Tech Stack")
    st.markdown("""
    | Layer | Tech |
    |---|---|
    | LLM | Groq LLaMA 3.3 |
    | Agents | LangChain |
    | Vector DB | Qdrant |
    | Backend | FastAPI |
    | Database | SQLite |
    | UI | Streamlit |
    """)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### 🏗️ Agent Pipeline")
    st.markdown("""
    1. 🔎 **Schema Retriever**
    2. ✍️ **SQL Generator**
    3. 🛡️ **Validator**
    4. ⚡ **Executor**
    5. 💬 **Explainer**
    """)
