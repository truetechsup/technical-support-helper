# Приложение поиска ошибок - Техническая поддержка

Простое веб-приложение для поиска информации об ошибках. Разработано для сотрудников технической поддержки.

## Технологии

- **Python 3.11** - Backend API (стандартная библиотека, без фреймворков)
- **Nginx** - Веб-сервер и reverse proxy
- **SQLite** - База данных
- **Docker** - Контейнеризация

## Структура проекта

```
app/
├── server.py              # Python HTTP сервер (API)
├── database.py            # Работа с БД
├── templates/
│   └── index.html         # HTML страница
├── static/
│   └── style.css          # CSS стили
├── nginx/
│   └── nginx.conf         # Конфигурация nginx
├── Dockerfile.nginx       # Образ для nginx
├── Dockerfile.python      # Образ для Python
├── docker-compose.yml     # Оркестрация контейнеров
└── README.md              # Инструкция
```

## Требования

- Ubuntu (или другой Linux дистрибутив)
- Docker
- Docker Compose

## Установка Docker на Ubuntu

Если Docker еще не установлен, выполните:

```bash
# Обновляем пакеты
sudo apt update

# Устанавливаем зависимости
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Добавляем официальный GPG ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавляем репозиторий Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Устанавливаем Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавляем текущего пользователя в группу docker (чтобы не использовать sudo)
sudo usermod -aG docker $USER

# Перезагружаем сессию или выполняем:
newgrp docker

# Проверяем установку
docker --version
docker compose version
```

## Развертывание приложения

### 1. Клонирование/копирование файлов

Скопируйте все файлы проекта на сервер в директорию, например `/opt/errors-app`:

```bash
# Создаем директорию
sudo mkdir -p /opt/errors-app
cd /opt/errors-app

# Копируем все файлы проекта в эту директорию
```

### 2. Создание директории для данных

```bash
mkdir -p data
chmod 777 data  # Разрешаем запись для контейнера
```

### 3. Сборка и запуск контейнеров

```bash
# Собираем и запускаем контейнеры
docker compose up -d --build
```

### 4. Проверка работы

```bash
# Проверяем статус контейнеров
docker compose ps

# Смотрим логи
docker compose logs -f
```

Приложение будет доступно по адресу: `http://ваш-ip-адрес:8080`

## Управление приложением

### Остановка

```bash
docker compose down
```

### Перезапуск

```bash
docker compose restart
```

### Просмотр логов

```bash
# Все логи
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f python-server
docker compose logs -f nginx
```

### Остановка и удаление (с данными)

```bash
docker compose down -v
```

## Работа с базой данных

### Добавление тестовых данных

Подключитесь к контейнеру Python:

```bash
docker exec -it errors-python python3
```

Затем в Python:

```python
from database import init_db, add_error
import uuid

# Инициализируем БД
init_db()

# Добавляем тестовую ошибку
error_data = {
    'uuid': str(uuid.uuid4()),
    'error': 'Connection timeout',
    'description': 'Ошибка возникает при попытке подключения к серверу, когда сервер не отвечает в течение установленного времени ожидания.',
    'solution': '1. Проверьте сетевое подключение\n2. Увеличьте таймаут подключения\n3. Проверьте доступность сервера',
    'tickets': ['TICKET-12345', 'TICKET-67890'],
    'tasks': ['https://jira.example.com/TASK-001', 'https://jira.example.com/TASK-002']
}

add_error(error_data)
print("Ошибка добавлена!")
```

### Прямая работа с SQLite

```bash
# Подключаемся к контейнеру
docker exec -it errors-python bash

# Запускаем sqlite3
sqlite3 /app/data/errors.db

# Примеры SQL команд:
# .tables - показать таблицы
# SELECT * FROM errors; - показать все ошибки
# .exit - выйти
```

### Резервное копирование БД

```bash
# Копируем файл БД
cp data/errors.db data/errors.db.backup

# Или через docker
docker cp errors-python:/app/data/errors.db ./errors.db.backup
```

### Восстановление БД

```bash
# Останавливаем контейнеры
docker compose down

# Восстанавливаем из бэкапа
cp errors.db.backup data/errors.db

# Запускаем снова
docker compose up -d
```

## Структура базы данных

Таблица `errors`:

| Поле | Тип | Описание |
|------|-----|----------|
| uuid | TEXT PRIMARY KEY | Уникальный идентификатор |
| error | TEXT | Текст ошибки |
| description | TEXT | Описание ошибки |
| solution | TEXT | Решение проблемы |
| tickets | TEXT | JSON массив номеров обращений |
| tasks | TEXT | JSON массив ссылок на задачи |

## API

### POST /api/search

Поиск ошибок по тексту.

**Запрос:**
```json
{
  "query": "Connection timeout"
}
```

**Ответ:**
```json
{
  "results": [
    {
      "uuid": "...",
      "error": "Connection timeout",
      "description": "...",
      "solution": "...",
      "tickets": ["TICKET-123"],
      "tasks": ["https://jira.com/TASK-001"]
    }
  ]
}
```

## Настройка портов

По умолчанию приложение использует порт **8080**. 

Чтобы изменить порт:

1. Отредактируйте `nginx/nginx.conf` - измените `listen 8080;`
2. Отредактируйте `docker-compose.yml` - измените `"8080:8080"` на нужный порт

## Устранение неполадок

### Контейнеры не запускаются

```bash
# Проверяем логи
docker compose logs

# Проверяем, не занят ли порт
sudo netstat -tulpn | grep 8080
```

### Ошибки доступа к БД

```bash
# Проверяем права на директорию data
ls -la data/

# Даем права на запись
chmod 777 data
```

### Nginx не может подключиться к Python серверу

```bash
# Проверяем, что оба контейнера в одной сети
docker network ls
docker network inspect errors-network
```

## Обновление приложения

```bash
# Останавливаем
docker compose down

# Обновляем файлы (если нужно)

# Пересобираем и запускаем
docker compose up -d --build
```

## Безопасность

⚠️ **Важно для продакшн:**

1. Настройте файрвол (UFW):
```bash
sudo ufw allow 8080/tcp
sudo ufw enable
```

2. Используйте HTTPS (настройте SSL сертификаты в nginx)

3. Ограничьте доступ к порту 8080 только для внутренней сети

4. Регулярно делайте резервные копии БД

## Поддержка

При возникновении проблем проверьте логи:
```bash
docker compose logs -f
```

