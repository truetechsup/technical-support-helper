#!/bin/bash
# Скрипт для обновления приложения из Git с бэкапом

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Определяем корневую директорию проекта
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$(cd "$VM_DIR/.." && pwd)"
APP_DIR="$PROJECT_DIR/app"
DATA_DIR="$VM_DIR/data"
BACKUPS_DIR="$VM_DIR/backups"

# Переходим в корень репозитория
cd "$PROJECT_DIR" || exit 1

echo -e "${YELLOW}🔄 Обновление приложения...${NC}"

# Создаем директорию для бэкапов
mkdir -p "$BACKUPS_DIR"

# Создаем бэкап перед обновлением
BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S).tar.gz"
BACKUP_PATH="$BACKUPS_DIR/$BACKUP_NAME"

echo -e "${YELLOW}💾 Создание бэкапа: $BACKUP_NAME${NC}"

# Создаем архив с кодом и БД
cd "$PROJECT_DIR" || exit 1
tar -czf "$BACKUP_PATH" \
    app/ \
    $([ -f "$DATA_DIR/support-helper.db" ] && echo "vm/data/support-helper.db" || true) \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Бэкап создан: $BACKUP_NAME${NC}"
else
    echo -e "${RED}❌ Ошибка при создании бэкапа${NC}"
    exit 1
fi

# Обновляем код из Git (из корня репозитория)
echo -e "\n${YELLOW}📥 Обновление из Git...${NC}"
cd "$PROJECT_DIR" || exit 1
git pull origin main

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Ошибка при обновлении из Git${NC}"
    exit 1
fi

# Убеждаемся, что директория data существует
mkdir -p "$DATA_DIR"
chmod 777 "$DATA_DIR"

# Перезапускаем контейнеры
echo -e "\n${YELLOW}🔄 Перезапуск контейнеров...${NC}"
cd "$VM_DIR" || exit 1
docker compose down
docker compose up -d --build

# Ждем запуска контейнера
echo -e "${YELLOW}⏳ Ожидание запуска контейнера...${NC}"
sleep 5

# Очистка старых бэкапов (оставляем последние 10)
echo -e "\n${YELLOW}🧹 Очистка старых бэкапов (оставляем последние 10)...${NC}"
cd "$BACKUPS_DIR" || exit 1
ls -t *.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null

echo -e "\n${GREEN}✅ Приложение обновлено!${NC}"
echo -e "${GREEN}💾 Бэкап сохранен: $BACKUP_NAME${NC}"

