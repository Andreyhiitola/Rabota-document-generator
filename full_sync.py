#!/usr/bin/env python3
import os
from datetime import datetime
import pandas as pd
from dropbox import Dropbox
from dropbox.exceptions import HttpError
import requests

print(f"[{(datetime.now())}] Trello → data.xls → Dropbox...")

# .env переменные (добавь в .env!)
DROPBOX_TOKEN = os.getenv('DROPBOX_TOKEN')
TRELLO_KEY = os.getenv('TRELLO_KEY') 
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')  # Получи из URL доски

if not all([DROPBOX_TOKEN, TRELLO_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID]):
    print("❌ .env неполный! Добавь TRELLO_* переменные")
    exit(1)

# 1. Trello API → JSON
print("📥 Trello данные...")
url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
params = {
    'key': TRELLO_KEY,
    'token': TRELLO_TOKEN,
    'fields': 'name,desc,due,lastActivity,idList'
}

response = requests.get(url, params=params)
cards = response.json()

data = []
for card in cards:
    # Получаем название списка
    list_url = f"https://api.trello.com/1/lists/{card['idList']}"
    list_params = {'key': TRELLO_KEY, 'token': TRELLO_TOKEN, 'fields': 'name'}
    list_name = requests.get(list_url, params=list_params).json()['name']
    
    data.append({
        'Список': list_name,
        'Название': card['name'],
        'Описание': card.get('desc', ''),
        'Дата активности': card.get('lastActivity', ''),
        'Дедлайн': card.get('due', ''),
        'URL': f"https://trello.com/c/{card['id']}"
    })

print(f"📊 Найдено {len(data)} карточек")

# 2. Excel файл
os.makedirs('data', exist_ok=True)
df = pd.DataFrame(data)
data_path = 'data/data.xls'
df.to_excel(data_path, index=False)
print(f"✅ data.xls создан: {data_path}")

# 3. Dropbox
print("📤 Dropbox...")
dbx = Dropbox(DROPBOX_TOKEN)
with open(data_path, 'rb') as f:
    dbx.files_upload(f.read(), '/data/data.xls', mode=dropbox.files.WriteMode('overwrite'))
print("✅ data.xls в Dropbox/data/data.xls")

print(f"✅ ГОТОВО: {datetime.now()}")
