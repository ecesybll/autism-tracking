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

def load_css():
    css_path = os.path.join('assets', 'styles', 'custom.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(
    page_title="Otizm Gelişim Takip Sistemi",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()
init_db()

st.title("🧠 Otizmli Çocuklar için Yapay Zeka Destekli Gelişim Takip Sistemi")

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