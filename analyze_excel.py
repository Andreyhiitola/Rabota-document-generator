#!/usr/bin/env python3
"""
ПРОСТОЙ ПРИМЕР: Как программа читает ВАШ Excel файл

Этот скрипт показывает ТОЧНО, какие данные программа извлекает
из вашего файла ПРИЛОЖЕНИЕ_1_3_4_ALL_IN_ONE_месяц_ноябрь_2025.xlsx
"""

import pandas as pd
from openpyxl import load_workbook
import json

def analyze_your_file(filename):
    """
    Анализирует ВАШ конкретный Excel файл
    и показывает что программа из него извлечет
    """
    
    print("=" * 80)
    print("АНАЛИЗ ВАШЕГО EXCEL ФАЙЛА")
    print("=" * 80)
    
    # 1. ЗАГРУЗКА ЛИСТА "Эксель"
    print("\n📋 Шаг 1: Чтение листа 'Эксель'")
    print("-" * 80)
    
    df = pd.read_excel(filename, sheet_name='Эксель')
    
    print(f"✅ Прочитано строк: {len(df)}")
    print(f"✅ Колонок в листе: {len(df.columns)}")
    
    # Показываем структуру
    print("\nСтруктура данных:")
    for i, col in enumerate(df.columns):
        print(f"  Колонка {i}: {col}")
    
    # 2. ИЗВЛЕЧЕНИЕ ЗАДАНИЙ
    print("\n📋 Шаг 2: Извлечение заданий")
    print("-" * 80)
    
    tasks = []
    for idx, row in df.iterrows():
        # Пропускаем пустые строки
        if pd.isna(row.iloc[0]):
            continue
        
        # Извлекаем данные
        task = {
            'row_number': idx + 1,  # Номер строки в Excel
            'number': row.iloc[2] if pd.notna(row.iloc[2]) else '',
            'district': row.iloc[3] if pd.notna(row.iloc[3]) else '',
            'address_full': row.iloc[-1] if pd.notna(row.iloc[-1]) else '',
            'notes': row.iloc[4] if pd.notna(row.iloc[4]) else ''
        }
        
        # Разбираем транзитные адреса
        if 'транзит' in str(task['address_full']).lower():
            parts = task['address_full'].split('транзитные адреса')
            task['main_address'] = parts[0].strip()
            
            if len(parts) > 1:
                transit_text = parts[1]
                # Разбиваем по запятым
                transits = [t.strip() for t in transit_text.split(',') if t.strip()]
                task['transit_addresses'] = transits
                task['has_transits'] = True
            else:
                task['transit_addresses'] = []
                task['has_transits'] = False
        else:
            task['main_address'] = task['address_full']
            task['transit_addresses'] = []
            task['has_transits'] = False
        
        tasks.append(task)
    
    print(f"✅ Найдено заданий: {len(tasks)}")
    
    # Показываем первые 3 задания
    print("\nПример заданий:")
    for i, task in enumerate(tasks[:3], 1):
        print(f"\n  Задание {i}:")
        print(f"    Номер: {task['number']}")
        print(f"    Район: {task['district']}")
        print(f"    Основной адрес: {task['main_address'][:50]}...")
        if task['has_transits']:
            print(f"    Транзитных адресов: {len(task['transit_addresses'])}")
            for j, transit in enumerate(task['transit_addresses'][:2], 1):
                print(f"      {j}. {transit}")
    
    # 3. ЗАГРУЗКА ПРАЙС-ЛИСТА
    print("\n📋 Шаг 3: Чтение прайс-листа")
    print("-" * 80)
    
    df_prices = pd.read_excel(filename, sheet_name='расценки')
    
    prices = {}
    for idx, row in df_prices.iterrows():
        if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):
            service_num = int(row.iloc[0])
            prices[service_num] = {
                'description': row.iloc[1],
                'price': float(row.iloc[2])
            }
    
    print(f"✅ Загружено услуг: {len(prices)}")
    
    print("\nДоступные услуги:")
    for num, service in prices.items():
        print(f"  {num}. {service['description'][:60]}... — {service['price']:.2f}₽")
    
    # 4. ИТОГОВАЯ СТАТИСТИКА
    print("\n" + "=" * 80)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    
    print(f"\n✅ Всего заданий: {len(tasks)}")
    print(f"✅ Заданий с транзитными адресами: {sum(1 for t in tasks if t['has_transits'])}")
    print(f"✅ Всего транзитных адресов: {sum(len(t['transit_addresses']) for t in tasks)}")
    print(f"✅ Услуг в прайс-листе: {len(prices)}")
    
    # Уникальные номера заданий
    unique_numbers = set(t['number'] for t in tasks if t['number'])
    print(f"✅ Уникальных номеров заданий: {len(unique_numbers)}")
    print(f"   Номера: {', '.join(sorted(unique_numbers))}")
    
    # 5. ЧТО БУДЕТ В ВЫПАДАЮЩИХ СПИСКАХ
    print("\n" + "=" * 80)
    print("ЧТО УВИДИТЕ В ИНТЕРФЕЙСЕ ПРОГРАММЫ")
    print("=" * 80)
    
    print("\n📋 Выпадающий список 'Номер задания':")
    for num in sorted(unique_numbers):
        print(f"   • {num}")
    
    print("\n📋 Чекбоксы 'Выбор услуг':")
    for num, service in sorted(prices.items()):
        desc_short = service['description'][:50]
        print(f"   ☐ {num}. {desc_short}... — {service['price']:.0f}₽")
    
    # 6. ПРИМЕР ГЕНЕРАЦИИ
    print("\n" + "=" * 80)
    print("ПРИМЕР: ЧТО ПОПАДЕТ В ДОКУМЕНТ")
    print("=" * 80)
    
    if tasks:
        example_task = tasks[0]
        print(f"\nЕсли выбрать задание '{example_task['number']}':")
        print(f"\nВ таблице документа будет:")
        print("\n┌────────────────────────────────────┬──────────────┬──────────────┬─────────────┐")
        print("│ Адрес                              │ Дата передачи│ Дата выполн. │ Вид услуги  │")
        print("├────────────────────────────────────┼──────────────┼──────────────┼─────────────┤")
        
        # Основной адрес
        addr_short = example_task['main_address'][:30]
        print(f"│ {addr_short:<34} │ 01.11.2025   │ 03.12.2025   │ Консультации│")
        
        # Транзитные адреса
        if example_task['has_transits']:
            for transit in example_task['transit_addresses']:
                transit_short = f"  → {transit}"[:30]
                print(f"│ {transit_short:<34} │ 01.11.2025   │ 03.12.2025   │ (транзитный)│")
        
        print("└────────────────────────────────────┴──────────────┴──────────────┴─────────────┘")
        
        # Расчет стоимости
        if len(prices) >= 2:
            example_services = [1, 4]  # Услуги 1 и 4
            total = sum(prices[s]['price'] for s in example_services if s in prices)
            
            print(f"\nЕсли выбрать услуги {example_services}:")
            for s in example_services:
                if s in prices:
                    print(f"  • {prices[s]['description'][:50]} — {prices[s]['price']:.2f}₽")
            print(f"\nИТОГО: {total:,.2f}₽")
    
    # 7. СОХРАНЕНИЕ АНАЛИЗА
    print("\n" + "=" * 80)
    print("СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")
    print("=" * 80)
    
    # Сохраняем в JSON для программы
    data = {
        'tasks': tasks,
        'prices': prices,
        'statistics': {
            'total_tasks': len(tasks),
            'tasks_with_transits': sum(1 for t in tasks if t['has_transits']),
            'total_transits': sum(len(t['transit_addresses']) for t in tasks),
            'total_services': len(prices),
            'unique_task_numbers': list(unique_numbers)
        }
    }
    
    with open('extracted_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Результаты сохранены в 'extracted_data.json'")
    print("✅ Программа будет использовать эти данные для генерации документов")
    
    return data


# ЗАПУСК
if __name__ == '__main__':
    import sys
    
    # Путь к вашему файлу
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = '/mnt/user-data/uploads/ПРИЛОЖЕНИЕ_1_3_4_ALL_IN_ONE_Задание_Отчет_АКТ_месяц_ноябрь_2025.xlsx'
    
    print(f"\n📂 Анализ файла: {filename}")
    print()
    
    try:
        data = analyze_your_file(filename)
        
        print("\n" + "=" * 80)
        print("✅ АНАЛИЗ ЗАВЕРШЕН!")
        print("=" * 80)
        
        print("\n💡 ЧТО ДАЛЬШЕ:")
        print("   1. Запустите программу: python gui_app.py")
        print("   2. Загрузите этот же файл через интерфейс")
        print("   3. Выберите параметры и создайте документы")
        print("   4. ВСЕ данные будут взяты автоматически!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\nПроверьте:")
        print("  • Файл существует")
        print("  • Листы 'Эксель' и 'расценки' присутствуют")
        print("  • Файл не поврежден")
