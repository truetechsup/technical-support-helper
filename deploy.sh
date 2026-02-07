#!/bin/bash
# Скрипт для быстрого деплоя на сервер через SSH

# Настройки (измените под свои)
SERVER_USER="tester"
SERVER_IP="your-server-ip"
SERVER_PATH="~/errors/Errors"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Начинаем деплой...${NC}"

# Проверяем, что мы в правильной директории
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Ошибка: docker-compose.yml не найден. Запустите скрипт из корня проекта."
    exit 1
fi

# Создаем временный архив
echo -e "${YELLOW}📦 Создаем архив...${NC}"
ARCHIVE_NAME="deploy-$(date +%Y%m%d-%H%M%S).tar.gz"

tar -czf "$ARCHIVE_NAME" \
    --exclude='data' \
    --exclude='*.db' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='.idea' \
    --exclude='.vscode' \
    --exclude='*.log' \
    --exclude='*.tar.gz' \
    server.py database.py init_db.py templates static nginx \
    Dockerfile.nginx Dockerfile.python docker-compose.yml \
    requirements.txt README.md QUICKSTART.md .dockerignore .gitignore

echo -e "${GREEN}✓ Архив создан: $ARCHIVE_NAME${NC}"

# Копируем на сервер
echo -e "${YELLOW}📤 Копируем на сервер...${NC}"
scp "$ARCHIVE_NAME" "$SERVER_USER@$SERVER_IP:/tmp/"

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при копировании на сервер"
    rm "$ARCHIVE_NAME"
    exit 1
fi

# Распаковываем и перезапускаем на сервере
echo -e "${YELLOW}🔄 Обновляем приложение на сервере...${NC}"
ssh "$SERVER_USER@$SERVER_IP" << EOF
    cd $SERVER_PATH
    tar -xzf /tmp/$ARCHIVE_NAME
    rm /tmp/$ARCHIVE_NAME
    docker compose down
    docker compose up -d --build
    echo "✅ Приложение обновлено!"
EOF

# Удаляем локальный архив
rm "$ARCHIVE_NAME"

echo -e "${GREEN}✅ Деплой завершен!${NC}"
echo -e "${GREEN}🌐 Приложение доступно: http://$SERVER_IP:8080${NC}"

