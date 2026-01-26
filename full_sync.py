#!/usr/bin/env python3
"""
full_sync.py - Полная синхронизация Trello ↔ Excel ↔ Dropbox
"""

import os
import sys
import subprocess

print("=" * 80)
print("🚀 ЗАПУСК ПОЛНОЙ СИНХРОНИЗАЦИИ")
print("=" * 80)
print()

# === ШАГ 1: СКАЧИВАНИЕ ИЗ DROPBOX ===
print("=" * 80)
print("ШАГ 1/3: СКАЧИВАНИЕ ИЗ DROPBOX")
print("=" * 80)

try:
    result = subprocess.run([
        'python3', 'dropbox_sync.py',
        '--local', 'excel_files/data.xlsx',
        '--filename', 'data.xlsx',
        '--download-only'
    ], check=True, capture_output=False)
    print("✅ Файл скачан из Dropbox")
except subprocess.CalledProcessError as e:
    print(f"❌ Ошибка скачивания: {e}")
    sys.exit(1)

print()

# === ШАГ 2: СИНХРОНИЗАЦИЯ TRELLO → EXCEL ===
print("=" * 80)
print("ШАГ 2/3: СИНХРОНИЗАЦИЯ TRELLO → EXCEL")
print("=" * 80)

try:
    result = subprocess.run([
        'python3', 'sync_trello_severen.py',
        '--file', 'excel_files/data.xlsx'
    ], check=True, capture_output=False)
    print("✅ Trello синхронизирован с Excel")
except subprocess.CalledProcessError as e:
    print(f"❌ Ошибка синхронизации Trello: {e}")
    sys.exit(1)

print()

# === ШАГ 3: ЗАГРУЗКА В DROPBOX ===
print("=" * 80)
print("ШАГ 3/3: ЗАГРУЗКА В DROPBOX")
print("=" * 80)

try:
    result = subprocess.run([
        'python3', 'dropbox_sync.py',
        '--local', 'excel_files/data.xlsx',
        '--filename', 'data.xlsx',
        '--upload-only'
    ], check=True, capture_output=False)
    print("✅ Файл загружен в Dropbox")
except subprocess.CalledProcessError as e:
    print(f"❌ Ошибка загрузки: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("✅ ПОЛНАЯ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА")
print("=" * 80)
print()
