#!/usr/bin/env python3
"""
Скрипт загрузки нового Excel файла в Dropbox
"""

import dropbox
import os
from dotenv import load_dotenv

load_dotenv()

DROPBOX_REFRESH_TOKEN = os.getenv('DROPBOX_REFRESH_TOKEN')
DROPBOX_APP_KEY = os.getenv('DROPBOX_APP_KEY')
DROPBOX_APP_SECRET = os.getenv('DROPBOX_APP_SECRET')

LOCAL_FILE = 'Рабочие_табл_СМР_v2.xlsx'
DROPBOX_PATH = '/Рабочие_табл_СМР_v2.xlsx'
OLD_FILE = '/Рабочие таб СЕВЕРЕН _2026_Новый_форма.xlsx'

def upload_to_dropbox():
    """Загружает файл в Dropbox"""

    print("🔄 Подключение к Dropbox...")
    dbx = dropbox.Dropbox(
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
        app_key=DROPBOX_APP_KEY,
        app_secret=DROPBOX_APP_SECRET
    )

    # Проверяем подключение
    account = dbx.users_get_current_account()
    print(f"✅ Подключен: {account.name.display_name}")

    # Удаляем старый файл если существует
    try:
        print(f"\n🗑️  Удаляю старый файл: {OLD_FILE}")
        dbx.files_delete_v2(OLD_FILE)
        print("✅ Старый файл удален")
    except dropbox.exceptions.ApiError as e:
        print(f"⚠️  Старый файл не найден (это OK)")

    # Загружаем новый файл
    print(f"\n📤 Загружаю новый файл: {LOCAL_FILE} → {DROPBOX_PATH}")

    if not os.path.exists(LOCAL_FILE):
        print(f"❌ Файл не найден: {LOCAL_FILE}")
        return

    with open(LOCAL_FILE, 'rb') as f:
        file_data = f.read()
        file_size = len(file_data)

        # Загружаем с перезаписью
        dbx.files_upload(
            file_data,
            DROPBOX_PATH,
            mode=dropbox.files.WriteMode.overwrite
        )

        print(f"✅ Файл загружен успешно ({file_size / 1024:.1f} KB)")
        print(f"   Путь в Dropbox: {DROPBOX_PATH}")

    print("\n✅ Готово! Теперь на VPS запустите:")
    print("   docker-compose restart severen-auto-sync")
    print("   docker-compose up -d severen-trello-sync")

if __name__ == '__main__':
    try:
        upload_to_dropbox()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
