import streamlit as st
from utils import ubah_password, ubah_username, ubah_nama, show_toast


# ── Helper: Tips box (terima list of plain strings) ──────────────────────────
def _tips(items: list[str]):
    li_html = "".join(f"<li>{item}</li>" for item in items)
    st.markdown(f"""
    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px;
                padding:1.2rem 1.4rem; margin-top:0.5rem; height:fit-content;">
        <div style="font-size:0.78rem; font-weight:600; color:#14532d;
                    margin-bottom:0.6rem; text-transform:uppercase;
                    letter-spacing:0.05em;">
            Panduan
        </div>
        <ul style="font-size:0.78rem; color:#3d6b50; margin:0; padding-left:1.1rem;
                   line-height:1.8;">
            {li_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)


def show():
    st.markdown('<div class="page-title">Profil Saya</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Informasi akun dan pengaturan keamanan</div>',
                unsafe_allow_html=True)

    # ── Kartu Informasi Pengguna ──────────────────────────────────────────
    username = st.session_state.get('username', '—')
    nama     = st.session_state.get('nama', '—')
    initial  = nama[0].upper() if nama and nama != '—' else '?'

    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #d4e8db; border-radius:12px;
                padding:1.8rem 2rem; margin-bottom:1.5rem;
                box-shadow:0 1px 3px rgba(0,0,0,0.04);">
        <div style="display:flex; align-items:center; gap:1.2rem; margin-bottom:1.4rem;">
            <div style="width:52px; height:52px; border-radius:50%;
                        background:linear-gradient(135deg,#16a34a,#14532d);
                        display:flex; align-items:center; justify-content:center;
                        font-size:1.4rem; color:#fff; font-weight:700; flex-shrink:0;">
                {initial}
            </div>
            <div>
                <div style="font-size:1.15rem; font-weight:600; color:#14532d;
                            line-height:1.3;">{nama}</div>
                <div style="font-size:0.82rem; color:#4b7a5e; margin-top:2px;">
                    @{username}
                </div>
            </div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.8rem;">
            <div style="background:#f8faf8; border-radius:8px; padding:0.9rem 1.1rem;
                        border:1px solid #e8f0eb;">
                <div style="font-size:0.68rem; color:#4b7a5e; text-transform:uppercase;
                            letter-spacing:0.06em; margin-bottom:0.3rem; font-weight:500;">
                    Username
                </div>
                <div style="font-size:0.95rem; font-weight:600; color:#14532d;">
                    {username}
                </div>
            </div>
            <div style="background:#f8faf8; border-radius:8px; padding:0.9rem 1.1rem;
                        border:1px solid #e8f0eb;">
                <div style="font-size:0.68rem; color:#4b7a5e; text-transform:uppercase;
                            letter-spacing:0.06em; margin-bottom:0.3rem; font-weight:500;">
                    Nama Lengkap
                </div>
                <div style="font-size:0.95rem; font-weight:600; color:#14532d;">
                    {nama}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tab navigasi ──────────────────────────────────────────────────────
    tab_pw, tab_un, tab_nm = st.tabs([
        "Ubah Password",
        "Ubah Username",
        "Ubah Nama Lengkap",
    ])

    # ── Tab 1: Ubah Password ─────────────────────────────────────────────
    with tab_pw:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #d4e8db; border-radius:12px;
                    padding:1.5rem 1.8rem; margin:1rem 0 0.8rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="font-size:0.95rem; font-weight:600; color:#14532d;
                        margin-bottom:0.3rem;">Ubah Password</div>
            <div style="font-size:0.82rem; color:#4b7a5e;">
                Masukkan password lama untuk verifikasi, lalu tentukan password baru.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_l, col_r = st.columns([1.2, 1])
        with col_l:
            with st.form("form_ubah_password", clear_on_submit=True):
                pw_lama    = st.text_input("Password Lama",             type="password")
                pw_baru    = st.text_input("Password Baru",             type="password")
                pw_konfirm = st.text_input("Konfirmasi Password Baru",  type="password")
                submitted  = st.form_submit_button("Simpan Password Baru",
                                                   use_container_width=True)
                if submitted:
                    if not pw_lama or not pw_baru or not pw_konfirm:
                        show_toast("Semua field harus diisi.", kind="error")
                    elif pw_baru != pw_konfirm:
                        show_toast("Password baru dan konfirmasi tidak cocok.", kind="error")
                    elif len(pw_baru) < 4:
                        show_toast("Password baru minimal 4 karakter.", kind="error")
                    else:
                        ok, msg = ubah_password(st.session_state['username'],
                                                pw_lama, pw_baru)
                        if ok:
                            show_toast(msg, kind="success")
                        else:
                            show_toast(msg, kind="error")
        with col_r:
            _tips([
                "Gunakan minimal 4 karakter",
                "Kombinasikan huruf dan angka",
                "Jangan gunakan password yang mudah ditebak",
                "Ubah password secara berkala untuk keamanan",
            ])

    # ── Tab 2: Ubah Username ─────────────────────────────────────────────
    with tab_un:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #d4e8db; border-radius:12px;
                    padding:1.5rem 1.8rem; margin:1rem 0 0.8rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="font-size:0.95rem; font-weight:600; color:#14532d;
                        margin-bottom:0.3rem;">Ubah Username</div>
            <div style="font-size:0.82rem; color:#4b7a5e;">
                Masukkan username baru dan verifikasi dengan password Anda.
                Setelah berhasil, Anda akan diminta login ulang.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_l2, col_r2 = st.columns([1.2, 1])
        with col_l2:
            with st.form("form_ubah_username", clear_on_submit=True):
                un_baru    = st.text_input("Username Baru",
                                           placeholder="contoh: operator_baru")
                pw_verify2 = st.text_input("Password (untuk verifikasi)", type="password")
                submitted2 = st.form_submit_button("Simpan Username Baru",
                                                    use_container_width=True)
                if submitted2:
                    if not un_baru or not pw_verify2:
                        show_toast("Semua field harus diisi.", kind="error")
                    elif len(un_baru) < 3:
                        show_toast("Username minimal 3 karakter.", kind="error")
                    elif un_baru == st.session_state['username']:
                        show_toast("Username baru sama dengan username saat ini.", kind="warning")
                    else:
                        ok, msg = ubah_username(st.session_state['username'],
                                                un_baru, pw_verify2)
                        if ok:
                            show_toast(msg, kind="success")
                            for key in ['logged_in', 'username', 'nama', 'current_page']:
                                st.session_state.pop(key, None)
                            st.query_params.clear()
                            st.rerun()
                        else:
                            show_toast(msg, kind="error")
        with col_r2:
            _tips([
                "Username minimal 3 karakter",
                "Disarankan menggunakan huruf kecil dan angka",
                "Karakter garis bawah (_) diperbolehkan",
                "Setelah ubah username, sesi akan berakhir dan Anda perlu login ulang",
            ])

    # ── Tab 3: Ubah Nama Lengkap ─────────────────────────────────────────
    with tab_nm:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #d4e8db; border-radius:12px;
                    padding:1.5rem 1.8rem; margin:1rem 0 0.8rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="font-size:0.95rem; font-weight:600; color:#14532d;
                        margin-bottom:0.3rem;">Ubah Nama Lengkap</div>
            <div style="font-size:0.82rem; color:#4b7a5e;">
                Perbarui nama lengkap yang ditampilkan di sistem.
                Verifikasi diperlukan menggunakan password Anda.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_l3, col_r3 = st.columns([1.2, 1])
        with col_l3:
            with st.form("form_ubah_nama", clear_on_submit=True):
                nm_baru    = st.text_input("Nama Lengkap Baru",
                                           placeholder="Masukkan nama lengkap baru")
                pw_verify3 = st.text_input("Password (untuk verifikasi)", type="password")
                submitted3 = st.form_submit_button("Simpan Nama Baru",
                                                    use_container_width=True)
                if submitted3:
                    if not nm_baru or not pw_verify3:
                        show_toast("Semua field harus diisi.", kind="error")
                    elif len(nm_baru.strip()) < 2:
                        show_toast("Nama lengkap minimal 2 karakter.", kind="error")
                    elif nm_baru.strip() == st.session_state.get('nama', ''):
                        show_toast("Nama baru sama dengan nama saat ini.", kind="warning")
                    else:
                        ok, msg = ubah_nama(st.session_state['username'],
                                            pw_verify3, nm_baru)
                        if ok:
                            st.session_state['nama'] = nm_baru.strip()
                            st.query_params['nama']  = nm_baru.strip()
                            show_toast(msg, kind="success")
                            st.rerun()
                        else:
                            show_toast(msg, kind="error")
        with col_r3:
            _tips([
                "Gunakan nama lengkap sesuai identitas resmi",
                "Nama akan ditampilkan di sidebar dan halaman profil",
                "Perubahan langsung berlaku tanpa perlu login ulang",
            ])
