# Руководство по разработке

## Варианты организации процесса разработки

### Вариант 1: Git Workflow (Рекомендуется) ⭐

**Процесс:**
1. Разработка на Windows (PyCharm/Cursor)
2. Commit и Push в GitHub
3. На сервере: `git pull` + перезапуск контейнеров

**Преимущества:**
- ✅ История изменений
- ✅ Резервное копирование кода
- ✅ Легко откатить изменения
- ✅ Можно работать с нескольких машин

**Настройка:**

1. **Инициализация Git (на Windows):**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/errors-app.git
git push -u origin main
```

2. **На сервере (первый раз):**
```bash
cd ~/errors
git clone https://github.com/your-username/errors-app.git Errors
cd Errors
mkdir -p data
chmod 777 data
docker compose up -d --build
```

3. **Обновление после изменений:**
```bash
# На Windows: commit и push
git add .
git commit -m "Описание изменений"
git push

# На сервере: обновление
cd ~/errors/Errors
git pull
docker compose down
docker compose up -d --build
```

4. **Автоматизация на сервере:**
Создайте скрипт `update.sh` на сервере:
```bash
#!/bin/bash
cd ~/errors/Errors
git pull
docker compose down
docker compose up -d --build
```

Использование:
```bash
chmod +x update.sh
./update.sh
```

---

### Вариант 2: Rsync (Быстрая синхронизация)

**Процесс:**
1. Разработка на Windows
2. Запуск скрипта `deploy.sh` для синхронизации
3. Автоматический перезапуск на сервере

**Преимущества:**
- ✅ Быстро (только измененные файлы)
- ✅ Не нужен Git
- ✅ Автоматизация

**Настройка:**

1. **Установите rsync на Windows** (через WSL или Git Bash)

2. **Используйте скрипт `deploy.sh`** (нужно настроить переменные):
```bash
# Отредактируйте deploy.sh:
SERVER_USER="tester"
SERVER_IP="your-server-ip"
SERVER_PATH="~/errors/Errors"
```

3. **Использование:**
```bash
# В Git Bash или WSL
chmod +x deploy.sh
./deploy.sh
```

---

### Вариант 3: Docker Volumes для разработки

**Процесс:**
1. Монтируем код как volume в Docker
2. Изменения применяются без пересборки
3. Перезапуск только Python сервера

**Преимущества:**
- ✅ Мгновенные изменения (без пересборки)
- ✅ Удобно для частых изменений

**Недостатки:**
- ⚠️ Нужен доступ к файлам с Windows на Linux (сложнее)

**Использование:**

```bash
# На сервере используйте docker-compose.dev.yml
docker compose -f docker-compose.dev.yml up -d

# После изменений в коде (на сервере):
docker compose -f docker-compose.dev.yml restart python-server
```

---

## Рекомендуемый Workflow (Git + Скрипт)

### Ежедневная работа:

**1. Разработка на Windows:**
```bash
# Вносите изменения в код
# Тестируете локально (если настроено)
```

**2. Commit и Push:**
```bash
git add .
git commit -m "Добавлена функция поиска"
git push
```

**3. Обновление на сервере:**
```bash
# Подключаетесь к серверу
ssh tester@your-server-ip

# Обновляете код
cd ~/errors/Errors
git pull
docker compose down
docker compose up -d --build
```

**4. Автоматизация (опционально):**
Создайте скрипт `update.sh` на сервере:
```bash
#!/bin/bash
cd ~/errors/Errors
git pull && docker compose down && docker compose up -d --build
```

Использование:
```bash
./update.sh
```

---

## Структура .gitignore

Убедитесь, что `.gitignore` содержит:
- `data/` - директория с БД
- `*.db` - файлы БД
- `__pycache__/` - кэш Python
- `.idea/`, `.vscode/` - настройки IDE

---

## Полезные команды

### На Windows (разработка):
```bash
# Проверка изменений
git status

# Commit
git add .
git commit -m "Описание"

# Push
git push

# Просмотр истории
git log --oneline
```

### На сервере (деплой):
```bash
# Обновление из Git
git pull

# Перезапуск контейнеров
docker compose down
docker compose up -d --build

# Просмотр логов
docker compose logs -f python-server

# Проверка статуса
docker compose ps
```

---

## Рекомендации

1. **Используйте Git** - это стандарт для разработки
2. **Делайте частые коммиты** - легче отслеживать изменения
3. **Пишите понятные сообщения коммитов**
4. **Тестируйте на сервере** после каждого деплоя
5. **Делайте бэкапы БД** перед обновлениями

---

## Автоматизация через GitHub Actions (опционально)

Можно настроить автоматический деплой при push в main ветку. Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd ~/errors/Errors
            git pull
            docker compose down
            docker compose up -d --build
```

---

## Выбор варианта

- **Для личного проекта:** Вариант 1 (Git) - простой и надежный
- **Для быстрой разработки:** Вариант 2 (Rsync) - если не нужен Git
- **Для частых изменений:** Вариант 3 (Volumes) - если есть доступ к файлам

**Рекомендация:** Используйте **Вариант 1 (Git)** - это стандартный подход, который даст вам историю изменений и возможность работать с нескольких мест.

