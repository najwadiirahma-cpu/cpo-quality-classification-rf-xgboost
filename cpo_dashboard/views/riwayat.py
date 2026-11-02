import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta

from utils import ambil_riwayat, hapus_semua_riwayat, hapus_riwayat_berdasarkan_ids, show_toast


# ── Ikon SVG inline ───────────────────────────────────────────────────────────
ICON_MANUAL = """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"
  viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px">
  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
</svg>"""

ICON_BATCH = """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"
  viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
  <polyline points="14 2 14 8 20 8"/>
  <line x1="16" y1="13" x2="8" y2="13"/>
  <line x1="16" y1="17" x2="8" y2="17"/>
  <polyline points="10 9 9 9 8 9"/>
</svg>"""

ICON_CLOCK = """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13"
  viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-1px">
  <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
</svg>"""

ICON_DOWNLOAD = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"
  viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
  <polyline points="7 10 12 15 17 10"/>
  <line x1="12" y1="15" x2="12" y2="3"/>
</svg>"""

ICON_CHEVRON_DOWN = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"
  viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px">
  <polyline points="6 9 12 15 18 9"/>
</svg>"""

ICON_CHEVRON_UP = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"
  viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px">
  <polyline points="18 15 12 9 6 15"/>
</svg>"""


# ── Pengelompokan sesi ────────────────────────────────────────────────────────
def _kelompokkan_sesi(df: pd.DataFrame, gap_detik: int = 60) -> list[dict]:
    """
    Kelompokkan baris menjadi sesi berdasarkan kedekatan timestamp.
    Baris yang selisih timestampnya <= gap_detik dari baris sebelumnya
    dianggap satu sesi (mengatasi kasus batch multi-sheet yang insertnya
    berlangsung beberapa detik karena iterasi baris).

    - 1 baris dalam satu sesi  → Manual
    - >1 baris dalam satu sesi → Batch
    """
    if df.empty:
        return []

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    sesi_list = []
    sesi_rows = [df.iloc[0]]
    ts_prev = df.iloc[0]["timestamp"]

    for i in range(1, len(df)):
        ts_cur = df.iloc[i]["timestamp"]
        if (ts_cur - ts_prev).total_seconds() <= gap_detik:
            sesi_rows.append(df.iloc[i])
        else:
            grp = pd.DataFrame(sesi_rows).reset_index(drop=True)
            sesi_list.append({
                "timestamp": grp["timestamp"].min(),
                "tipe":      "Manual" if len(grp) == 1 else "Batch",
                "jumlah":    len(grp),
                "df_detail": grp,
            })
            sesi_rows = [df.iloc[i]]
        ts_prev = ts_cur

    # Flush sesi terakhir
    grp = pd.DataFrame(sesi_rows).reset_index(drop=True)
    sesi_list.append({
        "timestamp": grp["timestamp"].min(),
        "tipe":      "Manual" if len(grp) == 1 else "Batch",
        "jumlah":    len(grp),
        "df_detail": grp,
    })

    sesi_list.sort(key=lambda x: x["timestamp"], reverse=True)
    return sesi_list


# ── Badge tipe sesi ───────────────────────────────────────────────────────────
def _badge(tipe: str) -> str:
    if tipe == "Manual":
        return (
            f'<span style="display:inline-flex;align-items:center;gap:4px;'
            f'background:#dbeafe;color:#1d4ed8;border-radius:999px;'
            f'padding:2px 10px;font-size:0.72rem;font-weight:600;">'
            f'{ICON_MANUAL} Manual</span>'
        )
    return (
        f'<span style="display:inline-flex;align-items:center;gap:4px;'
        f'background:#fef9c3;color:#854d0e;border-radius:999px;'
        f'padding:2px 10px;font-size:0.72rem;font-weight:600;">'
        f'{ICON_BATCH} Batch</span>'
    )


# ── Render kartu sesi ─────────────────────────────────────────────────────────
def _render_kartu(sesi: dict, idx: int):
    ts: datetime = sesi["timestamp"]
    tipe = sesi["tipe"]
    n = sesi["jumlah"]
    df_det = sesi["df_detail"].copy()

    # Bersihkan emoji hasil
    for col in ["hasil_prediksi"]:
        if col in df_det.columns:
            df_det[col] = (
                df_det[col].astype(str)
                .str.replace("✅ ", "", regex=False)
                .str.replace("❌ ", "", regex=False)
            )

    baik_prediksi = (df_det["hasil_prediksi"] == "Baik").sum() if "hasil_prediksi" in df_det.columns else 0

    tgl_str = ts.strftime("%d %B %Y, %H:%M:%S")

    if tipe == "Manual":
        label_exp = f"Manual  —  {tgl_str}"
    else:
        label_exp = f"Batch  —  {tgl_str}  ·  {n} sampel"

    with st.expander(label_exp, expanded=False):
        # Info baris
        col_a, col_b, col_c = st.columns([3, 1, 1])
        with col_a:
            jumlah_txt = (
                f'&ensp;<span style="font-size:0.78rem;color:#6b7280;">{n} baris</span>'
                if tipe == "Batch" else ""
            )
            st.markdown(
                f'{_badge(tipe)}{jumlah_txt}',
                unsafe_allow_html=True,
            )
        col_b.metric("Total Baik", f"{baik_prediksi}/{n}")

        # Tabel detail
        rename_cols = {
            "id":        "ID",
            "timestamp": "Waktu",
            "ffa":       "ALB (%)",
            "moisture":  "Moisture (%)",
            "dirt":      "Dirt (%)",
            "dobi":      "DOBI",
            "pv":        "PV (meq/kg)",
            "iv":        "IV (g I₂/100g)",
            "carotene":  "β-Karoten (ppm)",
            "hasil_prediksi": "Hasil Klasifikasi",
        }
        cols_ada = [c for c in rename_cols if c in df_det.columns]
        df_tampil = df_det[cols_ada].rename(columns=rename_cols)

        def color_hasil(val):
            if val == "Baik":
                return "background-color:#dcfce7;color:#16a34a"
            elif val == "Kurang Baik":
                return "background-color:#fee2e2;color:#dc2626"
            return ""

        subset = [c for c in ["Hasil Klasifikasi"] if c in df_tampil.columns]
        df_styled = df_tampil.style.map(color_hasil, subset=subset)
        tinggi = min(200 + n * 38, 500)
        st.dataframe(df_styled, use_container_width=True, height=tinggi)

        # Aksi per sesi
        import io
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_det.to_excel(writer, index=False)
        excel_sesi = excel_buffer.getvalue()
        
        nama_file = (
            f"manual_{ts.strftime('%Y%m%d_%H%M%S')}.xlsx"
            if tipe == "Manual"
            else f"batch_{ts.strftime('%Y%m%d_%H%M%S')}_{n}sampel.xlsx"
        )
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            st.download_button(
                "Unduh Sesi (.xlsx)",
                excel_sesi,
                file_name=nama_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_sesi_{idx}",
                use_container_width=True,
            )

        with col_btn2:
            popover = st.popover("Hapus Sesi", use_container_width=True)
            popover.warning("Apakah Anda yakin ingin menghapus sesi ini?")
            confirm_hapus = popover.button("Ya, Hapus Sesi", key=f"del_confirm_{idx}", use_container_width=True)
            if confirm_hapus:
                ids_to_delete = df_det["id"].tolist()
                success, msg = hapus_riwayat_berdasarkan_ids(ids_to_delete)
                if success:
                    show_toast(msg, kind="success")
                    st.rerun()
                else:
                    show_toast(msg, kind="error")



# ── Halaman utama ─────────────────────────────────────────────────────────────
def show():
    st.markdown('<div class="page-title">Riwayat Klasifikasi</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-sub">Rekap seluruh sesi pendataan — manual maupun batch — yang telah tersimpan.</div>',
        unsafe_allow_html=True,
    )

    # Filter tanggal
    st.markdown("##### Filter Tanggal")
    fc1, fc2, fc3 = st.columns([2, 2, 1])
    tgl_awal  = fc1.date_input("Dari",   value=date(2024, 1, 1))
    tgl_akhir = fc2.date_input("Sampai", value=date.today())
    with fc3:
        st.markdown("<br>", unsafe_allow_html=True)
        terapkan = st.button("Terapkan", use_container_width=True)

    df = ambil_riwayat(tgl_awal, tgl_akhir) if terapkan else ambil_riwayat()

    if df.empty:
        st.info("Belum ada riwayat prediksi yang tersimpan.")
        return

    # Ringkasan global
    df_s = df.copy()
    for col in ["hasil_prediksi"]:
        if col in df_s.columns:
            df_s[col] = (
                df_s[col].astype(str)
                .str.replace("✅ ", "", regex=False)
                .str.replace("❌ ", "", regex=False)
            )

    total         = len(df_s)
    baik_prediksi = (df_s["hasil_prediksi"] == "Baik").sum()

    m1, m2 = st.columns(2)
    m1.metric("Total Prediksi", total)
    m2.metric("Total Mutu Baik", f"{baik_prediksi} ({baik_prediksi/total*100:.1f}%)" if total > 0 else "0 (0%)")

    st.markdown("---")

    # Kelompokkan sesi
    sesi_list  = _kelompokkan_sesi(df)
    total_sesi = len(sesi_list)

    PREVIEW = 5
    if "riwayat_tampil_semua" not in st.session_state:
        st.session_state["riwayat_tampil_semua"] = False

    tampil_semua     = st.session_state["riwayat_tampil_semua"]
    sesi_ditampilkan = sesi_list if tampil_semua else sesi_list[:PREVIEW]

    # Header daftar
    st.markdown(
        f'<div style="font-size:1rem;font-weight:600;color:#14532d;margin-bottom:0.75rem;">'
        f'Daftar Sesi Pendataan '
        f'<span style="font-size:0.85rem;font-weight:400;color:#6b7280;">'
        f'({total_sesi} sesi total)</span></div>',
        unsafe_allow_html=True,
    )

    for i, sesi in enumerate(sesi_ditampilkan):
        _render_kartu(sesi, i)

    # Tombol lihat lebih / sembunyikan
    if total_sesi > PREVIEW:
        sisa = total_sesi - PREVIEW
        if not tampil_semua:
            if st.button(f"Tampilkan {sisa} sesi lainnya", key="btn_tampil_semua"):
                st.session_state["riwayat_tampil_semua"] = True
                st.rerun()
        else:
            if st.button("Sembunyikan", key="btn_sembunyikan"):
                st.session_state["riwayat_tampil_semua"] = False
                st.rerun()

    # ── Tabel lengkap ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div style="font-size:1rem;font-weight:600;color:#14532d;margin-bottom:0.6rem;">'
        "Tabel Seluruh Data"
        "</div>",
        unsafe_allow_html=True,
    )

    rename_cols = {
        "id":        "ID",
        "timestamp": "Waktu",
        "ffa":       "ALB (%)",
        "moisture":  "Moisture (%)",
        "dirt":      "Dirt (%)",
        "dobi":      "DOBI",
        "pv":        "PV (meq/kg)",
        "iv":        "IV (g I₂/100g)",
        "carotene":  "β-Karoten (ppm)",
        "hasil_prediksi": "Hasil Klasifikasi",
    }
    cols_ada   = [c for c in rename_cols if c in df_s.columns]
    df_tampil  = df_s[cols_ada].rename(columns=rename_cols)

    def color_hasil(val):
        if val == "Baik":
            return "background-color:#dcfce7;color:#16a34a"
        elif val == "Kurang Baik":
            return "background-color:#fee2e2;color:#dc2626"
        return ""

    subset_cols = [c for c in ["Hasil Klasifikasi"] if c in df_tampil.columns]
    df_styled   = df_tampil.style.map(color_hasil, subset=subset_cols)
    st.dataframe(df_styled, use_container_width=True, height=420)

    # Aksi global riwayat
    import io
    excel_buffer_all = io.BytesIO()
    with pd.ExcelWriter(excel_buffer_all, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_out = excel_buffer_all.getvalue()
    
    st.download_button(
        "Unduh Semua Riwayat (.xlsx)",
        excel_out,
        file_name=f"riwayat_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    # Hapus semua riwayat
    st.markdown("")
    with st.popover("Hapus Semua Riwayat", use_container_width=False):
        st.markdown("""
        <div style="padding:0.2rem 0 0.6rem;">
            <div style="font-size:0.88rem; font-weight:600; color:#991b1b; margin-bottom:0.4rem;">
                Konfirmasi Hapus Semua Riwayat
            </div>
            <div style="font-size:0.8rem; color:#7f1d1d; line-height:1.5;">
                Seluruh data riwayat klasifikasi akan dihapus secara permanen.<br>
                Tindakan ini tidak dapat dibatalkan.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ya, Hapus Semua", key="hapus_semua_confirm", use_container_width=True):
            success, msg = hapus_semua_riwayat()
            if success:
                show_toast(msg, kind="success")
                st.rerun()
            else:
                show_toast(msg, kind="error")
