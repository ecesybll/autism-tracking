from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_test_pdf():
    # PDF dosyası oluştur
    c = canvas.Canvas("test_rapor.pdf", pagesize=letter)
    width, height = letter
    
    # Başlık
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "ÇOCUK GÖZLEM RAPORU")
    
    # Alt başlık
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, "Çocuk Adı: Test Çocuk")
    c.drawString(50, height - 100, "Yaş: 8")
    c.drawString(50, height - 120, "Tarih: 2024-08-07")
    
    # Gözlem notları
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 160, "GÖZLEM NOTLARI:")
    
    c.setFont("Helvetica", 10)
    observations = [
        "• Çocuk puzzle yapmaya çok ilgi gösteriyor",
        "• Renkli bloklarla oynamayı seviyor",
        "• Müzik dinlerken sakinleşiyor",
        "• Resim yapmaya ilgi duyuyor",
        "• Sosyal etkileşimde biraz çekingen"
    ]
    
    y_position = height - 180
    for obs in observations:
        c.drawString(50, y_position, obs)
        y_position -= 20
    
    # Güçlü yönler
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position - 20, "GÜÇLÜ YÖNLER:")
    
    c.setFont("Helvetica", 10)
    strengths = [
        "• Görsel algı yeteneği yüksek",
        "• Dikkat süresi uzun",
        "• El-göz koordinasyonu iyi"
    ]
    
    y_position -= 40
    for strength in strengths:
        c.drawString(50, y_position, strength)
        y_position -= 20
    
    # Gelişim alanları
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position - 20, "GELİŞİM ALANLARI:")
    
    c.setFont("Helvetica", 10)
    areas = [
        "• Sosyal beceriler geliştirilebilir",
        "• İletişim becerileri desteklenebilir"
    ]
    
    y_position -= 40
    for area in areas:
        c.drawString(50, y_position, area)
        y_position -= 20
    
    # Öneriler
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position - 20, "ÖNERİLER:")
    
    c.setFont("Helvetica", 10)
    recommendations = [
        "• Puzzle aktiviteleri artırılabilir",
        "• Müzik terapisi denenebilir",
        "• Resim sanatı etkinlikleri planlanabilir"
    ]
    
    y_position -= 40
    for rec in recommendations:
        c.drawString(50, y_position, rec)
        y_position -= 20
    
    c.save()
    print("test_rapor.pdf dosyası oluşturuldu!")

if __name__ == "__main__":
    create_test_pdf()
