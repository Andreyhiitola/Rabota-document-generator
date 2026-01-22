#!/usr/bin/env python3
"""
Модуль интеграции с Dropbox
Скачивание, обновление и загрузка Excel файлов
"""

import os
import sys
import logging
from datetime import datetime

try:
    import dropbox
    from dropbox.exceptions import ApiError, AuthError
except ImportError:
    print("❌ Модуль dropbox не установлен")
    print("   Установите: pip install dropbox")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DropboxSync:
    """Синхронизация файлов с Dropbox"""
    
    def __init__(self, token: str):
        """
        Args:
            token: Dropbox API токен
        """
        self.token = token
        self.dbx = None
        
    def connect(self):
        """Подключение к Dropbox"""
        logger.info("Подключение к Dropbox...")
        try:
            self.dbx = dropbox.Dropbox(self.token)
            # Проверка подключения
            account = self.dbx.users_get_current_account()
            logger.info(f"✅ Подключен к Dropbox")
            logger.info(f"   Аккаунт: {account.name.display_name}")
            logger.info(f"   Email: {account.email}")
            return True
        except AuthError as e:
            logger.error(f"❌ Ошибка авторизации Dropbox: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Dropbox: {e}")
            return False
    
    def find_file(self, filename: str) -> str:
        """
        Найти файл в Dropbox по имени
        
        Args:
            filename: Имя файла для поиска
            
        Returns:
            Путь к файлу или None
        """
        logger.info(f"Поиск файла: {filename}")
        
        try:
            # Поиск в корне
            result = self.dbx.files_list_folder("")
            
            def search_recursive(path):
                """Рекурсивный поиск"""
                try:
                    result = self.dbx.files_list_folder(path)
                    for entry in result.entries:
                        if isinstance(entry, dropbox.files.FileMetadata):
                            if filename.lower() in entry.name.lower():
                                logger.info(f"✅ Найден файл: {entry.path_display}")
                                return entry.path_display
                        elif isinstance(entry, dropbox.files.FolderMetadata):
                            found = search_recursive(entry.path_lower)
                            if found:
                                return found
                except Exception as e:
                    logger.debug(f"Не удалось прочитать папку {path}: {e}")
                return None
            
            # Поиск по всем файлам и папкам
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    if filename.lower() in entry.name.lower():
                        logger.info(f"✅ Найден файл: {entry.path_display}")
                        return entry.path_display
                elif isinstance(entry, dropbox.files.FolderMetadata):
                    found = search_recursive(entry.path_lower)
                    if found:
                        return found
            
            logger.warning(f"⚠️ Файл не найден: {filename}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска файла: {e}")
            return None
    
    def download_file(self, dropbox_path: str, local_path: str) -> bool:
        """
        Скачать файл из Dropbox
        
        Args:
            dropbox_path: Путь к файлу в Dropbox
            local_path: Локальный путь для сохранения
            
        Returns:
            True если успешно
        """
        logger.info(f"Скачивание файла из Dropbox...")
        logger.info(f"  Источник: {dropbox_path}")
        logger.info(f"  Назначение: {local_path}")
        
        try:
            # Создание директории если нужно
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Скачивание файла
            metadata, response = self.dbx.files_download(dropbox_path)
            
            # Сохранение локально
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(local_path) / 1024  # KB
            logger.info(f"✅ Файл скачан успешно ({file_size:.1f} KB)")
            logger.info(f"   Изменён в Dropbox: {metadata.server_modified}")
            
            return True
            
        except ApiError as e:
            logger.error(f"❌ Ошибка API Dropbox: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка скачивания файла: {e}")
            return False
    
    def upload_file(self, local_path: str, dropbox_path: str) -> bool:
        """
        Загрузить файл в Dropbox
        
        Args:
            local_path: Локальный путь к файлу
            dropbox_path: Путь в Dropbox для сохранения
            
        Returns:
            True если успешно
        """
        logger.info(f"Загрузка файла в Dropbox...")
        logger.info(f"  Источник: {local_path}")
        logger.info(f"  Назначение: {dropbox_path}")
        
        try:
            if not os.path.exists(local_path):
                logger.error(f"❌ Локальный файл не найден: {local_path}")
                return False
            
            # Чтение файла
            with open(local_path, 'rb') as f:
                file_data = f.read()
            
            file_size = len(file_data) / 1024  # KB
            
            # Загрузка с перезаписью
            mode = dropbox.files.WriteMode.overwrite
            metadata = self.dbx.files_upload(
                file_data,
                dropbox_path,
                mode=mode,
                mute=True
            )
            
            logger.info(f"✅ Файл загружен успешно ({file_size:.1f} KB)")
            logger.info(f"   Путь в Dropbox: {metadata.path_display}")
            logger.info(f"   Revision: {metadata.rev}")
            
            return True
            
        except ApiError as e:
            logger.error(f"❌ Ошибка API Dropbox: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки файла: {e}")
            return False
    
    def get_file_info(self, dropbox_path: str) -> dict:
        """
        Получить информацию о файле
        
        Args:
            dropbox_path: Путь к файлу в Dropbox
            
        Returns:
            Словарь с информацией или None
        """
        try:
            metadata = self.dbx.files_get_metadata(dropbox_path)
            
            if isinstance(metadata, dropbox.files.FileMetadata):
                return {
                    'name': metadata.name,
                    'path': metadata.path_display,
                    'size': metadata.size,
                    'modified': metadata.server_modified,
                    'rev': metadata.rev
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о файле: {e}")
            return None


def sync_with_dropbox(
    token: str,
    local_file: str,
    dropbox_file: str = None,
    filename: str = None,
    download_only: bool = False,
    upload_only: bool = False
) -> bool:
    """
    Полная синхронизация с Dropbox
    
    Args:
        token: Dropbox токен
        local_file: Локальный путь к файлу
        dropbox_file: Путь к файлу в Dropbox (или None для автопоиска)
        filename: Имя файла для поиска (если dropbox_file не указан)
        download_only: Только скачать файл
        upload_only: Только загрузить файл
        
    Returns:
        True если успешно
    """
    sync = DropboxSync(token)
    
    # Подключение
    if not sync.connect():
        return False
    
    # Определение пути в Dropbox
    if not dropbox_file:
        if not filename:
            logger.error("❌ Не указан ни dropbox_file, ни filename")
            return False
        
        logger.info(f"Автопоиск файла: {filename}")
        dropbox_file = sync.find_file(filename)
        
        if not dropbox_file:
            logger.error(f"❌ Файл не найден в Dropbox: {filename}")
            return False
    
    # Скачивание
    if not upload_only:
        logger.info("=" * 80)
        logger.info("СКАЧИВАНИЕ ИЗ DROPBOX")
        logger.info("=" * 80)
        
        if not sync.download_file(dropbox_file, local_file):
            return False
    
    # Загрузка (если не только скачивание)
    if not download_only:
        logger.info("=" * 80)
        logger.info("ЗАГРУЗКА В DROPBOX")
        logger.info("=" * 80)
        
        if not sync.upload_file(local_file, dropbox_file):
            return False
    
    logger.info("=" * 80)
    logger.info("✅ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА")
    logger.info("=" * 80)
    
    return True


# ========================================================================
# ТОЧКА ВХОДА
# ========================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Синхронизация с Dropbox')
    parser.add_argument('--token', required=True, help='Dropbox API токен')
    parser.add_argument('--local', required=True, help='Локальный путь к файлу')
    parser.add_argument('--dropbox', help='Путь к файлу в Dropbox')
    parser.add_argument('--filename', help='Имя файла для автопоиска')
    parser.add_argument('--download-only', action='store_true', help='Только скачать')
    parser.add_argument('--upload-only', action='store_true', help='Только загрузить')
    
    args = parser.parse_args()
    
    success = sync_with_dropbox(
        token=args.token,
        local_file=args.local,
        dropbox_file=args.dropbox,
        filename=args.filename,
        download_only=args.download_only,
        upload_only=args.upload_only
    )
    
    sys.exit(0 if success else 1)
