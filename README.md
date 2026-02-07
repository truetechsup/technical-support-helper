# Technical Support Helper

Простое веб-приложение для поиска информации об ошибках. Разработано для сотрудников технической поддержки.

## Структура проекта

```
project/
├── app/                  # Код приложения (для GitHub)
│   ├── server.py
│   ├── database.py
│   ├── init_db.py
│   ├── templates/
│   ├── static/
│   ├── nginx/
│   └── Dockerfile.*
│
└── vm/                   # Файлы для виртуальной машины (НЕ в Git)
    ├── app/              # Клонируется из GitHub
    ├── data/             # База данных
    ├── backups/          # Бэкапы
    ├── scripts/
    │   └── update.sh     # Скрипт обновления
    └── docker-compose.yml
```

## Технологии

- **Python 3.11** - Backend API (стандартная библиотека)
- **Nginx** - Веб-сервер и reverse proxy
- **SQLite** - База данных
- **Docker** - Контейнеризация

## Развертывание

### На сервере (первый раз)

1. **Клонируйте репозиторий:**
```bash
cd ~
mkdir -p support-helper
cd support-helper
git clone https://github.com/your-username/support-helper.git support-helper
cd support-helper
```

2. **Создайте структуру для ВМ:**
```bash
# Создаем директории для данных и бэкапов
mkdir -p vm/data vm/backups
chmod 777 vm/data

# Копируем код приложения в vm/app
cp -r app vm/app
```

3. **Запустите приложение:**
```bash
cd vm
docker compose up -d --build

# Ждем несколько секунд для запуска контейнеров
sleep 5

# Инициализация БД (добавление тестовых данных)
docker exec -it support-helper-python python3 init_db.py
```

4. **Проверьте работу:**
```bash
# Проверка статуса контейнеров
docker compose ps

# Просмотр логов
docker compose logs -f

# Приложение доступно по адресу: http://ваш-ip:8080
```

### Настройка Git для работы скрипта обновления

После первого развертывания настройте Git в `vm/app`:

```bash
cd vm/app
git init
git remote add origin https://github.com/your-username/support-helper.git
git fetch origin
git checkout -b main origin/main
```

### Обновление приложения

После настройки Git используйте скрипт обновления:

```bash
cd vm
chmod +x scripts/update.sh
./scripts/update.sh
```

Скрипт автоматически:
- Создает бэкап кода и БД
- Обновляет код из Git
- Перезапускает контейнеры
- Проверяет и инициализирует БД если нужно

## Разработка

1. Разрабатывайте код в директории `app/`
2. Коммитьте и пушите в GitHub
3. На сервере запускайте `vm/scripts/update.sh` для обновления

## База данных

- БД хранится в `vm/data/` (не в Git)
- При старте приложение автоматически проверяет наличие БД
- Если БД пустая, она инициализируется тестовыми данными

## Бэкапы

- Бэкапы создаются автоматически перед каждым обновлением
- Хранятся в `vm/backups/`
- Автоматически сохраняются последние 10 бэкапов

## Документация

- `app/README.md` - документация по коду приложения
- `vm/README.md` - инструкции по развертыванию на сервере
