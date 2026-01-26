#!/bin/bash
#
# run_docker.sh - Запуск синхронизации через Docker
# Использование: ./run_docker.sh
#

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     🐳 ЗАПУСК ЧЕРЕЗ DOCKER                                    ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# === 1. ПРОВЕРКА DOCKER ===
echo "🐳 Проверка Docker..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo ""
    echo "Установите Docker:"
    echo "  Fedora: sudo dnf install docker docker-compose"
    echo "  Ubuntu: sudo apt install docker.io docker-compose"
    echo ""
    echo "После установки:"
    echo "  sudo systemctl start docker"
    echo "  sudo usermod -aG docker $USER"
    echo "  newgrp docker"
    exit 1
fi

echo "✅ Docker установлен: $(docker --version)"

# Проверка запущен ли Docker
if ! docker info &> /dev/null; then
    echo "⚠️  Docker не запущен"
    echo "   Запускаем..."
    sudo systemctl start docker
    sleep 2
fi

echo "✅ Docker работает"
echo ""

# === 2. ПРОВЕРКА .env ===
echo "⚙️  Проверка конфигурации..."

if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo ""
    echo "Создайте .env:"
    echo "  cp env.example .env"
    echo "  nano .env"
    exit 1
fi

echo "✅ .env найден"
echo ""

# === 3. ПЕРЕИМЕНОВАНИЕ ФАЙЛА (если нужно) ===
if [ -f "sync_trello_severen_NEW.py" ] && [ ! -f "sync_trello_severen.py" ]; then
    echo "🔄 Переименование sync_trello_severen_NEW.py..."
    mv sync_trello_severen_NEW.py sync_trello_severen.py
    echo "✅ Переименовано"
    echo ""
fi

# === 4. СБОРКА ОБРАЗА (если нужно) ===
echo "🔨 Проверка Docker образа..."

if ! docker images | grep -q "severen-sync"; then
    echo "🔄 Сборка образа (первый раз, может занять минуту)..."
    docker build -t severen-sync -f Dockerfile .
    echo "✅ Образ собран"
else
    echo "✅ Образ уже существует"
fi

echo ""

# === 5. ЗАПУСК СИНХРОНИЗАЦИИ ===
echo "════════════════════════════════════════════════════════════════"
echo "🚀 ЗАПУСК СИНХРОНИЗАЦИИ В DOCKER"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Используем docker-compose если есть
if [ -f "docker-compose.prod.yml" ]; then
    docker compose -f docker-compose.prod.yml run --rm sync
else
    # Или напрямую docker
    docker run --rm \
        --env-file .env \
        -v $(pwd)/excel_files:/app/excel_files \
        -v $(pwd)/output:/app/output \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/templates:/app/templates \
        severen-sync \
        python3 full_sync.py
fi

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "════════════════════════════════════════════════════════════════"
    echo "✅ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "📊 Результат: excel_files/data.xlsx"
else
    echo "════════════════════════════════════════════════════════════════"
    echo "❌ ОШИБКА СИНХРОНИЗАЦИИ"
    echo "════════════════════════════════════════════════════════════════"
    exit 1
fi

echo ""
