import streamlit as st
import pandas as pd
import sqlite3
from config.settings import DB_PATH

def get_children():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM children", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Çocuklar alınırken hata oluştu: {e}")
        return pd.DataFrame()

def add_child(name: str, age: int, diagnosis_date: str, strengths: str, challenges: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO children (name, age, diagnosis_date, strengths, challenges) VALUES (?, ?, ?, ?, ?)",
            (name, age, diagnosis_date, strengths, challenges)
        )
        conn.commit()
        conn.close()
        st.success("Çocuk başarıyla eklendi!")
    except Exception as e:
        st.error(f"Çocuk eklenirken hata oluştu: {e}")

def child_profile():
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            /* Başlık ve alt başlık stilleri */
            h2, h3 {
                color: #263859;
            }
            /* Genişletilebilir alan (Expander) başlıkları için stil */
            .st-emotion-cache-163k6s4 > div > div > p {
                font-size: 1.1em;
                font-weight: bold;
                color: #263859;
            }
            /* Genel ikon stilleri */
            .fas, .fa-plus-circle, .fa-user-plus {
                margin-right: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
        
    st.markdown("## <i class='fas fa-users'></i> Çocuk Profilleri", unsafe_allow_html=True)
    with st.expander("Yeni Çocuk Ekle", expanded=False):
        with st.form("add_child_form"):
            name = st.text_input("Ad Soyad", max_chars=100)
            age = st.number_input("Yaş", min_value=1, max_value=30, step=1)
            diagnosis_date = st.date_input("Tanı Tarihi")
            strengths = st.text_area("Güçlü Yönler", max_chars=250)
            challenges = st.text_area("Zorluklar", max_chars=250)
            submitted = st.form_submit_button("Ekle")
            if submitted:
                if not name.strip():
                    st.warning("İsim alanı zorunludur.")
                else:
                    add_child(name, age, str(diagnosis_date), strengths, challenges)
    st.markdown("---")
    st.markdown("### <i class='fas fa-user-check'></i> Kayıtlı Çocuklar", unsafe_allow_html=True)
    df = get_children()
    
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("Henüz çocuk kaydı yok.")