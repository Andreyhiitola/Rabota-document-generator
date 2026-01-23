#!/usr/bin/env python3
import requests
import openpyxl
from datetime import datetime
import os

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
EXCEL_FILE = '/app/files/Рабочие_табл_СМР_v2.xlsx'

class TrelloExcelSync:
    def __init__(self, api_key, token, board_id):
        self.api_key = api_key
        self.token = token
        self.board_id = board_id
        self.base_url = 'https://api.trello.com/1'
        
    def get_lists(self):
        """Получить все списки на доске"""
        url = f"{self.base_url}/boards/{self.board_id}/lists"
        params = {'key': self.api_key, 'token': self.token}
        response = requests.get(url, params=params)
        return response.json()
    
    def create_card(self, name, list_id, desc='', due_date=None, start_date=None):
        """Создать новую карточку"""
        url = f"{self.base_url}/cards"
        params = {
            'key': self.api_key,
            'token': self.token,
            'name': name,
            'idList': list_id,
            'desc': desc
        }
        
        if due_date:
            params['due'] = due_date.isoformat()
        if start_date:
            params['start'] = start_date.isoformat()
            
        response = requests.post(url, params=params)
        return response.json()
    
    def sync_to_trello(self, excel_file):
        """Синхронизировать Excel → Trello"""
        wb = openpyxl.load_workbook(excel_file)
        ws = wb['Работы']
        
        lists = self.get_lists()
        list_map = {l['name']: l['id'] for l in lists}
        
        for row in ws.iter_rows(min_row=2, values_only=False):
            if row[0].value == 'x':
                continue
            
            address = row[3].value  # D
            start_date = row[4].value  # E
            end_date = row[5].value  # F
            client = row[6].value  # G
            executor = row[7].value  # H
            status = row[8].value  # I
            service = row[9].value  # J
            price = row[10].value  # K
            transit = row[12].value  # M
            note = row[13].value  # N
            
            if not address:
                continue
            
            desc_parts = []
            if client:
                desc_parts.append(f"**Клиент:** {client}")
            if executor:
                desc_parts.append(f"**Исполнитель:** {executor}")
            if service:
                desc_parts.append(f"**Услуга:** {service}")
            if price:
                desc_parts.append(f"**Стоимость:** {price} руб.")
            if transit:
                desc_parts.append(f"\n**Транзитные адреса:**\n{transit}")
            if note:
                desc_parts.append(f"\n**Примечание:**\n{note}")
            
            description = '\n'.join(desc_parts)
            
            list_id = list_map.get(status) or list(list_map.values())[0]
            
            try:
                card = self.create_card(
                    name=address,
                    list_id=list_id,
                    desc=description,
                    start_date=start_date if isinstance(start_date, datetime) else None,
                    due_date=end_date if isinstance(end_date, datetime) else None
                )
                print(f"✅ Создана карточка: {address[:50]}...")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        print(f"\n✅ Синхронизация Excel → Trello завершена")

if __name__ == '__main__':
    syncer = TrelloExcelSync(TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID)
    syncer.sync_to_trello(EXCEL_FILE)
