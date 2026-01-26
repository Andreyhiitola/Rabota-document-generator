# 🚀 ВЫБОР МЕТОДА ЗАПУСКА

## 🎯 Что выбрать: Docker или локально?

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🐳 DOCKER (РЕКОМЕНДУЕМ!)                                    ║
║     ✅ Проще настроить                                          ║
║     ✅ Работает везде одинаково                                 ║
║     ✅ Легко переносить                                         ║
║                                                                  ║
║     🐍 ЛОКАЛЬНО                                                 ║
║     ✅ Быстрее запуск (после настройки)                        ║
║     ⚠️ Сложнее первоначальная настройка                        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🐳 ВАРИАНТ 1: DOCKER (рекомендуем!)

### Когда использовать Docker:
```
✅ Нужно работать на разных компьютерах
✅ Будет Windows / Mac / Linux
✅ Не хочется настраивать Python
✅ Нужна изоляция от системы
✅ Планируется деплой на сервер
```

### Быстрый старт:
```bash
# 1. Установить Docker (один раз)
sudo dnf install docker docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker

# 2. Настроить проект
cd ~/Desktop/Rabota-document-generator
mv sync_trello_severen_NEW.py sync_trello_severen.py
cp env.example .env
nano .env  # заполнить

# 3. Запустить
chmod +x run_docker.sh
./run_docker.sh
```

### Документация:
- **DOCKER_SETUP.md** - подробная инструкция
- **DOCKER_CHEATSHEET.md** - шпаргалка команд

---

## 🐍 ВАРИАНТ 2: ЛОКАЛЬНО

### Когда использовать локально:
```
✅ Работаете только на одном компьютере
✅ Python уже установлен и настроен
✅ Нужен максимально быстрый запуск
✅ Не планируется Windows
```

### Быстрый старт:
```bash
# 1. Настроить окружение (один раз)
cd ~/Desktop/Rabota-document-generator
chmod +x setup_local.sh
./setup_local.sh

# 2. Настроить .env
nano .env  # заполнить

# 3. Запустить
./run_sync_local.sh
```

### Документация:
- **LOCAL_SETUP.md** - подробная инструкция
- **CHEATSHEET.md** - шпаргалка команд

---

## ⚠️ ТЕКУЩАЯ ПРОБЛЕМА (локально)

У вас была ошибка:
```
❌ Модуль dropbox не установлен
```

**Быстрое исправление:**
```bash
source venv/bin/activate
pip install dropbox
./run_sync_local.sh
```

**НО** это показывает что Docker был бы проще - там всё уже установлено! 😊

---

## 📊 СРАВНЕНИЕ

| Критерий | 🐳 Docker | 🐍 Локально |
|----------|-----------|-------------|
| **Первая настройка** | 2 минуты | 5-10 минут |
| **Зависимости** | Автоматически | Вручную |
| **Работает везде** | ✅ Да | ⚠️ Нужна настройка |
| **Изоляция** | ✅ Полная | ❌ Нет |
| **Скорость запуска** | ~5 сек | ~2 сек |
| **Windows** | ✅ Да | ⚠️ Сложно |
| **Обновления** | `docker build` | `pip install` |
| **Проблемы с зависимостями** | ❌ Нет | ⚠️ Возможны |

---

## 💡 НАША РЕКОМЕНДАЦИЯ

### Для вашего случая: **DOCKER! 🐳**

**Почему:**
1. У вас уже возникла проблема с зависимостями (`dropbox` не установлен)
2. Вы упомянули что "может придется и виндоус запускать"
3. Docker решит обе проблемы сразу!

### План действий:

```bash
# === 1. УСТАНОВИТЬ DOCKER (5 минут) ===
sudo dnf install docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

# Проверка
docker --version
docker run hello-world

# === 2. НАСТРОИТЬ ПРОЕКТ (2 минуты) ===
cd ~/Desktop/Rabota-document-generator

# Переименовать
mv sync_trello_severen_NEW.py sync_trello_severen.py

# Скачать файлы из Claude (если ещё не скачали):
# - run_docker.sh
# - run_generate_act_docker.sh
# - full_sync.py
# - DOCKER_SETUP.md

# Настроить .env (если ещё не настроили)
cp env.example .env
nano .env  # заполнить ваши токены

# === 3. ЗАПУСТИТЬ (30 секунд!) ===
chmod +x run_docker.sh run_generate_act_docker.sh
./run_docker.sh

# ГОТОВО! 🎉
```

---

## 🔄 МОЖНО ЛИ ИСПОЛЬЗОВАТЬ ОБА МЕТОДА?

**Да!** Файлы совместимы. Можете:
- Локально: для быстрых тестов
- Docker: для продакшена

Но рекомендуем выбрать что-то одно чтобы не путаться.

---

## 📁 ФАЙЛЫ ДЛЯ СКАЧИВАНИЯ

### Для Docker:
```
✅ run_docker.sh
✅ run_generate_act_docker.sh
✅ full_sync.py
✅ DOCKER_SETUP.md
✅ DOCKER_CHEATSHEET.md
```

### Для локального запуска:
```
✅ setup_local.sh
✅ run_sync_local.sh
✅ run_generate_act_local.sh
✅ LOCAL_SETUP.md
✅ CHEATSHEET.md
```

### Общие:
```
✅ sync_trello_severen_NEW.py (переименовать в sync_trello_severen.py)
✅ dropbox_sync.py
✅ generate_act.py
✅ data.xlsx
✅ template.xlsx
✅ .env (создать из env.example)
```

---

## ✅ ИТОГОВЫЙ ЧЕКЛИСТ

```
☐ Выбрали метод (Docker или локально)
☐ Docker установлен (если выбрали Docker)
☐ Скачали нужные файлы из Claude
☐ Переименовали sync_trello_severen_NEW.py
☐ Создали и заполнили .env
☐ Сделали скрипты исполняемыми (chmod +x)
☐ Первый запуск прошёл успешно
☐ Данные синхронизировались
☐ Акт сгенерировался
☐ Всё работает! 🎉
```

---

## 🆘 ЕСЛИ НУЖНА ПОМОЩЬ

**Docker проблемы:**
→ См. DOCKER_SETUP.md раздел "Устранение проблем"

**Локальные проблемы:**
→ См. LOCAL_SETUP.md раздел "Устранение проблем"

**Общие вопросы:**
→ Проверьте .env правильно заполнен
→ Проверьте файлы переименованы
→ Проверьте права (chmod +x *.sh)

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

**Решили что выбрать?**

### Если Docker:
```bash
# Читайте DOCKER_SETUP.md
cat DOCKER_SETUP.md

# Или краткую шпаргалку
cat DOCKER_CHEATSHEET.md
```

### Если локально:
```bash
# Читайте LOCAL_SETUP.md
cat LOCAL_SETUP.md

# Или краткую шпаргалку
cat CHEATSHEET.md
```

---

**Удачи! Если что - спрашивайте! 🚀**
