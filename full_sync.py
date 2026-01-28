#!/usr/bin/env python3
import os
import dropbox
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv()

class DropboxAuth:
    def __init__(self):
        self.app_key = os.getenv('DROPBOX_APP_KEY')
        self.app_secret = os.getenv('DROPBOX_APP_SECRET')
        self.refresh_token = os.getenv('DROPBOX_REFRESH_TOKEN')
    
    def get_client(self):
        response = requests.post('https://api.dropbox.com/oauth2/token', data={
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.app_key,
            'client_secret': self.app_secret,
        }).json()
        return dropbox.Dropbox(response['access_token'])

def create_folder_if_not_exists(dbx, folder_path):
    """Создает папку в Dropbox если не существует"""
    try:
        dbx.files_list_folder(folder_path)
    except:
        dbx.files_create_folder_v2(folder_path)
        print(f"📁 Создана папка: {folder_path}")

def sync_data_only():
    print(f"[{datetime.now()}] Синхронизация data/ (Trello)...")
    
    auth = DropboxAuth()
    dbx = auth.get_client()
    
    folder = 'data'
    
    # 1. Создаем папку data/ если не существует
    create_folder_if_not_exists(dbx, f'/{folder}')
    
    # 2. Локальная папка
    os.makedirs(folder, exist_ok=True)
    
    # 3. Dropbox/data → Локально
    try:
        result = dbx.files_list_folder(f'/{folder}')
        print(f"📂 data/: {len(result.entries)} файлов")
        
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                local_file = Path(folder) / entry.name
                local_file.parent.mkdir(parents=True, exist_ok=True)
                dbx.files_download_to_file(local_file, f'/{folder}/{entry.name}')
                print(f"📥 data/{entry.name}")
    except Exception as e:
        print(f"⚠️ data/ пуста: {e}")
    
    # 4. Локально/data → Dropbox
    for local_file in Path(folder).rglob('*'):
        if local_file.is_file():
            dbx_path = f'/{folder}/{local_file.relative_to(folder)}'
            with open(local_file, 'rb') as f:
                dbx.files_upload(f.read(), dbx_path, 
                               mode=dropbox.files.WriteMode('overwrite'))
            print(f"📤 {dbx_path}")
    
    print(f"✅ data/ синхронизирована: {datetime.now()}")

if __name__ == '__main__':
    sync_data_only()
