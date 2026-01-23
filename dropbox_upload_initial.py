#!/usr/bin/env python3
import dropbox
from dropbox.exceptions import ApiError
import os

DROPBOX_TOKEN = os.getenv('DROPBOX_TOKEN')
DROPBOX_PATH = '/Рабочие таб СЕВЕРЕН _2026_Новый_форма.xlsx'
LOCAL_FILE = '/app/files/Рабочие_табл_СМР_v2.xlsx'

def upload_to_dropbox(local_path, dropbox_path):
    """Загрузить Excel файл в Dropbox"""
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    
    try:
        with open(local_path, 'rb') as f:
            file_data = f.read()
            
        dbx.files_upload(
            file_data,
            dropbox_path,
            mode=dropbox.files.WriteMode('overwrite')
        )
        
        print(f"✅ Файл загружен в Dropbox: {dropbox_path}")
        return True
        
    except ApiError as e:
        print(f"❌ Ошибка Dropbox API: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == '__main__':
    upload_to_dropbox(LOCAL_FILE, DROPBOX_PATH)
