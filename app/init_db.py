#!/usr/bin/env python3
"""
Скрипт для инициализации БД и добавления тестовых данных
"""
import uuid
from database import init_db, add_error

def add_test_data():
    """Добавляет тестовую запись в БД"""
    
    # Инициализируем БД
    print("Инициализация БД...")
    init_db()
    print("БД инициализирована!")
    
    # Тестовая запись
    test_error = {
        'uuid': str(uuid.uuid4()),
        'error': 'TestError',
        'description': 'Тестовая ошибка для проверки работы системы поиска.',
        'solution': 'Это тестовая запись. Замените её на реальные данные об ошибках.',
        'tickets': [],
        'tasks': []
    }
    
    # Добавляем тестовую запись
    print("\nДобавление тестовой записи...")
    if add_error(test_error):
        print(f"✓ Добавлена тестовая ошибка: {test_error['error']}")
    else:
        print(f"✗ Ошибка при добавлении тестовой записи")
    
    print("\nГотово! Тестовая запись добавлена.")

if __name__ == '__main__':
    add_test_data()

