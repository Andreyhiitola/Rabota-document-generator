# 🚀 Severen - Система автоматизации

Автоматическая синхронизация данных между Trello, Excel и Dropbox + генерация актов выполненных работ.

## 📋 Возможности

- ✅ Синхронизация карточек Trello → Excel
- ✅ Автоматическое заполнение таблицы данных
- ✅ Синхронизация с Dropbox
- ✅ Генерация актов выполненных работ
- ✅ Защита закрытых работ от изменений
- ✅ Автоматический расчёт стоимости
- ✅ Docker для лёгкого развёртывания

---

## 🚀 Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/andreysagurov/severen-generator.git
cd severen-generator
```

### 2. Настроить переменные окружения

```bash
cp env.example .env
nano .env
```

Заполните:
```env
# Trello
TRELLO_API_KEY=your_api_key
TRELLO_TOKEN=your_token
TRELLO_BOARD_ID=your_board_id

# Dropbox
DROPBOX_REFRESH_TOKEN=your_refresh_token
DROPBOX_APP_KEY=your_app_key
DROPBOX_APP_SECRET=your_app_secret
DROPBOX_FILE_PATH=/path/to/data.xlsx
```

### 3. Запустить

```bash
# Разовая синхронизация
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml run --rm sync

# Автоматическая синхронизация (каждый час)
docker compose -f docker-compose.prod.yml --profile auto-sync up -d
```

---

## 🔄 Workflow

```
1. Trello → Карточки создаются/обновляются
         ↓
2. GitHub Actions → Автосборка Docker образа (при push в main)
         ↓
3. Docker Hub → Образ andreysagurov/severen-generator:latest
         ↓
4. VPS → docker compose pull && up -d
         ↓
5. Excel ↔ Dropbox → Синхронизация каждый час
         ↓
6. Генерация актов → Готовый_Акт_*.xlsx
```

---

## 🚀 Развёртывание на VPS

```bash
# 1. Клонировать на VPS
ssh your-vps
git clone https://github.com/andreysagurov/severen-generator.git
cd severen-generator

# 2. Настроить .env
cp env.example .env
nano .env  # заполнить токены

# 3. Создать папки
mkdir -p excel_files output logs templates

# 4. Положить template.xlsx в templates/

# 5. Запустить
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml --profile auto-sync up -d

# ГОТОВО! Синхронизация каждый час автоматически!
```

---

## 🔄 Обновление на VPS

```bash
# Обновить код
git pull

# Обновить образ
docker compose -f docker-compose.prod.yml pull

# Перезапустить
docker compose -f docker-compose.prod.yml restart
```

---

## 🔐 GitHub Secrets

Для автоматической сборки в GitHub Actions:

1. Settings → Secrets and variables → Actions
2. Добавить:
   - `DOCKER_USERNAME` - логин Docker Hub
   - `DOCKER_PASSWORD` - токен Docker Hub

После этого каждый push в `main` автоматически собирает образ!

---

## 📝 Лицензия

MIT
