#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Синхронизация данных из Trello в Excel
Доска: Северен согласования
"""

import os
import sys
import requests
import openpyxl
from datetime import datetime
from pathlib import Path

# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

# Trello API credentials
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID', 'gfcln6rS')

# Excel файл
EXCEL_PATH = os.getenv('EXCEL_PATH', '/app/excel_files/ПРИЛОЖЕНИЕ_1_3_4_ALL_IN_ONE.xlsx')

# API endpoints
BASE_URL = "https://api.trello.com/1"


# ============================================================
# ФУНКЦИИ
# ============================================================

def check_credentials():
    """Проверка наличия учетных данных"""
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ ОШИБКА: Не заданы TRELLO_API_KEY или TRELLO_TOKEN")
        print("\nПроверьте .env файл:")
        print("  TRELLO_API_KEY=...")
        print("  TRELLO_TOKEN=...")
        return False
    
    if TRELLO_API_KEY == TRELLO_TOKEN:
        print("⚠️  ВНИМАНИЕ: TRELLO_API_KEY и TRELLO_TOKEN одинаковые!")
        print("   Это неправильно! Получите правильные ключи:")
        print("   https://trello.com/app-key")
        return False
    
    return True


def get_board_info():
    """Получение информации о доске"""
    url = f"{BASE_URL}/boards/{TRELLO_BOARD_ID}"
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к Trello: {e}")
        return None


def get_cards():
    """Получение всех карточек с доски"""
    url = f"{BASE_URL}/boards/{TRELLO_BOARD_ID}/cards"
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN,
        'fields': 'name,desc,due,labels,idList,dateLastActivity',
        'members': 'true',
        'checklists': 'all'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка получения карточек: {e}")
        return []


def get_lists():
    """Получение всех списков (колонок) с доски"""
    url = f"{BASE_URL}/boards/{TRELLO_BOARD_ID}/lists"
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return {lst['id']: lst['name'] for lst in response.json()}
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка получения списков: {e}")
        return {}


def sync_to_excel(cards, lists):
    """Синхронизация карточек в Excel"""
    
    # Проверка существования файла
    excel_file = Path(EXCEL_PATH)
    if not excel_file.exists():
        print(f"❌ Excel файл не найден: {EXCEL_PATH}")
        return False
    
    try:
        # Открываем Excel файл
        wb = openpyxl.load_workbook(EXCEL_PATH)
        
        # Ищем лист для синхронизации (первый лист)
        if len(wb.sheetnames) == 0:
            print("❌ В Excel файле нет листов")
            return False
        
        ws = wb.active
        
        # Находим начало таблицы (первая строка с данными после заголовков)
        start_row = 2  # Обычно данные начинаются со 2-й строки
        
        # Очищаем старые данные (кроме заголовков)
        max_row = ws.max_row
        if max_row > start_row:
            ws.delete_rows(start_row, max_row - start_row + 1)
        
        # Добавляем данные из Trello
        current_row = start_row
        
        for card in cards:
            # Колонка A: Номер п/п
            ws.cell(row=current_row, column=1, value=current_row - start_row + 1)
            
            # Колонка B: Адрес (название карточки)
            ws.cell(row=current_row, column=2, value=card.get('name', ''))
            
            # Колонка C: Список/Статус
            list_name = lists.get(card.get('idList', ''), '')
            ws.cell(row=current_row, column=3, value=list_name)
            
            # Колонка D: Описание
            ws.cell(row=current_row, column=4, value=card.get('desc', ''))
            
            # Колонка E: Дата (если есть)
            due_date = card.get('due')
            if due_date:
                try:
                    date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    ws.cell(row=current_row, column=5, value=date_obj.strftime('%d.%m.%Y'))
                except:
                    ws.cell(row=current_row, column=5, value='')
            
            # Колонка F: Метки
            labels = ', '.join([label.get('name', '') for label in card.get('labels', [])])
            ws.cell(row=current_row, column=6, value=labels)
            
            current_row += 1
        
        # Сохраняем файл
        wb.save(EXCEL_PATH)
        
        print(f"✅ Excel файл обновлен: {EXCEL_PATH}")
        print(f"   Добавлено записей: {len(cards)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при работе с Excel: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """Главная функция синхронизации"""
    
    print("=" * 60)
    print(" 🔄 СИНХРОНИЗАЦИЯ TRELLO → EXCEL")
    print("=" * 60)
    print()
    
    # Проверка учетных данных
    print("1️⃣  Проверка учетных данных...")
    if not check_credentials():
        sys.exit(1)
    print("   ✅ Учетные данные найдены")
    print()
    
    # Подключение к Trello
    print("2️⃣  Подключение к Trello...")
    board_info = get_board_info()
    if not board_info:
        print("   ❌ Не удалось подключиться к доске")
        sys.exit(1)
    
    print(f"   ✅ Доска найдена: {board_info.get('name', 'Unknown')}")
    print()
    
    # Получение списков
    print("3️⃣  Загрузка списков (колонок)...")
    lists = get_lists()
    print(f"   ✅ Найдено списков: {len(lists)}")
    print()
    
    # Получение карточек
    print("4️⃣  Загрузка карточек...")
    cards = get_cards()
    if not cards:
        print("   ⚠️  Карточки не найдены (или ошибка)")
    else:
        print(f"   ✅ Найдено карточек: {len(cards)}")
    print()
    
    # Синхронизация в Excel
    print("5️⃣  Обновление Excel файла...")
    if sync_to_excel(cards, lists):
        print()
        print("=" * 60)
        print(" ✅ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        print()
        print(f"📊 Обработано карточек: {len(cards)}")
        print(f"💾 Файл: {EXCEL_PATH}")
        print()
        return 0
    else:
        print()
        print("=" * 60)
        print(" ❌ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА С ОШИБКАМИ")
        print("=" * 60)
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
