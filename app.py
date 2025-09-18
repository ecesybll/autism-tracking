import streamlit as st
from config.settings import DB_PATH
from database.init_db import init_db
import os
from components.dashboard import dashboard
from components.child_profile import child_profile
from components.behavior_tracker import behavior_tracker
from components.interest_analyzer import interest_analyzer
from components.progress_visualizer import progress_visualizer
from components.recommendation_engine import recommendation_engine
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# === Flask tabanlı REST API ===
from flask import Flask, request, jsonify
import threading

api_app = Flask(__name__)
DB_PATH = 'autism_tracking.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_user_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'ebeveyn', 'uzman'))
    )''')
    conn.commit()
    conn.close()

@api_app.route('/api/children', methods=['GET'])
def list_children():
    conn = get_db_connection()
    children = conn.execute('SELECT * FROM children').fetchall()
    conn.close()
    return jsonify([dict(row) for row in children])

@api_app.route('/api/children', methods=['POST'])
def add_child():
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    diagnosis = data.get('diagnosis')
    if not name or not age or not diagnosis:
        return jsonify({'error': 'Eksik bilgi'}), 400
    conn = get_db_connection()
    conn.execute('INSERT INTO children (name, age, diagnosis) VALUES (?, ?, ?)', (name, age, diagnosis))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Çocuk profili eklendi'}), 201

# Flask'ı ayrı bir thread'de başlat
if __name__ == '__main__':
    def run_flask():
        api_app.run(port=5000)
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

def load_css():
    css_path = os.path.join('assets', 'styles', 'custom.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def login_user(email, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def register_user(email, password, role):
    try:
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        conn.execute('INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)', (email, password_hash, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# --- Main App Function Refactored ---
def main_app():
    st.set_page_config(
        page_title="Otizm Gelişim Takip Sistemi",
        page_icon="data:image/svg+xml;base64  ,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NDAgNjQwIj48IS0tIUZvbnQgQXdlc29tZSBGcmVlIDcuMC4wIGJ5IEBmb250YXdlc29tZSAtIGh0dHBzOi8vZm9udGF3ZXNvbWUuY29tIExpY2Vuc2UgLSBodHRwczovL2ZvbnRhd2Vzb21lLmNvbS9saWNlbnNlL2ZyZWUgQ29weXJpZ2h0IDIwMjUgRm9udGljb25zLCBJbmMuLS0+PHBhdGggZD0iTTE4NCAxMjBDMTg0IDg5LjEgMjA5LjEgNjQgMjQwIDY0TDI2NCA2NEMyODEuNyA2NCAyOTYgNzguMyAyOTYgOTZMMjk2IDU0NEMyOTYgNTYxLjcgMjgxLjcgNTc2IDI2NCA1NzZMMjMyIDU3NkMyMDIuMiA1NzYgMTc3LjEgNTU1LjYgMTcwIDUyOEMxNjkuMyA1MjggMTY4LjcgNTI4IDE2OCA1MjhDMTIzLjggNTI4IDg4IDQ5Mi4yIDg4IDQ0OEM4OCA0MzAgOTQgNDEzLjQgMTA0IDQwMEM4NC42IDM4NS40IDcyIDM2Mi4yIDcyIDMzNkM3MiAzMDUuMSA4OS42IDI3OC4yIDExNS4yIDI2NC45QzEwOC4xIDI1Mi45IDEwNCAyMzguOSAxMDQgMjI0QzEwNCAxNzkuOCAxMzkuOCAxNDQgMTg0IDE0NEwxODQgMTIwek00NTYgMTIwTDQ1NiAxNDRDNTAwLjIgMTQ0IDUzNiAxNzkuOCA1MzYgMjI0QzUzNiAyMzkgNTMxLjkgMjUzIDUyNC44IDI2NC45QzU1MC41IDI3OC4yIDU2OCAzMDUgNTY4IDMzNkM1NjggMzYyLjIgNTU1LjQgMzg1LjQgNTM2IDQwMEM1NDYgNDEzLjQgNTUyIDQzMCA1NTIgNDQ4QzU1MiA0OTIuMiA1MTYuMiA1MjggNDcyIDUyOEM0NzEuMyA1MjggNDcwLjcgNTI4IDQ3MCA1MjhDNDYyLjkgNTU1LjYgNDM3LjggNTc2IDQwOCA1NzZMMzc2IDU3NkMzNTguMyA1NzYgMzQ0IDU2MS43IDM0NCA1NDRMMzQ0IDk2QzM0NCA3OC4zIDM1OC4zIDY0IDM3NiA2NEw0MDAgNjRDNDMwLjkgNjQgNDU2IDg5LjEgNDU2IDEyMHoiLz48L3N2Zz4=",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    load_css()
    init_db()
    init_user_table()

    # Create a simple header. Note: This is not a fixed navbar,
    # but it gives a clean header appearance.
    st.markdown("""
        <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        </head>
    <style>
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
        }
        /* Başlık stili */
        .header-title-style {
            font-size: 1.8em; /* Orta boyutta bir başlık boyutu */
            font-weight: bold;
            margin: 0;
            color: #263859;
        }
        .header-icon {
            color: #71bed1; 
            margin-right: 10px; 
        }
        .profile-info {
            text-align: right;
        }
    </style>
    <div class="header-container">
        <h1 class="header-title-style"><span class="header-icon"><i class="fas fa-brain"></i></span> Otizmli Çocuklar için Gelişim Takip Sistemi</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Place user info and logout in the sidebar for better organization.
    # This is the closest native Streamlit can get to a "profile dropdown".
    with st.sidebar:
        st.markdown("<div class='sidebar-section-header'>Profil</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info-item'><span class='icon'><i class='fas fa-envelope'></i></span> {st.session_state.user_email}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info-item'><span class='icon'><i class='fas fa-user'></i></span> {st.session_state.user_role}</div>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Use a radio button in the sidebar for navigation.
        TABS = {
            "Dashboard": "Dashboard",
            "Çocuk Profilleri": "Çocuk Profilleri",
            "Davranış Takibi": "Davranış Takibi",
            "İlgi Alanı Analizi": "İlgi Alanı Analizi",
            "İlerleme Raporları": "İlerleme Raporları",
            "Öneriler": "Öneriler"
         }
        # This acts as your navbar
        selected_tab = st.radio("Bölümler", options=list(TABS))
        
        st.markdown("---") 

        # Çıkış yap butonu için özel div ve sınıf kullanma
        st.markdown("<div class='logout-button-container'>", unsafe_allow_html=True)
        if st.button("Çıkış Yap ", key="sidebar_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.user_role = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


    # Use if/elif statements to render the correct content based on the selected tab.
    if selected_tab == "Dashboard":
        dashboard()
    elif selected_tab == "Çocuk Profilleri":
        child_profile()
    elif selected_tab == "Davranış Takibi":
        behavior_tracker()
    elif selected_tab == "İlgi Alanı Analizi":
        interest_analyzer()
    elif selected_tab == "İlerleme Raporları":
        progress_visualizer()
    elif selected_tab == "Öneriler":
        recommendation_engine()

def login_page():
    # Kullanıcı tablosunu oluştur
    init_user_table()
    load_css()
    st.set_page_config(
        page_title="Giriş - Otizm Takip Sistemi",
        page_icon="data:image/svg+xml;base64  ,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NDAgNjQwIj48IS0tIUZvbnQgQXdlc29tZSBGcmVlIDcuMC4wIGJ5IEBmb250YXdlc29tZSAtIGh0dHBzOi8vZm9udGF3ZXNvbWUuY29tIExpY2Vuc2UgLSBodHRwczovL2ZvbnRhd2Vzb21lLmNvbS9saWNlbnNlL2ZyZWUgQ29weXJpZ2h0IDIwMjUgRm9udGljb25zLCBJbmMuLS0+PHBhdGggZD0iTTI1NiAxNjBMMjU2IDIyNEwzODQgMjI0TDM4NCAxNjBDMzg0IDEyNC43IDM1NS4zIDk2IDMyMCA5NkMyODQuNyA5NiAyNTYgMTI0LjcgMjU2IDE2MHpNMTkyIDIyNEwxOTIgMTYwQzE5MiA4OS4zIDI0OS4zIDMyIDMyMCAzMkMzOTAuNyAzMiA0NDggODkuMyA0NDggMTYwTDQ0OCAyMjRDNDgzLjMgMjI0IDUxMiAyNTIuNyA1MTIgMjg4TDUxMiA1MTJDNTEyIDU0Ny4zIDQ4My4zIDU3NiA0NDggNTc2TDE5MiA1NzZDMTU2LjcgNTc2IDEyOCA1NDcuMyAxMjggNTEyTDEyOCAyODhDMTI4IDI1Mi43IDE1Ni43IDIyNCAxOTIgMjI0eiIvPjwvc3ZnPg==",
        layout="centered"
    )
    
    #st.title("🔐 Otizm Takip Sistemi")
    # st.markdown("---")
    st.markdown(
        """
        <style>
            .fa-lock {
                color: #71bed1; /* Kilit ikonunun rengini mavi yapar */
            }
            /* Sekme başlıkları için özel stil */
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
                color: #326aa7 !important;
            }
            .stTabs [data-baseweb="tab-list"] button[aria-selected="false"] {
                color: #6c757d !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("""
        <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        </head>
        <div style="text-align: center; padding: 20px; border-radius: 10px; background-color: #f0f2f6;">
            <h1><i class="fa-solid fa-lock"></i> Otizm Takip Sistemi</h1>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        st.subheader("Giriş Yap")
        with st.form("login_form"):
            email = st.text_input("E-posta")
            password = st.text_input("Şifre", type="password")
            submitted = st.form_submit_button("Giriş Yap")
            
            if submitted:
                if email and password:
                    user = login_user(email, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_email = user['email']
                        st.session_state.user_role = user['role']
                        st.success("Giriş başarılı!")
                        st.rerun()
                    else:
                        st.error("Geçersiz e-posta veya şifre!")
                else:
                    st.warning("Lütfen tüm alanları doldurun!")
    
    with tab2:
        st.markdown("<h3><i class='fas fa-user-plus register-icon'></i> Kayıt Ol</h3>", unsafe_allow_html=True)
        with st.form("register_form"):
            email = st.text_input("E-posta", key="reg_email")
            password = st.text_input("Şifre", type="password", key="reg_password")
            confirm_password = st.text_input("Şifre Tekrar", type="password")
            role = st.selectbox("Rol", ["ebeveyn", "uzman", "admin"])
            submitted = st.form_submit_button("Kayıt Ol")
            
            if submitted:
                if email and password and confirm_password:
                    if password == confirm_password:
                        if register_user(email, password, role):
                            st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
                        else:
                            st.error("Bu e-posta adresi zaten kayıtlı!")
                    else:
                        st.error("Şifreler eşleşmiyor!")
                else:
                    st.warning("Lütfen tüm alanları doldurun!")

# Ana uygulama akışı
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main_app()
else:
    login_page()