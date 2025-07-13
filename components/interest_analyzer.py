import streamlit as st
import pandas as pd
import sqlite3
from config.settings import DB_PATH
from services.ai_service import analyze_interest

def get_children_options():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT id, name FROM children", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Çocuklar alınırken hata oluştu: {e}")
        return pd.DataFrame()

def interest_analyzer():
    st.subheader("İlgi Alanı Analizi (AI Destekli)")
    children_df = get_children_options()
    if children_df.empty:
        st.info("Önce çocuk eklemelisiniz.")
        return
    with st.form("interest_form"):
        child_name = st.selectbox("Çocuk", children_df['name'])
        activity_data = st.text_area("Aktivite/Etkileşim Verisi", help="Çocuğun son zamanlardaki aktiviteleri, oyunları, hobileri vb.")
        submitted = st.form_submit_button("AI ile Analiz Et")
        if submitted:
            if not activity_data.strip():
                st.warning("Aktivite verisi zorunludur.")
            else:
                with st.spinner("AI analiz ediyor..."):
                    result = analyze_interest(activity_data)
                st.success("AI Analiz Sonucu:")
                st.write(result)