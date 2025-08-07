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

def main_app():
    st.set_page_config(
        page_title="Otizm Gelişim Takip Sistemi",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    load_css()
    init_db()
    init_user_table()

    st.title("🧠 Otizmli Çocuklar için Yapay Zeka Destekli Gelişim Takip Sistemi")
    
    # Kullanıcı bilgilerini göster
    col1, col2 = st.columns([3, 1])
    with col2:
        st.write(f"**Hoşgeldin:** {st.session_state.user_email}")
        st.write(f"**Rol:** {st.session_state.user_role}")
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.user_role = None
            st.rerun()

    TABS = [
        "Dashboard",
        "Çocuk Profilleri",
        "Davranış Takibi",
        "İlgi Alanı Analizi",
        "İlerleme Raporları",
        "Öneriler"
    ]
    tab_objs = st.tabs(TABS)

    with tab_objs[0]:
        dashboard()
    with tab_objs[1]:
        child_profile()
    with tab_objs[2]:
        behavior_tracker()
    with tab_objs[3]:
        interest_analyzer()
    with tab_objs[4]:
        progress_visualizer()
    with tab_objs[5]:
        recommendation_engine()

def login_page():
    # Kullanıcı tablosunu oluştur
    init_user_table()
    
    st.set_page_config(
        page_title="Giriş - Otizm Takip Sistemi",
        page_icon="🔐",
        layout="centered"
    )
    
    st.title("🔐 Otizm Takip Sistemi")
    st.markdown("---")
    
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
        st.subheader("Kayıt Ol")
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