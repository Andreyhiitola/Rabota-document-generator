#!/usr/bin/env python3
"""
Скрипт для автоматической оптимизации загрузки скриптов в HTML
Добавляет атрибуты defer/async к тегам <script>

Использование:
    python optimize_scripts.py index.html
"""

import re
import sys
from pathlib import Path

# Паттерны для внешних сервисов (получат async)
EXTERNAL_PATTERNS = [
    r'maxi-booking\.ru',
    r'googleapis\.com',
    r'google-analytics\.com',
    r'yandex\.ru/metrika',
    r'cdn\.',
    r'cloudflare\.com'
]

# Скрипты, которые не нужно трогать (критичные)
CRITICAL_SCRIPTS = [
    'CONFIG',  # Встроенный CONFIG
]

def is_external_script(src):
    """Проверяет, является ли скрипт внешним"""
    for pattern in EXTERNAL_PATTERNS:
        if re.search(pattern, src, re.IGNORECASE):
            return True
    return False

def is_critical_script(content):
    """Проверяет, является ли скрипт критичным"""
    for critical in CRITICAL_SCRIPTS:
        if critical in content:
            return True
    return False

def optimize_html(html_content):
    """Оптимизирует HTML, добавляя defer/async к скриптам"""
    
    lines = html_content.split('\n')
    optimized_lines = []
    stats = {
        'total': 0,
        'defer_added': 0,
        'async_added': 0,
        'skipped_critical': 0,
        'skipped_already': 0
    }
    
    in_head = False
    body_scripts = []
    
    for i, line in enumerate(lines):
        # Отслеживаем, где мы находимся
        if '<head>' in line.lower():
            in_head = True
        elif '</head>' in line.lower():
            in_head = False
        
        # Ищем теги <script>
        if '<script' in line and not '<!--' in line:
            stats['total'] += 1
            
            # Пропускаем, если уже есть defer или async
            if 'defer' in line or 'async' in line:
                stats['skipped_already'] += 1
                optimized_lines.append(line)
                continue
            
            # Пропускаем критичные встроенные скрипты
            if 'src=' not in line and is_critical_script(line):
                stats['skipped_critical'] += 1
                optimized_lines.append(line)
                continue
            
            # Пропускаем встроенные скрипты в <head>
            if 'src=' not in line and in_head:
                stats['skipped_critical'] += 1
                optimized_lines.append(line)
                continue
            
            # Извлекаем src
            src_match = re.search(r'src=["\']([^"\']+)["\']', line)
            
            if src_match:
                src = src_match.group(1)
                
                # Внешние скрипты → async
                if is_external_script(src):
                    # Google Maps - особый случай (async defer)
                    if 'maps.googleapis.com' in src:
                        optimized_line = line.replace('<script ', '<script async defer ')
                    else:
                        optimized_line = line.replace('<script ', '<script async ')
                    stats['async_added'] += 1
                    print(f"✅ async: {src}")
                
                # Локальные скрипты → defer
                else:
                    optimized_line = line.replace('<script ', '<script defer ')
                    stats['defer_added'] += 1
                    print(f"✅ defer: {src}")
                
                optimized_lines.append(optimized_line)
            else:
                # Встроенный скрипт без src
                optimized_lines.append(line)
        else:
            optimized_lines.append(line)
    
    return '\n'.join(optimized_lines), stats

def main():
    if len(sys.argv) < 2:
        print("❌ Использование: python optimize_scripts.py index.html")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"❌ Файл не найден: {input_file}")
        sys.exit(1)
    
    # Создаём резервную копию
    backup_file = input_file.with_suffix('.html.backup')
    print(f"📦 Создание резервной копии: {backup_file}")
    backup_file.write_text(input_file.read_text(encoding='utf-8'))
    
    # Читаем оригинал
    print(f"📖 Чтение файла: {input_file}")
    html_content = input_file.read_text(encoding='utf-8')
    
    # Оптимизируем
    print("\n🔧 Оптимизация скриптов...\n")
    optimized_content, stats = optimize_html(html_content)
    
    # Сохраняем
    output_file = input_file.with_stem(f"{input_file.stem}_optimized")
    print(f"\n💾 Сохранение результата: {output_file}")
    output_file.write_text(optimized_content, encoding='utf-8')
    
    # Статистика
    print("\n" + "="*50)
    print("📊 СТАТИСТИКА ОПТИМИЗАЦИИ")
    print("="*50)
    print(f"Всего скриптов найдено: {stats['total']}")
    print(f"✅ Добавлено defer: {stats['defer_added']}")
    print(f"✅ Добавлено async: {stats['async_added']}")
    print(f"⏭️  Пропущено (критичные): {stats['skipped_critical']}")
    print(f"⏭️  Пропущено (уже оптимизированы): {stats['skipped_already']}")
    print("="*50)
    
    improvement = ((stats['defer_added'] + stats['async_added']) / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"\n🚀 Улучшение: ~{improvement:.0f}% скриптов оптимизировано")
    print(f"\n✅ Готово! Проверьте файл: {output_file}")
    print(f"📦 Резервная копия: {backup_file}")
    
    print("\n📝 Следующие шаги:")
    print("1. Откройте оптимизированный файл в браузере")
    print("2. Протестируйте все функции сайта")
    print("3. Проверьте консоль на ошибки (F12)")
    print("4. Если всё работает → замените оригинал")
    print("5. Измерьте производительность (Lighthouse)")

if __name__ == '__main__':
    main()
