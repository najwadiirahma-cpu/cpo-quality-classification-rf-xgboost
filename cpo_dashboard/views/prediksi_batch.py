import streamlit as st
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime

from utils import (
    FITUR, FITUR_LABEL, load_models, simpan_riwayat,
    label_konsensus, tampilkan_interpretasi_shap, tampilkan_shap_global,
)


# ── Helper: Deteksi & baca format Lonsum ──────────────────────────────────────
def is_format_lonsum(uploaded) -> bool:
    """Kembalikan True jika file Excel mempunyai struktur rekap Lonsum."""
    try:
        uploaded.seek(0)
        xl = pd.ExcelFile(uploaded)
        
        # Kata kunci pencarian Lonsum
        keywords = [
            'analysis parameter', 'parameters', 'parameter analisa', 
            'analisa parameter', 'qctl', 'lonsum', 'rekap'
        ]
        
        col_map_flat = [
            'moisture', 'kadar air', 'water content',
            'dirt', 'kadar kotoran', 'impurities', 'kotoran',
            'ffa', 'free fatty acid', 'asam lemak bebas', 'alb',
            'pv', 'peroxide value', 'bilangan peroksida', 'peroksida',
            'dobi',
            'carotene', 'karoten', 'beta-carotene',
            'iv', 'iodine value', 'bilangan iodium', 'iodium',
        ]
        
        for sheet in xl.sheet_names:
            df_s = xl.parse(sheet, header=None)
            if df_s.empty:
                continue
            
            flat = df_s.values.flatten().tolist()
            flat_str = [str(v).lower() for v in flat if pd.notna(v)]
            
            # Cek kata kunci
            if any(any(kw in s for kw in keywords) for s in flat_str):
                return True
                
            # Atau cek jika ada baris di sheet ini yang mengandung setidaknya 3 sinonim fitur di baris bukan nol
            for ri, row in df_s.iterrows():
                if ri == 0:
                    continue
                row_str = ' '.join(str(v).lower().strip() for v in row if pd.notna(v))
                matches = sum(1 for syn in col_map_flat if syn in row_str)
                if matches >= 3:
                    return True
    except Exception:
        pass
    return False


def baca_format_lonsum(uploaded) -> pd.DataFrame:
    """Baca semua sheet format rekap Lonsum dan kembalikan DataFrame bersatu."""
    uploaded.seek(0)
    xl = pd.ExcelFile(uploaded)
    all_rows = []

    # Sinonim diperluas — hanya kata bermakna, tidak satu huruf
    col_map = {
        'moisture': [
            'moisture', 'kadar air', 'water content', 'water',
            'moist', 'moisture content', 'mc',
        ],
        'dirt': [
            'dirt', 'kadar kotoran', 'impurities', 'impurity',
            'dirt content', 'kotoran',
        ],
        'ffa': [
            'ffa', 'free fatty acid', 'asam lemak bebas', 'alb',
            'fatty acid', 'free fatty',
        ],
        'pv': [
            'pv', 'peroxide value', 'bilangan peroksida', 'peroxide',
            'peroksida', 'peroxide val',
        ],
        'dobi': [
            'dobi', 'deterioration of bleachability index',
            'bleachability',
        ],
        'carotene': [
            'carotene', 'karoten', 'beta-carotene', 'beta karoten',
            'b-carotene', 'karotena', 'carotenoid',
        ],
        'iv': [
            'iv', 'iodine value', 'bilangan iodium', 'iodine',
            'iodine number', 'iodium',
        ],
    }

    debug_info = []

    for sheet in xl.sheet_names:
        df_s = xl.parse(sheet, header=None)
        if df_s.empty:
            debug_info.append({'sheet': sheet, 'status': 'skip (kosong)'})
            continue

        # ── 1. COBA DETEKSI FORMAT TRANSPOSE (LONSUM QCTL) ───────────────────
        analysis_pos = None
        for r in range(df_s.shape[0]):
            for c in range(df_s.shape[1]):
                val = str(df_s.iloc[r, c]).lower().strip()
                if 'analysis parameter' in val or 'parameter analisa' in val:
                    analysis_pos = (r, c)
                    break
            if analysis_pos:
                break

        is_transpose = False
        if analysis_pos:
            r_start, c_start = analysis_pos
            param_rows = {}
            # Cari baris parameter di bawah r_start
            for ri in range(r_start + 1, min(r_start + 15, df_s.shape[0])):
                cell_val = str(df_s.iloc[ri, c_start]).lower().strip()
                for std, syns in col_map.items():
                    if any(syn in cell_val for syn in syns):
                        param_rows[std] = ri
                        break
            # Jika ditemukan minimal 4 parameter secara vertikal, ini format transpose
            if len(param_rows) >= 4:
                is_transpose = True

        if is_transpose:
            r_start, c_start = analysis_pos
            # Cari baris nama PKS (biasanya r_start atau r_start+1)
            pks_row = r_start
            if c_start + 1 < df_s.shape[1]:
                val_next = str(df_s.iloc[r_start, c_start + 1]).strip().lower()
                if val_next == "" or "nan" in val_next or "parameter" in val_next:
                    if pd.notna(df_s.iloc[r_start + 1, c_start + 1]):
                        pks_row = r_start + 1

            sheet_data = []
            
            # Cari periode bulan/tahun dari baris-baris atas
            bulan_val, tahun_val = None, None
            months_id = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember']
            months_en = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
            
            for r_check in range(max(0, r_start - 5), r_start):
                for col_check in range(df_s.shape[1]):
                    val_check = str(df_s.iloc[r_check, col_check]).lower()
                    import re
                    years = re.findall(r'\b(20\d{2})\b', val_check)
                    if years:
                        tahun_val = int(years[0])
                    for m_id in months_id:
                        if m_id in val_check:
                            bulan_val = m_id.capitalize()
                            break
                    for m_en in months_en:
                        if m_en in val_check and not bulan_val:
                            bulan_val = months_id[months_en.index(m_en)].capitalize()
                            break

            for c in range(c_start + 1, df_s.shape[1]):
                pks_name = df_s.iloc[pks_row, c]
                if pd.isna(pks_name):
                    alt_row = r_start if pks_row != r_start else r_start + 1
                    if alt_row < df_s.shape[0]:
                        pks_name = df_s.iloc[alt_row, c]
                
                pks_str = str(pks_name).strip() if pd.notna(pks_name) else ""
                
                if pks_str == "" or any(kw in pks_str.lower() for kw in ['limit', 'target', 'comment', 'komentar', 'rata', 'average', 'mean']):
                    continue
                
                row_data = {}
                row_data['PKS'] = pks_str
                if bulan_val:
                    row_data['Bulan'] = bulan_val
                if tahun_val:
                    row_data['Tahun'] = tahun_val
                
                has_values = False
                for std, ri in param_rows.items():
                    val = df_s.iloc[ri, c]
                    if pd.notna(val):
                        if isinstance(val, str):
                            val_clean = val.replace(',', '.').strip()
                            try:
                                val = float(val_clean)
                            except ValueError:
                                pass
                        row_data[std] = val
                        has_values = True
                
                if has_values:
                    row_data['Sheet'] = sheet
                    sheet_data.append(row_data)

            if sheet_data:
                df_sheet = pd.DataFrame(sheet_data)
                found_params = [f for f in FITUR if f in df_sheet.columns]
                if len(found_params) >= 4:
                    all_rows.append(df_sheet)
                    debug_info.append({
                        'sheet': sheet,
                        'status': f'ok (Transpose) — {len(df_sheet)} sampel terdeteksi',
                        'kolom': found_params
                    })
                else:
                    debug_info.append({
                        'sheet': sheet,
                        'status': f'skip (Transpose) — kurang parameter (hanya {len(found_params)})',
                        'kolom': found_params
                    })
            else:
                debug_info.append({
                    'sheet': sheet,
                    'status': 'skip (Transpose) — tidak ada data sampel yang valid'
                })

        # ── 2. FALLBACK: FORMAT TABEL BIASA (HORIZONTAL HEADER) ────────────────
        else:
            header_row = None
            best_count = 0
            best_ri    = None

            for ri, row in df_s.iterrows():
                row_str = ' '.join(str(v).lower().strip() for v in row if pd.notna(v))
                count = sum(
                    1 for syns in col_map.values()
                    if any(syn in row_str for syn in syns)
                )
                if count > best_count:
                    best_count = count
                    best_ri    = ri
                if count >= 4:
                    header_row = ri
                    break

            if header_row is None and best_count >= 2:
                header_row = best_ri

            if header_row is None:
                debug_info.append({
                    'sheet': sheet,
                    'status': f'skip — header tidak ditemukan (best={best_count})',
                })
                continue

            df_data = xl.parse(sheet, header=header_row)
            df_data.columns = [
                str(c).lower().strip().split('(')[0].strip()
                for c in df_data.columns
            ]
            df_data = df_data.loc[:, ~df_data.columns.str.startswith('unnamed')]

            rename = {}
            for std, syns in col_map.items():
                if std in rename.values():
                    continue
                for col in df_data.columns:
                    if col in rename:
                        continue
                    col_clean = col.strip()
                    if any(syn == col_clean or col_clean.startswith(syn) or syn in col_clean
                           for syn in syns):
                        rename[col] = std
                        break

            df_data = df_data.rename(columns=rename)
            found = [f for f in FITUR if f in df_data.columns]

            if len(found) < 4:
                debug_info.append({
                    'sheet':   sheet,
                    'status':  f'skip — hanya {len(found)} kolom terdeteksi: {found}',
                    'kolom':   list(df_data.columns[:20]),
                })
                continue

            df_sub = df_data[found].copy()
            for extra_raw, extra_std in [('pks', 'PKS'), ('bulan', 'Bulan'), ('tahun', 'Tahun')]:
                if extra_raw in df_data.columns and extra_std not in df_sub.columns:
                    df_sub[extra_std] = df_data[extra_raw]
            df_sub['Sheet'] = sheet

            # Hapus baris yang semua kolom fitur-nya NaN
            df_sub = df_sub.dropna(subset=found, how='all')

            # Konversi semua kolom fitur ke numeric, ganti koma desimal jika ada
            for f in found:
                if df_sub[f].dtype == object:
                    df_sub[f] = df_sub[f].astype(str).str.replace(',', '.').str.strip()
                df_sub[f] = pd.to_numeric(df_sub[f], errors='coerce')

            if df_sub.empty:
                debug_info.append({'sheet': sheet, 'status': 'skip — semua baris NaN'})
                continue

            all_rows.append(df_sub)
            debug_info.append({
                'sheet': sheet, 
                'status': f'ok (Biasa) — {len(df_sub)} baris', 
                'kolom': found
            })

    # Simpan debug info ke session_state
    st.session_state['_lonsum_debug'] = debug_info

    if not all_rows:
        raise ValueError(
            "Tidak ada sheet yang cocok dengan format Lonsum. "
            "Buka expander 'Debug Info Sheet' untuk melihat detail."
        )
    return pd.concat(all_rows, ignore_index=True)


# ── Halaman utama ──────────────────────────────────────────────────────────────
def show():
    rf, xgb, exp_rf, exp_xgb, ok = load_models()
    if not ok:
        st.warning("Model belum tersedia.")
        return

    st.markdown('<div class="page-title"> Prediksi Batch</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Upload file Excel kolom biasa, '
                'atau file rekap standar Lonsum.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:1.2rem 1.5rem; margin-bottom:1.5rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            <span style="font-size:0.95rem; font-weight:600; color:#14532d;">Format File yang Didukung</span>
        </div>
        <ul style="font-size:0.85rem; color:#1a2e23; margin:0; padding-left:1.5rem; line-height:1.6;">
            <li><b>Format kolom biasa (Excel)</b> — harus memiliki kolom: <code>moisture</code>, <code>dirt</code>, <code>ffa</code>, <code>pv</code>, <code>dobi</code>, <code>carotene</code>, <code>iv</code></li>
            <li><b>Format rekap Lonsum (Excel multi-sheet)</b> — struktur mengikuti format laporan tahunan QCTL (Analysis Parameters)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:1.05rem; font-weight:600; color:#14532d; margin-bottom:0.5rem; display:flex; align-items:center; gap:0.4rem;">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        Upload Dataset
    </div>
    """, unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload file", type=['xlsx'], label_visibility="collapsed")

    if not uploaded:
        return

    # ── Baca file ─────────────────────────────────────────────────────────────
    try:
        format_lonsum = is_format_lonsum(uploaded)
        uploaded.seek(0)
        if format_lonsum:
            with st.spinner("Membaca format rekap Lonsum..."):
                df = baca_format_lonsum(uploaded)
            st.info(f"Format rekap Lonsum terdeteksi — "
                    f"{len(df)} baris dari semua sheet.", icon=":material/description:")
        else:
            df = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Gagal membaca file: {e}", icon=":material/error:")
        if '_lonsum_debug' in st.session_state:
            with st.expander("Detail Debug Info Sheet (Lonsum)"):
                st.write("Berikut detail pencarian sheet & kolom pada file Excel:")
                for item in st.session_state['_lonsum_debug']:
                    st.markdown(f"**Sheet: `{item['sheet']}`**")
                    st.write(f"Status: {item['status']}")
                    if 'kolom' in item:
                        st.write(f"Kolom yang terdeteksi: {item['kolom']}")
        return

    # ── Validasi kolom ────────────────────────────────────────────────────────
    # Jika ada fitur yang kurang, otomatis isi dengan default config agar tidak error
    missing = [f for f in FITUR if f not in df.columns]
    if missing:
        from utils import INPUT_CONFIG
        for f in missing:
            default_val = INPUT_CONFIG.get(f, {}).get('default', 0.0)
            df[f] = default_val
        st.warning(f"Parameter ini tidak ditemukan dan diisi otomatis dengan nilai default: `{'`, `'.join(missing)}`", icon=":material/warning:")


    st.success(f"File berhasil dibaca: **{len(df)} baris**", icon=":material/check_circle:")

    X = df[FITUR].apply(pd.to_numeric, errors='coerce')
    null_count = X.isnull().sum().sum()
    if null_count > 0:
        st.warning(f"{null_count} nilai kosong → diisi median.", icon=":material/warning:")
        X = X.fillna(X.median())

    # ── Prediksi ──────────────────────────────────────────────────────────────
    df['Hasil_RF']  = rf.predict(X)
    df['Hasil_XGB'] = xgb.predict(X)
    df['Hasil_RF']  = df['Hasil_RF'].map({1: 'Baik', 0: 'Kurang Baik'})
    df['Hasil_XGB'] = df['Hasil_XGB'].map({1: 'Baik', 0: 'Kurang Baik'})
    df['Konsensus'] = df.apply(
        lambda r: label_konsensus(
            1 if r['Hasil_RF'] == 'Baik' else 0,
            1 if r['Hasil_XGB'] == 'Baik' else 0,
        ), axis=1
    )

    # Simpan ke Supabase menggunakan label konsensus
    for _, row in df.iterrows():
        params = {f: row[f] for f in FITUR}
        simpan_riwayat(params, row['Konsensus'])

    # ── Ringkasan metrik ──────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.5rem; margin-top:2rem; margin-bottom:1rem;">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
        <span style="font-size:1.1rem; font-weight:600; color:#14532d;">
            Ringkasan Hasil Prediksi
        </span>
    </div>
    """, unsafe_allow_html=True)
    total        = len(df)
    baik_rf      = (df['Hasil_RF']  == 'Baik').sum()
    baik_xgb     = (df['Hasil_XGB'] == 'Baik').sum()
    baik_kons    = (df['Konsensus'] == 'Baik').sum()
    tdk_kons     = (df['Konsensus'] == 'Tidak Konsisten').sum()
    kurang_rf    = total - baik_rf
    kurang_xgb   = total - baik_xgb

    pct_rf   = baik_rf   / total * 100 if total else 0
    pct_xgb  = baik_xgb  / total * 100 if total else 0
    pct_kons = baik_kons / total * 100 if total else 0

    st.html(f"""
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:0.75rem; margin-bottom:1.5rem;">

        <!-- Total Sampel -->
        <div style="background:#f8fafc; border:1.5px solid #e2e8f0; border-radius:14px;
                    padding:1rem 1.2rem; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                        letter-spacing:0.1em; color:#94a3b8; margin-bottom:0.4rem;">Total Sampel</div>
            <div style="font-size:2rem; font-weight:900; color:#1e293b; line-height:1;">{total}</div>
            <div style="font-size:0.75rem; color:#94a3b8; margin-top:0.3rem;">keseluruhan batch</div>
        </div>

        <!-- RF -->
        <div style="background:linear-gradient(135deg,#eff6ff,#dbeafe); border:2px solid #2563eb;
                    border-radius:14px; padding:1rem 1.2rem;
                    box-shadow:0 2px 8px rgba(37,99,235,0.12);">
            <div style="display:flex; align-items:center; gap:0.4rem; margin-bottom:0.4rem;">
                <span style="background:#2563eb; color:#fff; font-size:0.55rem; font-weight:800;
                            padding:1px 6px; border-radius:20px; text-transform:uppercase;
                            letter-spacing:0.08em;">RF</span>
                <span style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                            letter-spacing:0.08em; color:#2563eb;">Random Forest</span>
            </div>
            <div style="font-size:2rem; font-weight:900; color:#1d4ed8; line-height:1;">{baik_rf}</div>
            <div style="font-size:0.75rem; color:#3b82f6; margin-top:0.3rem;">
                Baik &nbsp;&#xb7;&nbsp; {pct_rf:.1f}%
                &nbsp;|&nbsp; {kurang_rf} kurang baik
            </div>
        </div>

        <!-- XGBoost -->
        <div style="background:linear-gradient(135deg,#f0fdf4,#dcfce7); border:2px solid #16a34a;
                    border-radius:14px; padding:1rem 1.2rem;
                    box-shadow:0 2px 8px rgba(22,163,74,0.12);">
            <div style="display:flex; align-items:center; gap:0.4rem; margin-bottom:0.4rem;">
                <span style="background:#16a34a; color:#fff; font-size:0.55rem; font-weight:800;
                            padding:1px 6px; border-radius:20px; text-transform:uppercase;
                            letter-spacing:0.08em;">XGB</span>
                <span style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                            letter-spacing:0.08em; color:#16a34a;">XGBoost</span>
            </div>
            <div style="font-size:2rem; font-weight:900; color:#15803d; line-height:1;">{baik_xgb}</div>
            <div style="font-size:0.75rem; color:#22c55e; margin-top:0.3rem;">
                Baik &nbsp;&#xb7;&nbsp; {pct_xgb:.1f}%
                &nbsp;|&nbsp; {kurang_xgb} kurang baik
            </div>
        </div>

        <!-- Konsensus -->
        <div style="background:linear-gradient(135deg,#faf5ff,#ede9fe); border:2px solid #7c3aed;
                    border-radius:14px; padding:1rem 1.2rem;
                    box-shadow:0 2px 8px rgba(124,58,237,0.12);">
            <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                        letter-spacing:0.1em; color:#7c3aed; margin-bottom:0.4rem;">Konsensus</div>
            <div style="font-size:2rem; font-weight:900; color:#6d28d9; line-height:1;">{baik_kons}</div>
            <div style="font-size:0.75rem; color:#8b5cf6; margin-top:0.3rem;">
                Baik &nbsp;&#xb7;&nbsp; {pct_kons:.1f}%
                &nbsp;|&nbsp;
                <span style="color:#d97706;">{tdk_kons} tidak konsisten</span>
            </div>
        </div>
    </div>
    """)

    # ── Tabel hasil ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.95rem; font-weight:600; color:#14532d; margin-top:1rem; margin-bottom:0.5rem;
                display:flex; align-items:center; gap:0.6rem;">
        <span>Data Lengkap &amp; Hasil Prediksi</span>
        <span style="background:#eff6ff; color:#2563eb; font-size:0.65rem; font-weight:700;
                    border-radius:12px; padding:2px 8px; border:1px solid #bfdbfe;">RF</span>
        <span style="background:#f0fdf4; color:#16a34a; font-size:0.65rem; font-weight:700;
                    border-radius:12px; padding:2px 8px; border:1px solid #bbf7d0;">XGB</span>
        <span style="background:#faf5ff; color:#7c3aed; font-size:0.65rem; font-weight:700;
                    border-radius:12px; padding:2px 8px; border:1px solid #ddd6fe;">Konsensus</span>
    </div>
    """, unsafe_allow_html=True)

    def color_rf(val):
        """Warna biru untuk kolom RF."""
        if val == "Baik":       return 'background-color:#dbeafe; color:#1d4ed8; font-weight:600'
        if val == "Kurang Baik": return 'background-color:#fee2e2; color:#b91c1c; font-weight:600'
        return ''

    def color_xgb(val):
        """Warna hijau untuk kolom XGB."""
        if val == "Baik":       return 'background-color:#dcfce7; color:#15803d; font-weight:600'
        if val == "Kurang Baik": return 'background-color:#fee2e2; color:#b91c1c; font-weight:600'
        return ''

    def color_kons(val):
        """Warna ungu/amber untuk kolom Konsensus."""
        if val == "Baik":            return 'background-color:#ede9fe; color:#6d28d9; font-weight:700'
        if val == "Kurang Baik":     return 'background-color:#fee2e2; color:#b91c1c; font-weight:700'
        if val == "Tidak Konsisten": return 'background-color:#fef9c3; color:#92400e; font-weight:700'
        return ''

    # Rename kolom hanya untuk tampilan tabel
    tampil_df = df.rename(columns={
        'Hasil_RF':  'Hasil RF',
        'Hasil_XGB': 'Hasil XGBoost',
        'Konsensus': 'Konsensus',
    })
    df_styled = (
        tampil_df.style
        .map(color_rf,   subset=['Hasil RF'])
        .map(color_xgb,  subset=['Hasil XGBoost'])
        .map(color_kons, subset=['Konsensus'])
    )

    st.dataframe(df_styled, use_container_width=True, height=380)

    import io
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        tampil_df.to_excel(writer, index=False)
    excel_out = excel_buffer.getvalue()

    st.download_button(
        "Unduh Hasil (.xlsx)", excel_out,
        file_name=f"hasil_prediksi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        icon=":material/download:"
    )


    # ══════════════════════════════════════════════════════════════════════════
    # INTERPRETASI SHAP
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.5rem; margin-top:3rem; margin-bottom:1rem;">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><rect x="7" y="10" width="4" height="7"/><rect x="15" y="5" width="4" height="12"/></svg>
        <span style="font-size:1.1rem; font-weight:600; color:#14532d;">
            Interpretasi SHAP — Analisis Pengaruh Parameter
        </span>
    </div>
    """, unsafe_allow_html=True)

    col_shap_lbl, col_shap_sel = st.columns([2, 1])
    with col_shap_lbl:
        st.markdown(
            '<div style="font-size:0.85rem; color:#4b7a5e; padding-top:0.45rem;">'
            'Pilih model untuk interpretasi SHAP:</div>',
            unsafe_allow_html=True,
        )
    with col_shap_sel:
        model_shap_batch = st.selectbox(
            "Model SHAP Batch",
            options=["XGBoost", "Random Forest"],
            index=0,
            label_visibility="collapsed",
            key="shap_model_batch",
        )

    if model_shap_batch == "Random Forest":
        explainer_batch = exp_rf
        col_pred_batch  = 'Hasil_RF'
    else:
        explainer_batch = exp_xgb
        col_pred_batch  = 'Hasil_XGB'

    tab1, tab2 = st.tabs([
        "Global — Seluruh Batch",
        "Individual — Pilih Baris"
    ])

    # ── Tab 1: SHAP Global ────────────────────────────────────────────────────
    with tab1:
        st.markdown("""
        <div style="font-size:0.9rem; color:#4b7a5e; margin-bottom:1.5rem;">
            Penjelasan di bawah ini merangkum parameter mana saja yang secara
            rata-rata paling berperan dalam memisahkan CPO bermutu baik dan
            kurang baik pada keseluruhan data batch yang Anda unggah.
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Menganalisis seluruh batch..."):
            tampilkan_shap_global(explainer_batch, X)

    # ── Tab 2: SHAP Individual ────────────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div style="font-size:0.9rem; color:#4b7a5e; margin-bottom:1rem;">
            Pilih nomor baris dari tabel hasil untuk melihat penjelasan prediksi
            secara detail — lengkap dengan narasi, grafik batang, dan kartu parameter.
        </div>
        """, unsafe_allow_html=True)

        # Buat label pilihan yang informatif
        label_options = []
        for i, row in df.iterrows():
            info_parts = []
            if 'PKS' in df.columns:
                info_parts.append(str(row['PKS']))
            if 'Bulan' in df.columns:
                info_parts.append(str(row['Bulan']))
            if 'Tahun' in df.columns:
                info_parts.append(str(row['Tahun']))
            info = ' · '.join(info_parts) if info_parts else f"Baris {i+1}"
            label_options.append(f"#{i+1} — {info} [RF:{row['Hasil_RF']} / XGB:{row['Hasil_XGB']}]")

        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            pilihan = st.selectbox(
                "Pilih sampel:",
                options=range(len(label_options)),
                format_func=lambda i: label_options[i],
                key="shap_individual_select"
            )
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            tampilkan = st.button("Tampilkan SHAP", use_container_width=True)

        if tampilkan:
            st.session_state["batch_selected_sample"] = pilihan

        if "batch_selected_sample" in st.session_state and st.session_state["batch_selected_sample"] < len(df):
            sel_idx = st.session_state["batch_selected_sample"]
            X_row = X.iloc[[sel_idx]]
            row   = df.iloc[sel_idx]
            pred  = 1 if row[col_pred_batch] == 'Baik' else 0

            # Info sampel terpilih
            st.markdown("""
            <div style="font-size:0.85rem; font-weight:600; color:#4b7a5e;
                        margin-bottom:0.5rem; margin-top:1rem;">
                NILAI PARAMETER SAMPEL TERPILIH
            </div>
            """, unsafe_allow_html=True)
            info_cols = st.columns(len(FITUR))
            for col, f in zip(info_cols, FITUR):
                col.metric(f.upper(), f"{row[f]:.3f}" if f != 'carotene'
                           else f"{row[f]:.0f}")

            # Hasil dual model
            rf_color  = "#16a34a" if row['Hasil_RF']  == 'Baik' else "#dc2626"
            xgb_color = "#16a34a" if row['Hasil_XGB'] == 'Baik' else "#dc2626"
            kons_color = "#15803d" if row['Konsensus'] == 'Baik' else (
                         "#dc2626" if row['Konsensus'] == 'Kurang Baik' else "#92400e")
            st.markdown(
                f'<div style="font-size:0.88rem; font-weight:600; margin-bottom:0.4rem;">'
                f'<span style="color:#2563eb;">RF: {row["Hasil_RF"]}</span>'
                f' &nbsp;|&nbsp; '
                f'<span style="color:#16a34a;">XGB: {row["Hasil_XGB"]}</span>'
                f' &nbsp;&mdash;&nbsp; '
                f'<span style="color:{kons_color}; font-weight:700;">Konsensus: {row["Konsensus"]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            # Interpretasi SHAP visual lengkap
            with st.spinner("Menganalisis sampel..."):
                tampilkan_interpretasi_shap(explainer_batch, X_row, pred)