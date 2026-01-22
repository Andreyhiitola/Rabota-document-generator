#!/bin/bash
# Генерация отчета через Docker

MONTH=${1:-$(date +%m)}
YEAR=${2:-$(date +%Y)}
CLIENT=${3:-"Все клиенты"}
STATUS=${4:-""}
EXECUTOR=${5:-""}

echo "🚀 Генерация отчета через Docker..."
echo "📅 Период: ${MONTH}/${YEAR}"
echo "👤 Клиент: ${CLIENT}"

CMD="python3 report_generator_v2.py \
    --source /app/files/Рабочие_табл_СМР_v2.xlsx \
    --output /app/output/отчет_${MONTH}_${YEAR}.xlsx \
    --month ${MONTH} \
    --year ${YEAR} \
    --client '${CLIENT}'"

if [ ! -z "$STATUS" ]; then
    CMD="$CMD --status '$STATUS'"
fi

if [ ! -z "$EXECUTOR" ]; then
    CMD="$CMD --executor '$EXECUTOR'"
fi

docker-compose exec report-generator bash -c "$CMD"

if [ $? -eq 0 ]; then
    echo "✅ Отчет создан: ./output/отчет_${MONTH}_${YEAR}.xlsx"
    ls -lh output/отчет_${MONTH}_${YEAR}.xlsx
else
    echo "❌ Ошибка генерации отчета"
    exit 1
fi
