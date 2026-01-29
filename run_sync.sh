#!/bin/bash
cd $(pwd)

echo "🚀 Локальный запуск full_sync.py"
echo "⏰ $(date)"

python3 full_sync.py

echo ""
echo "✅ Готово! Проверьте:"
echo "ls -lh data.xlsx"
echo "ls -lh data/"
