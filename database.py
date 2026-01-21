#!/usr/bin/env python3
"""
Модуль для работы с базой данных
Сохранение истории созданных документов, статистика, поиск
"""

import sqlite3
from datetime import datetime
import json
import os


class DocumentDatabase:
    """База данных для хранения истории документов"""
    
    def __init__(self, db_path='documents.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица документов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_number TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                start_date TEXT,
                end_date TEXT,
                total_amount REAL,
                services_json TEXT,
                file_path TEXT,
                notes TEXT
            )
        ''')
        
        # Таблица услуг (для статистики)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                service_type INTEGER,
                service_desc TEXT,
                price REAL,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        ''')
        
        # Индексы для быстрого поиска
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_number ON documents(task_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON documents(created_at)')
        
        conn.commit()
        conn.close()
    
    def save_document(self, task_number, doc_type, start_date, end_date, services, file_path, notes=''):
        """Сохранение информации о созданном документе"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        total_amount = sum(s.get('price', 0) for s in services)
        services_json = json.dumps(services, ensure_ascii=False)
        
        cursor.execute('''
            INSERT INTO documents (task_number, doc_type, start_date, end_date, total_amount, services_json, file_path, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_number, doc_type, start_date, end_date, total_amount, services_json, file_path, notes))
        
        document_id = cursor.lastrowid
        
        # Сохранение услуг
        for service in services:
            cursor.execute('''
                INSERT INTO services (document_id, service_type, service_desc, price)
                VALUES (?, ?, ?, ?)
            ''', (document_id, service.get('type'), service.get('description', ''), service.get('price', 0)))
        
        conn.commit()
        conn.close()
        
        return document_id
    
    def get_documents(self, task_number=None, doc_type=None, date_from=None, date_to=None):
        """Получение списка документов с фильтрацией"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM documents WHERE 1=1'
        params = []
        
        if task_number:
            query += ' AND task_number = ?'
            params.append(task_number)
        
        if doc_type:
            query += ' AND doc_type = ?'
            params.append(doc_type)
        
        if date_from:
            query += ' AND created_at >= ?'
            params.append(date_from)
        
        if date_to:
            query += ' AND created_at <= ?'
            params.append(date_to)
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        documents = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return documents
    
    def get_statistics(self, period='month'):
        """Получение статистики по документам"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Общая статистика
        stats = {}
        
        # Количество документов
        cursor.execute('SELECT doc_type, COUNT(*) as count FROM documents GROUP BY doc_type')
        stats['by_type'] = dict(cursor.fetchall())
        
        # Сумма по месяцам
        cursor.execute('''
            SELECT strftime('%Y-%m', created_at) as month, SUM(total_amount) as total
            FROM documents
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        ''')
        stats['by_month'] = dict(cursor.fetchall())
        
        # Популярные услуги
        cursor.execute('''
            SELECT service_type, service_desc, COUNT(*) as count, SUM(price) as total
            FROM services
            GROUP BY service_type
            ORDER BY count DESC
        ''')
        stats['popular_services'] = [
            {
                'type': row[0],
                'description': row[1],
                'count': row[2],
                'total': row[3]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return stats
    
    def search_documents(self, search_text):
        """Поиск документов по тексту"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM documents
            WHERE task_number LIKE ? OR notes LIKE ? OR services_json LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
        
        documents = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return documents
    
    def delete_document(self, document_id):
        """Удаление документа из базы"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Удаление услуг
        cursor.execute('DELETE FROM services WHERE document_id = ?', (document_id,))
        
        # Удаление документа
        cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
        
        conn.commit()
        conn.close()
    
    def export_to_excel(self, output_file='statistics.xlsx'):
        """Экспорт статистики в Excel"""
        import pandas as pd
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        
        # Получение данных
        documents = self.get_documents()
        stats = self.get_statistics()
        
        # Создание Excel файла
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Лист с документами
            df_docs = pd.DataFrame(documents)
            df_docs.to_excel(writer, sheet_name='Документы', index=False)
            
            # Лист со статистикой по типам
            if stats['by_type']:
                df_types = pd.DataFrame(list(stats['by_type'].items()), columns=['Тип', 'Количество'])
                df_types.to_excel(writer, sheet_name='По типам', index=False)
            
            # Лист со статистикой по месяцам
            if stats['by_month']:
                df_months = pd.DataFrame(list(stats['by_month'].items()), columns=['Месяц', 'Сумма'])
                df_months.to_excel(writer, sheet_name='По месяцам', index=False)
            
            # Лист с популярными услугами
            if stats['popular_services']:
                df_services = pd.DataFrame(stats['popular_services'])
                df_services.to_excel(writer, sheet_name='Услуги', index=False)
        
        return output_file
    
    def backup_database(self, backup_path=None):
        """Создание резервной копии базы данных"""
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'backup_documents_{timestamp}.db'
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        
        return backup_path


# Пример использования
if __name__ == '__main__':
    db = DocumentDatabase()
    
    # Сохранение документа
    services = [
        {'type': 1, 'description': 'Консультация', 'price': 1850},
        {'type': 4, 'description': 'Согласование', 'price': 8600}
    ]
    
    doc_id = db.save_document(
        task_number='11-1',
        doc_type='zadanie',
        start_date='01.11.2025',
        end_date='03.12.2025',
        services=services,
        file_path='output/Задание_11-1.docx',
        notes='Тестовый документ'
    )
    
    print(f"Документ сохранен с ID: {doc_id}")
    
    # Получение статистики
    stats = db.get_statistics()
    print("\nСтатистика:")
    print(f"По типам: {stats['by_type']}")
    print(f"По месяцам: {stats['by_month']}")
    
    # Экспорт в Excel
    excel_file = db.export_to_excel()
    print(f"\nСтатистика экспортирована в: {excel_file}")
