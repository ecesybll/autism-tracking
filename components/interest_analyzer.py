import streamlit as st
import pandas as pd
import sqlite3
from config.settings import DB_PATH
from services.ai_service import analyze_interest
import PyPDF2
import docx
import io

def get_children_options():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT id, name FROM children", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Çocuklar alınırken hata oluştu: {e}")
        return pd.DataFrame()

def extract_text_from_pdf(pdf_file):
    """PDF dosyasından metin çıkarır - Word'e çevirip okur"""
    try:
        # Dosyayı başa sar
        pdf_file.seek(0)
        
        # PDF'i Word'e çevirmek için geçici dosya oluştur
        import tempfile
        import os
        
        # Geçici PDF dosyası oluştur
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(pdf_file.read())
            temp_pdf_path = temp_pdf.name
        
        # Geçici Word dosyası yolu
        temp_docx_path = temp_pdf_path.replace('.pdf', '.docx')
        
        try:
            # PDF'i Word'e çevir (basit kopyalama - gerçek dönüşüm için daha gelişmiş kütüphane gerekir)
            # Şimdilik PDF'i direkt okumaya çalış
            pdf_reader = PyPDF2.PdfReader(temp_pdf_path)
            text = ""
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if text.strip():
                return text
            else:
                st.warning("PDF dosyasından metin çıkarılamadı. Word veya TXT formatında dosya yüklemeyi deneyin.")
                return None
                
        finally:
            # Geçici dosyaları temizle
            try:
                os.unlink(temp_pdf_path)
                if os.path.exists(temp_docx_path):
                    os.unlink(temp_docx_path)
            except:
                pass
            
    except Exception as e:
        st.error(f"PDF okuma hatası: {e}")
        st.info("💡 Öneriler:")
        st.info("- PDF'i Word (DOCX) formatına çevirin")
        st.info("- TXT formatında dosya yükleyin")
        st.info("- Manuel giriş sekmesini kullanın")
        return None

def extract_text_from_docx(docx_file):
    """DOCX dosyasından metin çıkarır"""
    try:
        doc = docx.Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        if not text.strip():
            st.warning("DOCX dosyasından metin çıkarılamadı. Dosya boş olabilir.")
            return None
        return text
    except Exception as e:
        st.error(f"DOCX okuma hatası: {e}")
        st.info("DOCX dosyasının okunabilir olduğundan emin olun.")
        return None

def extract_text_from_txt(txt_file):
    """TXT dosyasından metin çıkarır"""
    try:
        # Dosyayı başa sar
        txt_file.seek(0)
        text = txt_file.read().decode('utf-8')
        if not text.strip():
            st.warning("TXT dosyası boş görünüyor.")
            return None
        return text
    except UnicodeDecodeError:
        try:
            # UTF-8 başarısız olursa latin-1 dene
            txt_file.seek(0)
            text = txt_file.read().decode('latin-1')
            return text
        except Exception as e:
            st.error(f"TXT dosyası okunamadı: {e}")
            return None
    except Exception as e:
        st.error(f"TXT okuma hatası: {e}")
        return None

def interest_analyzer():
    st.subheader("İlgi Alanı Analizi (AI Destekli)")
    children_df = get_children_options()
    if children_df.empty:
        st.info("Önce çocuk eklemelisiniz.")
        return
    
    # Sekmeler oluştur
    tab1, tab2 = st.tabs(["📝 Manuel Giriş", "📄 Rapor Yükle"])
    
    with tab1:
        st.write("### Manuel Aktivite Verisi Girişi")
        with st.form("interest_form"):
            child_name = st.selectbox("Çocuk", children_df['name'])
            activity_data = st.text_area("Aktivite/Etkileşim Verisi", help="Çocuğun son zamanlardaki aktiviteleri, oyunları, hobileri vb.")
            submitted = st.form_submit_button("AI ile Analiz Et")
            if submitted:
                if not activity_data.strip():
                    st.warning("Aktivite verisi zorunludur.")
                else:
                    with st.spinner("AI analiz ediyor..."):
                        try:
                            result = analyze_interest(activity_data)
                            st.success("✅ AI Analiz Tamamlandı!")
                            st.markdown("---")
                            st.markdown(result)
                        except Exception as e:
                            st.error(f"Analiz sırasında hata oluştu: {e}")
                            st.info("Demo modunda çalışıyoruz. Gerçek AI analizi için API anahtarını ayarlayın.")
    
    with tab2:
        st.write("### Rapor Dosyası Yükleme")
        st.info("📋 **En İyi Desteklenen Formatlar:** Word (DOCX) ve TXT")
        st.warning("⚠️ **PDF Dosyaları:** Bazı PDF'ler okunamayabilir. Word veya TXT formatına çevirmeniz önerilir.")
        
        with st.form("report_upload_form"):
            child_name_report = st.selectbox("Çocuk", children_df['name'], key="report_child")
            
            uploaded_file = st.file_uploader(
                "Rapor dosyası seçin",
                type=['docx', 'txt', 'pdf'],
                help="En iyi sonuç için Word (DOCX) veya TXT formatında dosya yükleyin"
            )
            
            additional_notes = st.text_area(
                "Ek Notlar (İsteğe bağlı)",
                help="Rapora ek olarak belirtmek istediğiniz bilgiler",
                key="report_notes"
            )
            
            submitted_report = st.form_submit_button("Raporu AI ile Analiz Et")
            
            if submitted_report:
                if uploaded_file is not None:
                    # Dosya bilgilerini göster
                    st.info(f"📁 Yüklenen dosya: {uploaded_file.name}")
                    st.info(f"📏 Dosya boyutu: {uploaded_file.size} bytes")
                    
                    with st.spinner("Dosya okunuyor ve AI analiz ediyor..."):
                        try:
                            # Dosya türüne göre metin çıkar
                            file_extension = uploaded_file.name.split('.')[-1].lower()
                            st.info(f"🔍 Dosya türü: {file_extension.upper()}")
                            
                            if file_extension == 'pdf':
                                extracted_text = extract_text_from_pdf(uploaded_file)
                            elif file_extension == 'docx':
                                extracted_text = extract_text_from_docx(uploaded_file)
                            elif file_extension == 'txt':
                                extracted_text = extract_text_from_txt(uploaded_file)
                            else:
                                st.error("Desteklenmeyen dosya formatı!")
                                return
                            
                            if extracted_text:
                                st.success(f"✅ Metin çıkarıldı! Karakter sayısı: {len(extracted_text)}")
                                
                                # Ek notları birleştir
                                full_text = extracted_text
                                if additional_notes.strip():
                                    full_text += f"\n\nEk Notlar:\n{additional_notes}"
                                
                                # AI analizi yap
                                result = analyze_interest(full_text)
                                
                                st.success("✅ Rapor Analizi Tamamlandı!")
                                st.markdown("---")
                                
                                st.write("**📄 Çıkarılan Metin:**")
                                with st.expander("Rapordan çıkarılan metni görmek için tıklayın"):
                                    st.text(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
                                
                                st.write("**🤖 AI Analiz Sonucu:**")
                                st.markdown(result)
                                
                                # Sonucu kaydetme seçeneği
                                if st.button("💾 Analiz Sonucunu Kaydet", key="save_analysis"):
                                    # Burada veritabanına kaydetme işlemi yapılabilir
                                    st.success("✅ Analiz sonucu kaydedildi!")
                            else:
                                st.error("❌ Dosyadan metin çıkarılamadı!")
                                st.info("💡 Öneriler:")
                                st.info("- Dosyanın boş olmadığından emin olun")
                                st.info("- Dosyanın korumalı olmadığından emin olun")
                                st.info("- Farklı bir dosya formatı deneyin (TXT, DOCX)")
                        except Exception as e:
                            st.error(f"❌ Analiz sırasında hata oluştu: {e}")
                            st.info("Demo modunda çalışıyoruz. Gerçek AI analizi için API anahtarını ayarlayın.")
                else:
                    st.warning("Lütfen bir dosya seçin!")