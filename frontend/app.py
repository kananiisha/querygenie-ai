"""
QueryGenie AI — Full UI v3 with all fixes
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

    .hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 16px;
        padding: 36px 40px;
        margin-bottom: 24px;
        color: white;
    }
    .hero h1 { font-size: 2.2rem; font-weight: 800; margin: 0 0 6px 0; color: white; }
    .hero p { font-size: 1rem; opacity: 0.9; margin: 0; color: white; }

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

    [data-testid="stSidebar"] { background: white !important; border-right: 1px solid #e2e8f0 !important; }
    .step-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; color: #475569; font-size: 0.9rem; border-bottom: 1px solid #f1f5f9; }
    .step-num { background: #ede9fe; color: #6366f1; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem; flex-shrink: 0; }
    .user-badge { background: #f1f5f9; border-radius: 10px; padding: 10px 14px; display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
</style>
""", unsafe_allow_html=True)


def auto_chart(df, question):
    if df is None or df.empty or len(df) < 2:
        return False
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if not numeric_cols:
        return False
    q_lower = question.lower()
    chart_type = "line" if any(w in q_lower for w in ["trend", "over time", "monthly", "daily", "yearly"]) else "bar"
    num_col = numeric_cols[0]
    label_col = text_cols[0] if text_cols else None
    st.markdown("### 📈 Auto Chart")
    if label_col and len(df) <= 20:
        chart_df = df.set_index(label_col)[num_col]
        st.line_chart(chart_df) if chart_type == "line" else st.bar_chart(chart_df)
    else:
        st.bar_chart(df[num_col])
    return True


def run_query(question):
    try:
        payload = {"question": question}
        if st.session_state.mode == "upload" and st.session_state.uploaded_table:
            payload["table_hint"] = st.session_state.uploaded_table
        res = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=120)
        return res.json(), res.status_code
    except requests.exceptions.ConnectionError:
        return {"detail": "Backend not running."}, 503
    except requests.exceptions.Timeout:
        return {"detail": "Timed out — please try again."}, 408
    except Exception as e:
        return {"detail": str(e)}, 500


defaults = {
    "logged_in": False, "token": None, "user_email": None,
    "mode": "demo", "uploaded_table": None, "uploaded_columns": [],
    "uploaded_filename": None, "recommendations": [],
    "selected_question": "", "auto_execute": False,
    "history": [], "reg_success": False, "auth_tab": "login",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def show_auth_page():
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("""
        <div style="text-align:center; padding:32px 0 16px 0;">
            <div style="font-size:3rem;">🔍</div>
            <div style="font-size:2rem; font-weight:900; background:linear-gradient(135deg,#6366f1,#8b5cf6); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">QueryGenie AI</div>
            <div style="color:#94a3b8; font-size:0.9rem; margin:6px 0 24px 0;">Ask your database anything in plain English</div>
        </div>
        """, unsafe_allow_html=True)

        t1, t2 = st.columns(2)
        with t1:
            if st.button("🔐 Login", key="tab_login", use_container_width=True):
                st.session_state.auth_tab = "login"
                st.session_state.reg_success = False
        with t2:
            if st.button("📝 Register", key="tab_register", use_container_width=True):
                st.session_state.auth_tab = "register"

        active = "Login" if st.session_state.auth_tab == "login" else "Register"
        st.markdown(f"<div style='text-align:center;color:#6366f1;font-size:0.8rem;font-weight:700;margin:-6px 0 12px 0;'>▼ {active}</div>", unsafe_allow_html=True)

        if st.session_state.auth_tab == "login":
            with st.container():
                st.markdown("<div style='background:white;border-radius:16px;padding:28px;box-shadow:0 4px 24px rgba(99,102,241,0.10);border:1px solid #e2e8f0;'>", unsafe_allow_html=True)
                st.markdown("#### 👋 Welcome back!")
                email = st.text_input("Email address", placeholder="you@example.com", key="login_email")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
                if st.button("Login to QueryGenie →", type="primary", key="login_btn"):
                    if not email:
                        st.error("❌ Please enter your email address.")
                    elif "@" not in email:
                        st.error("❌ Please enter a valid email address.")
                    elif not password:
                        st.error("❌ Please enter your password.")
                    else:
                        with st.spinner("Logging in..."):
                            try:
                                res = requests.post(f"{BACKEND_URL}/auth/login", json={"email": email, "password": password}, timeout=10)
                                if res.status_code == 200:
                                    st.session_state.logged_in = True
                                    st.session_state.token = res.json()["access_token"]
                                    st.session_state.user_email = email
                                    st.rerun()
                                elif res.status_code == 401:
                                    st.error("❌ Email or password is incorrect.")
                                    st.info("💡 Not registered yet? Click **Register** above to create a free account.")
                                else:
                                    st.error("❌ Login failed. Please try again.")
                            except requests.exceptions.ConnectionError:
                                st.error("❌ Cannot connect to server. Make sure backend is running.")
                            except Exception:
                                st.error("❌ Something went wrong. Please try again.")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center;color:#94a3b8;font-size:0.82rem;margin-top:10px;'>No account? Click <b>Register</b> above — it's free.</div>", unsafe_allow_html=True)

        else:
            with st.container():
                st.markdown("<div style='background:white;border-radius:16px;padding:28px;box-shadow:0 4px 24px rgba(99,102,241,0.10);border:1px solid #e2e8f0;'>", unsafe_allow_html=True)
                st.markdown("#### 🚀 Create your free account")
                if st.session_state.reg_success:
                    st.success("✅ Account created! Logging you in...")
                else:
                    reg_email = st.text_input("Email address", placeholder="you@example.com", key="reg_email")
                    reg_pass = st.text_input("Password", type="password", placeholder="Minimum 6 characters", key="reg_pass")
                    reg_pass2 = st.text_input("Confirm password", type="password", placeholder="Re-enter your password", key="reg_pass2")
                    if st.button("Create Account & Start →", type="primary", key="reg_btn"):
                        if not reg_email:
                            st.error("❌ Please enter your email address.")
                        elif "@" not in reg_email or "." not in reg_email:
                            st.error("❌ Please enter a valid email (e.g. name@gmail.com).")
                        elif not reg_pass:
                            st.error("❌ Please enter a password.")
                        elif len(reg_pass) < 6:
                            st.error("❌ Password must be at least 6 characters.")
                        elif reg_pass != reg_pass2:
                            st.error("❌ Passwords don't match. Please try again.")
                        else:
                            with st.spinner("Creating your account..."):
                                try:
                                    res = requests.post(f"{BACKEND_URL}/auth/register", json={"email": reg_email, "password": reg_pass}, timeout=10)
                                    if res.status_code == 200:
                                        login_res = requests.post(f"{BACKEND_URL}/auth/login", json={"email": reg_email, "password": reg_pass}, timeout=10)
                                        if login_res.status_code == 200:
                                            st.session_state.logged_in = True
                                            st.session_state.token = login_res.json()["access_token"]
                                            st.session_state.user_email = reg_email
                                            st.rerun()
                                        else:
                                            st.session_state.auth_tab = "login"
                                            st.session_state.reg_success = True
                                            st.rerun()
                                    elif res.status_code == 400:
                                        st.error("❌ This email is already registered.")
                                        st.info("💡 Already have an account? Click **Login** above.")
                                    else:
                                        st.error("❌ Registration failed. Please try again.")
                                except requests.exceptions.ConnectionError:
                                    st.error("❌ Cannot connect to server. Make sure backend is running.")
                                except Exception:
                                    st.error("❌ Something went wrong. Please try again.")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center;color:#94a3b8;font-size:0.82rem;margin-top:10px;'>Already have an account? Click <b>Login</b> above.</div>", unsafe_allow_html=True)


def show_main_app():
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

        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
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
            for i, q in enumerate(samples):
                if st.button(f"▸ {q}", key=f"sb_{i}", use_container_width=True):
                    st.session_state.selected_question = q
                    st.session_state.auto_execute = True
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
        for num, label in [("1","Schema Retriever"),("2","SQL Generator"),("3","Validator"),("4","Executor"),("5","Explainer")]:
            st.markdown(f'<div class="step-item"><div class="step-num">{num}</div><span>{label}</span></div>', unsafe_allow_html=True)

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

    st.markdown("""
    <div class="hero">
        <h1>🔍 QueryGenie AI</h1>
        <p>Ask your database anything in plain English — works with your own CSV, Excel, or our demo dataset.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Mode Selector with active/inactive styling ─────────────────────────────
    st.markdown("#### Choose your data source:")
    col_demo, col_upload = st.columns(2)
    with col_demo:
        is_demo = st.session_state.mode == "demo"
        if is_demo:
            st.markdown('<div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:10px;padding:1px;">', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:white;border:2px solid #6366f1;border-radius:10px;padding:1px;">', unsafe_allow_html=True)
        if st.button("🏪 Demo Dataset (E-Commerce)", key="demo_mode_btn", use_container_width=True):
            st.session_state.mode = "demo"
            st.session_state.recommendations = []
            st.session_state.selected_question = ""
        st.markdown('</div>', unsafe_allow_html=True)

    with col_upload:
        is_upload = st.session_state.mode == "upload"
        if is_upload:
            st.markdown('<div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:10px;padding:1px;">', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:white;border:2px solid #6366f1;border-radius:10px;padding:1px;">', unsafe_allow_html=True)
        if st.button("📁 Upload Your Own File (CSV/Excel)", key="upload_mode_btn", use_container_width=True):
            st.session_state.mode = "upload"
            st.session_state.selected_question = ""
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    if st.session_state.mode == "upload":
        st.markdown("### 📁 Upload Your Dataset")
        c1, c2, c3 = st.columns(3)
        with c1: st.info("📄 **CSV** — up to 500MB")
        with c2: st.info("📊 **Excel** — .xlsx / .xls")
        with c3: st.info("⚡ **Large files** — 1M+ rows")

        uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"], label_visibility="collapsed")
        if uploaded_file:
            size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.markdown(f"**File:** `{uploaded_file.name}` — {size_mb:.1f}MB")
            if size_mb > 10:
                st.warning(f"⚠️ Large file ({size_mb:.0f}MB) — may take a minute.")
            if st.button("⚡ Process & Index File", key="process_file_btn", type="primary"):
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
                            with st.spinner("Generating smart questions..."):
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
            st.markdown("### 💡 Click a question to ask instantly:")
            rcols = st.columns(2)
            for i, rec in enumerate(st.session_state.recommendations):
                with rcols[i % 2]:
                    if st.button(f"▸ {rec}", key=f"rec_{i}", use_container_width=True):
                        st.session_state.selected_question = rec
                        st.session_state.auto_execute = True

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
        except Exception:
            pass

        if st.session_state.uploaded_filename:
            st.info(f"📊 Active: **{st.session_state.uploaded_filename}** — {len(st.session_state.uploaded_columns)} columns")

        st.divider()

    if st.session_state.mode == "demo":
        st.markdown("""
        <div style="margin-bottom:8px;">
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
        question = st.text_input("q", value=default_q, placeholder=placeholder, label_visibility="collapsed", key="main_question")
        if default_q:
            st.session_state.selected_question = ""
    with col2:
        ask = st.button("⚡ Ask", key="ask_btn", type="primary", use_container_width=True)

    should_execute = ask or (st.session_state.auto_execute and question)
    if st.session_state.auto_execute:
        st.session_state.auto_execute = False

    if should_execute and question:
        if st.session_state.mode == "upload" and not st.session_state.uploaded_table:
            st.warning("⚠️ Please upload a file first.")
        else:
            with st.spinner("🤖 Running AI agents..."):
                data, status_code = run_query(question)
                if status_code == 200:
                    cached = data.get("cached", False)
                    confidence = data.get("confidence", {})
                    conf_score = confidence.get("score", 0)
                    conf_label = confidence.get("label", "")

                    st.session_state.history.insert(0, {
                        "question": question, "sql": data["sql"],
                        "answer": data["answer"], "status": "success",
                        "cached": cached, "confidence": conf_score,
                    })

                    st.markdown(f"""
                    <div class="answer-card">
                        <div class="answer-label">💬 Answer {'⚡ cached' if cached else ''}</div>
                        <div class="answer-text">{data['answer']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    m1, m2, m3, m4 = st.columns(4)
                    with m1: st.metric("📊 Rows", len(data.get("results", [])))
                    with m2: st.metric("🤖 Agents", 5)
                    with m3: st.metric("✅ Status", "Cached ⚡" if cached else "Success")
                    with m4: st.metric("🎯 Confidence", f"{conf_score}% {conf_label}")

                    with st.expander("🔍 View Generated SQL"):
                        st.code(data["sql"], language="sql")

                    if data.get("results"):
                        df = pd.DataFrame(data["results"])
                        charted = auto_chart(df, question)
                        with st.expander(f"📋 Raw Data — {len(data['results'])} row(s)", expanded=not charted):
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            csv = df.to_csv(index=False)
                            st.download_button("⬇️ Download CSV", csv, "results.csv", "text/csv", key="dl_csv")
                else:
                    st.error(f"❌ {data.get('detail', 'Something went wrong.')}")
    elif should_execute:
        st.warning("⚠️ Please type a question first.")

    st.divider()

    st.subheader("📜 Query History")
    h1, h2 = st.columns([3, 1])
    with h1:
        search_term = st.text_input("🔍", placeholder="Search history...", label_visibility="collapsed", key="hist_search")
    with h2:
        if st.button("🔄 Refresh", key="refresh_hist", use_container_width=True):
            try:
                hist = requests.get(f"{BACKEND_URL}/query/history", timeout=10).json()
                st.session_state.history = [
                    {"question": i["question"], "sql": i["sql"], "answer": "",
                     "status": i["status"], "cached": False, "confidence": 0}
                    for i in hist
                ]
            except Exception as e:
                st.error(str(e))

    display_history = st.session_state.history
    if search_term:
        display_history = [h for h in st.session_state.history if search_term.lower() in h["question"].lower()]

    if display_history:
        st.markdown(f"*{len(display_history)} result(s)*")
        for idx, item in enumerate(display_history[:20]):
            icon = "✅" if item["status"] == "success" else "❌"
            cached_tag = " ⚡" if item.get("cached") else ""
            conf = f" — 🎯{item.get('confidence', 0)}%" if item.get("confidence") else ""
            with st.expander(f"{icon} {item['question']}{cached_tag}{conf}"):
                if item.get("answer"):
                    st.markdown(f"**Answer:** {item['answer']}")
                if item.get("sql"):
                    st.code(item["sql"], language="sql")
                if st.button("▶ Ask again", key=f"rerun_{idx}"):
                    st.session_state.selected_question = item["question"]
                    st.session_state.auto_execute = True
    elif search_term:
        st.info(f"No results for '{search_term}'")
    else:
        st.info("No queries yet — ask something above!")


if not st.session_state.logged_in:
    show_auth_page()
else:
    show_main_app()
