
import sqlite3
from datetime import datetime

def init_db():
    """Создает таблицы в базе данных, если их нет"""
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    
    # Таблица для хранения запросов к специалистам
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_name TEXT,
            department TEXT,
            question TEXT,
            status TEXT DEFAULT 'новый',
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных инициализирована")

def add_request(user_id, user_name, department, question):
    """Добавляет новый запрос от пользователя"""
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO requests (user_id, user_name, department, question, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, user_name, department, question, 'новый', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()

def get_all_requests():
    """Получает все запросы (для администратора)"""
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM requests ORDER BY created_at DESC')
    requests = cursor.fetchall()
    
    conn.close()
    return requests

def update_request_status(request_id, new_status):
    """Обновляет статус запроса"""
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE requests SET status = ? WHERE id = ?', (new_status, request_id))
    
    conn.commit()
    conn.close()

def get_requests_by_department(department):
    """Получает запросы по отделу"""
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM requests WHERE department = ? ORDER BY created_at DESC', (department,))
    requests = cursor.fetchall()
    
    conn.close()
    return requests