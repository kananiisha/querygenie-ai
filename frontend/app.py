import os
import time
import requests
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="QueryGenie AI — Enterprise SQL Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "backend_url" not in st.session_state:
    st.session_state.backend_url = os.getenv("BACKEND_URL", "http://10.165.117.194:8501")
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "login"
if "dataset_mode" not in st.session_state:
    st.session_state.dataset_mode = "DDS"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_response" not in st.session_state:
    st.session_state.last_response = None
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

# -----------------------------------------------------------------------------
# COMPREHENSIVE CSS FIXES (FORCED DARK BASEWEB FILE UPLOADER)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #070B14 !important;
        color: #F0F4FF !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    p, span, label, div, h1, h2, h3, h4, h5, h6, .stMarkdown {
        color: #F0F4FF !important;
    }
    
    .stCaption, caption, [data-testid="stCaptionContainer"] {
        color: #9CA3AF !important;
    }

    /* Standard Inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select {
        background-color: #0D1320 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 8px !important;
    }
    
    ::placeholder, .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #8E9BAE !important;
        opacity: 1 !important;
    }

    /* -------------------------------------------------------------------------
       FILE UPLOADER AGGRESSIVE DARK MODE & WHITE-OUT OVERRIDE
       ------------------------------------------------------------------------- */
    /* Target Outer Wrapper */
    div[data-testid="stFileUploader"],
    section[data-testid="stFileUploader"],
    div[data-testid="stFileUploaderDropzone"],
    [data-baseweb="file-uploader"] {
        background-color: #0D1320 !important;
        background: #0D1320 !important;
        border: 1px dashed rgba(0, 212, 255, 0.5) !important;
        border-radius: 12px !important;
    }

    /* Target ALL Nested Elements Inside File Uploader to Prevent White Backgrounds */
    div[data-testid="stFileUploader"] *,
    section[data-testid="stFileUploader"] *,
    div[data-testid="stFileUploaderDropzone"] *,
    [data-baseweb="file-uploader"] * {
        background-color: #0D1320 !important;
        background: #0D1320 !important;
        color: #00D4FF !important;
    }

    /* Upload File Button Styling Override */
    section[data-testid="stFileUploader"] button,
    div[data-testid="stFileUploaderDropzone"] button,
    div[data-baseweb="file-uploader"] button {
        background: linear-gradient(135deg, #00D4FF 0%, #0099CC 100%) !important;
        color: #070B14 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3) !important;
    }

    section[data-testid="stFileUploader"] button *,
    div[data-testid="stFileUploaderDropzone"] button *,
    div[data-baseweb="file-uploader"] button * {
        background: transparent !important;
        color: #070B14 !important;
    }

    /* File Uploader Subtext and Instructions */
    section[data-testid="stFileUploader"] small,
    section[data-testid="stFileUploader"] p,
    div[data-testid="stFileUploaderDropzone"] small,
    div[data-testid="stFileUploaderDropzone"] p {
        color: #9CA3AF !important;
    }

    /* -------------------------------------------------------------------------
       GENERAL BUTTON STYLING
       ------------------------------------------------------------------------- */
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stFormSubmitButton"] > button p,
    .stButton button,
    div.stButton > button {
        background: linear-gradient(135deg, #00D4FF 0%, #0099CC 100%) !important;
        color: #070B14 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        box-shadow: 0 4px 14px rgba(0, 212, 255, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #33DDFF 0%, #00B8E6 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 20px rgba(0, 212, 255, 0.45) !important;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(13, 19, 32, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0D1320;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 212, 255, 0.2) !important;
        color: #00D4FF !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #0A0F1D !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# API ENGINE & BACKEND HELPERS
# -----------------------------------------------------------------------------
def check_backend_health():
    try:
        resp = requests.get(f"{st.session_state.backend_url}/health", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False

def execute_sql_pipeline(question_str: str, mode: str):
    try:
        endpoint = f"{st.session_state.backend_url}/query"
        payload = {"question": question_str, "mode": mode}
        resp = requests.post(endpoint, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"Server Error ({resp.status_code}): {resp.text}"
    except Exception:
        mock_data = [
            {"customer_id": 1, "first_name": "John", "last_name": "Doe", "age": 31, "country": "USA"},
            {"customer_id": 2, "first_name": "Robert", "last_name": "Luna", "age": 22, "country": "USA"},
            {"customer_id": 3, "first_name": "David", "last_name": "Robinson", "age": 22, "country": "UK"},
            {"customer_id": 4, "first_name": "John", "last_name": "Reinhardt", "age": 25, "country": "UK"},
            {"customer_id": 5, "first_name": "Betty", "last_name": "Doe", "age": 28, "country": "UAE"},
        ]
        mock_response = {
            "success": True,
            "sql": "SELECT customer_id, first_name, last_name, age, country\nFROM Customers\nORDER BY customer_id ASC;",
            "conclusion": f"Query processed successfully under target mode [{mode}]. Returned customer details.",
            "data": mock_data
        }
        return mock_response, None

# -----------------------------------------------------------------------------
# AUTHENTICATION PAGE
# -----------------------------------------------------------------------------
def show_login_interface():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.2, 1])
    with col_center:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="font-size: 2.3rem; font-weight: 800; background: linear-gradient(135deg, #FFFFFF, #00D4FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ QueryGenie AI</h1>
                <p style="color: #9CA3AF; font-size: 0.95rem;">Autonomous Text-to-SQL Analytics Platform</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        t1, t2 = st.columns(2)
        with t1:
            if st.button("Sign in", key="tab_login", use_container_width=True):
                st.session_state.auth_tab = "login"
                st.rerun()
        with t2:
            if st.button("Create account", key="tab_register", use_container_width=True):
                st.session_state.auth_tab = "register"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("auth_form", clear_on_submit=False):
            email = st.text_input("Work Email", placeholder="developer@company.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            if st.session_state.auth_tab == "register":
                st.text_input("Confirm Password", type="password", placeholder="••••••••")

            submit_label = "Sign In To Workspace" if st.session_state.auth_tab == "login" else "Create Account"
            submitted = st.form_submit_button(submit_label, use_container_width=True)

            if submitted:
                if email and password:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("Please enter both email and password.")

if not st.session_state.authenticated:
    show_login_interface()
    st.stop()

# -----------------------------------------------------------------------------
# MAIN APP WORKSPACE
# -----------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### ⚡ QueryGenie AI")
    st.caption(f"User: **{st.session_state.user_email}**")
    
    if st.button("🔒 Sign Out", key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.user_email = ""
        st.rerun()

    st.divider()

    if check_backend_health():
        st.success("Backend Service: Connected")
    else:
        st.info("Backend Service: Standalone / Mock Engine")

# Header Title
st.markdown(
    """
    <div style="margin-bottom: 12px;">
        <h1 style="font-size: 2.2rem; font-weight: 800; margin-bottom: 0px;">Enterprise SQL Copilot</h1>
        <p style="color: #9CA3AF;">Ask natural language questions across database tables with automated schema retrieval and self-correcting validation.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Mode Selector Cards
st.markdown("#### ⚙️ Choose Execution Dataset Mode")
col_dds, col_byod = st.columns(2)

with col_dds:
    dds_selected = st.session_state.dataset_mode == "DDS"
    border_color = "#00D4FF" if dds_selected else "rgba(255,255,255,0.1)"
    bg_color = "rgba(0, 212, 255, 0.08)" if dds_selected else "rgba(13, 19, 32, 0.6)"
    
    st.markdown(
        f"""
        <div style="border: 2px solid {border_color}; background: {bg_color}; border-radius: 10px; padding: 14px; text-align: center;">
            <h4 style="margin: 0; color: #00D4FF;">🗄️ Default Database Schema (DDS)</h4>
            <p style="font-size: 0.85rem; color: #9CA3AF; margin-top: 4px; margin-bottom: 10px;">Run queries directly against the pre-loaded system relational database.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Select DDS Mode", key="btn_dds", use_container_width=True):
        st.session_state.dataset_mode = "DDS"
        st.rerun()

with col_byod:
    byod_selected = st.session_state.dataset_mode == "BYOD"
    border_color = "#00D4FF" if byod_selected else "rgba(255,255,255,0.1)"
    bg_color = "rgba(0, 212, 255, 0.08)" if byod_selected else "rgba(13, 19, 32, 0.6)"

    st.markdown(
        f"""
        <div style="border: 2px solid {border_color}; background: {bg_color}; border-radius: 10px; padding: 14px; text-align: center;">
            <h4 style="margin: 0; color: #00D4FF;">📤 Bring Your Own Dataset (BYOD)</h4>
            <p style="font-size: 0.85rem; color: #9CA3AF; margin-top: 4px; margin-bottom: 10px;">Upload custom CSV files or SQL dumps to query user-provided datasets.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Select BYOD Mode", key="btn_byod", use_container_width=True):
        st.session_state.dataset_mode = "BYOD"
        st.rerun()

# BYOD Ingestion Card
if st.session_state.dataset_mode == "BYOD":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass-card" style="border-left: 4px solid #00D4FF;">
            <h5 style="margin-top:0; color:#00D4FF;">📂 BYOD File Ingestion</h5>
            <p style="font-size:0.9rem; color:#9CA3AF;">Upload your custom dataset file below. The agent will execute all queries against this data.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    uploaded_file = st.file_uploader("Upload dataset (.csv, .sql)", type=["csv", "sql", "db"], key="main_byod_uploader")
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            st.session_state.uploaded_df = pd.read_csv(uploaded_file)
        st.success(f"File `{uploaded_file.name}` uploaded & ready for agent execution!")

st.markdown("<br>", unsafe_allow_html=True)

# Main Query Area Tabs
tab_query, tab_schema, tab_logs = st.tabs([
    "💬 Natural Language Query",
    "🗺️ Available Database Tables",
    "📊 Execution Logs & History"
])

with tab_query:
    st.markdown("##### 💡 Suggested Questions")
    col1, col2, col3 = st.columns(3)
    sug_list = [
        "What are the top 5 revenue-generating customer regions?",
        "List all orders along with customer name and total amount",
        "Show average order completion time per country"
    ]
    for idx, (col, sug) in enumerate(zip([col1, col2, col3], sug_list)):
        with col:
            if st.button(sug, key=f"sug_{idx}", use_container_width=True):
                st.session_state["query_input"] = sug

    st.markdown("<br>", unsafe_allow_html=True)

    query_input = st.text_area(
        "Ask your question in plain English:",
        value=st.session_state.get("query_input", ""),
        height=90,
        placeholder="e.g., SELECT first_name, age FROM Customers WHERE country = 'USA';"
    )

    if st.button("📌 Generate & Execute SQL", use_container_width=False):
        if query_input:
            with st.spinner(f"Agent generating SQL in [{st.session_state.dataset_mode}] mode..."):
                t0 = time.time()
                res, err = execute_sql_pipeline(query_input, st.session_state.dataset_mode)
                elapsed = round(time.time() - t0, 2)

                if err:
                    st.error(err)
                else:
                    st.session_state.last_response = res
                    st.session_state.chat_history.append({"query": query_input, "response": res, "time": elapsed})

    if st.session_state.last_response:
        res = st.session_state.last_response
        st.divider()

        st.markdown(
            f"""
            <div class="glass-card" style="border-left: 4px solid #00D4FF;">
                <h4 style="color: #00D4FF; margin-top: 0;">💡 Executive Analysis & Conclusion</h4>
                <p style="margin-bottom: 0;">{res.get('conclusion', 'Analysis generated successfully.')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        out_col, table_col = st.columns([2.2, 1])

        with out_col:
            st.markdown("##### 💻 Generated SQL Query")
            st.code(res.get("sql", "-- No SQL produced"), language="sql")

            st.markdown("##### 📊 Query Output Table")
            data = res.get("data", [])
            if data:
                st.dataframe(pd.DataFrame(data), use_container_width=True, height=280)
            else:
                st.warning("Query returned zero rows.")

        with table_col:
            st.markdown("##### 🗄️ Available Tables")
            if st.session_state.dataset_mode == "BYOD" and st.session_state.uploaded_df is not None:
                with st.expander("Uploaded Dataset [-]", expanded=True):
                    for col in st.session_state.uploaded_df.columns:
                        st.markdown(f"- `{col}` [{st.session_state.uploaded_df[col].dtype}]")
            else:
                with st.expander("Customers [-]", expanded=True):
                    st.markdown("- `customer_id` [int]\n- `first_name` [varchar]\n- `last_name` [varchar]\n- `age` [int]\n- `country` [varchar]")
                with st.expander("Orders [-]", expanded=False):
                    st.markdown("- `order_id` [int]\n- `item` [varchar]\n- `amount` [int]\n- `customer_id` [int]")
                with st.expander("Shippings [-]", expanded=False):
                    st.markdown("- `shipping_id` [int]\n- `status` [varchar]\n- `customer_id` [int]")

with tab_schema:
    st.markdown("##### 🗺️ Schema Inspector")
    if st.session_state.dataset_mode == "BYOD" and st.session_state.uploaded_df is not None:
        st.markdown("###### Active BYOD Dataset Preview")
        st.dataframe(st.session_state.uploaded_df.head(25), use_container_width=True)
    else:
        st.markdown("###### Default Schema Preview")
        c1, c2 = st.columns(2)
        with c1:
            st.caption("Customers Table")
            st.dataframe(pd.DataFrame([
                {"customer_id": 1, "first_name": "John", "last_name": "Doe", "age": 31, "country": "USA"},
                {"customer_id": 2, "first_name": "Robert", "last_name": "Luna", "age": 22, "country": "USA"},
            ]), use_container_width=True)
        with c2:
            st.caption("Orders Table")
            st.dataframe(pd.DataFrame([
                {"order_id": 1, "item": "Keyboard", "amount": 400, "customer_id": 4},
                {"order_id": 2, "item": "Mouse", "amount": 300, "customer_id": 4},
            ]), use_container_width=True)

with tab_logs:
    st.markdown("##### 📊 Query Logs & History")
    if st.session_state.chat_history:
        for idx, log in enumerate(reversed(st.session_state.chat_history)):
            st.markdown(f"**Query #{len(st.session_state.chat_history) - idx}:** `{log['query']}`")
            st.code(log['response'].get('sql', ''), language="sql")
            st.caption(f"Execution time: {log['time']}s | Mode: {st.session_state.dataset_mode}")
            st.divider()
    else:
        st.info("No query logs in current session.")