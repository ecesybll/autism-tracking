import streamlit as st
import pandas as pd
import sqlite3
from config.settings import DB_PATH
from services.ai_service import generate_recommendation

def get_children_options():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM children", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Çocuklar alınırken hata oluştu: {e}")
        return pd.DataFrame()

def recommendation_engine():
    st.subheader("Kişiselleştirilmiş AI Önerileri")
    children_df = get_children_options()
    if children_df.empty:
        st.info("Önce çocuk eklemelisiniz.")
        return
    with st.form("recommendation_form"):
        child_name = st.selectbox("Çocuk", children_df['name'])
        extra_notes = st.text_area("Ek Notlar (isteğe bağlı)", help="Özel ihtiyaç, ilgi veya açıklama ekleyebilirsiniz.")
        submitted = st.form_submit_button("AI'dan Öneri Al")
        if submitted:
            # Seçilen çocuğun tüm bilgilerini al
            child_row = children_df[children_df['name'] == child_name].iloc[0]
            age = child_row['age']
            strengths = child_row.get('strengths', '')
            challenges = child_row.get('challenges', '')
            with st.spinner("AI öneri üretiyor..."):
                result = generate_recommendation(child_name, age, strengths, challenges, extra_notes)
            st.success("AI Önerisi:")
            st.write(result)