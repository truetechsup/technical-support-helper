#!/usr/bin/env python3
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from database import search_errors, init_db, add_error, delete_error, get_all_errors
import uuid

class APIHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP запросов для API"""
    
    def do_OPTIONS(self):
        """Обработка CORS preflight запросов"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/api/search':
            self.handle_search()
        elif self.path == '/api/add':
            self.handle_add()
        elif self.path == '/api/delete':
            self.handle_delete()
        else:
            self.send_error(404)
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        elif self.path == '/api/all':
            self.handle_get_all()
        elif self.path == '/add' or self.path == '/add.html':
            self.send_static_file('add.html')
        elif self.path == '/' or self.path == '/index.html':
            self.send_static_file('index.html')
        else:
            self.send_error(404)
    
    def send_static_file(self, filename):
        """Отправляет статический HTML файл"""
        try:
            file_path = f'/app/templates/{filename}'
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404)
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            self.send_error(500)
    
    def handle_search(self):
        """Обработка запроса поиска"""
        try:
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Парсим JSON
            data = json.loads(post_data.decode('utf-8'))
            query = data.get('query', '').strip()
            
            if not query:
                self.send_json_response({'results': []}, 200)
                return
            
            # Ищем ошибки
            results = search_errors(query)
            
            # Отправляем ответ
            self.send_json_response({'results': results}, 200)
            
        except json.JSONDecodeError:
            self.send_json_response({'error': 'Invalid JSON'}, 400)
        except Exception as e:
            print(f"Ошибка при обработке запроса: {e}")
            self.send_json_response({'error': 'Internal server error'}, 500)
    
    def handle_add(self):
        """Обработка запроса на добавление ошибки"""
        try:
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Парсим JSON
            data = json.loads(post_data.decode('utf-8'))
            
            # Валидация обязательных полей
            error_text = data.get('error', '').strip()
            description = data.get('description', '').strip()
            
            if not error_text or not description:
                self.send_json_response({'success': False, 'error': 'Поля "Ошибка" и "Описание" обязательны'}, 400)
                return
            
            # Формируем данные для БД
            error_data = {
                'uuid': str(uuid.uuid4()),
                'error': error_text,
                'description': description,
                'solution': data.get('solution', '').strip(),
                'tickets': data.get('tickets', []),
                'tasks': data.get('tasks', [])
            }
            
            # Добавляем в БД
            if add_error(error_data):
                self.send_json_response({'success': True, 'message': 'Ошибка успешно добавлена'}, 200)
            else:
                self.send_json_response({'success': False, 'error': 'Не удалось добавить ошибку в БД'}, 500)
            
        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'error': 'Invalid JSON'}, 400)
        except Exception as e:
            print(f"Ошибка при добавлении: {e}")
            self.send_json_response({'success': False, 'error': 'Internal server error'}, 500)
    
    def handle_delete(self):
        """Обработка запроса на удаление ошибки"""
        try:
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Парсим JSON
            data = json.loads(post_data.decode('utf-8'))
            uuid = data.get('uuid', '').strip()
            
            if not uuid:
                self.send_json_response({'success': False, 'error': 'UUID не указан'}, 400)
                return
            
            # Удаляем из БД
            if delete_error(uuid):
                self.send_json_response({'success': True, 'message': 'Ошибка успешно удалена'}, 200)
            else:
                self.send_json_response({'success': False, 'error': 'Ошибка не найдена или не удалось удалить'}, 404)
            
        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'error': 'Invalid JSON'}, 400)
        except Exception as e:
            print(f"Ошибка при удалении: {e}")
            self.send_json_response({'success': False, 'error': 'Internal server error'}, 500)
    
    def handle_get_all(self):
        """Обработка запроса на получение всех ошибок"""
        try:
            results = get_all_errors()
            self.send_json_response({'results': results}, 200)
        except Exception as e:
            print(f"Ошибка при получении всех ошибок: {e}")
            self.send_json_response({'error': 'Internal server error'}, 500)
    
    def send_json_response(self, data, status_code=200):
        """Отправляет JSON ответ"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Отключаем стандартное логирование для чистоты"""
        pass

def run_server(port=8000):
    """Запускает HTTP сервер"""
    from database import is_db_empty
    from init_db import add_test_data
    
    # Инициализируем БД при старте (создает таблицы если нужно)
    init_db()
    
    # Если БД пустая, добавляем тестовые данные
    if is_db_empty():
        print("База данных пустая, инициализация тестовыми данными...")
        add_test_data()
        print("Тестовые данные добавлены!")
    
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, APIHandler)
    print(f'Python API сервер запущен на порту {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()

