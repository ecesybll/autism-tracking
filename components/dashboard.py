import streamlit as st
import plotly.express as px
import pandas as pd
import sqlite3
from config.settings import DB_PATH

def get_dashboard_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        children = pd.read_sql_query("SELECT * FROM children", conn)
        behaviors = pd.read_sql_query("SELECT * FROM behaviors", conn)
        progress = pd.read_sql_query("SELECT * FROM progress_records", conn)
        conn.close()
        return children, behaviors, progress
    except Exception as e:
        st.error(f"Veri alınırken hata oluştu: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def dashboard():
    st.subheader("Genel Durum Paneli")
    children, behaviors, progress = get_dashboard_data()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Toplam Çocuk", len(children))
    with col2:
        st.metric("Kayıtlı Davranış", len(behaviors))
    with col3:
        st.metric("İlerleme Kaydı", len(progress))

    st.markdown("---")
    st.write("### Son Eklenen Çocuklar")
    if not children.empty:
        st.dataframe(children.sort_values("id", ascending=False).head(5))
    else:
        st.info("Henüz çocuk kaydı yok.")

    st.markdown("---")
    st.write("### Davranış Frekansları (Özet Grafik)")
    if not behaviors.empty:
        freq_df = behaviors.groupby("behavior_type")["frequency"].sum().reset_index()
        fig = px.bar(freq_df, x="behavior_type", y="frequency", title="Davranış Frekansları")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Davranış verisi bulunamadı.")

    st.markdown("---")
    st.write("### Gelişim İlerlemesi (Örnek Grafik)")
    if not progress.empty:
        progress['date'] = pd.to_datetime(progress['date'], errors='coerce')
        progress = progress.sort_values('date')
        fig2 = px.line(progress, x='date', y='value', color='metric', title='Gelişim İlerlemesi')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("İlerleme verisi bulunamadı.")