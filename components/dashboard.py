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
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            /* Genel başlık stili */
            h2, h3 {
                color: #326aa7;
            }
            /* Metrik kutucukları stilleri */
            [data-testid="stMetricValue"] {
                font-size: 2.5em;
                color: #263859;
            }
            [data-testid="stMetricLabel"] {
                font-size: 1.2em;
                color: #636b7b;
            }
            .metric-container {
                display: flex;
                align-items: center;
            }
            .metric-icon {
                font-size: 2em;
                margin-right: 15px;
            }
            .metric-box {
                border-radius: 10px;
                padding: 20px;
                background-color: #f0f2f6;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            /* Genel ikon stilleri */
            .fas {
                margin-right: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
        
    st.markdown("## <i class='fas fa-tachometer-alt'></i> Genel Durum Paneli", unsafe_allow_html=True)
    children, behaviors, progress = get_dashboard_data()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-box'><div class='metric-container'><i class='fas fa-user-friends metric-icon'></i><p>Toplam Çocuk</p></div><h2>{len(children)}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-box'><div class='metric-container'><i class='fas fa-history metric-icon'></i><p>Kayıtlı Davranış</p></div><h2>{len(behaviors)}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-box'><div class='metric-container'><i class='fas fa-chart-line metric-icon'></i><p>İlerleme Kaydı</p></div><h2>{len(progress)}</h2></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### <i class='fas fa-user-plus'></i> Son Eklenen Çocuklar", unsafe_allow_html=True)
    if not children.empty:
        st.dataframe(children.sort_values("id", ascending=False).head(5))
    else:
        st.info("Henüz çocuk kaydı yok.")

    st.markdown("---")
    st.markdown("### <i class='fas fa-chart-bar'></i> Davranış Frekansları (Özet Grafik)", unsafe_allow_html=True)
    if not behaviors.empty:
        freq_df = behaviors.groupby("behavior_type")["frequency"].sum().reset_index()
        fig = px.bar(freq_df, x="behavior_type", y="frequency", title="Davranış Frekansları")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Davranış verisi bulunamadı.")

    st.markdown("---")
    st.markdown("### <i class='fas fa-chart-area'></i> Gelişim İlerlemesi (Örnek Grafik)", unsafe_allow_html=True)
    if not progress.empty:
        progress['date'] = pd.to_datetime(progress['date'], errors='coerce')
        progress = progress.sort_values('date')
        fig2 = px.line(progress, x='date', y='value', color='metric', title='Gelişim İlerlemesi')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("İlerleme verisi bulunamadı.")