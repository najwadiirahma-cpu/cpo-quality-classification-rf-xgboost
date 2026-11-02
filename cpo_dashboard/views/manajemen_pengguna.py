import streamlit as st
import pandas as pd
from utils import ambil_semua_pengguna, tambah_pengguna, edit_pengguna, hapus_pengguna, show_toast

# ── Inline SVG Icons ─────────────────────────────────────────────────────────
_ICON = {
    "users": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#14532d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "plus": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
    "edit": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
    "trash": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>',
    "save": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1-2 2h11l5 5v11z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>',
    "x": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    "alert": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#991b1b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "warn": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#92400e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "total": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#14532d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "xred": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
}


def show():
    # ── Proteksi Role ────────────────────────────────────────────────────
    role_aktif = st.session_state.get('role', '').lower()
    if role_aktif not in ['admin', 'admin it']:
        st.error("Akses ditolak. Halaman ini hanya untuk Admin IT.", icon=":material/error:")
        st.stop()

    st.markdown('<div class="page-title">Manajemen Pengguna</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Kelola akun pengguna sistem</div>',
                unsafe_allow_html=True)

    # ── Data Pengguna ────────────────────────────────────────────────────
    df = ambil_semua_pengguna()

    # ── Statistik Ringkas ────────────────────────────────────────────────
    total       = len(df) if not df.empty else 0
    aktif       = int(df['is_active'].sum()) if not df.empty else 0
    nonaktif    = total - aktif
    admin_count = int(df['role'].isin(['admin', 'admin it']).sum()) if not df.empty else 0

    stats = [
        ("Total Pengguna", total, "#14532d", _ICON["total"]),
        ("Aktif",          aktif, "#16a34a", _ICON["check"]),
        ("Nonaktif",       nonaktif, "#dc2626", _ICON["xred"]),
        ("Admin IT",       admin_count, "#2563eb", _ICON["shield"]),
    ]

    cols_stat = st.columns(4, gap="medium")
    for col, (label, val, color, icon) in zip(cols_stat, stats):
        with col:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #d4e8db; border-radius:10px;
                        padding:1.1rem 1.3rem; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <div>
                        <div style="font-size:0.68rem; color:#4b7a5e; text-transform:uppercase;
                                    letter-spacing:0.05em; font-weight:500;">{label}</div>
                        <div style="font-size:1.6rem; font-weight:700; color:{color};
                                    margin-top:0.15rem;">{val}</div>
                    </div>
                    <div style="opacity:0.25;">{icon}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Page-level CSS ───────────────────────────────────────────────────
    st.markdown("""
    <style>
    .usr-badge {
        display:inline-block; padding:0.18rem 0.6rem; border-radius:20px;
        font-size:0.67rem; font-weight:600; text-transform:uppercase;
        letter-spacing:0.04em;
    }
    .b-admin  { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
    .b-user   { background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; }
    .b-active { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
    .b-inactive { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }

    /* icon-only action buttons */
    .icon-btn-edit button {
        background:#f0fdf4 !important; color:#16a34a !important;
        border:1px solid #bbf7d0 !important;
        min-height:36px !important; max-height:36px !important;
        padding:0 0.5rem !important; border-radius:8px !important;
    }
    .icon-btn-edit button:hover { background:#dcfce7 !important; }
    .icon-btn-edit button span,
    .icon-btn-edit button svg { color:#16a34a !important; fill:#16a34a !important; }
    .icon-btn-edit button p { display:none !important; }

    .icon-btn-del button {
        background:#fef2f2 !important; color:#dc2626 !important;
        border:1px solid #fecaca !important;
        min-height:36px !important; max-height:36px !important;
        padding:0 0.5rem !important; border-radius:8px !important;
    }
    .icon-btn-del button:hover { background:#fee2e2 !important; }
    .icon-btn-del button span,
    .icon-btn-del button svg { color:#dc2626 !important; fill:#dc2626 !important; }
    .icon-btn-del button p { display:none !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Header: Daftar Pengguna + Tambah Button ──────────────────────────
    col_title, col_btn = st.columns([3, 1], vertical_alignment="center")
    with col_title:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.55rem;">
            {_ICON["users"]}
            <span style="font-size:1.08rem; font-weight:600; color:#14532d;">
                Daftar Pengguna
            </span>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        if st.button(f"Tambah Pengguna", use_container_width=True,
                      key="btn_toggle_tambah", icon=":material/person_add:"):
            st.session_state['show_tambah_form'] = not st.session_state.get(
                'show_tambah_form', False)
            st.rerun()

    # ── Collapsible Add User Form ────────────────────────────────────────
    if st.session_state.get('show_tambah_form', False):
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #d4e8db; border-radius:12px;
                    padding:1.3rem 1.6rem; margin-bottom:1rem;
                    box-shadow:0 2px 8px rgba(22,163,74,0.08);">
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.2rem;">
                {_ICON["plus"]}
                <span style="font-size:0.95rem; font-weight:600; color:#14532d;">
                    Tambah Pengguna Baru
                </span>
            </div>
            <div style="font-size:0.76rem; color:#4b7a5e;">
                Isi semua field untuk membuat akun baru.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_tambah_pengguna", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                new_username = st.text_input("Username", placeholder="contoh: operator1")
                new_password = st.text_input("Password", type="password")
            with col_b:
                new_nama = st.text_input("Nama Lengkap", placeholder="Nama lengkap pengguna")
                new_role = st.selectbox("Role", options=["admin staff", "admin it"],
                                        format_func=lambda x: x.title())

            col_submit, col_cancel, _ = st.columns([1, 1, 3])
            with col_submit:
                submitted_add = st.form_submit_button("Simpan Pengguna",
                                                       use_container_width=True,
                                                       icon=":material/save:")
            with col_cancel:
                cancel_add = st.form_submit_button("Batal",
                                                    use_container_width=True,
                                                    icon=":material/close:")

            if cancel_add:
                st.session_state['show_tambah_form'] = False
                st.rerun()

            if submitted_add:
                if not new_username or not new_password or not new_nama:
                    show_toast("Semua field harus diisi.", kind="error")
                elif len(new_password) < 4:
                    show_toast("Password minimal 4 karakter.", kind="error")
                else:
                    ok, msg = tambah_pengguna(new_username, new_password, new_nama, new_role)
                    if ok:
                        show_toast(msg, kind="success")
                        st.session_state['show_tambah_form'] = False
                        st.rerun()
                    else:
                        show_toast(msg, kind="error")

    # ── User List ────────────────────────────────────────────────────────
    if df.empty:
        st.info("Belum ada data pengguna.", icon=":material/info:")
    else:
        # Container card
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #d4e8db; border-radius:12px;
                    overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.04);
                    margin-bottom:1.2rem;">
        """, unsafe_allow_html=True)

        # Table header row
        hdr_cols = st.columns([0.4, 2.2, 1, 1, 1], gap="small")
        with hdr_cols[0]:
            st.markdown("")
        for idx, label in enumerate(["PENGGUNA", "ROLE", "STATUS", "AKSI"], start=1):
            with hdr_cols[idx]:
                st.markdown(f"""
                <div style="font-size:0.68rem; font-weight:600; color:#4b7a5e;
                            text-transform:uppercase; letter-spacing:0.06em;
                            padding:0.5rem 0; border-bottom:2px solid #d4e8db;">
                    {label}
                </div>
                """, unsafe_allow_html=True)

        # User rows
        for _, row in df.iterrows():
            initial = row['nama'][0].upper() if row['nama'] else '?'
            role_cls = 'b-admin' if row['role'] in ['admin', 'admin it'] else 'b-user'
            stat_cls = 'b-active' if row['is_active'] else 'b-inactive'
            stat_txt = 'Aktif' if row['is_active'] else 'Nonaktif'
            is_self  = row['username'] == st.session_state.get('username')
            uid      = row['id']

            r = st.columns([0.4, 2.2, 1, 1, 1], gap="small",
                           vertical_alignment="center")

            # Avatar
            with r[0]:
                st.markdown(f"""
                <div style="width:36px; height:36px; border-radius:50%;
                            background:linear-gradient(135deg,#16a34a,#14532d);
                            display:flex; align-items:center; justify-content:center;
                            font-size:0.9rem; color:#fff; font-weight:700;">
                    {initial}
                </div>
                """, unsafe_allow_html=True)

            # Name + username
            with r[1]:
                st.markdown(f"""
                <div>
                    <div style="font-size:0.88rem; font-weight:600; color:#14532d;
                                line-height:1.3;">{row['nama']}</div>
                    <div style="font-size:0.72rem; color:#4b7a5e;">@{row['username']}</div>
                </div>
                """, unsafe_allow_html=True)

            # Role badge
            with r[2]:
                st.markdown(f"""
                <span class="usr-badge {role_cls}">{row['role'].title()}</span>
                """, unsafe_allow_html=True)

            # Status badge
            with r[3]:
                st.markdown(f"""
                <span class="usr-badge {stat_cls}">{stat_txt}</span>
                """, unsafe_allow_html=True)

            # Action buttons — icon-only
            with r[4]:
                bc1, bc2 = st.columns(2, gap="small")
                with bc1:
                    st.markdown('<div class="icon-btn-edit">', unsafe_allow_html=True)
                    if st.button("\u200b", key=f"edit_{uid}",
                                 help=f"Edit {row['nama']}",
                                 use_container_width=True,
                                 icon=":material/edit:"):
                        st.session_state['editing_user_id'] = uid
                        st.session_state['confirm_delete_id'] = None
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with bc2:
                    st.markdown('<div class="icon-btn-del">', unsafe_allow_html=True)
                    if is_self:
                        st.button("\u200b", key=f"del_{uid}", disabled=True,
                                  help="Tidak bisa menghapus akun sendiri",
                                  use_container_width=True,
                                  icon=":material/delete:")
                    else:
                        if st.button("\u200b", key=f"del_{uid}",
                                     help=f"Hapus {row['nama']}",
                                     use_container_width=True,
                                     icon=":material/delete:"):
                            st.session_state['confirm_delete_id'] = uid
                            st.session_state['confirm_delete_name'] = row['nama']
                            st.session_state['editing_user_id'] = None
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            # Separator line
            st.markdown("""
            <div style="border-bottom:1px solid #e8f0eb; margin:0 1.2rem;"></div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Delete Confirmation ──────────────────────────────────────────────
    if st.session_state.get('confirm_delete_id'):
        del_id   = st.session_state['confirm_delete_id']
        del_name = st.session_state.get('confirm_delete_name', '')

        st.markdown(f"""
        <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:12px;
                    padding:1.3rem 1.6rem; margin-bottom:1rem;
                    box-shadow:0 2px 8px rgba(220,38,38,0.08);">
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">
                {_ICON["alert"]}
                <span style="font-size:0.95rem; font-weight:600; color:#991b1b;">
                    Konfirmasi Hapus Pengguna
                </span>
            </div>
            <div style="font-size:0.82rem; color:#991b1b;">
                Apakah Anda yakin ingin menghapus pengguna
                <strong>{del_name}</strong>?
                Tindakan ini tidak dapat dibatalkan.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_yes, col_no, _ = st.columns([1, 1, 3])
        with col_yes:
            if st.button("Ya, Hapus", key="confirm_delete_yes",
                         use_container_width=True,
                         icon=":material/delete_forever:"):
                ok, msg = hapus_pengguna(del_id)
                if ok:
                    show_toast(msg, kind="success")
                    st.session_state['confirm_delete_id'] = None
                    st.session_state['confirm_delete_name'] = None
                    st.rerun()
                else:
                    show_toast(msg, kind="error")
        with col_no:
            if st.button("Batal", key="confirm_delete_no",
                         use_container_width=True,
                         icon=":material/close:"):
                st.session_state['confirm_delete_id'] = None
                st.session_state['confirm_delete_name'] = None
                st.rerun()

    # ── Edit User Panel ──────────────────────────────────────────────────
    if st.session_state.get('editing_user_id') and not df.empty:
        edit_id  = st.session_state['editing_user_id']
        user_row = df[df['id'] == edit_id]

        if not user_row.empty:
            user    = user_row.iloc[0]
            is_self = user['username'] == st.session_state.get('username')

            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #d4e8db; border-radius:12px;
                        padding:1.3rem 1.6rem; margin-top:0.5rem;
                        box-shadow:0 2px 8px rgba(22,163,74,0.08);">
                <div style="display:flex; align-items:center; gap:0.5rem;">
                    {_ICON["edit"]}
                    <span style="font-size:0.95rem; font-weight:600; color:#14532d;">
                        Edit Pengguna — {user['nama']}
                    </span>
                    <span style="margin-left:auto; font-size:0.7rem; color:#4b7a5e;
                                 background:#f0fdf4; padding:0.18rem 0.55rem;
                                 border-radius:12px; border:1px solid #bbf7d0;">
                        @{user['username']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if is_self:
                st.markdown(f"""
                <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px;
                            padding:0.55rem 1rem; margin:0.5rem 0;">
                    <div style="display:flex; align-items:center; gap:0.4rem;">
                        {_ICON["warn"]}
                        <span style="font-size:0.76rem; color:#92400e;">
                            Anda sedang mengedit akun sendiri — role dan status tidak dapat diubah.
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with st.form(f"form_edit_{edit_id}"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    edit_nama = st.text_input("Nama Lengkap", value=user['nama'])
                    edit_password = st.text_input(
                        "Password Baru (kosongkan jika tidak diubah)",
                        type="password")
                with col_e2:
                    if is_self:
                        st.selectbox("Role",
                                     options=[user['role'].title()],
                                     disabled=True,
                                     help="Anda tidak dapat mengubah role akun sendiri.")
                        edit_role = user['role']
                        st.selectbox("Status Aktif",
                                     options=["Aktif"], disabled=True,
                                     help="Anda tidak dapat menonaktifkan akun sendiri.")
                        edit_active = True
                    else:
                        idx_role = 0 if user['role'] not in ['admin it', 'admin'] else 1
                        edit_role = st.selectbox(
                            "Role",
                            options=["admin staff", "admin it"],
                            index=idx_role,
                            format_func=lambda x: x.title())
                        edit_active = st.selectbox(
                            "Status Aktif",
                            options=["Aktif", "Nonaktif"],
                            index=0 if user['is_active'] else 1) == "Aktif"

                col_save, col_cancel_edit, _ = st.columns([1, 1, 3])
                with col_save:
                    submitted_edit = st.form_submit_button("Simpan Perubahan",
                                                           use_container_width=True,
                                                           icon=":material/save:")
                with col_cancel_edit:
                    cancel_edit = st.form_submit_button("Batal",
                                                        use_container_width=True,
                                                        icon=":material/close:")

                if cancel_edit:
                    st.session_state['editing_user_id'] = None
                    st.rerun()

                if submitted_edit:
                    update_data = {
                        "nama": edit_nama,
                        "role": edit_role,
                        "is_active": edit_active,
                    }
                    if edit_password:
                        if len(edit_password) < 4:
                            show_toast("Password minimal 4 karakter.", kind="error")
                            st.stop()
                        update_data["password"] = edit_password

                    ok, msg = edit_pengguna(edit_id, update_data)
                    if ok:
                        show_toast(msg, kind="success")
                        st.session_state['editing_user_id'] = None
                        st.rerun()
                    else:
                        show_toast(msg, kind="error")
