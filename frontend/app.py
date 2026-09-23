"""
QueryGenie AI — 10/10 UI
Deep navy + electric cyan terminal aesthetic
"""

import streamlit as st
import requests
import pandas as pd
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="QueryGenie AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #070B14 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    color: #F0F4FF !important;
}

#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0D1320 !important;
    border-right: 1px solid rgba(0,212,255,0.12) !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] * { font-family: 'Space Grotesk', sans-serif !important; }
[data-testid="stSidebarContent"] { padding: 0 !important; }

/* ── Inputs ── */
.stTextInput > div > div > input {
    background: #0D1320 !important;
    border: 1px solid rgba(0,212,255,0.25) !important;
    border-radius: 8px !important;
    color: #F0F4FF !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1rem !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00D4FF !important;
    box-shadow: 0 0 0 3px rgba(0,212,255,0.1) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(240,244,255,0.3) !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #00D4FF, #0099CC) !important;
    color: #070B14 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 12px 20px !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #33DDFF, #00B8E6) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(0,212,255,0.25) !important;
}

/* ── Outline button variant ── */
.btn-outline > button {
    background: transparent !important;
    border: 1px solid rgba(0,212,255,0.4) !important;
    color: #00D4FF !important;
    font-weight: 500 !important;
}
.btn-outline > button:hover {
    background: rgba(0,212,255,0.08) !important;
    border-color: #00D4FF !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── Active mode button ── */
.btn-active > button {
    background: linear-gradient(135deg, #00D4FF, #0099CC) !important;
    color: #070B14 !important;
    box-shadow: 0 4px 16px rgba(0,212,255,0.3) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #0D1320 !important;
    border: 1px solid rgba(0,212,255,0.12) !important;
    border-radius: 8px !important;
    color: #F0F4FF !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
.streamlit-expanderContent {
    background: #0D1320 !important;
    border: 1px solid rgba(0,212,255,0.12) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

/* ── Metrics ── */
[data-testid="stMetricValue"] {
    color: #00D4FF !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.4rem !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(240,244,255,0.5) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #0D1320 !important;
    border: 1px dashed rgba(0,212,255,0.3) !important;
    border-radius: 12px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    background: #0D1320 !important;
    border: 1px solid rgba(0,212,255,0.12) !important;
    border-radius: 8px !important;
}

/* ── Code blocks ── */
.stCodeBlock {
    background: #050810 !important;
    border: 1px solid rgba(0,212,255,0.12) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Charts ── */
[data-testid="stArrowVegaLiteChart"], [data-testid="stVegaLiteChart"] {
    background: #0D1320 !important;
    border-radius: 12px !important;
    border: 1px solid rgba(0,212,255,0.12) !important;
}

/* ── Info/success/error ── */
.stAlert {
    background: #0D1320 !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0D1320 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(240,244,255,0.5) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,212,255,0.15) !important;
    color: #00D4FF !important;
}

/* ── Custom components ── */
.qg-sidebar-header {
    background: linear-gradient(180deg, #0D1320 0%, #070B14 100%);
    border-bottom: 1px solid rgba(0,212,255,0.12);
    padding: 20px 20px 16px 20px;
}

.qg-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: #00D4FF;
    letter-spacing: -0.02em;
}

.qg-logo-sub {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    color: rgba(0,212,255,0.5);
    letter-spacing: 0.1em;
    margin-top: 2px;
}

.user-pill {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(0,212,255,0.06);
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 10px;
    padding: 10px 14px;
    margin: 12px 0;
}

.user-dot {
    width: 8px;
    height: 8px;
    background: #00FF88;
    border-radius: 50%;
    box-shadow: 0 0 8px #00FF88;
    flex-shrink: 0;
}

.user-email {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    color: #F0F4FF;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.sidebar-section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: rgba(0,212,255,0.4);
    letter-spacing: 0.12em;
    padding: 16px 20px 8px 20px;
    text-transform: uppercase;
}

.sidebar-sample {
    display: block;
    padding: 8px 20px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    color: rgba(240,244,255,0.6);
    border-left: 2px solid transparent;
    transition: all 0.15s;
    cursor: pointer;
    text-decoration: none;
}
.sidebar-sample:hover {
    color: #00D4FF;
    border-left-color: #00D4FF;
    background: rgba(0,212,255,0.04);
}

.step-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 20px;
    border-bottom: 1px solid rgba(240,244,255,0.04);
}
.step-num {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    background: rgba(0,212,255,0.12);
    border: 1px solid rgba(0,212,255,0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #00D4FF;
    font-weight: 600;
    flex-shrink: 0;
}
.step-label {
    font-size: 0.82rem;
    color: rgba(240,244,255,0.6);
}

.qg-hero {
    padding: 32px 0 24px 0;
}
.qg-hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #00D4FF;
    letter-spacing: 0.15em;
    margin-bottom: 12px;
}
.qg-hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #F0F4FF;
    line-height: 1.15;
    letter-spacing: -0.03em;
    margin-bottom: 10px;
}
.qg-hero-title span { color: #00D4FF; }
.qg-hero-sub {
    font-size: 1rem;
    color: rgba(240,244,255,0.5);
    max-width: 520px;
    line-height: 1.6;
}

.answer-surface {
    background: #0D1320;
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 12px;
    padding: 24px;
    margin: 16px 0;
    position: relative;
    overflow: hidden;
}
.answer-surface::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00D4FF, #00FF88, #00D4FF);
}
.answer-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #00D4FF;
    letter-spacing: 0.12em;
    margin-bottom: 12px;
}
.answer-text {
    font-size: 1.05rem;
    color: #F0F4FF;
    line-height: 1.7;
}

.mode-bar {
    display: flex;
    gap: 8px;
    background: #0D1320;
    border: 1px solid rgba(0,212,255,0.12);
    border-radius: 10px;
    padding: 6px;
    margin-bottom: 20px;
}

.schema-tag {
    display: inline-block;
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.2);
    color: #00D4FF;
    border-radius: 6px;
    padding: 3px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    margin: 2px;
}

.sample-chip {
    display: inline-block;
    background: rgba(0,212,255,0.06);
    border: 1px solid rgba(0,212,255,0.15);
    color: rgba(240,244,255,0.7);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.8rem;
    margin: 3px;
    cursor: pointer;
    transition: all 0.15s;
}

.metric-card {
    background: #0D1320;
    border: 1px solid rgba(0,212,255,0.12);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.metric-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    color: #00D4FF;
}
.metric-lbl {
    font-size: 0.7rem;
    color: rgba(240,244,255,0.4);
    margin-top: 4px;
    letter-spacing: 0.05em;
}

/* Auth page */
.auth-terminal {
    background: #050810;
    border-radius: 12px;
    border: 1px solid rgba(0,212,255,0.15);
    padding: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.8;
    min-height: 320px;
    overflow: hidden;
}
.term-prompt { color: #00D4FF; }
.term-query { color: #F0F4FF; }
.term-result { color: #00FF88; }
.term-comment { color: rgba(240,244,255,0.3); }

.auth-card {
    background: #0D1320;
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 16px;
    padding: 36px 32px;
}

/* Spinner override */
.stSpinner > div { border-top-color: #00D4FF !important; }

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: rgba(0,212,255,0.1) !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    color: #00D4FF !important;
    font-weight: 500 !important;
}

/* Hide streamlit branding from tabs */
.stTabs [data-baseweb="tab-highlight"] { background: #00D4FF !important; }

@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
.cursor { animation: blink 1s infinite; color: #00D4FF; }

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeSlideUp 0.4s ease forwards; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def auto_chart(df, question):
    if df is None or df.empty or len(df) < 2:
        return False
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if not numeric_cols:
        return False
    q_lower = question.lower()
    chart_type = "line" if any(w in q_lower for w in ["trend","over time","monthly","daily","yearly"]) else "bar"
    num_col = numeric_cols[0]
    label_col = text_cols[0] if text_cols else None
    st.markdown('<div style="background:#0D1320;border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:16px;margin:12px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#00D4FF;letter-spacing:0.12em;margin-bottom:8px;">VISUALIZATION</div>', unsafe_allow_html=True)
    if label_col and len(df) <= 20:
        chart_df = df.set_index(label_col)[num_col]
        st.line_chart(chart_df) if chart_type == "line" else st.bar_chart(chart_df)
    else:
        st.bar_chart(df[num_col])
    st.markdown('</div>', unsafe_allow_html=True)
    return True


def run_query(question):
    try:
        payload = {"question": question}
        if st.session_state.mode == "upload" and st.session_state.uploaded_table:
            payload["table_hint"] = st.session_state.uploaded_table
        res = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=120)
        return res.json(), res.status_code
    except requests.exceptions.ConnectionError:
        return {"detail": "Cannot reach backend — run `uvicorn backend.main:app --reload`"}, 503
    except requests.exceptions.Timeout:
        return {"detail": "Request timed out. Please try again."}, 408
    except Exception as e:
        return {"detail": str(e)}, 500


# ── Session defaults ───────────────────────────────────────────────────────────
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


# ── Auth ───────────────────────────────────────────────────────────────────────
def show_auth_page():
    col_l, col_m, col_r = st.columns([1, 1.6, 1])
    with col_m:
        st.markdown("""
        <div style="text-align:center; padding: 32px 0 28px 0;">
            <div style="font-family:'JetBrains Mono',monospace; font-size:1.8rem; font-weight:600; color:#00D4FF; letter-spacing:-0.02em;">QueryGenie<span style="color:rgba(0,212,255,0.4);">_</span></div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:0.85rem; color:rgba(240,244,255,0.4); margin-top:6px; letter-spacing:0.05em;">SQL INTELLIGENCE PLATFORM</div>
        </div>
        """, unsafe_allow_html=True)

        # Live terminal preview
        st.markdown("""
        <div class="auth-terminal">
            <div class="term-comment">-- QueryGenie AI • Natural Language SQL Engine</div>
            <br>
            <div><span class="term-prompt">querygenie&gt; </span><span class="term-query">SELECT name, city FROM customers WHERE city = 'Mumbai';</span></div>
            <div class="term-result">→ Rohan Mehta | Mumbai</div>
            <br>
            <div><span class="term-prompt">querygenie&gt; </span><span class="term-query">SELECT SUM(amount) FROM payments WHERE status = 'success';</span></div>
            <div class="term-result">→ ₹29,525.00</div>
            <br>
            <div><span class="term-prompt">querygenie&gt; </span><span class="term-query">SELECT category, COUNT(*) FROM products GROUP BY category;</span></div>
            <div class="term-result">→ Electronics: 3 | Clothing: 3 | Home: 3 | Books: 3</div>
            <br>
            <div><span class="term-prompt">querygenie&gt; </span><span class="term-query cursor">█</span></div>
        </div>
        <div style="text-align:center; font-family:Space Grotesk,sans-serif; font-size:0.75rem; color:rgba(240,244,255,0.25); margin:10px 0 20px 0; letter-spacing:0.05em;">Type anything. Get answers. No SQL needed.</div>
        """, unsafe_allow_html=True)

        # Tab pills
        t1, t2 = st.columns(2)
        with t1:
            is_login = st.session_state.auth_tab == "login"
            tab_class = "btn-active" if is_login else "btn-outline"
            st.markdown(f'<div class="{tab_class}">', unsafe_allow_html=True)
            if st.button("Sign in", key="tab_login", use_container_width=True):
                st.session_state.auth_tab = "login"
            st.markdown('</div>', unsafe_allow_html=True)
        with t2:
            is_reg = st.session_state.auth_tab == "register"
            tab_class = "btn-active" if is_reg else "btn-outline"
            st.markdown(f'<div class="{tab_class}">', unsafe_allow_html=True)
            if st.button("Create account", key="tab_register", use_container_width=True):
                st.session_state.auth_tab = "register"
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        if st.session_state.auth_tab == "login":
            st.markdown('<div style="font-family:Space Grotesk,sans-serif; font-size:1.2rem; font-weight:600; color:#F0F4FF; margin-bottom:20px;">Welcome back</div>', unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="you@example.com", key="login_email", label_visibility="collapsed")
            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
            password = st.text_input("Password", type="password", placeholder="Password", key="login_pass", label_visibility="collapsed")
            st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
            if st.button("Sign in →", type="primary", key="login_btn"):
                if not email:
                    st.error("Enter your email address.")
                elif "@" not in email:
                    st.error("Enter a valid email address.")
                elif not password:
                    st.error("Enter your password.")
                else:
                    with st.spinner(""):
                        try:
                            res = requests.post(f"{BACKEND_URL}/auth/login", json={"email": email, "password": password}, timeout=10)
                            if res.status_code == 200:
                                st.session_state.logged_in = True
                                st.session_state.token = res.json()["access_token"]
                                st.session_state.user_email = email
                                st.rerun()
                            elif res.status_code == 401:
                                st.error("Email or password is incorrect.")
                                st.markdown('<div style="font-size:0.82rem; color:rgba(240,244,255,0.4); margin-top:8px;">No account? Switch to <b>Create account</b> above.</div>', unsafe_allow_html=True)
                            else:
                                st.error("Sign in failed. Please try again.")
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot reach server — is the backend running?")
                        except Exception:
                            st.error("Something went wrong.")

        else:
            st.markdown('<div style="font-family:Space Grotesk,sans-serif; font-size:1.2rem; font-weight:600; color:#F0F4FF; margin-bottom:20px;">Create your account</div>', unsafe_allow_html=True)
            if st.session_state.reg_success:
                st.success("Account created! Signing you in...")
            else:
                reg_email = st.text_input("Email", placeholder="you@example.com", key="reg_email", label_visibility="collapsed")
                st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
                reg_pass = st.text_input("Password", type="password", placeholder="Password (min 6 chars)", key="reg_pass", label_visibility="collapsed")
                st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
                reg_pass2 = st.text_input("Confirm", type="password", placeholder="Confirm password", key="reg_pass2", label_visibility="collapsed")
                st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
                if st.button("Create account →", type="primary", key="reg_btn"):
                    if not reg_email:
                        st.error("Enter your email address.")
                    elif "@" not in reg_email or "." not in reg_email:
                        st.error("Enter a valid email (e.g. name@gmail.com).")
                    elif not reg_pass:
                        st.error("Enter a password.")
                    elif len(reg_pass) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif reg_pass != reg_pass2:
                        st.error("Passwords don't match.")
                    else:
                        with st.spinner(""):
                            try:
                                res = requests.post(f"{BACKEND_URL}/auth/register", json={"email": reg_email, "password": reg_pass}, timeout=10)
                                if res.status_code == 200:
                                    lr = requests.post(f"{BACKEND_URL}/auth/login", json={"email": reg_email, "password": reg_pass}, timeout=10)
                                    if lr.status_code == 200:
                                        st.session_state.logged_in = True
                                        st.session_state.token = lr.json()["access_token"]
                                        st.session_state.user_email = reg_email
                                        st.rerun()
                                    else:
                                        st.session_state.auth_tab = "login"
                                        st.session_state.reg_success = True
                                        st.rerun()
                                elif res.status_code == 400:
                                    st.error("Email already registered.")
                                    st.markdown('<div style="font-size:0.82rem; color:rgba(240,244,255,0.4); margin-top:8px;">Already have an account? Switch to <b>Sign in</b> above.</div>', unsafe_allow_html=True)
                                else:
                                    st.error("Registration failed. Please try again.")
                            except requests.exceptions.ConnectionError:
                                st.error("Cannot reach server — is the backend running?")
                            except Exception:
                                st.error("Something went wrong.")

        st.markdown('</div>', unsafe_allow_html=True)


# ── Main App ───────────────────────────────────────────────────────────────────
def show_main_app():

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class="qg-sidebar-header">
            <div class="qg-logo">QueryGenie<span style="opacity:0.4;">_</span></div>
            <div class="qg-logo-sub">SQL INTELLIGENCE</div>
            <div class="user-pill" style="margin-top:14px;">
                <div class="user-dot"></div>
                <div class="user-email">{st.session_state.user_email}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="btn-outline" style="padding:8px 12px;">', unsafe_allow_html=True)
        if st.button("Sign out", key="logout_btn", use_container_width=True):
            for k in defaults:
                st.session_state[k] = defaults[k]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.mode == "demo":
            st.markdown('<div class="sidebar-section-label">SAMPLE QUERIES</div>', unsafe_allow_html=True)
            samples = [
                "Customers from Mumbai?",
                "Total revenue from payments?",
                "How many orders delivered?",
                "Top selling category?",
                "Customers from Bangalore?",
                "How many orders cancelled?",
            ]
            for i, q in enumerate(samples):
                if st.button(f"↳ {q}", key=f"sb_{i}", use_container_width=True):
                    st.session_state.selected_question = q
                    st.session_state.auto_execute = True
        else:
            st.markdown('<div class="sidebar-section-label">ACTIVE DATASET</div>', unsafe_allow_html=True)
            if st.session_state.uploaded_filename:
                st.markdown(f'<div style="padding:0 20px 8px 20px; font-size:0.82rem; color:#00D4FF; font-weight:500;">{st.session_state.uploaded_filename}</div>', unsafe_allow_html=True)
                st.markdown('<div class="sidebar-section-label" style="padding-top:4px;">COLUMNS</div>', unsafe_allow_html=True)
                for col in st.session_state.uploaded_columns[:15]:
                    st.markdown(f'<div class="sidebar-sample">⬡ {col}</div>', unsafe_allow_html=True)
                if len(st.session_state.uploaded_columns) > 15:
                    st.markdown(f'<div style="padding:4px 20px; font-size:0.72rem; color:rgba(240,244,255,0.3);">+{len(st.session_state.uploaded_columns)-15} more</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="padding:8px 20px; font-size:0.82rem; color:rgba(240,244,255,0.3);">No dataset uploaded yet.</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-label" style="margin-top:8px;">PIPELINE</div>', unsafe_allow_html=True)
        for num, label in [("1","Schema Retriever"),("2","SQL Generator"),("3","Validator"),("4","Executor"),("5","Explainer")]:
            st.markdown(f'<div class="step-row"><div class="step-num">{num}</div><div class="step-label">{label}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-label" style="margin-top:8px;">STACK</div>', unsafe_allow_html=True)
        stack = [("LLM","Groq GPT-OSS-120B"),("Embed","sentence-transformers"),("VectorDB","Qdrant"),("API","FastAPI"),("DB","SQLite / PostgreSQL")]
        for k, v in stack:
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:6px 20px;border-bottom:1px solid rgba(240,244,255,0.04);"><span style="font-family:JetBrains Mono,monospace;font-size:0.65rem;color:rgba(0,212,255,0.5);">{k}</span><span style="font-size:0.75rem;color:rgba(240,244,255,0.5);">{v}</span></div>', unsafe_allow_html=True)

    # ── Main content ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="qg-hero fade-in">
        <div class="qg-hero-eyebrow">NATURAL LANGUAGE → SQL → ANSWER</div>
        <div class="qg-hero-title">Ask your data<br><span>anything.</span></div>
        <div class="qg-hero-sub">No SQL. No analysts. Just type your question and get instant answers from your database.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Mode selector ─────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        is_demo = st.session_state.mode == "demo"
        st.markdown(f'<div class="{"btn-active" if is_demo else "btn-outline"}">', unsafe_allow_html=True)
        if st.button("⬡  Demo — E-Commerce", key="demo_mode_btn", use_container_width=True):
            st.session_state.mode = "demo"
            st.session_state.recommendations = []
            st.session_state.selected_question = ""
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        is_up = st.session_state.mode == "upload"
        st.markdown(f'<div class="{"btn-active" if is_up else "btn-outline"}">', unsafe_allow_html=True)
        if st.button("⬡  Upload CSV / Excel", key="upload_mode_btn", use_container_width=True):
            st.session_state.mode = "upload"
            st.session_state.selected_question = ""
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    # ── Upload mode ───────────────────────────────────────────────────────────
    if st.session_state.mode == "upload":
        st.markdown("""
        <div style="background:#0D1320; border:1px solid rgba(0,212,255,0.12); border-radius:12px; padding:24px; margin-bottom:20px;">
            <div style="font-family:JetBrains Mono,monospace; font-size:0.65rem; color:#00D4FF; letter-spacing:0.12em; margin-bottom:16px;">DATASET INGESTION</div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        for col, label in [(c1,"CSV — up to 500MB"),(c2,"Excel — .xlsx / .xls"),(c3,"Large files — 1M+ rows")]:
            with col:
                st.markdown(f'<div style="background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.1);border-radius:8px;padding:10px 14px;font-size:0.78rem;color:rgba(240,244,255,0.6);">⬡ {label}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader("", type=["csv","xlsx","xls"], label_visibility="collapsed")
        if uploaded_file:
            size_mb = len(uploaded_file.getvalue()) / (1024*1024)
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.78rem;color:rgba(240,244,255,0.5);margin:8px 0;">{uploaded_file.name} — {size_mb:.1f}MB</div>', unsafe_allow_html=True)
            if st.button("⚡  Process & index dataset", key="process_file_btn", type="primary"):
                with st.spinner("Ingesting and indexing..."):
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
                            st.success(f"Indexed {data['rows']:,} rows · {len(data['columns'])} columns")
                            cols_html = " ".join([f'<span class="schema-tag">{c}</span>' for c in data["columns"]])
                            st.markdown(cols_html, unsafe_allow_html=True)
                            with st.spinner("Generating suggested queries..."):
                                try:
                                    rec_res = requests.post(f"{BACKEND_URL}/recommendations", json={"question": "suggest", "table_hint": data["table_name"]}, timeout=30)
                                    if rec_res.status_code == 200:
                                        st.session_state.recommendations = rec_res.json().get("recommendations", [])
                                except Exception:
                                    pass
                        else:
                            st.error(data.get("detail","Upload failed."))
                    except requests.exceptions.Timeout:
                        st.error("Upload timed out — try a smaller file.")
                    except Exception as e:
                        st.error(str(e))

        if st.session_state.recommendations:
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#00D4FF;letter-spacing:0.12em;margin:20px 0 10px 0;">AI-SUGGESTED QUERIES — CLICK TO ASK</div>', unsafe_allow_html=True)
            rc1, rc2 = st.columns(2)
            for i, rec in enumerate(st.session_state.recommendations):
                with (rc1 if i % 2 == 0 else rc2):
                    st.markdown(f'<div class="btn-outline">', unsafe_allow_html=True)
                    if st.button(f"↳ {rec}", key=f"rec_{i}", use_container_width=True):
                        st.session_state.selected_question = rec
                        st.session_state.auto_execute = True
                    st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.uploaded_filename:
            st.markdown(f'<div style="background:rgba(0,255,136,0.06);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px 16px;font-size:0.82rem;color:#00FF88;margin:12px 0;">Active: {st.session_state.uploaded_filename} · {len(st.session_state.uploaded_columns)} columns</div>', unsafe_allow_html=True)

        try:
            tables_res = requests.get(f"{BACKEND_URL}/tables", timeout=5)
            if tables_res.status_code == 200:
                tables = tables_res.json().get("tables", [])
                if tables:
                    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#00D4FF;letter-spacing:0.12em;margin:20px 0 8px 0;">PREVIOUS DATASETS</div>', unsafe_allow_html=True)
                    for t in tables:
                        ct1, ct2 = st.columns([3,1])
                        with ct1:
                            dn = t["table"].replace("uploaded_","").replace("_"," ").title()
                            st.markdown(f'<div style="font-size:0.82rem;color:rgba(240,244,255,0.6);padding:8px 0;">{dn} · {t["rows"]:,} rows</div>', unsafe_allow_html=True)
                        with ct2:
                            st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
                            if st.button("Use", key=f"use_{t['table']}"):
                                st.session_state.uploaded_table = t["table"]
                                st.session_state.uploaded_columns = t["columns"]
                                st.session_state.uploaded_filename = dn
                            st.markdown('</div>', unsafe_allow_html=True)
        except Exception:
            pass

        st.markdown('<div style="height:16px;border-top:1px solid rgba(0,212,255,0.08);margin:20px 0;"></div>', unsafe_allow_html=True)

    # ── Demo chips ─────────────────────────────────────────────────────────────
    if st.session_state.mode == "demo":
        st.markdown("""
        <div style="margin-bottom:12px;">
        <span class="sample-chip">Customers from Mumbai?</span>
        <span class="sample-chip">Total revenue?</span>
        <span class="sample-chip">Orders delivered?</span>
        <span class="sample-chip">Top category?</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Query input ───────────────────────────────────────────────────────────
    col1, col2 = st.columns([5, 1])
    with col1:
        ph = "Ask about your dataset..." if st.session_state.mode == "upload" else "Ask anything — e.g. Which customers are from Mumbai?"
        default_q = st.session_state.get("selected_question", "")
        question = st.text_input("q", value=default_q, placeholder=ph, label_visibility="collapsed", key="main_question")
        if default_q:
            st.session_state.selected_question = ""
    with col2:
        ask = st.button("⚡  Ask", key="ask_btn", type="primary", use_container_width=True)

    should_execute = ask or (st.session_state.auto_execute and question)
    if st.session_state.auto_execute:
        st.session_state.auto_execute = False

    # ── Pipeline result ───────────────────────────────────────────────────────
    if should_execute and question:
        if st.session_state.mode == "upload" and not st.session_state.uploaded_table:
            st.warning("Upload a dataset first.")
        else:
            with st.spinner("Running agents..."):
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
                    <div class="answer-surface fade-in">
                        <div class="answer-label">ANSWER {'· ⚡ CACHED' if cached else ''}</div>
                        <div class="answer-text">{data['answer']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    m1, m2, m3, m4 = st.columns(4)
                    for col, val, lbl in [
                        (m1, len(data.get("results",[])), "ROWS RETURNED"),
                        (m2, 5, "AGENTS USED"),
                        (m3, "CACHED" if cached else "SUCCESS", "STATUS"),
                        (m4, f"{conf_score}% {conf_label}", "CONFIDENCE"),
                    ]:
                        with col:
                            st.markdown(f'<div class="metric-card"><div class="metric-val">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

                    st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

                    with st.expander("SQL QUERY"):
                        st.code(data["sql"], language="sql")

                    if data.get("results"):
                        df = pd.DataFrame(data["results"])
                        charted = auto_chart(df, question)
                        with st.expander(f"RAW DATA — {len(data['results'])} row(s)", expanded=not charted):
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            st.download_button("Download CSV", df.to_csv(index=False), "results.csv", "text/csv", key="dl_csv")
                else:
                    st.error(data.get("detail","Something went wrong."))

    elif should_execute:
        st.warning("Type a question first.")

    # ── History ───────────────────────────────────────────────────────────────
    st.markdown('<div style="height:32px; border-top:1px solid rgba(0,212,255,0.08); margin:24px 0 20px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#00D4FF;letter-spacing:0.12em;margin-bottom:12px;">QUERY HISTORY</div>', unsafe_allow_html=True)

    h1, h2 = st.columns([4, 1])
    with h1:
        search_term = st.text_input("search", placeholder="Filter history...", label_visibility="collapsed", key="hist_search")
    with h2:
        st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if st.button("Refresh", key="refresh_hist", use_container_width=True):
            try:
                hist = requests.get(f"{BACKEND_URL}/query/history", timeout=10).json()
                st.session_state.history = [
                    {"question": i["question"], "sql": i["sql"], "answer": "",
                     "status": i["status"], "cached": False, "confidence": 0}
                    for i in hist
                ]
            except Exception as e:
                st.error(str(e))
        st.markdown('</div>', unsafe_allow_html=True)

    display_history = st.session_state.history
    if search_term:
        display_history = [h for h in st.session_state.history if search_term.lower() in h["question"].lower()]

    if display_history:
        for idx, item in enumerate(display_history[:20]):
            status_color = "#00FF88" if item["status"] == "success" else "#FF4D6D"
            conf = f" · {item.get('confidence',0)}%" if item.get("confidence") else ""
            cached_tag = " · ⚡" if item.get("cached") else ""
            with st.expander(f"{'▸'} {item['question']}{cached_tag}{conf}"):
                if item.get("answer"):
                    st.markdown(f'<div style="font-size:0.9rem;color:rgba(240,244,255,0.7);margin-bottom:12px;line-height:1.6;">{item["answer"]}</div>', unsafe_allow_html=True)
                if item.get("sql"):
                    st.code(item["sql"], language="sql")
                st.markdown('<div class="btn-outline" style="margin-top:8px;">', unsafe_allow_html=True)
                if st.button("Run again", key=f"rerun_{idx}"):
                    st.session_state.selected_question = item["question"]
                    st.session_state.auto_execute = True
                st.markdown('</div>', unsafe_allow_html=True)
    elif search_term:
        st.markdown(f'<div style="font-size:0.85rem;color:rgba(240,244,255,0.3);padding:16px 0;">No results for "{search_term}"</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:0.85rem;color:rgba(240,244,255,0.3);padding:16px 0;">No queries yet — ask something above.</div>', unsafe_allow_html=True)


# ── Router ─────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_auth_page()
else:
    show_main_app()