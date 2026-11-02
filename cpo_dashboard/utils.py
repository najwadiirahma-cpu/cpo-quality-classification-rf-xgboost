import streamlit as st
import joblib
import os
import pandas as pd
import numpy as np
from supabase import create_client, Client
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    import plotly.graph_objects as go
    _PLOTLY = True
except ImportError:
    _PLOTLY = False


# ── TOAST NOTIFICATION ────────────────────────────────────────────────────────
def show_toast(message: str, kind: str = "success", duration: int = 4000):
    """
    Tampilkan toast notification di pojok kanan atas halaman.

    Args:
        message : Teks pesan yang ditampilkan.
        kind    : "success" | "error" | "warning" | "info"
        duration: Durasi tampil dalam milidetik (default 4000).
    """
    _cfg = {
        "success": {
            "bg": "#f0fdf4", "border": "#16a34a", "color": "#14532d",
            "icon": (
                '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" '
                'viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" '
                'stroke-linecap="round" stroke-linejoin="round">'
                '<polyline points="20 6 9 17 4 12"/></svg>'
            ),
            "label": "Berhasil",
        },
        "error": {
            "bg": "#fef2f2", "border": "#dc2626", "color": "#991b1b",
            "icon": (
                '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" '
                'viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.5" '
                'stroke-linecap="round" stroke-linejoin="round">'
                '<circle cx="12" cy="12" r="10"/>'
                '<line x1="15" y1="9" x2="9" y2="15"/>'
                '<line x1="9" y1="9" x2="15" y2="15"/></svg>'
            ),
            "label": "Gagal",
        },
        "warning": {
            "bg": "#fffbeb", "border": "#d97706", "color": "#92400e",
            "icon": (
                '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" '
                'viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2.5" '
                'stroke-linecap="round" stroke-linejoin="round">'
                '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 '
                '1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
                '<line x1="12" y1="9" x2="12" y2="13"/>'
                '<line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
            ),
            "label": "Perhatian",
        },
        "info": {
            "bg": "#eff6ff", "border": "#2563eb", "color": "#1e40af",
            "icon": (
                '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" '
                'viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.5" '
                'stroke-linecap="round" stroke-linejoin="round">'
                '<circle cx="12" cy="12" r="10"/>'
                '<line x1="12" y1="8" x2="12" y2="12"/>'
                '<line x1="12" y1="16" x2="12.01" y2="16"/></svg>'
            ),
            "label": "Informasi",
        },
    }
    c = _cfg.get(kind, _cfg["info"])
    import uuid, html as _html
    uid   = uuid.uuid4().hex[:8]
    safe  = _html.escape(message)
    toast_html = f"""
    <style>
    @keyframes _toast_in_{uid} {{
        from {{ opacity:0; transform:translateX(40px); }}
        to   {{ opacity:1; transform:translateX(0); }}
    }}
    @keyframes _toast_out_{uid} {{
        from {{ opacity:1; transform:translateX(0); }}
        to   {{ opacity:0; transform:translateX(40px); }}
    }}
    #toast_{uid} {{
        position: fixed;
        top: 24px;
        right: 24px;
        z-index: 999999;
        min-width: 300px;
        max-width: 420px;
        background: {c['bg']};
        border: 1.5px solid {c['border']};
        border-left: 4px solid {c['border']};
        border-radius: 10px;
        padding: 14px 16px 14px 14px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
        animation: _toast_in_{uid} 0.3s cubic-bezier(0.16,1,0.3,1) forwards;
        font-family: 'Inter', sans-serif;
    }}
    #toast_{uid}.hide {{
        animation: _toast_out_{uid} 0.3s cubic-bezier(0.55,0,1,0.45) forwards;
    }}
    #toast_{uid} .t-icon {{ flex-shrink:0; margin-top:1px; }}
    #toast_{uid} .t-body {{ flex:1; min-width:0; }}
    #toast_{uid} .t-label {{
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: {c['border']};
        margin-bottom: 3px;
    }}
    #toast_{uid} .t-msg {{
        font-size: 0.86rem;
        color: {c['color']};
        line-height: 1.5;
        word-break: break-word;
    }}
    #toast_{uid} .t-close {{
        flex-shrink: 0;
        background: transparent;
        border: none;
        cursor: pointer;
        padding: 2px;
        color: {c['color']};
        opacity: 0.5;
        font-size: 1rem;
        line-height: 1;
        margin-top: -2px;
    }}
    #toast_{uid} .t-close:hover {{ opacity:1; }}
    #toast_{uid} .t-progress {{
        position: absolute;
        bottom: 0; left: 0;
        height: 3px;
        background: {c['border']};
        border-radius: 0 0 0 8px;
        opacity: 0.35;
        animation: _progress_{uid} {duration}ms linear forwards;
    }}
    @keyframes _progress_{uid} {{
        from {{ width:100%; }}
        to   {{ width:0%; }}
    }}
    </style>
    <div id="toast_{uid}" style="position:relative; overflow:hidden;">
        <div class="t-icon">{c['icon']}</div>
        <div class="t-body">
            <div class="t-label">{c['label']}</div>
            <div class="t-msg">{safe}</div>
        </div>
        <button class="t-close" onclick="
            var el=document.getElementById('toast_{uid}');
            el.classList.add('hide');
            setTimeout(function(){{el.remove();}},{300});
        ">&#x2715;</button>
        <div class="t-progress"></div>
    </div>
    <script>
    (function() {{
        setTimeout(function() {{
            var el = document.getElementById('toast_{uid}');
            if (el) {{
                el.classList.add('hide');
                setTimeout(function(){{ el.remove(); }}, 300);
            }}
        }}, {duration});
    }})();
    </script>
    """
    st.html(toast_html)


# ── KONSTANTA ─────────────────────────────────────────────────────────────────
FITUR = ['moisture', 'dirt', 'ffa', 'pv', 'dobi', 'carotene', 'iv']

FITUR_LABEL = {
    'ffa':      'Asam Lemak Bebas / ALB (%)',
    'moisture': 'Kadar Air / Moisture (%)',
    'dirt':     'Kadar Kotoran / Dirt (%)',
    'dobi':     'DOBI (indeks)',
    'pv':       'Bilangan Peroksida / PV (meq/kg)',
    'iv':       'Bilangan Iodium / IV (g I₂/100g)',
    'carotene': 'β-Karoten (ppm)',
}

THRESHOLD = {
    'ffa':      ('≤', 3.0),
    'moisture': ('≤', 0.20),
    'dirt':     ('≤', 0.030),
    'dobi':     ('≥', 2.5),
    'pv':       ('≤', 1.0),
    'iv':       ('≥', 50),
    'carotene': ('≥', 500),
}

INPUT_CONFIG = {
    'ffa':      {'min': 0.0,   'max': 10.0,   'step': 0.01,  'default': 3.0, 'format': '%.2f'},
    'moisture': {'min': 0.0,   'max': 1.0,    'step': 0.001, 'default': 0.20, 'format': '%.3f'},
    'dirt':     {'min': 0.0,   'max': 0.5,    'step': 0.001, 'default': 0.030, 'format': '%.4f'},
    'dobi':     {'min': 0.0,   'max': 5.0,    'step': 0.01,  'default': 2.50, 'format': '%.2f'},
    'pv':       {'min': 0.0,   'max': 5.0,    'step': 0.01,  'default': 1.0, 'format': '%.2f'},
    'iv':       {'min': 30.0,  'max': 70.0,   'step': 0.1,   'default': 50.0, 'format': '%.2f'},
    'carotene': {'min': 100.0, 'max': 1000.0, 'step': 1.0,   'default': 500.0,'format': '%.0f'},
}

# ── MODEL LOADER ──────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    """Load kedua model (RF + XGB) beserta SHAP explainer masing-masing.
    Returns: (rf, xgb, exp_rf, exp_xgb, ok)
    """
    base = "models"
    try:
        rf      = joblib.load(os.path.join(base, "model_rf.pkl"))
        xgb     = joblib.load(os.path.join(base, "model_xgb.pkl"))
        exp_rf  = joblib.load(os.path.join(base, "shap_explainer_rf.pkl"))
        exp_xgb = joblib.load(os.path.join(base, "shap_explainer_xgb.pkl"))
        return rf, xgb, exp_rf, exp_xgb, True
    except Exception as e:
        st.error(f"Model tidak dapat dimuat: {e}")
        return None, None, None, None, False

# ── SUPABASE ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["supabase"]["url"].strip()
    if url.endswith("/"):
        url = url[:-1]
    if url.endswith("/rest/v1"):
        url = url[:-8]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def simpan_riwayat(params: dict, hasil_prediksi: str):
    try:
        sb = get_supabase()
        sb.table("riwayat").insert({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ffa":       params['ffa'],
            "moisture":  params['moisture'],
            "dirt":      params['dirt'],
            "dobi":      params['dobi'],
            "pv":        params['pv'],
            "iv":        params['iv'],
            "carotene":  params['carotene'],
            "hasil_prediksi": hasil_prediksi,
        }).execute()
    except Exception as e:
        st.warning(f"Gagal menyimpan riwayat: {e}")

def ambil_riwayat(tgl_awal=None, tgl_akhir=None) -> pd.DataFrame:
    try:
        sb   = get_supabase()
        q    = sb.table("riwayat").select("*").order("id", desc=True)
        if tgl_awal and tgl_akhir:
            q = q.gte("timestamp", str(tgl_awal)).lte("timestamp", str(tgl_akhir) + " 23:59:59")
        res  = q.execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Gagal mengambil riwayat: {e}")
        return pd.DataFrame()

def hapus_semua_riwayat() -> tuple[bool, str]:
    try:
        sb = get_supabase()
        sb.table("riwayat").delete().gt("id", 0).execute()
        return True, "Seluruh riwayat berhasil dihapus."
    except Exception as e:
        return False, f"Gagal menghapus riwayat: {e}"

def hapus_riwayat_berdasarkan_ids(ids: list) -> tuple[bool, str]:
    try:
        sb = get_supabase()
        sb.table("riwayat").delete().in_("id", ids).execute()
        return True, "Sesi riwayat terpilih berhasil dihapus."
    except Exception as e:
        return False, f"Gagal menghapus sesi: {e}"

# ── HELPERS ───────────────────────────────────────────────────────────────────
def label_str(pred: int) -> str:
    return "Baik" if pred == 1 else "Kurang Baik"

def label_konsensus(pred_rf: int, pred_xgb: int) -> str:
    """Menentukan hasil konsensus dua model via voting mayoritas."""
    if pred_rf == pred_xgb:
        return "Baik" if pred_rf == 1 else "Kurang Baik"
    return "Tidak Konsisten"

def pred_konsensus_int(pred_rf: int, pred_xgb: int) -> int:
    """Voting: 1=Baik, 0=Kurang Baik, -1=Tidak Konsisten."""
    if pred_rf == pred_xgb:
        return pred_rf
    return -1

def result_html(pred: int) -> str:
    cls   = "result-baik"   if pred == 1 else "result-kurang"
    color = "#16a34a"       if pred == 1 else "#dc2626"
    text  = "BAIK"          if pred == 1 else "KURANG BAIK"
    return f"""
    <div class="{cls}">
        <div class="result-model">Hasil Klasifikasi Sistem</div>
        <p class="result-label" style="color:{color}">{text}</p>
    </div>"""

def result_html_dual(pred_rf: int, pred_xgb: int) -> str:
    """Render dua kartu model berdampingan + badge konsensus di bawahnya dengan tampilan enterprise modern."""
    svg_check = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>"""
    svg_cross = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>"""
    svg_alert = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>"""

    def _card(pred: int, model_name: str, model_short: str, top_color: str) -> str:
        is_good   = (pred == 1)
        short_lbl = "BAIK" if is_good else "KURANG BAIK"
        icon      = svg_check if is_good else svg_cross
        badge_bg  = "#f0fdf4" if is_good else "#fef2f2"
        badge_border = "#bbf7d0" if is_good else "#fecdd3"
        txt_color = "#15803d" if is_good else "#991b1b"
        icon_bg   = "#dcfce7" if is_good else "#fee2e2"
        sub_txt   = "Kategori Mutu Standar QCTL" if is_good else "Memerlukan Penanganan QC"

        return f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px;
                    padding:1.2rem 1.4rem; box-shadow:0 4px 20px -2px rgba(0,0,0,0.04);
                    position:relative; overflow:hidden; display:flex; flex-direction:column; justify-content:space-between;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:{top_color};"></div>
            
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.85rem;">
                <div style="display:flex; align-items:center; gap:0.5rem;">
                    <span style="font-weight:700; font-size:0.9rem; color:#0f172a; letter-spacing:0.01em;">{model_name}</span>
                    <span style="font-size:0.68rem; font-weight:700; background:#f1f5f9; color:#475569; padding:2px 8px; border-radius:20px; border:1px solid #e2e8f0;">{model_short}</span>
                </div>
                <span style="font-size:0.72rem; color:#64748b; font-weight:500;">Dual-Model Testing</span>
            </div>

            <div style="display:flex; align-items:center; gap:1rem; background:{badge_bg}; border:1px solid {badge_border}; border-radius:10px; padding:0.9rem 1.1rem;">
                <div style="width:42px; height:42px; border-radius:50%; background:{icon_bg}; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                    {icon}
                </div>
                <div>
                    <div style="font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:#64748b;">Hasil Model {model_short}</div>
                    <div style="font-size:1.15rem; font-weight:800; color:{txt_color}; line-height:1.2;">{short_lbl}</div>
                    <div style="font-size:0.73rem; color:#475569; margin-top:2px;">{sub_txt}</div>
                </div>
            </div>
        </div>"""

    card_rf  = _card(pred_rf,  "Random Forest", "RF",  "#2563eb")
    card_xgb = _card(pred_xgb, "XGBoost",       "XGB", "#16a34a")

    vs_html = """
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:0 0.2rem; flex-shrink:0;">
        <div style="width:30px; height:30px; border-radius:50%; background:#f8fafc; border:1px solid #cbd5e1; color:#64748b; font-size:0.68rem; font-weight:800; display:flex; align-items:center; justify-content:center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">VS</div>
    </div>"""

    konsensus = label_konsensus(pred_rf, pred_xgb)
    if konsensus == "Baik":
        k_bg = "#f0fdf4"
        k_border = "#bbf7d0"
        k_accent = "#16a34a"
        k_icon_bg = "#dcfce7"
        k_main_color = "#14532d"
        k_icon = svg_check
        k_verif = "TERVERIFIKASI MEMENUHI STANDAR"
        k_sub = "Kedua model AI (RF & XGBoost) sepakat — Seluruh parameter mutu CPO berada dalam ambang batas aman laboratorium."
    elif konsensus == "Kurang Baik":
        k_bg = "#fef2f2"
        k_border = "#fecdd3"
        k_accent = "#dc2626"
        k_icon_bg = "#fee2e2"
        k_main_color = "#7f1d1d"
        k_icon = svg_cross
        k_verif = "PERBAIKAN MUTU DIPERLUKAN"
        k_sub = "Kedua model AI sepakat — Ditemukan parameter mutu CPO yang melebihi/di bawah toleransi standar mutu PT Lonsum."
    else:
        k_bg = "#fffbeb"
        k_border = "#fde68a"
        k_accent = "#d97706"
        k_icon_bg = "#fef3c7"
        k_main_color = "#78350f"
        k_icon = svg_alert
        k_verif = "EVALUASI MANUAL DIPERLUKAN"
        k_sub = "Prediksi model RF dan XGBoost berbeda (Tidak Konsisten) — Harap lakukan pengujian ulang atau konsultasikan dengan tim lab QCTL."

    return f"""
    <div style="display:grid; grid-template-columns: 1fr auto 1fr; gap:0.85rem; align-items:stretch; margin-bottom:1rem;">
        {card_rf}
        {vs_html}
        {card_xgb}
    </div>
    <div style="background:{k_bg}; border:1px solid {k_border}; border-left:5px solid {k_accent};
                border-radius:12px; padding:1.1rem 1.4rem; display:flex; align-items:center;
                justify-content:space-between; box-shadow:0 2px 10px rgba(0,0,0,0.03);">
        <div style="display:flex; align-items:center; gap:1rem;">
            <div style="width:44px; height:44px; border-radius:10px; background:{k_icon_bg};
                        display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                {k_icon}
            </div>
            <div>
                <div style="font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#64748b; margin-bottom:0.15rem;">
                    KONSENSUS DUAL MODEL QCTL
                </div>
                <div style="font-size:1.25rem; font-weight:800; color:{k_main_color}; line-height:1.2;">
                    KONSENSUS: {konsensus.upper()}
                </div>
                <div style="font-size:0.8rem; color:#475569; margin-top:0.2rem; line-height:1.4;">
                    {k_sub}
                </div>
            </div>
        </div>
        <div style="text-align:right; border-left:1px solid {k_border}; padding-left:1.2rem; flex-shrink:0;">
            <div style="font-size:0.68rem; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Status Konsensus</div>
            <div style="font-size:0.78rem; font-weight:800; color:{k_main_color}; margin-top:2px;">{k_verif}</div>
        </div>
    </div>"""


def render_parameter_status_cards(params: dict) -> str:
    """Render 7 kartu status parameter mutu CPO dalam bentuk grid enterprise yang rapi."""
    cards_html = []
    
    for f in FITUR:
        op, thresh = THRESHOLD[f]
        val = params.get(f, 0.0)
        satuan = _SATUAN[f]
        nama_fitur = FITUR_LABEL[f].split('(')[0].strip()
        
        lulus = (val <= thresh) if op == '≤' else (val >= thresh)
        
        cfg = INPUT_CONFIG.get(f, {})
        fmt = cfg.get('format', '%.2f')
        val_formatted = fmt % val
        
        if op == '≤':
            pct = min(max((val / (thresh * 1.4)) * 100, 5), 100)
        else:
            pct = min(max((val / (thresh * 1.2)) * 100, 5), 100)
            
        if lulus:
            card_border = "#bbf7d0"
            card_bg     = "#ffffff"
            pill_bg     = "#f0fdf4"
            status_color = "#15803d"
            bar_color   = "#16a34a"
            status_txt  = "✓ OK (Memenuhi)"
        else:
            card_border = "#fecdd3"
            card_bg     = "#ffffff"
            pill_bg     = "#fef2f2"
            status_color = "#991b1b"
            bar_color   = "#dc2626"
            status_txt  = "✕ Tidak Memenuhi"
            
        cards_html.append(f"""
        <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:12px;
                    padding:0.9rem 1rem; box-shadow:0 2px 6px rgba(0,0,0,0.02);
                    display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.25rem;">
                    <span style="font-size:0.75rem; font-weight:800; color:#1e293b; letter-spacing:0.04em;">{f.upper()}</span>
                    <span style="font-size:0.65rem; font-weight:600; color:#64748b; background:#f1f5f9; padding:1px 5px; border-radius:4px;">
                        {op} {thresh} {satuan}
                    </span>
                </div>
                <div style="font-size:0.72rem; color:#64748b; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="{nama_fitur}">
                    {nama_fitur}
                </div>
            </div>
            
            <div style="margin:0.6rem 0 0.4rem 0;">
                <div style="font-size:1.35rem; font-weight:800; color:#0f172a; line-height:1.1;">
                    {val_formatted} <span style="font-size:0.75rem; font-weight:500; color:#64748b;">{satuan}</span>
                </div>
                <div style="background:#f1f5f9; border-radius:4px; height:5px; margin-top:0.4rem; overflow:hidden;">
                    <div style="background:{bar_color}; width:{pct:.0f}%; height:100%; border-radius:4px;"></div>
                </div>
            </div>
            
            <div style="background:{pill_bg}; color:{status_color}; font-size:0.7rem; font-weight:700;
                        padding:3px 8px; border-radius:6px; display:inline-flex; align-items:center;
                        justify-content:space-between;">
                <span>{status_txt}</span>
            </div>
        </div>
        """)
        
    grid_html = f"""
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap:0.75rem; margin-top:0.5rem;">
        {"".join(cards_html)}
    </div>"""
    return grid_html

# ── AUTENTIKASI ───────────────────────────────────────────────────────────────
def login_user(username: str, password: str):
    """Cek kredensial terhadap tabel pengguna di Supabase.
    Mengembalikan dict data pengguna jika berhasil, None jika gagal."""
    try:
        sb  = get_supabase()
        res = (sb.table("pengguna")
               .select("*")
               .eq("username", username)
               .eq("password", password)
               .limit(1)
               .execute())
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        st.error(f"Gagal menghubungi database: {e}")
        return None

def ubah_password(username: str, password_lama: str, password_baru: str) -> tuple[bool, str]:
    """Ubah password pengguna. Mengembalikan (berhasil, pesan)."""
    try:
        sb  = get_supabase()
        # Verifikasi password lama
        res = (sb.table("pengguna")
               .select("id")
               .eq("username", username)
               .eq("password", password_lama)
               .limit(1)
               .execute())
        if not res.data:
            return False, "Password lama tidak sesuai."
        user_id = res.data[0]["id"]
        sb.table("pengguna").update({"password": password_baru}).eq("id", user_id).execute()
        return True, "Password berhasil diubah."
    except Exception as e:
        return False, f"Gagal mengubah password: {e}"

def ubah_username(username_lama: str, username_baru: str, password: str) -> tuple[bool, str]:
    """Ubah username pengguna (verifikasi dengan password). Mengembalikan (berhasil, pesan)."""
    try:
        sb = get_supabase()
        # Verifikasi akun saat ini
        res = (sb.table("pengguna")
               .select("id")
               .eq("username", username_lama)
               .eq("password", password)
               .limit(1)
               .execute())
        if not res.data:
            return False, "Password tidak sesuai. Verifikasi gagal."
        # Cek apakah username baru sudah dipakai
        cek = sb.table("pengguna").select("id").eq("username", username_baru).limit(1).execute()
        if cek.data:
            return False, f"Username '{username_baru}' sudah digunakan oleh akun lain."
        user_id = res.data[0]["id"]
        sb.table("pengguna").update({"username": username_baru}).eq("id", user_id).execute()
        return True, "Username berhasil diubah. Silakan login ulang."
    except Exception as e:
        return False, f"Gagal mengubah username: {e}"

def ubah_nama(username: str, password: str, nama_baru: str) -> tuple[bool, str]:
    """Ubah nama lengkap pengguna (verifikasi dengan password). Mengembalikan (berhasil, pesan)."""
    try:
        sb = get_supabase()
        # Verifikasi akun saat ini
        res = (sb.table("pengguna")
               .select("id")
               .eq("username", username)
               .eq("password", password)
               .limit(1)
               .execute())
        if not res.data:
            return False, "Password tidak sesuai. Verifikasi gagal."
        if not nama_baru.strip():
            return False, "Nama lengkap tidak boleh kosong."
        user_id = res.data[0]["id"]
        sb.table("pengguna").update({"nama": nama_baru.strip()}).eq("id", user_id).execute()
        return True, "Nama lengkap berhasil diubah."
    except Exception as e:
        return False, f"Gagal mengubah nama: {e}"

# ── MANAJEMEN PENGGUNA (Admin IT) ─────────────────────────────────────────────
def ambil_semua_pengguna() -> pd.DataFrame:
    """Ambil seluruh data pengguna dari tabel pengguna."""
    try:
        sb  = get_supabase()
        res = sb.table("pengguna").select("*").order("id").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Gagal mengambil data pengguna: {e}")
        return pd.DataFrame()

def tambah_pengguna(username: str, password: str, nama: str, role: str) -> tuple[bool, str]:
    """Tambah pengguna baru. Mengembalikan (berhasil, pesan)."""
    try:
        sb = get_supabase()
        # Cek username sudah ada
        cek = sb.table("pengguna").select("id").eq("username", username).limit(1).execute()
        if cek.data:
            return False, f"Username '{username}' sudah digunakan."
        sb.table("pengguna").insert({
            "username":  username.strip(),
            "password":  password,
            "nama":      nama.strip(),
            "role":      role,
            "is_active": True,
        }).execute()
        return True, f"Pengguna '{username}' berhasil ditambahkan."
    except Exception as e:
        return False, f"Gagal menambah pengguna: {e}"

def edit_pengguna(user_id: int, data: dict) -> tuple[bool, str]:
    """Update data pengguna berdasarkan id. Mengembalikan (berhasil, pesan)."""
    try:
        sb = get_supabase()
        sb.table("pengguna").update(data).eq("id", user_id).execute()
        return True, "Data pengguna berhasil diperbarui."
    except Exception as e:
        return False, f"Gagal memperbarui pengguna: {e}"

def hapus_pengguna(user_id: int) -> tuple[bool, str]:
    """Hapus pengguna berdasarkan id. Mengembalikan (berhasil, pesan)."""
    try:
        sb = get_supabase()
        sb.table("pengguna").delete().eq("id", user_id).execute()
        return True, "Pengguna berhasil dihapus."
    except Exception as e:
        return False, f"Gagal menghapus pengguna: {e}"


# ── SHAP VISUALIZATION HELPERS ────────────────────────────────────────────────
_NAMA_PANJANG = {
    'ffa':      'Asam Lemak Bebas (ALB)',
    'moisture': 'Kadar Air (Moisture)',
    'dirt':     'Kadar Kotoran (Dirt)',
    'dobi':     'DOBI',
    'pv':       'Bilangan Peroksida (PV)',
    'iv':       'Bilangan Iodium (IV)',
    'carotene': 'β-Karoten (Carotene)',
}
_SATUAN = {
    'ffa':      '%',
    'moisture': '%',
    'dirt':     '%',
    'dobi':     'indeks',
    'pv':       'meq/kg',
    'iv':       'g I₂/100g',
    'carotene': 'ppm',
}


def _get_tingkat(abs_val: float) -> str:
    if abs_val > 1.5:  return "Sangat Tinggi"
    if abs_val > 0.8:  return "Tinggi"
    if abs_val > 0.3:  return "Sedang"
    return "Rendah"


def _extract_shap_row(sv, row_idx=0, target_class=1) -> np.ndarray:
    """Safely extract 1D float array of SHAP values for a single row and target class (class 1=Baik)."""
    if hasattr(sv, "values"):
        sv = sv.values
        
    if isinstance(sv, list):
        c_idx = target_class if target_class < len(sv) else 0
        class_sv = sv[c_idx]
        if hasattr(class_sv, "values"):
            class_sv = class_sv.values
        arr = np.asarray(class_sv, dtype=float)
        if arr.ndim == 2:
            return arr[row_idx]
        elif arr.ndim == 1:
            return arr

    arr = np.asarray(sv, dtype=float)
    if arr.ndim == 3:
        c_idx = target_class if target_class < arr.shape[2] else (arr.shape[2] - 1)
        return arr[row_idx, :, c_idx]
    elif arr.ndim == 2:
        return arr[row_idx]
    elif arr.ndim == 1:
        return arr
        
    return arr.flatten()


def tampilkan_interpretasi_shap(explainer, X_row: pd.DataFrame, prediction: int):
    """Tampilkan interpretasi SHAP secara visual dan naratif (individual row)."""
    try:
        sv = explainer.shap_values(X_row)
        values = _extract_shap_row(sv, row_idx=0, target_class=1)
    except Exception as e:
        st.warning(f"Interpretasi tidak tersedia: {e}")
        return

    # ── Susun DataFrame ───────────────────────────────────────────────────────
    rows = []
    for i, f in enumerate(FITUR):
        val   = float(values[i])
        abs_v = float(abs(val))
        efek  = "Positif" if val > 0 else ("Negatif" if val < 0 else "Netral")
        rows.append({
            "fitur":    f,
            "label":    f.upper() if f != 'carotene' else "CAROTENE",
            "nama":     _NAMA_PANJANG[f],
            "satuan":   _SATUAN[f],
            "shap_val": val,
            "abs_val":  abs_v,
            "efek":     efek,
            "tingkat":  _get_tingkat(abs_v),
        })
    df = pd.DataFrame(rows).sort_values("abs_val", ascending=False).reset_index(drop=True)

    # ── 1. RINGKASAN NARASI ────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.5rem;
                margin-top:2.5rem; margin-bottom:1rem;">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22"
             viewBox="0 0 24 24" fill="none" stroke="#16a34a"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span style="font-size:1.1rem; font-weight:600; color:#14532d;">
            Ringkasan Hasil Analisis
        </span>
    </div>
    """, unsafe_allow_html=True)

    negatif_df = df[df['efek'] == 'Negatif']
    positif_df = df[df['efek'] == 'Positif']

    if prediction == 0:  # Kurang Baik
        bg, border, icon_judul = "#fef2f2", "#fca5a5", ""
        judul  = "CPO ini dinilai <b>KURANG BAIK</b>"
        pesan  = (f"Sistem menemukan <b>{len(negatif_df)} parameter</b> yang "
                  f"menarik mutu ke arah <b>Kurang Baik</b>:")
        daftar = negatif_df
        warna_daftar = "#991b1b"
        ikon_item    = ""
        rekomendasi_fitur = ", ".join(
            [r['nama'] for _, r in daftar.head(2).iterrows()]
        ) if not daftar.empty else "—"
        rekomendasi = (f"<b>Rekomendasi:</b> Fokuskan perbaikan pada pengendalian "
                       f"<b>{rekomendasi_fitur}</b> pada proses produksi.")
    else:                # Baik
        bg, border, icon_judul = "#f0fdf4", "#86efac", ""
        judul  = "CPO ini dinilai <b>BAIK</b>"
        pesan  = (f"<b>{len(positif_df)} parameter</b> secara aktif mendorong mutu "
                  f"ke arah <b>Baik</b>:")
        daftar = positif_df
        warna_daftar = "#15803d"
        ikon_item    = ""
        rekomendasi  = "<b>Pertahankan</b> kondisi proses produksi yang sudah baik ini."

    items_html = "".join(
        f"<li><b>{r['nama']}</b> — pengaruh <b>{r['tingkat'].lower()}</b></li>"
        for _, r in daftar.head(3).iterrows()
    ) if not daftar.empty else "<li>Tidak ada parameter dominan terdeteksi.</li>"

    if not positif_df.empty and prediction == 0:
        catatan = (
            f"<div style='margin-top:0.6rem; font-size:0.82rem; color:#4b7a5e;'>"
            f"Parameter lain ({', '.join(positif_df['nama'].tolist())}) "
            f"sudah baik dan mendorong ke arah positif, namun kontribusinya "
            f"belum cukup mengimbangi parameter bermasalah di atas.</div>"
        )
    else:
        catatan = ""

    st.markdown(f"""
    <div style="background:{bg}; border:1px solid {border}; border-radius:12px;
                padding:1.2rem 1.4rem; margin-bottom:1.2rem;">
        <div style="font-size:1rem; font-weight:700; color:#1a2e23;
                    margin-bottom:0.4rem;">{icon_judul} {judul}</div>
        <div style="font-size:0.88rem; color:#1a2e23; margin-bottom:0.4rem;">
            {pesan}
        </div>
        <ul style="font-size:0.86rem; color:{warna_daftar}; margin:0.3rem 0 0.3rem 1rem;
                   padding:0; line-height:1.8;">
            {items_html}
        </ul>
        {catatan}
        <div style="font-size:0.82rem; color:#374151; margin-top:0.8rem;
                    border-top:1px solid {border}; padding-top:0.6rem;">
            {rekomendasi}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. BAR CHART ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.5rem;
                margin-top:1.8rem; margin-bottom:0.8rem;">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22"
             viewBox="0 0 24 24" fill="none" stroke="#16a34a"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 3v18h18"/><rect x="7" y="10" width="4" height="7"/>
            <rect x="15" y="5" width="4" height="12"/>
        </svg>
        <span style="font-size:1.1rem; font-weight:600; color:#14532d;">
            Pengaruh Setiap Parameter terhadap Prediksi
        </span>
    </div>
    <div style="font-size:0.82rem; color:#4b7a5e; margin-bottom:1rem;">
        Semakin panjang batangnya, semakin besar pengaruh parameter tersebut.
        Merah = mendorong ke Kurang Baik &nbsp;|&nbsp; Hijau = mendorong ke Baik
    </div>
    """, unsafe_allow_html=True)

    df_plot    = df.sort_values("abs_val", ascending=True)
    bar_colors = ["#ef4444" if e == "Negatif" else "#22c55e" for e in df_plot["efek"]]
    tick_labels = df_plot["nama"].tolist()

    if _PLOTLY:
        hover_texts = [
            f"<b>{r['nama']}</b><br>"
            f"Nilai SHAP: {r['shap_val']:+.4f}<br>"
            f"Efek: {r['efek']}<br>"
            f"Tingkat: {r['tingkat']}"
            for _, r in df_plot.iterrows()
        ]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x            = df_plot["abs_val"],
            y            = tick_labels,
            orientation  = "h",
            marker_color = bar_colors,
            text         = df_plot["tingkat"],
            textposition = "outside",
            textfont     = dict(size=11, color="#374151"),
            hovertemplate= "%{customdata}<extra></extra>",
            customdata   = hover_texts,
        ))
        fig.update_layout(
            xaxis=dict(
                title="Tingkat Pengaruh (|SHAP value|)",
                showgrid=True, gridcolor="#e8f0eb",
                zeroline=True, zerolinecolor="#d4e8db",
                title_font=dict(size=11, color="#4b7a5e"),
            ),
            yaxis=dict(
                tickfont=dict(size=12, color="#14532d"),
                automargin=True,
            ),
            height        = 320,
            margin        = dict(l=10, r=80, t=10, b=30),
            plot_bgcolor  = "#ffffff",
            paper_bgcolor = "#ffffff",
            showlegend    = False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(tick_labels, df_plot["abs_val"], color=bar_colors)
        ax.set_xlabel("Tingkat Pengaruh (|SHAP value|)")
        ax.set_facecolor("#ffffff")
        fig.patch.set_facecolor("#ffffff")
        st.pyplot(fig)
        plt.close(fig)

    # ── 3. KARTU PARAMETER ─────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:1rem; font-weight:600; color:#14532d;
                margin-top:1.8rem; margin-bottom:0.8rem;">
        Detail Per Parameter
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4, gap="small")
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % 4]:
            if row['efek'] == 'Positif':
                card_border = "#22c55e"
                card_bg     = "#f0fdf4"
                efek_color  = "#15803d"
                efek_icon   = ""
                efek_teks   = "Mendorong ke BAIK"
            elif row['efek'] == 'Negatif':
                card_border = "#ef4444"
                card_bg     = "#fef2f2"
                efek_color  = "#991b1b"
                efek_icon   = ""
                efek_teks   = "Menarik ke KURANG BAIK"
            else:
                card_border = "#d1d5db"
                card_bg     = "#f9fafb"
                efek_color  = "#6b7280"
                efek_icon   = ""
                efek_teks   = "Netral"

            pct = int((row['abs_val'] / (df['abs_val'].max() + 1e-9)) * 100)
            bar_html = (
                f'<div style="background:#e5e7eb; border-radius:4px; '
                f'height:6px; margin:0.5rem 0;">'
                f'<div style="background:{card_border}; width:{pct}%; '
                f'height:6px; border-radius:4px;"></div></div>'
            )

            st.markdown(f"""
            <div style="background:{card_bg}; border:2px solid {card_border};
                        border-radius:10px; padding:0.75rem 0.8rem;
                        margin-bottom:0.6rem; min-height:130px;">
                <div style="font-size:0.72rem; font-weight:700; color:#4b7a5e;
                            text-transform:uppercase; letter-spacing:0.05em;">
                    #{i+1} &nbsp;{row['tingkat']}
                </div>
                <div style="font-size:0.88rem; font-weight:700; color:#14532d;
                            margin-top:0.25rem; line-height:1.3;">
                    {row['nama']}
                </div>
                {bar_html}
                <div style="font-size:0.78rem; font-weight:600; color:{efek_color};
                            margin-top:0.2rem;">
                    {efek_teks}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── 4. TABEL DETAIL (collapsible) ──────────────────────────────────────────
    with st.expander("Lihat Tabel Detail SHAP"):
        df_tabel = df[['nama', 'satuan', 'shap_val', 'efek', 'tingkat']].copy()
        df_tabel.columns = ['Parameter', 'Satuan', 'Nilai SHAP', 'Efek', 'Tingkat Pengaruh']
        df_tabel['Nilai SHAP'] = df_tabel['Nilai SHAP'].map(lambda v: f"{v:+.4f}")
        st.dataframe(df_tabel, use_container_width=True, hide_index=True)


def tampilkan_shap_global(explainer, X: pd.DataFrame):
    """Tampilkan interpretasi SHAP global (rata-rata seluruh batch) secara visual."""
    try:
        sv = explainer.shap_values(X)
        if hasattr(sv, "values"):
            sv = sv.values
        if isinstance(sv, list):
            sv_matrix = np.asarray(sv[1] if len(sv) > 1 else sv[0], dtype=float)
        else:
            sv_arr = np.asarray(sv, dtype=float)
            if sv_arr.ndim == 3:
                sv_matrix = sv_arr[:, :, 1 if sv_arr.shape[2] > 1 else 0]
            else:
                sv_matrix = sv_arr
        mean_abs = np.abs(sv_matrix).mean(axis=0)
    except Exception as e:
        st.warning(f"Interpretasi global tidak tersedia: {e}")
        return

    # ── Susun DataFrame ───────────────────────────────────────────────────────
    rows = []
    for i, f in enumerate(FITUR):
        abs_v = float(mean_abs[i])
        rows.append({
            "fitur":   f,
            "nama":    _NAMA_PANJANG[f],
            "satuan":  _SATUAN[f],
            "mean_abs": abs_v,
            "tingkat": _get_tingkat(abs_v),
        })
    df = pd.DataFrame(rows).sort_values("mean_abs", ascending=False).reset_index(drop=True)

    # ── Ringkasan narasi global ────────────────────────────────────────────────
    top1 = df.iloc[0]
    top2 = df.iloc[1] if len(df) > 1 else None

    top_nama = top1['nama']
    if top2 is not None:
        top_nama += f" dan {top2['nama']}"

    st.markdown(f"""
    <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:12px;
                padding:1.2rem 1.4rem; margin-bottom:1.2rem;">
        <div style="font-size:1rem; font-weight:700; color:#14532d;
                    margin-bottom:0.5rem;">Ringkasan Analisis Batch</div>
        <div style="font-size:0.88rem; color:#1a2e23; line-height:1.7;">
            Berdasarkan analisis terhadap <b>{len(X)} sampel</b> dalam batch ini,
            parameter yang secara rata-rata paling berpengaruh dalam membedakan
            CPO Baik dan Kurang Baik adalah:
        </div>
        <div style="font-size:0.9rem; font-weight:700; color:#15803d;
                    margin-top:0.5rem;">{top_nama}</div>
        <div style="font-size:0.82rem; color:#4b7a5e; margin-top:0.4rem;">
            <b>Catatan:</b> Nilai di bawah ini adalah rata-rata pengaruh absolut (Mean |SHAP|)
            — semakin besar nilainya, semakin konsisten parameter tersebut berperan
            dalam memisahkan kelas Baik dan Kurang Baik.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bar chart global ──────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.5rem;
                margin-top:1.5rem; margin-bottom:0.8rem;">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22"
             viewBox="0 0 24 24" fill="none" stroke="#16a34a"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 3v18h18"/><rect x="7" y="10" width="4" height="7"/>
            <rect x="15" y="5" width="4" height="12"/>
        </svg>
        <span style="font-size:1.1rem; font-weight:600; color:#14532d;">
            Tingkat Pengaruh Rata-rata per Parameter
        </span>
    </div>
    <div style="font-size:0.82rem; color:#4b7a5e; margin-bottom:1rem;">
        Semakin panjang batangnya, semakin besar pengaruh rata-rata parameter tersebut.
        Oranye = pengaruh terbesar &nbsp;|&nbsp; Hijau = pengaruh lebih kecil
    </div>
    """, unsafe_allow_html=True)

    df_plot = df.sort_values("mean_abs", ascending=True)
    max_val = df_plot["mean_abs"].max() + 1e-9
    bar_colors = [
        "#f97316" if (v / max_val) > 0.6 else
        "#facc15" if (v / max_val) > 0.3 else
        "#22c55e"
        for v in df_plot["mean_abs"]
    ]

    if _PLOTLY:
        hover_texts = [
            f"<b>{r['nama']}</b><br>"
            f"Mean |SHAP|: {r['mean_abs']:.4f}<br>"
            f"Tingkat: {r['tingkat']}"
            for _, r in df_plot.iterrows()
        ]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x            = df_plot["mean_abs"],
            y            = df_plot["nama"].tolist(),
            orientation  = "h",
            marker_color = bar_colors,
            text         = df_plot["tingkat"],
            textposition = "outside",
            textfont     = dict(size=11, color="#374151"),
            hovertemplate= "%{customdata}<extra></extra>",
            customdata   = hover_texts,
        ))
        fig.update_layout(
            xaxis=dict(
                title="Mean |SHAP value| (rata-rata pengaruh absolut)",
                showgrid=True, gridcolor="#e8f0eb",
                zeroline=True, zerolinecolor="#d4e8db",
                title_font=dict(size=11, color="#4b7a5e"),
            ),
            yaxis=dict(
                tickfont=dict(size=12, color="#14532d"),
                automargin=True,
            ),
            height        = 320,
            margin        = dict(l=10, r=80, t=10, b=30),
            plot_bgcolor  = "#ffffff",
            paper_bgcolor = "#ffffff",
            showlegend    = False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(df_plot["nama"].tolist(), df_plot["mean_abs"], color=bar_colors)
        ax.set_xlabel("Mean |SHAP value|")
        ax.set_facecolor("#ffffff")
        fig.patch.set_facecolor("#ffffff")
        st.pyplot(fig)
        plt.close(fig)

    # ── Kartu ranking parameter global ────────────────────────────────────────
    st.markdown("""
    <div style="font-size:1rem; font-weight:600; color:#14532d;
                margin-top:1.8rem; margin-bottom:0.8rem;">
        Ranking Parameter berdasarkan Pengaruh Rata-rata
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4, gap="small")
    rank_colors = ["#f97316", "#f97316", "#facc15", "#facc15",
                   "#22c55e", "#22c55e", "#22c55e"]
    rank_bg     = ["#fff7ed", "#fff7ed", "#fefce8", "#fefce8",
                   "#f0fdf4", "#f0fdf4", "#f0fdf4"]
    rank_icons  = ["1", "2", "3", "4", "5", "6", "7"]

    for i, (_, row) in enumerate(df.iterrows()):
        color  = rank_colors[i] if i < len(rank_colors) else "#22c55e"
        bg     = rank_bg[i]     if i < len(rank_bg)     else "#f0fdf4"
        icon   = f"Peringkat {rank_icons[i]}" if i < len(rank_icons) else "▫️"

        pct = int((row['mean_abs'] / (df['mean_abs'].max() + 1e-9)) * 100)
        bar_html = (
            f'<div style="background:#e5e7eb; border-radius:4px; '
            f'height:6px; margin:0.5rem 0;">'
            f'<div style="background:{color}; width:{pct}%; '
            f'height:6px; border-radius:4px;"></div></div>'
        )

        with cols[i % 4]:
            st.markdown(f"""
            <div style="background:{bg}; border:2px solid {color};
                        border-radius:10px; padding:0.75rem 0.8rem;
                        margin-bottom:0.6rem; min-height:120px;">
                <div style="font-size:0.8rem; font-weight:600; color:{color}; margin-bottom:0.2rem;">{icon}</div>
                <div style="font-size:0.86rem; font-weight:700; color:#14532d;
                            line-height:1.3;">{row['nama']}</div>
                {bar_html}
                <div style="font-size:0.75rem; color:#6b7280;">{row['satuan']}</div>
                <div style="font-size:0.78rem; font-weight:600; color:{color};
                            margin-top:0.2rem;">{row['tingkat']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tabel detail global (collapsible) ─────────────────────────────────────
    with st.expander("Lihat Tabel Detail Pengaruh Global"):
        df_tabel = df[['nama', 'satuan', 'mean_abs', 'tingkat']].copy()
        df_tabel.columns = ['Parameter', 'Satuan', 'Mean |SHAP|', 'Tingkat Pengaruh']
        df_tabel['Mean |SHAP|'] = df_tabel['Mean |SHAP|'].map(lambda v: f"{v:.4f}")
        st.dataframe(df_tabel, use_container_width=True, hide_index=True)
