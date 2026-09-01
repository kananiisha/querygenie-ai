"""
QueryGenie AI — Full UI with Login, Upload, Charts, History Search, Confidence
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
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background-color: #f8fafc; }

    /* Auth page */
    .auth-container {
        max-width: 420px;
        margin: 60px auto;
        background: white;
        border-radius: 20px;
        padding: 48px 40px;
        box-shadow: 0 8px 40px rgba(99,102,241,0.12);
        border: 1px solid #e2e8f0;
    }
    .auth-logo {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .auth-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 32px;
    }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 16px;
        padding: 36px 40px;
        margin-bottom: 24px;
        color: white;
    }
    .hero h1 { font-size: 2.2rem; font-weight: 800; margin: 0 0 6px 0; color: white; }
    .hero p { font-size: 1rem; opacity: 0.9; margin: 0; color: white; }

    /* Answer card */
    .answer-card {
        background: white;
        border-left: 4px solid #6366f1;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    }
    .answer-label { color: #6366f1; font-size: 0.72rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; }
    .answer-text { color: #1e293b; font-size: 1.05rem; line-height: 1.75; }

    /* Schema pill */
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

    /* Sample pill */
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

    /* Inputs */
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

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 12px !important;
        width: 100% !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.9 !important; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: white !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    /* Step items */
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

    /* Confidence badge */
    .conf-high { color: #16a34a; font-weight: 700; }
    .conf-medium { color: #d97706; font-weight: 700; }
    .conf-low { color: #dc2626; font-weight: 700; }

    /* User badge in sidebar */
    .user-badge {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 10px 14px;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Auto Chart ────────────────────────────────────────────────────────────────
def auto_chart(df: pd.DataFrame, question: str) -> bool:
    if df is None or df.empty or len(df) < 2:
        return False
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if not numeric_cols:
        return False
    q_lower = question.lower()
    chart_type = "bar"
    if any(w in q_lower for w in ["trend", "over time", "monthly", "daily", "yearly"]):
        chart_type = "line"
    num_col = numeric_cols[0]
    label_col = text_cols[0] if text_cols else None
    st.markdown("### 📈 Auto Chart")
    if label_col and len(df) <= 20:
        chart_df = df.set_index(label_col)[num_col]
        if chart_type == "line":
            st.line_chart(chart_df)
        else:
            st.bar_chart(chart_df)
    else:
        st.bar_chart(df[num_col])
    return True


# ─── Session State ─────────────────────────────────────────────────────────────
defaults = {
    "logged_in": False,
    "token": None,
    "user_email": None,
    "auth_mode": "login",
    "mode": "demo",
    "uploaded_table": None,
    "uploaded_columns": [],
    "uploaded_filename": None,
    "recommendations": [],
    "selected_question": "",
    "history": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Auth Page ─────────────────────────────────────────────────────────────────
def show_auth_page():
    st.markdown("""
    <div class="auth-container">
        <div class="auth-logo">🔍 QueryGenie AI</div>
        <div class="auth-subtitle">Ask your database anything in plain English</div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            st.markdown("#### Welcome back!")
            email = st.text_input("Email", placeholder="you@example.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
            if st.button("Login →", type="primary", key="login_btn"):
                if not email:
                    st.error("❌ Please enter your email address.")
                elif "@" not in email or "." not in email:
                    st.error("❌ Please enter a valid email address.")
                elif not password:
                    st.error("❌ Please enter your password.")
                else:
                    try:
                        res = requests.post(
                            f"{BACKEND_URL}/auth/login",
                            json={"email": email, "password": password},
                            timeout=10,
                        )
                        if res.status_code == 200:
                            st.session_state.logged_in = True
                            st.session_state.token = res.json()["access_token"]
                            st.session_state.user_email = email
                            st.rerun()
                        elif res.status_code == 401:
                            st.error("❌ Incorrect email or password. Please try again.")
                        else:
                            st.error("❌ Login failed. Please try again.")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to server. Make sure the backend is running.")
                    except requests.exceptions.Timeout:
                        st.error("❌ Server took too long to respond. Please try again.")
                    except Exception:
                        st.error("❌ Something went wrong. Please try again.")

            st.markdown("---")
            st.markdown(
                "<div style='text-align:center; color:#94a3b8; font-size:0.85rem;'>Demo: use any email + password to register first</div>",
                unsafe_allow_html=True
            )

        with tab2:
            st.markdown("#### Create your account")
            reg_email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
            reg_pass = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_pass")
            reg_pass2 = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="reg_pass2")
            if st.button("Create Account →", type="primary", key="reg_btn"):
                if not reg_email:
                    st.error("❌ Please enter your email address.")
                elif "@" not in reg_email or "." not in reg_email:
                    st.error("❌ Please enter a valid email address (e.g. name@gmail.com).")
                elif not reg_pass:
                    st.error("❌ Please enter a password.")
                elif len(reg_pass) < 6:
                    st.error("❌ Password must be at least 6 characters long.")
                elif not reg_pass2:
                    st.error("❌ Please confirm your password.")
                elif reg_pass != reg_pass2:
                    st.error("❌ Passwords do not match. Please try again.")
                else:
                    try:
                        res = requests.post(
                            f"{BACKEND_URL}/auth/register",
                            json={"email": reg_email, "password": reg_pass},
                            timeout=10,
                        )
                        if res.status_code == 200:
                            st.success("✅ Account created successfully! Please go to Login tab.")
                        elif res.status_code == 400:
                            st.error("❌ This email is already registered. Please login instead.")
                        else:
                            try:
                                detail = res.json().get("detail", "Registration failed.")
                                st.error(f"❌ {detail}")
                            except Exception:
                                st.error("❌ Something went wrong. Please try again.")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to server. Make sure the backend is running.")
                    except requests.exceptions.Timeout:
                        st.error("❌ Server took too long to respond. Please try again.")
                    except Exception as e:
                        st.error("❌ Something went wrong. Please try again.")


# ─── Main App ──────────────────────────────────────────────────────────────────
def show_main_app():

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class="user-badge">
            <span style="font-size:1.5rem">👤</span>
            <div>
                <div style="font-weight:600; color:#1e293b; font-size:0.9rem">{st.session_state.user_email}</div>
                <div style="color:#94a3b8; font-size:0.75rem">Logged in</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True):
            for k in defaults:
                st.session_state[k] = defaults[k]
            st.rerun()

        st.markdown("---")

        if st.session_state.mode == "demo":
            st.markdown("### 💡 Sample Questions")
            samples = [
                "Which customers are from Mumbai?",
                "Total revenue from successful payments?",
                "How many orders were delivered?",
                "Which product category has most orders?",
                "Show all customers from Bangalore",
                "How many orders were cancelled?",
            ]
            for q in samples:
                if st.button(f"▸ {q}", key=f"sample_{q[:20]}", use_container_width=True):
                    st.session_state.selected_question = q
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
            ("1", "Schema Retriever"),
            ("2", "SQL Generator"),
            ("3", "Validator"),
            ("4", "Executor"),
            ("5", "Explainer"),
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
| LLM | Groq GPT-OSS-120B |
| Embeddings | sentence-transformers |
| Vector DB | Qdrant |
| Backend | FastAPI |
| DB | SQLite / PostgreSQL |
| UI | Streamlit |
        """)

    # ── Hero ───────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero">
        <h1>🔍 QueryGenie AI</h1>
        <p>Ask your database anything in plain English — works with your own CSV, Excel, or our demo dataset.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Mode Selector ──────────────────────────────────────────────────────────
    st.markdown("#### Choose your data source:")
    col_demo, col_upload = st.columns(2)
    with col_demo:
        if st.button("🏪 Demo Dataset (E-Commerce)", use_container_width=True):
            st.session_state.mode = "demo"
            st.session_state.recommendations = []
    with col_upload:
        if st.button("📁 Upload Your Own File (CSV/Excel)", use_container_width=True):
            st.session_state.mode = "upload"

    st.markdown(f"**Current mode:** {'🏪 Demo Dataset' if st.session_state.mode == 'demo' else '📁 Upload Mode'}")
    st.divider()

    # ── Upload Mode ────────────────────────────────────────────────────────────
    if st.session_state.mode == "upload":
        st.markdown("### 📁 Upload Your Dataset")

        col_i1, col_i2, col_i3 = st.columns(3)
        with col_i1:
            st.info("📄 **CSV** — up to 500MB")
        with col_i2:
            st.info("📊 **Excel** — .xlsx / .xls")
        with col_i3:
            st.info("⚡ **Large files** — 1M+ rows")

        uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"], label_visibility="collapsed")

        if uploaded_file:
            size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.markdown(f"**File:** `{uploaded_file.name}` — {size_mb:.1f}MB")
            if size_mb > 10:
                st.warning(f"⚠️ Large file ({size_mb:.0f}MB) — may take a minute.")

            if st.button("⚡ Process & Index File", type="primary"):
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    try:
                        res = requests.post(
                            f"{BACKEND_URL}/upload",
                            files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                            timeout=300,
                        )
                        data = res.json()
                        if res.status_code == 200:
                            st.session_state.uploaded_table = data["table_name"]
                            st.session_state.uploaded_columns = data["columns"]
                            st.session_state.uploaded_filename = data["filename"]
                            st.success(f"✅ **{data['filename']}** — {data['rows']:,} rows, {len(data['columns'])} columns")
                            cols_html = " ".join([f'<span class="schema-pill">{c}</span>' for c in data["columns"]])
                            st.markdown(cols_html, unsafe_allow_html=True)

                            st.markdown("### 💡 AI-Suggested Questions")
                            with st.spinner("Generating..."):
                                try:
                                    rec_res = requests.post(
                                        f"{BACKEND_URL}/recommendations",
                                        json={"question": "suggest", "table_hint": data["table_name"]},
                                        timeout=30,
                                    )
                                    if rec_res.status_code == 200:
                                        st.session_state.recommendations = rec_res.json().get("recommendations", [])
                                except Exception:
                                    pass
                        else:
                            st.error(f"❌ {data.get('detail', 'Upload failed.')}")
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Timed out — try a smaller file.")
                    except Exception as e:
                        st.error(f"❌ {e}")

        if st.session_state.recommendations:
            st.markdown("### 💡 Suggested Questions")
            cols = st.columns(2)
            for i, rec in enumerate(st.session_state.recommendations):
                with cols[i % 2]:
                    if st.button(f"▸ {rec}", key=f"rec_{i}", use_container_width=True):
                        st.session_state.selected_question = rec

        try:
            tables_res = requests.get(f"{BACKEND_URL}/tables", timeout=5)
            if tables_res.status_code == 200:
                tables = tables_res.json().get("tables", [])
                if tables:
                    st.markdown("### 📂 Previously Uploaded Datasets")
                    for t in tables:
                        ct1, ct2 = st.columns([3, 1])
                        with ct1:
                            dn = t["table"].replace("uploaded_", "").replace("_", " ").title()
                            st.markdown(f"**{dn}** — {t['rows']:,} rows, {len(t['columns'])} cols")
                        with ct2:
                            if st.button("Use", key=f"use_{t['table']}"):
                                st.session_state.uploaded_table = t["table"]
                                st.session_state.uploaded_columns = t["columns"]
                                st.session_state.uploaded_filename = dn
                                st.success(f"Switched to {dn}")
        except Exception:
            pass

        if st.session_state.uploaded_filename:
            st.info(f"📊 Active: **{st.session_state.uploaded_filename}** — {len(st.session_state.uploaded_columns)} columns")

        st.divider()

    # ── Query Input ────────────────────────────────────────────────────────────
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
        placeholder = "Ask about your data..." if st.session_state.mode == "upload" else "e.g. Which customers are from Mumbai?"
        default_q = st.session_state.get("selected_question", "")
        question = st.text_input("q", value=default_q, placeholder=placeholder, label_visibility="collapsed")
        if default_q:
            st.session_state.selected_question = ""
    with col2:
        ask = st.button("⚡ Ask", type="primary", use_container_width=True)

    # ── Pipeline ───────────────────────────────────────────────────────────────
    if ask and question:
        if st.session_state.mode == "upload" and not st.session_state.uploaded_table:
            st.warning("⚠️ Please upload a file first.")
        else:
            with st.spinner("🤖 Running AI agents..."):
                try:
                    payload = {"question": question}
                    if st.session_state.mode == "upload" and st.session_state.uploaded_table:
                        payload["table_hint"] = st.session_state.uploaded_table

                    res = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=120)
                    data = res.json()

                    if res.status_code == 200:
                        cached = data.get("cached", False)
                        confidence = data.get("confidence", {})
                        conf_score = confidence.get("score", 0)
                        conf_label = confidence.get("label", "")
                        conf_color = confidence.get("color", "green")

                        st.session_state.history.insert(0, {
                            "question": question,
                            "sql": data["sql"],
                            "answer": data["answer"],
                            "status": "success",
                            "cached": cached,
                            "confidence": conf_score,
                        })

                        st.markdown(f"""
                        <div class="answer-card">
                            <div class="answer-label">💬 Answer {'⚡ cached' if cached else ''}</div>
                            <div class="answer-text">{data['answer']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.metric("📊 Rows", len(data.get("results", [])))
                        with c2:
                            st.metric("🤖 Agents", 5)
                        with c3:
                            st.metric("✅ Status", "Cached ⚡" if cached else "Success")
                        with c4:
                            st.metric("🎯 Confidence", f"{conf_score}% {conf_label}")

                        with st.expander("🔍 View Generated SQL"):
                            st.code(data["sql"], language="sql")

                        if data.get("results"):
                            df = pd.DataFrame(data["results"])
                            charted = auto_chart(df, question)
                            with st.expander(f"📋 Raw Data — {len(data['results'])} row(s)", expanded=not charted):
                                st.dataframe(df, use_container_width=True, hide_index=True)
                                csv = df.to_csv(index=False)
                                st.download_button("⬇️ Download CSV", csv, "results.csv", "text/csv")
                    else:
                        st.error(f"❌ {data.get('detail', 'Something went wrong.')}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Backend not running. Start: `python -m uvicorn backend.main:app --reload`")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Timed out — please try again.")
                except Exception as e:
                    st.error(f"❌ {e}")

    elif ask:
        st.warning("⚠️ Please type a question first.")

    st.divider()

    # ── History with Search ────────────────────────────────────────────────────
    st.subheader("📜 Query History")

    h1, h2 = st.columns([3, 1])
    with h1:
        search_term = st.text_input("🔍", placeholder="Search history...", label_visibility="collapsed", key="hist_search")
    with h2:
        if st.button("🔄 Refresh", use_container_width=True):
            try:
                hist = requests.get(f"{BACKEND_URL}/query/history", timeout=10).json()
                st.session_state.history = [
                    {"question": i["question"], "sql": i["sql"], "answer": "", "status": i["status"], "cached": False, "confidence": 0}
                    for i in hist
                ]
            except Exception as e:
                st.error(str(e))

    display_history = st.session_state.history
    if search_term:
        display_history = [h for h in st.session_state.history if search_term.lower() in h["question"].lower()]

    if display_history:
        st.markdown(f"*{len(display_history)} result(s)*")
        for item in display_history[:20]:
            icon = "✅" if item["status"] == "success" else "❌"
            cached_tag = " ⚡" if item.get("cached") else ""
            conf = f" — 🎯{item.get('confidence', 0)}%" if item.get("confidence") else ""
            with st.expander(f"{icon} {item['question']}{cached_tag}{conf}"):
                if item.get("answer"):
                    st.markdown(f"**Answer:** {item['answer']}")
                if item.get("sql"):
                    st.code(item["sql"], language="sql")
                if st.button("▶ Ask again", key=f"rerun_{item['question'][:25]}"):
                    st.session_state.selected_question = item["question"]
    elif search_term:
        st.info(f"No results for '{search_term}'")
    else:
        st.info("No queries yet — ask something above!")


# ─── Router ────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_auth_page()
else:
    show_main_app()
