#!/usr/bin/env python3
"""
full_sync.py - Полная синхронизация Trello ↔ Excel ↔ Dropbox + Генерация документов
"""

import os
import sys
import subprocess

print("=" * 80)
print("🚀 ЗАПУСК ПОЛНОЙ СИНХРОНИЗАЦИИ")
print("=" * 80)
print()

# Рабочие файлы внутри контейнера
data_file = '/tmp/data.xlsx'
output_dir = '/tmp/output'
os.makedirs(output_dir, exist_ok=True)

# === ШАГ 1: СКАЧИВАНИЕ data.xlsx ИЗ DROPBOX ===
print("=" * 80)
print("ШАГ 1/4: СКАЧИВАНИЕ data.xlsx ИЗ DROPBOX")
print("=" * 80)

try:
    subprocess.run([
        'curl', '-L',
        'https://www.dropbox.com/scl/fi/fsrhazmth8e8cf4xkcbvu/data.xlsx?rlkey=ka2y3rz85bhamxibyyc1p47js&dl=1',
        '-o', data_file
    ], check=True)
    print("✅ data.xlsx скачан")
except subprocess.CalledProcessError as e:
    print(f"❌ Ошибка скачивания: {e}")
    sys.exit(1)

print()

# === ШАГ 2: СИНХРОНИЗАЦИЯ TRELLO → EXCEL ===
print("=" * 80)
print("ШАГ 2/4: СИНХРОНИЗАЦИЯ TRELLO → data.xlsx")
print("=" * 80)

try:
    subprocess.run([
        'python3', 'sync_trello_severen.py',
        '--file', data_file
    ], check=True, capture_output=False)
    print("✅ Trello синхронизирован")
except subprocess.CalledProcessError as e:
    print(f"❌ Ошибка синхронизации: {e}")
    sys.exit(1)

print()

# === ШАГ 3: ГЕНЕРАЦИЯ ДОКУМЕНТА ИЗ TEMPLATE ===
print("=" * 80)
print("ШАГ 3/4: ГЕНЕРАЦИЯ ДОКУМЕНТА ИЗ template.xlsx")
print("=" * 80)

try:
    subprocess.run([
        'python3', 'generate_act.py',
        '--input', data_file,
        '--template', 'template.xlsx',
        '--output', output_dir
    ], check=True, capture_output=False)
    print("✅ Документ сгенерирован")
except subprocess.CalledProcessError as e:
    print(f"❌ Ошибка генерации: {e}")
    # Продолжаем даже если генерация не удалась
    pass

print()

# === ШАГ 4: ЗАГРУЗКА ОБРАТНО В DROPBOX ===
print("=" * 80)
print("ШАГ 4/4: ЗАГРУЗКА В DROPBOX")
print("=" * 80)

# Загружаем обновленный data.xlsx
try:
    subprocess.run([
        'python3', 'dropbox_sync.py', '--token', os.getenv('TOKEN'),
        '--local', data_file,
        '--dropbox', '/data.xlsx',
        '--upload-only'
    ], check=True, capture_output=False)
    print("✅ data.xlsx загружен в Dropbox")
except subprocess.CalledProcessError as e:
    print(f"❌ Ошибка загрузки data.xlsx: {e}")

# Загружаем сгенерированные документы
print("\n📤 Загрузка сгенерированных документов...")
for filename in os.listdir(output_dir):
    if filename.endswith('.xlsx') or filename.endswith('.docx'):
        local_path = os.path.join(output_dir, filename)
        dropbox_path = f'/generated/{filename}'
        
        try:
            subprocess.run([
                'python3', 'dropbox_sync.py', '--token', os.getenv('TOKEN'),
                '--local', local_path,
                '--dropbox', dropbox_path,
                '--upload-only'
            ], check=True, capture_output=False)
            print(f"✅ {filename} загружен")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Не удалось загрузить {filename}")

print()
print("=" * 80)
print("✅ ПОЛНАЯ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА")
print("=" * 80)
print()
