import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from config.settings import DB_PATH

def get_children_options():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT id, name FROM children", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Çocuklar alınırken hata oluştu: {e}")
        return pd.DataFrame()

def get_progress(child_id=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        if child_id:
            df = pd.read_sql_query(f"SELECT * FROM progress_records WHERE child_id={child_id}", conn)
        else:
            df = pd.read_sql_query("SELECT * FROM progress_records", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"İlerleme verisi alınırken hata oluştu: {e}")
        return pd.DataFrame()

def progress_visualizer():
    st.subheader("İlerleme Raporları ve Grafikler")
    children_df = get_children_options()
    if children_df.empty:
        st.info("Önce çocuk eklemelisiniz.")
        return
    child_name = st.selectbox("Çocuk Seç", children_df['name'])
    child_id = int(children_df[children_df['name'] == child_name]['id'].values[0])
    df = get_progress(child_id)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.sort_values('date')
        st.dataframe(df)
        st.markdown("---")
        st.write("### Gelişim İlerlemesi Grafiği")
        fig = px.line(df, x='date', y='value', color='metric', title='Gelişim İlerlemesi')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Seçili çocuk için ilerleme verisi yok.")