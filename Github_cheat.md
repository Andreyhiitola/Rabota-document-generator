# ⚡ GITHUB WORKFLOW - ШПАРГАЛКА

## 🎯 ВСЁ ПРОСТО:

```
Код → GitHub → Auto-Build → Docker Hub → VPS Pull
```

---

## 📦 ФАЙЛЫ ДЛЯ СКАЧИВАНИЯ:

```
✅ .gitignore
✅ github-actions-docker-build.yml → сохранить как .github/workflows/docker-build.yml
✅ docker-compose.prod.yml.GITHUB → заменить docker-compose.prod.yml
✅ Dockerfile.GITHUB → заменить Dockerfile
✅ README_GITHUB.md → заменить README.md
✅ full_sync.py (если ещё нет)
```

---

## 🚀 SETUP (10 минут):

### 1. GitHub
```bash
cd ~/Desktop/Rabota-document-generator

# Создайте репозиторий на github.com: severen-generator

# Переименуйте файл
mv sync_trello_severen_NEW.py sync_trello_severen.py

# Инициализация
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/severen-generator.git
git push -u origin main
```

### 2. Docker Hub
```
1. hub.docker.com → Create Repository → severen-generator
2. Account Settings → Security → New Access Token
3. Скопировать токен
```

### 3. GitHub Secrets
```
1. GitHub repo → Settings → Secrets → Actions
2. New secret:
   - DOCKER_USERNAME = ваш логин
   - DOCKER_PASSWORD = токен из шага 2
```

### 4. Триггер
```
GitHub → Actions → Run workflow
Или просто сделайте push - автоматом соберётся!
```

---

## 🎯 VPS ДЕПЛОЙ:

```bash
ssh your-vps

# Клонировать
git clone https://github.com/YOUR_USERNAME/severen-generator.git
cd severen-generator

# Настроить
cp env.example .env
nano .env  # заполнить токены
mkdir -p excel_files output logs templates
# Скопировать template.xlsx в templates/

# Запустить
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml --profile auto-sync up -d

# ВСЁ! 🎉
```

---

## 🔄 ОБНОВЛЕНИЯ:

### Локально:
```bash
# Изменить код
nano sync_trello_severen.py

# Пуш
git add .
git commit -m "Описание"
git push

# GitHub Actions автоматом соберёт образ!
```

### На VPS:
```bash
git pull
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml restart
```

---

## ✅ ПРЕИМУЩЕСТВА:

```
✅ Код на GitHub = один источник правды
✅ Автосборка = никаких ручных действий
✅ Docker Hub = готовый образ
✅ VPS = просто pull и запуск
✅ БЕЗ патчей
✅ БЕЗ локальной сборки
✅ Работает везде одинаково
```

---

**Подробности:** GITHUB_WORKFLOW.md
