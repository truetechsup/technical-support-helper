import sqlite3
import json
import os
from typing import List, Dict, Optional

DB_PATH = '/app/data/errors.db'

def get_db_connection():
    """Создает и возвращает соединение с БД"""
    # Создаем директорию для БД если её нет
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
    return conn

def init_db():
    """Инициализирует БД и создает таблицу если её нет"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS errors (
            uuid TEXT PRIMARY KEY,
            error TEXT NOT NULL,
            description TEXT,
            solution TEXT,
            tickets TEXT,
            tasks TEXT
        )
    ''')
    
    # Создаем индекс для быстрого поиска
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_error ON errors(error)
    ''')
    
    conn.commit()
    conn.close()

def search_errors(query: str) -> List[Dict]:
    """Ищет ошибки по тексту (без учета регистра)"""
    if not query or not query.strip():
        return []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Поиск без учета регистра
    search_pattern = f'%{query.strip()}%'
    cursor.execute('''
        SELECT uuid, error, description, solution, tickets, tasks
        FROM errors
        WHERE LOWER(error) LIKE LOWER(?)
        ORDER BY error
    ''', (search_pattern,))
    
    results = []
    for row in cursor.fetchall():
        # Парсим JSON поля если они есть
        tickets = []
        tasks = []
        
        if row['tickets']:
            try:
                tickets = json.loads(row['tickets'])
            except:
                tickets = []
        
        if row['tasks']:
            try:
                tasks = json.loads(row['tasks'])
            except:
                tasks = []
        
        results.append({
            'uuid': row['uuid'],
            'error': row['error'],
            'description': row['description'] or '',
            'solution': row['solution'] or '',
            'tickets': tickets,
            'tasks': tasks
        })
    
    conn.close()
    return results

def get_error_by_uuid(uuid: str) -> Optional[Dict]:
    """Получает ошибку по UUID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT uuid, error, description, solution, tickets, tasks
        FROM errors
        WHERE uuid = ?
    ''', (uuid,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    tickets = []
    tasks = []
    
    if row['tickets']:
        try:
            tickets = json.loads(row['tickets'])
        except:
            tickets = []
    
    if row['tasks']:
        try:
            tasks = json.loads(row['tasks'])
        except:
            tasks = []
    
    return {
        'uuid': row['uuid'],
        'error': row['error'],
        'description': row['description'] or '',
        'solution': row['solution'] or '',
        'tickets': tickets,
        'tasks': tasks
    }

def add_error(error_data: Dict) -> bool:
    """Добавляет новую ошибку в БД"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Конвертируем списки в JSON
        tickets_json = json.dumps(error_data.get('tickets', []))
        tasks_json = json.dumps(error_data.get('tasks', []))
        
        cursor.execute('''
            INSERT INTO errors (uuid, error, description, solution, tickets, tasks)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            error_data.get('uuid'),
            error_data.get('error'),
            error_data.get('description', ''),
            error_data.get('solution', ''),
            tickets_json,
            tasks_json
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка при добавлении: {e}")
        return False

