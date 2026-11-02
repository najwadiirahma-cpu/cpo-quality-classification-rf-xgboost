import streamlit as st
import os
import base64

def render_logo(width="100px", margin_bottom="10px"):
    img_path = "Lonsum.jpg"
    if os.path.exists(img_path):
        with open(img_path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode()
            return f'<img src="data:image/png;base64,{b64}" width="{width}" style="margin-bottom: {margin_bottom}; object-fit: contain;">'
    return ""

st.set_page_config(
    page_title="Sistem Klasifikasi Mutu CPO | PT Lonsum",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

if not st.session_state.get('logged_in', False):
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ── CSS GLOBAL ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: #f8faf8;
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: #f0fdf4 !important;
    border-right: 1px solid #bbf7d0;
}
[data-testid="stSidebar"] * { color: #1e3a2f !important; }

/* Global text color — nuclear override for light theme */
.stApp {
    color: #1a2e23 !important;
}
/* Streamlit main content area — pastikan semua teks terlihat */
.stMainBlockContainer *,
.stMain *,
[data-testid="stAppViewContainer"] *,
[data-testid="stMainBlockContainer"] *,
.main *,
.block-container *,
.element-container * {
    color: #1a2e23 !important;
}
/* Semua teks Markdown */
.stMarkdown, .stMarkdown *,
.stMarkdown p, .stMarkdown span,
.stMarkdown li, .stMarkdown h1, .stMarkdown h2,
.stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
.stMarkdown strong, .stMarkdown em, .stMarkdown code,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] *,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
/* Labels & widgets */
label, small, strong, em,
.stCaption, [data-testid="stCaptionContainer"],
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"],
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stElementContainer"] *,
.stTextInput label, .stNumberInput label,
.stDateInput label, .stSelectbox label,
.stFileUploader label,
[data-testid="stForm"] *,
/* Teks heading Streamlit */
h1, h2, h3, h4, h5, h6,
[data-testid="stHeadingWithActionElements"],
[data-testid="stHeadingWithActionElements"] * {
    color: #1a2e23 !important;
}
/* Ensure buttons keep white text */
.stButton > button, .stButton > button *,
[data-testid="stFormSubmitButton"] button,
[data-testid="stFormSubmitButton"] button *,
[data-testid="stDownloadButton"] button,
[data-testid="stDownloadButton"] button * {
    color: #ffffff !important;
}

/* Global Buttons */
.stButton > button {
    background: #16a34a !important;
    color: white !important; border: none !important;
    border-radius: 6px !important; font-weight: 500 !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #15803d !important;
    transform: none !important;
}

/* Sidebar Menu Buttons */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #14532d !important;
    border-radius: 4px !important;
    justify-content: flex-start !important;
    padding: 0.25rem 1rem !important;
    min-height: 28px !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
}
[data-testid="stSidebar"] .stButton > button * {
    color: #14532d !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #dcfce7 !important;
    color: #14532d !important;
}
[data-testid="stSidebar"] .stButton > button:hover * {
    color: #14532d !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #dcfce7 !important;
    color: #14532d !important;
    font-weight: 500 !important;
    border-left: 3px solid #16a34a !important;
    border-radius: 0 4px 4px 0 !important;
}

/* Inputs */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 6px !important; color: #1a2e23 !important;
}
[data-testid="stNumberInput"] input::placeholder,
[data-testid="stTextInput"] input::placeholder,
::placeholder,
::-webkit-input-placeholder,
::-moz-placeholder,
:-ms-input-placeholder {
    color: #9ca3af !important;
    opacity: 1 !important;
}
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #16a34a !important;
    box-shadow: 0 0 0 1px #16a34a !important;
}

/* Cards & Layout */
.card {
    background: #ffffff;
    border: 1px solid #d4e8db;
    border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.page-title {
    font-size: 1.75rem; font-weight: 600;
    color: #14532d; margin-bottom: 0.25rem;
}
.page-sub {
    color: #4b7a5e;
    font-size: 0.9rem; margin-bottom: 1.5rem;
}
.result-baik {
    background: #f0fdf4;
    border: 1px solid #22c55e;
    border-radius: 8px; padding: 1rem; text-align: center;
}
.result-kurang {
    background: #fef2f2;
    border: 1px solid #ef4444;
    border-radius: 8px; padding: 1rem; text-align: center;
}
.result-label {
    font-size: 1.25rem; font-weight: 600; margin: 0;
}
.result-model {
    font-size: 0.75rem; color: #6b7280;
    margin-bottom: 0.25rem; text-transform: uppercase; letter-spacing: 0.05em;
}
hr { border-color: #d4e8db !important; }

/* Tab styling */
[data-baseweb="tab-list"] {
    gap: 4px !important;
    border-bottom: 1px solid #d4e8db !important;
    padding-bottom: 0 !important;
}
[data-baseweb="tab"] {
    color: #3d6b50 !important;
    padding: 0.55rem 1.2rem !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    border-radius: 6px 6px 0 0 !important;
    margin-right: 2px !important;
    white-space: nowrap !important;
}
[data-baseweb="tab"]:hover {
    background: #f0fdf4 !important;
    color: #14532d !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: #16a34a !important;
    font-weight: 600 !important;
}
[data-baseweb="tab-highlight"] {
    background-color: #16a34a !important;
    height: 2px !important;
}
[data-baseweb="tab-border"] {
    background-color: #d4e8db !important;
}

/* Selectbox, Date input */
[data-baseweb="select"] > div {
    background: #ffffff !important;
    border-color: #d1d5db !important;
    color: #1a2e23 !important;
}
[data-baseweb="input"] {
    background: #ffffff !important;
    color: #1a2e23 !important;
}




/* Expander */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border-color: #d4e8db !important;
}
[data-testid="stExpander"] summary {
    color: #1a2e23 !important;
}

/* Date Input */
[data-testid="stDateInput"] input {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 6px !important;
    color: #1a2e23 !important;
}
[data-testid="stDateInput"] input:focus {
    border-color: #16a34a !important;
    box-shadow: 0 0 0 1px #16a34a !important;
}
[data-testid="stDateInput"] label {
    color: #16a34a !important;
}
[data-testid="stDateInput"] svg {
    fill: #16a34a !important;
    color: #16a34a !important;
}

/* All labels in green */
[data-testid="stWidgetLabel"] label,
[data-testid="stWidgetLabel"] p,
.stSelectbox label,
.stMultiSelect label,
.stDateInput label,
.stNumberInput label {
    color: #1a2e23 !important;
}

/* Selectbox */
[data-baseweb="select"] {
    background: #ffffff !important;
}
[data-baseweb="select"] > div {
    background: #ffffff !important;
    border-color: #d1d5db !important;
    color: #1a2e23 !important;
}
[data-baseweb="select"] svg {
    fill: #16a34a !important;
    color: #16a34a !important;
}
/* Selectbox dropdown */
[data-baseweb="popover"] {
    background: #ffffff !important;
    border: 1px solid #d4e8db !important;
}
[data-baseweb="popover"] [role="listbox"] {
    background: #ffffff !important;
}
[data-baseweb="popover"] [role="option"] {
    background: #ffffff !important;
    color: #1a2e23 !important;
}
[data-baseweb="popover"] [role="option"]:hover {
    background: #f0fdf4 !important;
}
[data-baseweb="popover"] [role="option"][aria-selected="true"] {
    background: #dcfce7 !important;
    color: #14532d !important;
}
/* Calendar / Date Picker popover */
[data-baseweb="calendar"] {
    background: #ffffff !important;
    color: #1a2e23 !important;
}
[data-baseweb="calendar"] [role="gridcell"] button {
    color: #1a2e23 !important;
}
[data-baseweb="calendar"] [role="gridcell"] button:hover {
    background: #dcfce7 !important;
}
[data-baseweb="calendar"] [role="gridcell"] button[aria-selected="true"] {
    background: #16a34a !important;
    color: #ffffff !important;
}
[data-baseweb="calendar"] [data-baseweb="calendar-header"] {
    background: #f0fdf4 !important;
    color: #14532d !important;
}

/* Input (baseweb generic) */
[data-baseweb="input"] {
    background: #ffffff !important;
    color: #1a2e23 !important;
    border-color: #d1d5db !important;
}
[data-baseweb="input"] input {
    color: #1a2e23 !important;
    -webkit-text-fill-color: #1a2e23 !important;
}

/* Form container */
[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1px solid #d4e8db !important;
    border-radius: 12px !important;
}

/* Metric */
[data-testid="stMetric"] {
    background: transparent;
}
[data-testid="stMetricValue"] {
    color: #14532d !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"] {
    color: #4b7a5e !important;
}
[data-testid="stMetricDelta"] svg {
    fill: currentColor !important;
}

/* Alert boxes */
[data-testid="stAlert"] {
    color: #1a2e23 !important;
}
.stAlert [data-testid="stMarkdownContainer"] p {
    color: inherit !important;
}

/* Info box */
div[data-baseweb="notification"] {
    color: #1a2e23 !important;
}

/* Success message */
.stSuccess, .element-container .stAlert {
    border-radius: 6px !important;
}

/* Download button */
[data-testid="stDownloadButton"] button {
    background: #16a34a !important;
    color: #ffffff !important;
    border: none !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #15803d !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    color: #1a2e23 !important;
}
[data-testid="stFileUploader"] section {
    background: #f0fdf4 !important;
    border: 2px dashed #16a34a !important;
    border-radius: 12px !important;
    padding: 2rem !important;
    text-align: center;
}
[data-testid="stFileUploader"] section:hover {
    background: #dcfce7 !important;
    border-color: #15803d !important;
}
[data-testid="stFileUploader"] [data-testid="baseButton-secondary"] {
    background: #16a34a !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
}
[data-testid="stFileUploader"] [data-testid="baseButton-secondary"],
[data-testid="stFileUploader"] [data-testid="baseButton-secondary"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
}
[data-testid="stFileUploader"] [data-testid="baseButton-secondary"]:hover {
    background: #15803d !important;
}




[data-testid="stFileUploader"] section [data-testid="stMarkdownContainer"] p,
[data-testid="stFileUploader"] section small {
    color: #14532d !important;
    font-weight: 500;
}
[data-testid="stFileUploader"] section svg {
    color: #16a34a !important;
    fill: #16a34a !important;
    width: 48px !important;
    height: 48px !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #16a34a !important;
}

/* Icon overrides — all SVG icons should be green */
[data-testid="stSidebar"] svg {
    fill: #16a34a !important;
    color: #16a34a !important;
}
.stApp svg.icon,
[data-testid="stIconMaterial"],
[data-testid="stHeader"] svg {
    color: #16a34a !important;
    fill: #16a34a !important;
}

/* Number input +/- buttons */
[data-testid="stNumberInput"] button {
    background: #f0fdf4 !important;
    color: #16a34a !important;
    border-color: #d4e8db !important;
}
[data-testid="stNumberInput"] button:hover {
    background: #dcfce7 !important;
}
[data-testid="stNumberInput"] button svg {
    fill: #16a34a !important;
    color: #16a34a !important;
    stroke: #16a34a !important;
}

/* Streamlit toolbar */
[data-testid="stToolbar"] {
    background: transparent !important;
}
[data-testid="stToolbar"] button {
    background: transparent !important;
    color: #4b7a5e !important;
}

/* Caption */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #4b7a5e !important;
}

/* Form submit button */
[data-testid="stFormSubmitButton"] button {
    background: #16a34a !important;
    color: #ffffff !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: #15803d !important;
}

/* Tooltip */
[data-baseweb="tooltip"] {
    background: #ffffff !important;
    color: #1a2e23 !important;
    border: 1px solid #d4e8db !important;
}

/* Multiselect */
[data-baseweb="tag"] {
    background: #dcfce7 !important;
    color: #14532d !important;
}

/* Progress bar */
.stProgress > div > div {
    background: #16a34a !important;
}

/* Header / top bar */
[data-testid="stHeader"] {
    background: rgba(248, 250, 248, 0.95) !important;
    backdrop-filter: blur(10px) !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #f0fdf4;
}
::-webkit-scrollbar-thumb {
    background: #bbf7d0;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #86efac;
}


/* ── Manajemen Pengguna: action mini-buttons ─────────────────────── */
/* Edit / Delete icon buttons inside user list */
div[data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"] {
    min-height: 32px !important;
    padding: 0.2rem 0.6rem !important;
    font-size: 0.85rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── LOGIN ─────────────────────────────────────────────────────────────────────
from utils import login_user

def halaman_login():
    logo_html = render_logo(width="80px", margin_bottom="10px")
    st.markdown(f"""
<div style="max-width:420px; margin: 8vh auto 0;">
    <div style="text-align:center;">
        {logo_html}
    </div>
    <div style="text-align:center; font-family:'Inter',sans-serif;
                font-size:2rem; font-weight:700; color:#14532d;">
        CPO QC System
    </div>
    <div style="text-align:center; color:#4b7a5e;
                font-size:0.85rem; margin-bottom:1.8rem;">
        PT PP London Sumatra Indonesia Tbk<br>Quality Control Testing Laboratory
    </div>
</div>
""", unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("#### Masuk ke Sistem")
        username = st.text_input("Username", placeholder="username")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        if st.button("Masuk", use_container_width=True):
            user = login_user(username, password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['username']  = user['username']
                st.session_state['nama']      = user['nama']
                st.session_state['role']      = user.get('role', 'admin staff')
                st.query_params['logged_in'] = 'true'
                st.query_params['username']  = user['username']
                st.query_params['nama']      = user['nama']
                st.query_params['role']      = st.session_state['role']
                st.rerun()
            else:
                st.error("Username atau password salah, atau akun tidak aktif.")
        st.markdown('</div>', unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        logo_html = render_logo(width="60px", margin_bottom="6px")
        st.markdown(f"""
<div style="text-align:center; padding:1rem 0 1.5rem;">
    {logo_html}
    <div style="font-family:'Inter',sans-serif; font-size:1.3rem;
                font-weight:700; color:#14532d;">CPO QC</div>
    <div style="font-size:0.72rem; color:#4b7a5e; margin-top:2px;">
        PT Lonsum · QCTL
    </div>
</div>
""", unsafe_allow_html=True)

        role = st.session_state.get('role', '').lower()
        if role in ['admin it', 'admin']:
            menu_options = [
                "Manajemen Pengguna",
                "Profil"
            ]
        else:
            menu_options = [
                "Prediksi Manual",
                "Prediksi Batch",
                "Riwayat Prediksi",
                "Profil"
            ]

        if 'current_page' not in st.session_state or st.session_state['current_page'] not in menu_options:
            st.session_state['current_page'] = menu_options[0]

        for option in menu_options:
            is_active = st.session_state['current_page'] == option
            if st.button(option, use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state['current_page'] = option
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        nama_display = st.session_state.get('nama', st.session_state.get('username', '—'))
        role_display = st.session_state.get('role', '—').title()
        st.markdown(f"""
        <div style="font-size:0.78rem; color:#4b7a5e; padding:0.5rem 0;">
            Login sebagai<br>
            <span style="color:#14532d; font-weight:600;">
                {nama_display} ({role_display})
            </span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Keluar", use_container_width=True):
            for key in ['logged_in', 'username', 'nama', 'role', 'current_page']:
                st.session_state.pop(key, None)
            st.query_params.clear()
            st.rerun()

    return st.session_state['current_page']

# ── MAIN ──────────────────────────────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    if st.query_params.get('logged_in') == 'true':
        st.session_state['logged_in'] = True
        st.session_state['username'] = st.query_params.get('username', '—')
        st.session_state['nama']     = st.query_params.get('nama', '—')
        st.session_state['role']     = st.query_params.get('role', 'admin staff')
    else:
        st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    halaman_login()
    st.stop()

menu = render_sidebar()

if menu == "Prediksi Manual":
    from views.prediksi_manual import show
    show()
elif menu == "Prediksi Batch":
    from views.prediksi_batch import show
    show()
elif menu == "Riwayat Prediksi":
    from views.riwayat import show
    show()
elif menu == "Manajemen Pengguna":
    from views.manajemen_pengguna import show
    show()
elif menu == "Profil":
    from views.profil import show
    show()
