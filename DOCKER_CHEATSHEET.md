# 🐳 DOCKER - ШПАРГАЛКА

## ⚡ БЫСТРЫЙ СТАРТ (30 секунд!)

```bash
# 1. Переименовать файл
mv sync_trello_severen_NEW.py sync_trello_severen.py

# 2. Настроить .env (если ещё не сделано)
cp env.example .env
nano .env  # заполнить

# 3. Запустить!
chmod +x *.sh
./run_docker.sh
```

**ГОТОВО! 🎉**

---

## 🚀 ОСНОВНЫЕ КОМАНДЫ

```bash
# Синхронизация
./run_docker.sh

# Генерация акта
./run_generate_act_docker.sh

# Автосинхронизация (каждый час, фоном)
docker compose -f docker-compose.prod.yml --profile auto-sync up -d

# Посмотреть логи
docker compose logs -f

# Остановить
docker compose down
```

---

## 🔧 ПЕРВАЯ УСТАНОВКА DOCKER

### Fedora
```bash
sudo dnf install docker docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

### Ubuntu
```bash
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

### Проверка
```bash
docker --version
docker run hello-world
```

---

## 📁 СТРУКТУРА

```
Rabota-document-generator/
├── run_docker.sh                      ← ⚡ ЗАПУСК
├── run_generate_act_docker.sh         ← 📄 АКТ
│
├── sync_trello_severen.py             ← Переименовать из _NEW!
├── dropbox_sync.py
├── full_sync.py
├── generate_act.py
│
├── data.xlsx
├── template.xlsx
├── .env                               ← Настроить!
│
├── Dockerfile
└── docker-compose.prod.yml
```

---

## ❌ ПРОБЛЕМЫ

**"docker: command not found"**
→ Установить Docker (см. выше)

**"permission denied"**
→ `sudo usermod -aG docker $USER && newgrp docker`

**"Cannot connect to daemon"**
→ `sudo systemctl start docker`

**Образ не собирается**
→ `docker system prune -a && docker build -t severen-sync .`

---

## 💡 СОВЕТ

**Docker = Работает везде одинаково!**

Настроили раз - работает на:
- ✅ Вашем Fedora
- ✅ Windows коллеги
- ✅ Ubuntu сервере
- ✅ Mac

Без установки Python, без venv, без проблем с зависимостями!

---

## 🔄 ОБНОВЛЕНИЕ

```bash
# Пересобрать образ (если изменили код)
docker compose build

# Или напрямую
docker build -t severen-sync -f Dockerfile .
```

---

## 📊 ЛОГИ

```bash
# Логи контейнера
docker compose logs

# Следить в реальном времени
docker compose logs -f

# Логи автосинхронизации
docker compose logs -f auto-sync
```

---

## 🎯 ДВА РЕЖИМА

### 1. Разовый запуск (рекомендуется)
```bash
./run_docker.sh
```
Контейнер запускается, делает работу, останавливается.

### 2. Постоянная работа (для автоматизации)
```bash
docker compose --profile auto-sync up -d
```
Контейнер работает постоянно, синхронизирует каждый час.

---

**Подробности:** см. DOCKER_SETUP.md
