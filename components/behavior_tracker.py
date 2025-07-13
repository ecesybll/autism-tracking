import streamlit as st
import pandas as pd
import sqlite3
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

def get_behaviors():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM behaviors", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Davranışlar alınırken hata oluştu: {e}")
        return pd.DataFrame()

def add_behavior(child_id: int, behavior_type: str, frequency: int, triggers: str, context: str, date: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO behaviors (child_id, behavior_type, frequency, triggers, context, date) VALUES (?, ?, ?, ?, ?, ?)",
            (child_id, behavior_type, frequency, triggers, context, date)
        )
        conn.commit()
        conn.close()
        st.success("Davranış kaydı eklendi!")
    except Exception as e:
        st.error(f"Davranış eklenirken hata oluştu: {e}")

def behavior_tracker():
    st.subheader("Davranış Takibi")
    with st.expander("Yeni Davranış Kaydı", expanded=False):
        children_df = get_children_options()
        if children_df.empty:
            st.info("Önce çocuk eklemelisiniz.")
        else:
            with st.form("add_behavior_form"):
                child_name = st.selectbox("Çocuk", children_df['name'])
                child_id = int(children_df[children_df['name'] == child_name]['id'].values[0])
                behavior_type = st.text_input("Davranış Türü", max_chars=100)
                frequency = st.number_input("Frekans", min_value=1, max_value=100, step=1)
                triggers = st.text_area("Tetikleyiciler", max_chars=200)
                context = st.text_area("Bağlam", max_chars=200)
                date = st.date_input("Tarih")
                submitted = st.form_submit_button("Kaydet")
                if submitted:
                    if not behavior_type.strip():
                        st.warning("Davranış türü zorunludur.")
                    else:
                        add_behavior(child_id, behavior_type, frequency, triggers, context, str(date))
    st.markdown("---")
    st.write("### Davranış Kayıtları")
    df = get_behaviors()
    if not df.empty:
        st.dataframe(df)
        st.markdown("---")
        st.write("#### Davranış Türü Dağılımı")
        summary = df.groupby('behavior_type')['frequency'].sum().reset_index()
        st.bar_chart(summary.set_index('behavior_type'))
    else:
        st.info("Henüz davranış kaydı yok.")