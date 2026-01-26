#!/bin/bash
#
# setup_local.sh - Первоначальная настройка локального окружения
# Использование: ./setup_local.sh
#

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     ⚙️  НАСТРОЙКА ЛОКАЛЬНОГО ОКРУЖЕНИЯ                        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# === 1. ПРОВЕРКА PYTHON ===
echo "🐍 Проверка Python..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен!"
    echo ""
    echo "Установите Python3:"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Ubuntu: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"
echo ""

# === 2. СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ ===
echo "📦 Создание виртуального окружения..."

if [ -d "venv" ]; then
    echo "⚠️  venv уже существует"
    read -p "Пересоздать? (y/N): " RECREATE
    if [ "$RECREATE" = "y" ] || [ "$RECREATE" = "Y" ]; then
        echo "🔄 Удаление старого venv..."
        rm -rf venv
    else
        echo "✅ Используем существующий venv"
    fi
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ venv создано"
fi

# Активация
source venv/bin/activate
echo "✅ venv активировано"
echo ""

# === 3. УСТАНОВКА ЗАВИСИМОСТЕЙ ===
echo "📥 Установка зависимостей..."

if [ ! -f "requirements_full.txt" ]; then
    echo "❌ requirements_full.txt не найден!"
    exit 1
fi

pip install --upgrade pip
pip install -r requirements_full.txt

echo "✅ Зависимости установлены"
echo ""

# === 4. СОЗДАНИЕ ПАПОК ===
echo "📁 Создание рабочих папок..."

mkdir -p excel_files
mkdir -p output
mkdir -p logs
mkdir -p templates

echo "✅ Папки созданы:"
echo "   - excel_files/  (рабочие данные)"
echo "   - output/       (результаты)"
echo "   - logs/         (логи)"
echo "   - templates/    (шаблоны)"
echo ""

# === 5. НАСТРОЙКА .env ===
echo "⚙️  Настройка .env..."

if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ .env создан из env.example"
        echo ""
        echo "⚠️  ВАЖНО: Заполните .env своими данными!"
        echo ""
        echo "Откройте файл:"
        echo "  nano .env"
        echo ""
        echo "Заполните:"
        echo "  1. TRELLO_API_KEY     - https://trello.com/power-ups/admin"
        echo "  2. TRELLO_TOKEN       - там же"
        echo "  3. TRELLO_BOARD_ID    - из URL доски"
        echo "  4. DROPBOX_REFRESH_TOKEN - из настроек Dropbox App"
        echo "  5. DROPBOX_APP_KEY    - из настроек Dropbox App"
        echo "  6. DROPBOX_APP_SECRET - из настроек Dropbox App"
        echo ""
        read -p "Нажмите Enter когда заполните .env..."
    else
        echo "❌ env.example не найден!"
        exit 1
    fi
else
    echo "✅ .env уже существует"
fi

echo ""

# === 6. ПЕРЕИМЕНОВАНИЕ ФАЙЛОВ ===
echo "📝 Проверка файлов..."

if [ -f "sync_trello_severen_NEW.py" ]; then
    if [ -f "sync_trello_severen.py" ]; then
        echo "⚠️  sync_trello_severen.py уже существует"
        read -p "Заменить на NEW версию? (y/N): " REPLACE
        if [ "$REPLACE" = "y" ] || [ "$REPLACE" = "Y" ]; then
            mv sync_trello_severen.py sync_trello_severen_OLD.py
            mv sync_trello_severen_NEW.py sync_trello_severen.py
            chmod +x sync_trello_severen.py
            echo "✅ Заменено (старая версия → sync_trello_severen_OLD.py)"
        fi
    else
        mv sync_trello_severen_NEW.py sync_trello_severen.py
        chmod +x sync_trello_severen.py
        echo "✅ sync_trello_severen_NEW.py → sync_trello_severen.py"
    fi
fi

# Делаем скрипты исполняемыми
chmod +x *.sh 2>/dev/null || true
chmod +x *.py 2>/dev/null || true

echo "✅ Файлы проверены"
echo ""

# === 7. ПРОВЕРКА ШАБЛОНА ===
echo "📄 Проверка шаблона..."

if [ -f "template.xlsx" ] && [ ! -f "templates/template.xlsx" ]; then
    echo "🔄 Перемещение template.xlsx в templates/"
    mv template.xlsx templates/
    echo "✅ template.xlsx → templates/template.xlsx"
elif [ ! -f "templates/template.xlsx" ] && [ ! -f "template.xlsx" ]; then
    echo "⚠️  template.xlsx не найден!"
    echo "   Поместите шаблон акта в templates/template.xlsx"
fi

echo ""

# === 8. ИТОГОВАЯ ИНФОРМАЦИЯ ===
echo "════════════════════════════════════════════════════════════════"
echo "✅ НАСТРОЙКА ЗАВЕРШЕНА"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📂 Структура проекта:"
tree -L 1 -d 2>/dev/null || ls -la
echo ""
echo "🚀 СЛЕДУЮЩИЕ ШАГИ:"
echo ""
echo "1️⃣  Проверьте .env:"
echo "    nano .env"
echo ""
echo "2️⃣  Запустите синхронизацию:"
echo "    ./run_sync_local.sh"
echo ""
echo "3️⃣  Сгенерируйте акт:"
echo "    ./run_generate_act_local.sh"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
