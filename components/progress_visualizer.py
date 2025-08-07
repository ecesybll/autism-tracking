import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
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

def save_progress_record(child_id, metric, value, date, notes):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            INSERT INTO progress_records (child_id, metric, value, date, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (child_id, metric, value, date, notes))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"İlerleme kaydedilirken hata oluştu: {e}")
        return False

def progress_visualizer():
    st.subheader("📊 İlerleme Raporları ve Grafikler")
    
    children_df = get_children_options()
    if children_df.empty:
        st.info("Önce çocuk eklemelisiniz.")
        return
    
    # Sekmeler oluştur
    tab1, tab2, tab3 = st.tabs(["📝 Veri Girişi", "📈 Grafikler", "📋 Raporlar"])
    
    with tab1:
        st.write("### İlerleme Verisi Girişi")
        
        with st.form("progress_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                child_name = st.selectbox("Çocuk Seç", children_df['name'])
                metric = st.selectbox("Metrik Türü", [
                    "Sosyal Beceriler",
                    "İletişim Becerileri", 
                    "Motor Beceriler",
                    "Dikkat Süresi",
                    "Davranış Kontrolü",
                    "Öğrenme Becerileri",
                    "Duygusal Düzenleme",
                    "Oyun Becerileri"
                ])
            
            with col2:
                value = st.slider("Puan (0-100)", 0, 100, 50, help="0: Çok zayıf, 100: Mükemmel")
                date = st.date_input("Tarih", value=datetime.now().date())
            
            notes = st.text_area("Notlar (İsteğe bağlı)", help="Gözlemlerinizi ve detayları yazın")
            
            submitted = st.form_submit_button("💾 İlerleme Kaydet")
            
            if submitted:
                child_id = int(children_df[children_df['name'] == child_name]['id'].values[0])
                if save_progress_record(child_id, metric, value, date.strftime('%Y-%m-%d'), notes):
                    st.success("✅ İlerleme verisi başarıyla kaydedildi!")
                    st.rerun()
    
    with tab2:
        st.write("### Gelişim Grafikleri")
        
        child_name_graph = st.selectbox("Çocuk Seç", children_df['name'], key="graph_child_select")
        child_id_graph = int(children_df[children_df['name'] == child_name_graph]['id'].values[0])
        df = get_progress(child_id_graph)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.sort_values('date')
            
            # Grafik türü seçimi
            chart_type = st.selectbox("Grafik Türü", [
                "Çizgi Grafik (Zaman Serisi)",
                "Çubuk Grafik (Metrik Karşılaştırması)",
                "Radar Grafik (Güncel Durum)",
                "Isı Haritası (Metrik-Zaman)"
            ], key="chart_type_select")
            
            if chart_type == "Çizgi Grafik (Zaman Serisi)":
                fig = px.line(df, x='date', y='value', color='metric', 
                            title=f'{child_name_graph} - Zaman İçinde Gelişim',
                            labels={'value': 'Puan', 'date': 'Tarih', 'metric': 'Metrik'})
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
            elif chart_type == "Çubuk Grafik (Metrik Karşılaştırması)":
                # En son değerleri al
                latest_data = df.loc[df.groupby('metric')['date'].idxmax()]
                fig = px.bar(latest_data, x='metric', y='value', 
                           title=f'{child_name_graph} - Güncel Metrik Durumu',
                           labels={'value': 'Puan', 'metric': 'Metrik'})
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
            elif chart_type == "Radar Grafik (Güncel Durum)":
                # En son değerleri al
                latest_data = df.loc[df.groupby('metric')['date'].idxmax()]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=latest_data['value'].tolist(),
                    theta=latest_data['metric'].tolist(),
                    fill='toself',
                    name=child_name_graph
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    title=f'{child_name_graph} - Radar Grafik (Güncel Durum)',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
            elif chart_type == "Isı Haritası (Metrik-Zaman)":
                # Pivot tablo oluştur
                pivot_df = df.pivot(index='date', columns='metric', values='value')
                fig = px.imshow(pivot_df.T, 
                              title=f'{child_name_graph} - Metrik-Zaman Isı Haritası',
                              labels=dict(x="Tarih", y="Metrik", color="Puan"))
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            # Veri tablosu
            st.write("### 📋 Ham Veri")
            st.dataframe(df, use_container_width=True)
            
        else:
            st.info("Seçili çocuk için ilerleme verisi yok. Önce 'Veri Girişi' sekmesinden veri ekleyin.")
    
    with tab3:
        st.write("### 📋 İlerleme Raporları")
        
        child_name_report = st.selectbox("Çocuk Seç", children_df['name'], key="report_child_select")
        child_id_report = int(children_df[children_df['name'] == child_name_report]['id'].values[0])
        df_report = get_progress(child_id_report)
        
        if not df_report.empty:
            df_report['date'] = pd.to_datetime(df_report['date'], errors='coerce')
            df_report = df_report.sort_values('date')
            
            # Özet istatistikler
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Toplam Kayıt", len(df_report))
            
            with col2:
                avg_score = df_report['value'].mean()
                st.metric("Ortalama Puan", f"{avg_score:.1f}")
            
            with col3:
                max_score = df_report['value'].max()
                st.metric("En Yüksek Puan", f"{max_score:.0f}")
            
            with col4:
                min_score = df_report['value'].min()
                st.metric("En Düşük Puan", f"{min_score:.0f}")
            
            st.markdown("---")
            
            # Metrik bazlı analiz
            st.write("### 📊 Metrik Bazlı Analiz")
            
            for metric in df_report['metric'].unique():
                metric_data = df_report[df_report['metric'] == metric]
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig = px.line(metric_data, x='date', y='value',
                                title=f"{metric} - Gelişim Trendi",
                                labels={'value': 'Puan', 'date': 'Tarih'})
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.write(f"**{metric} İstatistikleri:**")
                    st.write(f"• Ortalama: {metric_data['value'].mean():.1f}")
                    st.write(f"• En Yüksek: {metric_data['value'].max():.0f}")
                    st.write(f"• En Düşük: {metric_data['value'].min():.0f}")
                    st.write(f"• Kayıt Sayısı: {len(metric_data)}")
                    
                    # Trend analizi
                    if len(metric_data) > 1:
                        first_value = metric_data.iloc[0]['value']
                        last_value = metric_data.iloc[-1]['value']
                        change = last_value - first_value
                        
                        if change > 0:
                            st.success(f"📈 İyileşme: +{change:.1f} puan")
                        elif change < 0:
                            st.error(f"📉 Düşüş: {change:.1f} puan")
                        else:
                            st.info("➡️ Değişim yok")
                
                st.markdown("---")
            
            # Son kayıtlar
            st.write("### 📝 Son Kayıtlar")
            recent_data = df_report.tail(10)
            st.dataframe(recent_data[['date', 'metric', 'value', 'notes']], use_container_width=True)
            
        else:
            st.info("Seçili çocuk için ilerleme verisi yok. Önce 'Veri Girişi' sekmesinden veri ekleyin.")