import streamlit as st
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from utils import (
    FITUR, FITUR_LABEL, THRESHOLD, INPUT_CONFIG,
    load_models, simpan_riwayat, label_konsensus,
    result_html_dual, render_parameter_status_cards, tampilkan_interpretasi_shap,
    show_toast
)


def show():
    rf, xgb, exp_rf, exp_xgb, ok = load_models()
    if not ok:
        st.warning("Model belum tersedia. Pastikan file `.pkl` ada di folder `models/`.")
        return

    st.markdown('<div class="page-title">Prediksi Manual</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Masukkan 7 parameter mutu CPO untuk mendapatkan hasil klasifikasi dari dua model (Random Forest &amp; XGBoost).</div>', unsafe_allow_html=True)

    with st.form("form_prediksi"):
        st.markdown("""
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:1rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>
            <span style="font-size:1.1rem; font-weight:600; color:#14532d;">
                Input Parameter Mutu CPO
            </span>
        </div>
        """, unsafe_allow_html=True)

        col_utama, col_sekunder = st.columns(2, gap="large")
        params = {}

        fitur_utama    = ["ffa", "moisture", "dirt"]
        fitur_sekunder = ["pv", "dobi", "carotene", "iv"]

        with col_utama:
            st.markdown("""
            <div style="font-size:0.85rem; font-weight:600; color:#4b7a5e; margin-bottom:0.8rem;
                        border-bottom:1px solid #e8f0eb; padding-bottom:0.3rem;">
                PARAMETER UTAMA
            </div>
            """, unsafe_allow_html=True)
            for f in fitur_utama:
                op, thresh = THRESHOLD[f]
                cfg = INPUT_CONFIG[f]
                params[f] = st.number_input(
                    f"{FITUR_LABEL[f]} (Batas: {op} {thresh})",
                    min_value=cfg['min'], max_value=cfg['max'],
                    value=None, step=cfg['step'],
                    key=f"inp_{f}",
                    placeholder=str(cfg['default'])
                )
        with col_sekunder:
            st.markdown("""
            <div style="font-size:0.85rem; font-weight:600; color:#4b7a5e; margin-bottom:0.8rem;
                        border-bottom:1px solid #e8f0eb; padding-bottom:0.3rem;">
                INDIKATOR SEKUNDER
            </div>
            """, unsafe_allow_html=True)
            for f in fitur_sekunder:
                op, thresh = THRESHOLD[f]
                cfg = INPUT_CONFIG[f]
                params[f] = st.number_input(
                    f"{FITUR_LABEL[f]} (Batas: {op} {thresh})",
                    min_value=cfg['min'], max_value=cfg['max'],
                    value=None, step=cfg['step'],
                    key=f"inp_{f}",
                    placeholder=str(cfg['default'])
                )
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Jalankan Prediksi", use_container_width=True)

    if submitted:
        if None in params.values():
            st.error(
                "Mohon isi semua parameter mutu CPO dengan angka sebelum menjalankan prediksi.",
                icon=":material/error:"
            )
        else:
            st.session_state["manual_params"] = params
            st.session_state["manual_has_prediction"] = True
            
            # Predict & Save to Supabase (only once when submitted)
            X_init = pd.DataFrame([params], columns=FITUR)
            p_rf  = int(rf.predict(X_init)[0])
            p_xgb = int(xgb.predict(X_init)[0])
            kons  = label_konsensus(p_rf, p_xgb)
            simpan_riwayat(params, kons)
            show_toast("Prediksi berhasil dijalankan dan disimpan ke riwayat.", kind="success")

    if st.session_state.get("manual_has_prediction") and "manual_params" in st.session_state:
        current_params = st.session_state["manual_params"]
        X = pd.DataFrame([current_params], columns=FITUR)

        pred_rf  = int(rf.predict(X)[0])
        pred_xgb = int(xgb.predict(X)[0])

        # ── Hasil Klasifikasi Dua Model ────────────────────────────────────────
        st.markdown("""
        <div style="display:flex; align-items:center; gap:0.5rem; margin-top:2.5rem; margin-bottom:1rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
                 fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
            </svg>
            <span style="font-size:1.1rem; font-weight:600; color:#14532d;">
                Hasil Klasifikasi Dua Model
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.html(result_html_dual(pred_rf, pred_xgb))

        # ── Status tiap parameter ──────────────────────────────────────────────
        st.markdown("""
        <div style="display:flex; align-items:center; gap:0.5rem; margin-top:2.5rem; margin-bottom:1rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
                 fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <span style="font-size:1.1rem; font-weight:600; color:#14532d;">
                Status Parameter Individu
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.html(render_parameter_status_cards(current_params))

        # ── SHAP Interpretation ────────────────────────────────────────────────
        st.markdown("""
        <div style="display:flex; align-items:center; gap:0.5rem; margin-top:2.5rem; margin-bottom:0.8rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
                 fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 3v18h18"/>
                <rect x="7" y="10" width="4" height="7"/>
                <rect x="15" y="5" width="4" height="12"/>
            </svg>
            <span style="font-size:1.1rem; font-weight:600; color:#14532d;">
                Interpretasi SHAP — Analisis Pengaruh Parameter
            </span>
        </div>
        """, unsafe_allow_html=True)

        col_lbl, col_sel = st.columns([2, 1])
        with col_lbl:
            st.markdown(
                '<div style="font-size:0.85rem; color:#4b7a5e; padding-top:0.45rem;">'
                'Pilih model untuk interpretasi SHAP:</div>',
                unsafe_allow_html=True,
            )
        with col_sel:
            model_shap = st.selectbox(
                "Model SHAP",
                options=["XGBoost", "Random Forest"],
                index=0,
                label_visibility="collapsed",
                key="shap_model_manual",
            )

        if model_shap == "Random Forest":
            explainer_shap = exp_rf
            pred_for_shap  = pred_rf
        else:
            explainer_shap = exp_xgb
            pred_for_shap  = pred_xgb

        tampilkan_interpretasi_shap(explainer_shap, X, pred_for_shap)

