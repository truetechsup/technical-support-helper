# Быстрый старт

## 1. Установка Docker (если не установлен)

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker
```

## 2. Подготовка проекта

```bash
# Создаем директорию для данных
mkdir -p data
chmod 777 data
```

## 3. Запуск приложения

```bash
# Собираем и запускаем
docker compose up -d --build
```

## 4. Добавление тестовых данных

```bash
# Запускаем скрипт инициализации
docker exec -it errors-python python3 init_db.py
```

## 5. Доступ к приложению

Откройте в браузере: `http://ваш-ip:8080`

## Полезные команды

```bash
# Просмотр логов
docker compose logs -f

# Остановка
docker compose down

# Перезапуск
docker compose restart

# Статус контейнеров
docker compose ps
```

