import os

def configure_gemini():
    """Gemini AI modelini yapılandırır - lazy loading ile"""
    try:
        import google.generativeai as genai
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "*")
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        print(f"Gemini yapılandırma hatası: {e}")
        return None
