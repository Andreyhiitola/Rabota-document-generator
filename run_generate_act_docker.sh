#!/bin/bash
#
# run_generate_act_docker.sh - Генерация акта через Docker
# Использование: ./run_generate_act_docker.sh
#

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     📄 ГЕНЕРАЦИЯ АКТА ЧЕРЕЗ DOCKER                            ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# === 1. ПРОВЕРКА DOCKER ===
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    exit 1
fi

echo "✅ Docker: $(docker --version)"
echo ""

# === 2. ПРОВЕРКА ОБРАЗА ===
if ! docker images | grep -q "severen-sync"; then
    echo "❌ Образ severen-sync не найден!"
    echo "   Сначала запустите: ./run_docker.sh"
    exit 1
fi

# === 3. ПРОВЕРКА ФАЙЛОВ ===
echo "📋 Проверка файлов..."

if [ ! -f "excel_files/data.xlsx" ] && [ ! -f "data.xlsx" ]; then
    echo "❌ data.xlsx не найден!"
    echo "   Сначала запустите синхронизацию: ./run_docker.sh"
    exit 1
fi

if [ ! -f "templates/template.xlsx" ] && [ ! -f "template.xlsx" ]; then
    echo "❌ template.xlsx не найден!"
    exit 1
fi

echo "✅ Файлы готовы"
echo ""

# === 4. ГЕНЕРАЦИЯ ===
echo "════════════════════════════════════════════════════════════════"
echo "🚀 ЗАПУСК ГЕНЕРАТОРА В DOCKER"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Определяем пути к файлам
if [ -f "excel_files/data.xlsx" ]; then
    DATA_FILE="/app/excel_files/data.xlsx"
else
    DATA_FILE="/app/data.xlsx"
fi

if [ -f "templates/template.xlsx" ]; then
    TEMPLATE_FILE="/app/templates/template.xlsx"
else
    TEMPLATE_FILE="/app/template.xlsx"
fi

# Запуск в Docker
docker run --rm \
    -v $(pwd):/app \
    -w /app \
    severen-sync \
    python3 generate_act.py \
    --data "$DATA_FILE" \
    --template "$TEMPLATE_FILE"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "════════════════════════════════════════════════════════════════"
    echo "✅ АКТ СГЕНЕРИРОВАН"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    # Показываем последний созданный файл
    LATEST_ACT=$(ls -t Готовый_Акт_*.xlsx 2>/dev/null | head -1)
    if [ ! -z "$LATEST_ACT" ]; then
        echo "📄 $LATEST_ACT"
        ls -lh "$LATEST_ACT"
    fi
else
    echo "════════════════════════════════════════════════════════════════"
    echo "❌ ОШИБКА ГЕНЕРАЦИИ"
    echo "════════════════════════════════════════════════════════════════"
    exit 1
fi

echo ""
