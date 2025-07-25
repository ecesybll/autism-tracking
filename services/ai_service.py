from config.gemini_config import configure_gemini

def analyze_interest(activity_data: str) -> str:
    prompt = f"""
Çocuğun aktivite ve etkileşim verilerinden ilgi alanlarını tespit et:
- Güçlü ilgi alanları
- Gelişim potansiyeli
- Önerilen aktiviteler

Veri: {activity_data}
"""
    try:
        model = configure_gemini()
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        return f"AI analizinde hata oluştu: {e}"

def generate_recommendation(child_name: str, age: int, strengths: str = "", challenges: str = "", extra_notes: str = "") -> str:
    prompt = f"""
Çocuğa özel gelişim ve etkinlik önerileri üret:
- Çocuğun adı: {child_name}
- Yaşı: {age}
- Güçlü yönleri: {strengths}
- Zorlukları: {challenges}
- Ek bilgiler: {extra_notes}

Kısa, uygulanabilir ve kişiselleştirilmiş öneriler sun.
"""
    try:
        model = configure_gemini()
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        return f"AI öneri üretiminde hata oluştu: {e}"