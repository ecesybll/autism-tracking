import sqlite3
from config.settings import DB_PATH

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # children
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                diagnosis_date TEXT,
                strengths TEXT,
                challenges TEXT
            )
        ''')
        # behaviors
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER,
                behavior_type TEXT,
                frequency INTEGER,
                triggers TEXT,
                context TEXT,
                date TEXT,
                FOREIGN KEY(child_id) REFERENCES children(id)
            )
        ''')
        # interests
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER,
                interest_type TEXT,
                intensity INTEGER,
                duration INTEGER,
                impact TEXT,
                FOREIGN KEY(child_id) REFERENCES children(id)
            )
        ''')
        # assessments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER,
                assessment_type TEXT,
                results TEXT,
                date TEXT,
                notes TEXT,
                FOREIGN KEY(child_id) REFERENCES children(id)
            )
        ''')
        # progress_records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER,
                metric TEXT,
                value REAL,
                date TEXT,
                notes TEXT,
                FOREIGN KEY(child_id) REFERENCES children(id)
            )
        ''')
        # recommendations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER,
                recommendation_type TEXT,
                content TEXT,
                ai_generated BOOLEAN,
                FOREIGN KEY(child_id) REFERENCES children(id)
            )
        ''')
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database initialization failed: {e}")
    finally:
        conn.close()