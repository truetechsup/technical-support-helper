#!/usr/bin/env python3
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from database import search_errors, init_db

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
        else:
            self.send_error(404)
    
    def do_GET(self):
        """Обработка GET запросов (для проверки здоровья)"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        else:
            self.send_error(404)
    
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
    # Инициализируем БД при старте (проверяет наличие и создает таблицы если нужно)
    init_db()
    
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, APIHandler)
    print(f'Python API сервер запущен на порту {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()

