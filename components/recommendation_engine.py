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
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            /* Başlık ve alt başlık stilleri */
            h2, h3 {
                color: #263859;
            }
            /* Genel ikon stilleri */
            .fas {
                margin-right: 8px;
            }
            /* Başarılı ve Hata mesajları için özel ikon renkleri */
            div[data-testid="stStatusIcon-success"] svg { color: #28a745; }
            div[data-testid="stStatusIcon-error"] svg { color: #dc3545; }
            div[data-testid="stStatusIcon-warning"] svg { color: #ffc107; }
        </style>
        """,
        unsafe_allow_html=True
    )
        
    st.markdown("## <i class='fa-regular fa-lightbulb'></i> Kişiselleştirilmiş AI Önerileri", unsafe_allow_html=True)
    children_df = get_children_options()
    if children_df.empty:
        st.info("Önce çocuk eklemelisiniz.")
        return
    with st.form("recommendation_form"):
        st.markdown("### <i class='fas fa-user'></i> Öneri Alınacak Çocuk", unsafe_allow_html=True)
        child_name = st.selectbox("Çocuk", children_df['name'])
        st.markdown("### <i class='fas fa-sticky-note'></i> Ek Notlar", unsafe_allow_html=True)
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