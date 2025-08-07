import streamlit as st

def analyze_interest(activity_data: str) -> str:
    prompt = f"""
Çocuğun aktivite ve etkileşim verilerinden ilgi alanlarını tespit et:
- Güçlü ilgi alanları
- Gelişim potansiyeli
- Önerilen aktiviteler

Veri: {activity_data}
"""
    try:
        # AI kütüphanesini sadece gerektiğinde yükle
        from config.gemini_config import configure_gemini
        model = configure_gemini()
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        # Hata mesajını log'la ama kullanıcıya gösterme
        print(f"AI analiz hatası: {e}")
        
        # Demo yanıtı döndür
        return f"""
🔍 **AI Analiz Sonucu (Demo Modu)**

**Girilen Veri:** {activity_data[:200]}...

**Güçlü İlgi Alanları:**
- Görsel algı ve renk tanıma
- Yapılandırılmış aktiviteler
- Tekrarlayan oyunlar

**Gelişim Potansiyeli:**
- Sosyal etkileşim becerileri
- İletişim ve dil gelişimi
- Motor beceriler

**Önerilen Aktiviteler:**
1. **Puzzle ve Yapbozlar:** Görsel algıyı geliştirir
2. **Renkli Bloklar:** El-göz koordinasyonunu artırır
3. **Müzik Terapisi:** Sakinleştirici etki yapar
4. **Resim Sanatı:** Yaratıcılığı destekler
5. **Sosyal Oyunlar:** İletişim becerilerini geliştirir

**Not:** Bu demo yanıtıdır. Gerçek AI analizi için Gemini API anahtarını ayarlayın.
"""

def generate_recommendation(child_name: str, age: str, strengths: str, challenges: str, extra_notes: str = "") -> str:
    prompt = f"""
{child_name} için kişiselleştirilmiş öneriler oluştur:

**Çocuk Bilgileri:**
- İsim: {child_name}
- Yaş: {age}
- Güçlü Yönler: {strengths}
- Gelişim Alanları: {challenges}
- Ek Notlar: {extra_notes}

**İstenen:**
- Yaşa uygun aktiviteler
- Güçlü yönleri destekleyen öneriler
- Gelişim alanlarını iyileştiren etkinlikler
- Pratik uygulama önerileri
"""
    try:
        # AI kütüphanesini sadece gerektiğinde yükle
        from config.gemini_config import configure_gemini
        model = configure_gemini()
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        # Hata mesajını log'la ama kullanıcıya gösterme
        print(f"AI öneri hatası: {e}")
        
        # Demo yanıtı döndür
        return f"""
🎯 **Kişiselleştirilmiş Öneriler (Demo Modu)**

**Çocuk:** {child_name} ({age} yaşında)

**Güçlü Yönler:** {strengths}
**Gelişim Alanları:** {challenges}

**Önerilen Aktiviteler:**

1. **Görsel Algı Geliştirme:**
   - Renkli puzzle'lar
   - Şekil eşleştirme oyunları
   - Görsel hafıza kartları

2. **Motor Beceriler:**
   - İnce motor: Boncuk dizme, boyama
   - Kaba motor: Dans, koordinasyon oyunları

3. **Sosyal Beceriler:**
   - Sıra alma oyunları
   - Grup aktiviteleri
   - İletişim oyunları

4. **Dikkat ve Odaklanma:**
   - Konsantrasyon oyunları
   - Dikkat süresini artıran aktiviteler

**Pratik Uygulama:**
- Günde 15-20 dakika düzenli aktivite
- Çocuğun ilgi alanlarına göre uyarlama
- Sabırlı ve destekleyici yaklaşım

**Not:** Bu demo yanıtıdır. Gerçek AI önerileri için Gemini API anahtarını ayarlayın.
"""