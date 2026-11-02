import streamlit as st
import os

def show():
    st.markdown('<div class="page-title">Interpretasi SHAP Global</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Analisis kontribusi tiap parameter terhadap hasil klasifikasi model.</div>', unsafe_allow_html=True)

    # File SHAP dari hasil Colab
    shap_files = {
        'bar_xgb': 'shap_bar_xgb.png',
        'sum_xgb': 'shap_summary_xgb.png',
    }

    tab1, tab2 = st.tabs([
        "Tingkat Pengaruh Parameter (Bar)",
        "Distribusi Nilai (Dot)"
    ])

    with tab1:
        # Header section dengan divider visual
        st.markdown("""
        <div style="
            border-left: 4px solid #16a34a;
            padding: 0.4rem 0.9rem;
            margin-bottom: 1.2rem;
            background: #f0fdf4;
            border-radius: 0 8px 8px 0;
        ">
            <div style="font-size:0.85rem;font-weight:600;color:#14532d;">
                Grafik Batang — Tingkat Pengaruh Parameter
            </div>
            <div style="font-size:0.78rem;color:#4b7a5a;margin-top:2px;">
                Semakin panjang garisnya, semakin besar pengaruh fitur tersebut terhadap hasil klasifikasi akhir secara rata-rata.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if os.path.exists(shap_files['bar_xgb']):
            st.image(shap_files['bar_xgb'], use_container_width=True)
        else:
            st.info("File gambar analisis belum tersedia.")

    with tab2:
        st.markdown("""
        <div style="
            border-left: 4px solid #16a34a;
            padding: 0.4rem 0.9rem;
            margin-bottom: 1.2rem;
            background: #f0fdf4;
            border-radius: 0 8px 8px 0;
        ">
            <div style="font-size:0.85rem;font-weight:600;color:#14532d;">
                Grafik Sebaran — Distribusi Nilai Parameter
            </div>
            <div style="font-size:0.78rem;color:#4b7a5a;margin-top:2px;">
                Melihat lebih detail bagaimana nilai tinggi (merah) atau rendah (biru) dari suatu parameter mendorong hasil prediksi.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if os.path.exists(shap_files['sum_xgb']):
            st.image(shap_files['sum_xgb'], use_container_width=True)
        else:
            st.info("File gambar analisis belum tersedia.")

    # Kesimpulan
    st.markdown("---")
    st.markdown("""
    <div style="
        font-size:0.95rem;font-weight:600;color:#14532d;
        margin-bottom:0.75rem;display:flex;align-items:center;gap:6px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24"
          fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
        Kesimpulan Analisis Sistem
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
Berdasarkan analisis sistem secara keseluruhan:

- **ALB (FFA)** merupakan parameter dengan pengaruh terbesar yang menentukan mutu CPO. Jika nilainya terlalu tinggi, sistem akan langsung menilainya sebagai *Kurang Baik*.
- **DOBI** dan **PV** berada di urutan berikutnya, yang berarti kualitas oksidasi minyak sangat diperhitungkan oleh sistem.
- **Kadar Air (Moisture)** dan **Kotoran (Dirt)** memiliki pengaruh menengah, karena biasanya parameter ini lebih mudah dijaga konsistensinya.
- **β-Karoten** dan **IV** memiliki pengaruh paling kecil secara rata-rata, tetapi tetap digunakan sistem sebagai indikator pelengkap.
    """)
