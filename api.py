import sqlite3
from flask import Flask, request, jsonify
import threading
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_PATH = 'autism_tracking.db'
SECRET_KEY = 'supersecretkey'  # Bunu production'da gizli tut!

# SMTP ayarlarını ortam değişkenlerinden oku (güvenlik için .env dosyası önerilir)
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', 'your_gmail@gmail.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'your_app_password')

api_app = Flask(__name__)
CORS(api_app)
api_app.config['SECRET_KEY'] = SECRET_KEY

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_user_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'ebeveyn', 'uzman'))
    )''')
    conn.commit()
    conn.close()

init_user_table()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[-1]
        if not token:
            return jsonify({'message': 'Token gerekli!'}), 401
        try:
            data = jwt.decode(token, api_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['email']
            current_role = data['role']
        except Exception as e:
            return jsonify({'message': 'Token geçersiz!', 'error': str(e)}), 401
        return f(current_user, current_role, *args, **kwargs)
    return decorated

@api_app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    if not email or not password or not role:
        return jsonify({'error': 'Eksik bilgi'}), 400
    if role not in ['admin', 'ebeveyn', 'uzman']:
        return jsonify({'error': 'Geçersiz rol'}), 400
    password_hash = generate_password_hash(password)
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)', (email, password_hash, role))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Kullanıcı kaydedildi!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Bu e-posta zaten kayıtlı!'}), 409

@api_app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Eksik bilgi'}), 400
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        token = jwt.encode({
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, api_app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token, 'role': user['role']}), 200
    else:
        return jsonify({'error': 'Geçersiz e-posta veya şifre!'}), 401

# Örnek: Sadece adminlerin erişebileceği bir endpoint
@api_app.route('/api/admin-only', methods=['GET'])
@token_required
def admin_only(current_user, current_role):
    if current_role != 'admin':
        return jsonify({'error': 'Yetkisiz!'}), 403
    return jsonify({'message': f'Hoşgeldin admin {current_user}!'}), 200

# Var olan çocuk endpointleri aşağıda
@api_app.route('/api/children', methods=['GET'])
@token_required
def list_children(current_user, current_role):
    conn = get_db_connection()
    children = conn.execute('SELECT * FROM children').fetchall()
    conn.close()
    return jsonify([dict(row) for row in children])

@api_app.route('/api/children', methods=['POST'])
@token_required
def add_child(current_user, current_role):
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    diagnosis = data.get('diagnosis')
    if not name or not age or not diagnosis:
        return jsonify({'error': 'Eksik bilgi'}), 400
    conn = get_db_connection()
    conn.execute('INSERT INTO children (name, age, diagnosis) VALUES (?, ?, ?)', (name, age, diagnosis))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Çocuk profili eklendi'}), 201

@api_app.route('/api/send-recommendation-mail', methods=['POST'])
@token_required
def send_recommendation_mail(current_user, current_role):
    data = request.get_json()
    recommendation = data.get('recommendation')
    if not recommendation:
        return jsonify({'error': 'Öneri metni eksik!'}), 400
    # Kullanıcının e-posta adresini JWT'den alıyoruz (current_user)
    to_email = current_user
    subject = 'AI Gelişim ve Etkinlik Öneriniz'
    body = f"Merhaba,\n\nİşte sizin için oluşturulan AI önerisi:\n\n{recommendation}\n\nSevgilerle, Otizm Takip Sistemi"
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        return jsonify({'message': 'Öneri e-posta ile gönderildi!'}), 200
    except Exception as e:
        return jsonify({'error': f'Mail gönderilemedi: {e}'}), 500

if __name__ == '__main__':
    api_app.run(host='0.0.0.0', port=5000) 