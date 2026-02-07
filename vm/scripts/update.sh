#!/bin/bash
# Скрипт для обновления приложения из Git с бэкапом

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Определяем корневую директорию проекта
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$(cd "$VM_DIR/.." && pwd)"
APP_DIR="$PROJECT_DIR/app"
DATA_DIR="$VM_DIR/data"
BACKUPS_DIR="$VM_DIR/backups"

# Переходим в директорию приложения (из корня репозитория)
cd "$APP_DIR" || exit 1

echo -e "${YELLOW}🔄 Обновление приложения...${NC}"

# Создаем директорию для бэкапов если её нет
mkdir -p "$BACKUPS_DIR"

# Создаем бэкап перед обновлением
BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
BACKUP_PATH="$BACKUPS_DIR/$BACKUP_NAME"

echo -e "${YELLOW}💾 Создание бэкапа: $BACKUP_NAME${NC}"

# Создаем директорию для бэкапа
mkdir -p "$BACKUP_PATH"

# Копируем код приложения
echo "  📦 Копирование кода приложения..."
cp -r "$APP_DIR" "$BACKUP_PATH/app" 2>/dev/null || {
    echo -e "${RED}❌ Ошибка при копировании кода${NC}"
    exit 1
}

# Копируем БД если она существует
if [ -f "$DATA_DIR/support-helper.db" ]; then
    echo "  💾 Копирование базы данных..."
    mkdir -p "$BACKUP_PATH/data"
    cp "$DATA_DIR/support-helper.db" "$BACKUP_PATH/data/support-helper.db" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Предупреждение: не удалось скопировать БД${NC}"
    }
else
    echo "  ℹ️  База данных не найдена, пропускаем"
fi

# Сохраняем информацию о бэкапе
echo "Backup created: $(date)" > "$BACKUP_PATH/backup-info.txt"
echo "App directory: $APP_DIR" >> "$BACKUP_PATH/backup-info.txt"
echo "Data directory: $DATA_DIR" >> "$BACKUP_PATH/backup-info.txt"

echo -e "${GREEN}✓ Бэкап создан: $BACKUP_PATH${NC}"

# Обновляем код из Git
echo -e "\n${YELLOW}📥 Обновление из Git...${NC}"
git pull origin main

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Ошибка при обновлении из Git${NC}"
    exit 1
fi

# Убеждаемся, что директория data существует
mkdir -p "$DATA_DIR"
chmod 777 "$DATA_DIR"

# Перезапускаем контейнеры (из директории vm)
echo -e "\n${YELLOW}🔄 Перезапуск контейнеров...${NC}"
cd "$VM_DIR" || exit 1
docker compose down
docker compose up -d --build

# Ждем запуска контейнера
echo -e "${YELLOW}⏳ Ожидание запуска контейнера...${NC}"
sleep 5

# Проверяем и инициализируем БД если она пустая
echo -e "${YELLOW}🔍 Проверка базы данных...${NC}"
DB_EMPTY=$(docker exec support-helper-python python3 -c "from database import is_db_empty; print('empty' if is_db_empty() else 'not_empty')" 2>/dev/null)

if [ "$DB_EMPTY" = "empty" ]; then
    echo -e "${YELLOW}📝 База данных пустая, инициализация тестовыми данными...${NC}"
    docker exec support-helper-python python3 init_db.py
else
    echo -e "${GREEN}✅ База данных содержит данные, инициализация не требуется${NC}"
fi

# Очистка старых бэкапов (оставляем последние 10)
echo -e "\n${YELLOW}🧹 Очистка старых бэкапов (оставляем последние 10)...${NC}"
cd "$BACKUPS_DIR" || exit 1
ls -t | tail -n +11 | xargs rm -rf 2>/dev/null

echo -e "\n${GREEN}✅ Приложение обновлено!${NC}"
echo -e "${GREEN}💾 Бэкап сохранен: $BACKUP_PATH${NC}"

