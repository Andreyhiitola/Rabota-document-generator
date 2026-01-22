#!/usr/bin/env python3
"""
Главный скрипт полной синхронизации
Dropbox → Локально → Обновление из Trello → Dropbox
"""

import os
import sys
import logging
from datetime import datetime

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dropbox_sync import sync_with_dropbox
    from sync_trello_severen import sync_trello_to_excel
except ImportError as e:
    print(f"❌ Ошибка импорта модулей: {e}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/full_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def full_sync():
    """Полная синхронизация Dropbox ↔ Trello ↔ Excel"""
    
    logger.info("=" * 80)
    logger.info("🚀 ЗАПУСК ПОЛНОЙ СИНХРОНИЗАЦИИ")
    logger.info("=" * 80)
    logger.info(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Получение переменных окружения
    dropbox_token = os.getenv('DROPBOX_TOKEN')
    dropbox_file_path = os.getenv('DROPBOX_FILE_PATH')
    local_file = os.getenv('EXCEL_FILE_PATH', '/app/excel_files/workbook.xlsx')
    
    # Проверка конфигурации
    if not dropbox_token:
        logger.error("❌ Не задан DROPBOX_TOKEN")
        logger.error("   Установите переменную окружения!")
        return False
    
    if not dropbox_file_path:
        logger.warning("⚠️ DROPBOX_FILE_PATH не задан")
        logger.info("   Будет использован автопоиск файла по имени")
        # Попытка извлечь имя файла из локального пути
        filename = os.path.basename(local_file)
    else:
        filename = None
    
    try:
        # ШАГ 1: Скачивание файла из Dropbox
        logger.info("")
        logger.info("=" * 80)
        logger.info("ШАГ 1/3: СКАЧИВАНИЕ ИЗ DROPBOX")
        logger.info("=" * 80)
        
        # Создание директории для файла
        os.makedirs(os.path.dirname(local_file), exist_ok=True)
        
        success = sync_with_dropbox(
            token=dropbox_token,
            local_file=local_file,
            dropbox_file=dropbox_file_path,
            filename=filename or "рабочая",  # поиск по ключевому слову
            download_only=True
        )
        
        if not success:
            logger.error("❌ Не удалось скачать файл из Dropbox")
            return False
        
        logger.info("✅ Файл успешно скачан")
        
        # ШАГ 2: Синхронизация данных из Trello
        logger.info("")
        logger.info("=" * 80)
        logger.info("ШАГ 2/3: СИНХРОНИЗАЦИЯ TRELLO → EXCEL")
        logger.info("=" * 80)
        
        success = sync_trello_to_excel(local_file)
        
        if not success:
            logger.error("❌ Не удалось синхронизировать данные из Trello")
            return False
        
        logger.info("✅ Данные из Trello синхронизированы")
        
        # ШАГ 3: Загрузка обновлённого файла в Dropbox
        logger.info("")
        logger.info("=" * 80)
        logger.info("ШАГ 3/3: ЗАГРУЗКА В DROPBOX")
        logger.info("=" * 80)
        
        # Если путь не был задан, используем найденный на шаге 1
        if not dropbox_file_path:
            # Нужно получить путь из предыдущего шага
            # Для простоты используем тот же механизм поиска
            from dropbox_sync import DropboxSync
            sync_obj = DropboxSync(dropbox_token)
            if sync_obj.connect():
                dropbox_file_path = sync_obj.find_file(filename or "рабочая")
        
        if not dropbox_file_path:
            logger.error("❌ Не удалось определить путь к файлу в Dropbox")
            return False
        
        success = sync_with_dropbox(
            token=dropbox_token,
            local_file=local_file,
            dropbox_file=dropbox_file_path,
            upload_only=True
        )
        
        if not success:
            logger.error("❌ Не удалось загрузить файл в Dropbox")
            return False
        
        logger.info("✅ Файл успешно загружен в Dropbox")
        
        # ИТОГИ
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ПОЛНАЯ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        logger.info("=" * 80)
        logger.info(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        
        return True
        
    except Exception as e:
        logger.error("")
        logger.error("=" * 80)
        logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА")
        logger.error("=" * 80)
        logger.error(f"Ошибка: {e}")
        
        import traceback
        traceback.print_exc()
        
        return False


if __name__ == "__main__":
    success = full_sync()
    sys.exit(0 if success else 1)
