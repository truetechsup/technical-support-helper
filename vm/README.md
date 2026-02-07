# Структура для виртуальной машины

Эта директория содержит файлы для развертывания приложения на сервере.

## Структура

```
vm/
├── data/             # База данных (НЕ в Git)
├── backups/          # Бэкапы приложения (НЕ в Git)
├── scripts/
│   └── update.sh     # Скрипт обновления с бэкапом
├── docker-compose.yml # Docker Compose для ВМ
└── README.md         # Этот файл
```

**Примечание:** Код приложения находится в `../app/` (из корня репозитория), не копируется в `vm/`.

## Первоначальная настройка (первый раз)

1. **Клонирование репозитория:**
```bash
cd ~
mkdir -p support-helper
cd support-helper
git clone https://github.com/your-username/support-helper.git support-helper
cd support-helper
```

2. **Создание структуры на сервере:**
```bash
# Создаем директории для данных и бэкапов
mkdir -p vm/data vm/backups
chmod 777 vm/data
```

3. **Запуск приложения:**
```bash
cd vm
docker compose up -d --build
```

**Готово!** БД автоматически инициализируется при первом запуске.

4. **Проверка работы:**
```bash
docker compose ps
docker compose logs -f
# Приложение: http://ваш-ip:8080
```

## Обновление приложения

```bash
cd vm
chmod +x scripts/update.sh
./scripts/update.sh
```

**Скрипт автоматически:**
1. Создает бэкап кода и БД в архив (tar.gz)
2. Обновляет код из Git
3. Перезапускает контейнеры
4. БД остается без изменений
5. Очищает старые бэкапы (оставляет последние 10)

## Восстановление из бэкапа

```bash
# Найти нужный бэкап
ls -la backups/

# Распаковать архив
cd ~/support-helper
tar -xzf vm/backups/backup-YYYYMMDD-HHMMSS.tar.gz

# Перезапустить
cd vm
docker compose restart
```

## Важно

- Директории `data/` и `backups/` НЕ должны попадать в Git
- Код приложения находится в `app/` и синхронизируется с GitHub
- Бэкапы создаются автоматически перед каждым обновлением

