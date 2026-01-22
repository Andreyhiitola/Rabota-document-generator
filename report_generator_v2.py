#!/usr/bin/env python3
"""
Генератор отчётов ПРИЛОЖЕНИЕ 1 и 3
Версия 2.0 - Чтение из листа Северен_новая
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
import logging
from calendar import monthrange

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, Border, Side
except ImportError:
    print("❌ Модуль openpyxl не установлен")
    print("   pip install openpyxl")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReportGeneratorV2:
    """Генератор отчётов из листа Северен_новая"""
    
    # Индексы колонок (из sync_trello_severen.py)
    COL_NUM = 1         # A - № (=ROW()-1)
    COL_HIDE = 2        # B - Скрыть (x)
    COL_ACT = 3         # C - Акты
    COL_DISTRICT = 4    # D - Район города
    COL_DESC = 5        # E - Описание
    COL_ADDRESS = 6     # F - Адрес предоставления услуги
    COL_DATE_START = 7  # G - Дата начала отчёта
    COL_DATE_END = 8    # H - Дата окончания отчёта  
    COL_PRICE = 9       # I - Стоимость
    COL_SERVICE = 10    # J - Вид услуги
    COL_STATUS = 18     # R - Статус
    COL_CLIENT = 22     # V - Клиент
    COL_WORK_START = 26 # Z - Начало работ
    COL_EXECUTOR = 28   # AB - Исполнитель
    
    def __init__(self, excel_file: str):
        self.excel_file = excel_file
        self.wb = None
        self.ws_data = None
        
    def load_workbook(self) -> bool:
        """Загрузка книги"""
        try:
            logger.info(f"📂 Загрузка: {self.excel_file}")
            self.wb = openpyxl.load_workbook(self.excel_file)
            
            # Ищем лист Северен_новая (как в sync_trello_severen.py)
            for name in self.wb.sheetnames:
                if 'Северен_новая' in name:
                    self.ws_data = self.wb[name]
                    logger.info(f"✅ Рабочий лист: {name}")
                    break
            
            if not self.ws_data:
                logger.error("❌ Лист 'Северен_новая' не найден")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            return False
    
    def extract_data_for_month(self, month: int, year: int) -> List[Dict]:
        """
        Извлечение данных за месяц
        
        Args:
            month: Месяц (1-12)
            year: Год
            
        Returns:
            Список словарей с данными работ
        """
        logger.info(f"📊 Извлечение данных за {month:02d}.{year}")
        
        # Границы месяца
        _, last_day = monthrange(year, month)
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, last_day, 23, 59, 59)
        
        data = []
        
        # Проходим по строкам (со 2-й, т.к. 1-я - заголовок)
        for row_idx in range(2, self.ws_data.max_row + 1):
            # Проверяем скрыта ли строка
            hide_marker = self.ws_data.cell(row_idx, self.COL_HIDE).value
            if hide_marker and str(hide_marker).strip().lower() == 'x':
                continue
            
            # Адрес (обязательное поле)
            address = self.ws_data.cell(row_idx, self.COL_ADDRESS).value
            if not address or str(address).strip() == '':
                continue
            
            # Дата начала отчёта (колонка G)
            date_cell = self.ws_data.cell(row_idx, self.COL_DATE_START).value
            
            if not date_cell:
                continue
                
            try:
                # Парсим дату
                if isinstance(date_cell, datetime):
                    work_date = date_cell
                else:
                    # Пробуем разные форматы
                    date_str = str(date_cell).strip()
                    try:
                        work_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    except:
                        try:
                            work_date = datetime.strptime(date_str, '%Y-%m-%d')
                        except:
                            continue
                
                # Проверяем попадание в месяц
                if not (start_date <= work_date <= end_date):
                    continue
                    
            except (ValueError, TypeError):
                continue
            
            # Извлекаем данные строки
            work_data = {
                'row': row_idx,
                'address': str(address).strip(),
                'district': self.ws_data.cell(row_idx, self.COL_DISTRICT).value,
                'date_start': date_cell,
                'date_end': self.ws_data.cell(row_idx, self.COL_DATE_END).value,
                'price': self.ws_data.cell(row_idx, self.COL_PRICE).value,
                'service': self.ws_data.cell(row_idx, self.COL_SERVICE).value,
                'status': self.ws_data.cell(row_idx, self.COL_STATUS).value,
                'client': self.ws_data.cell(row_idx, self.COL_CLIENT).value,
                'work_start': self.ws_data.cell(row_idx, self.COL_WORK_START).value,
                'executor': self.ws_data.cell(row_idx, self.COL_EXECUTOR).value,
            }
            
            data.append(work_data)
        
        logger.info(f"✅ Найдено работ: {len(data)}")
        return data
    
    def update_prilozhenie_1(self, data: List[Dict], month: int, year: int) -> bool:
        """Обновление ПРИЛОЖЕНИЕ 1"""
        logger.info("📄 Обновление ПРИЛОЖЕНИЕ 1...")
        
        # Ищем лист
        sheet_name = None
        for name in self.wb.sheetnames:
            if 'прил_1' in name.lower() or ('акт' in name.lower() and '1' in name):
                sheet_name = name
                break
        
        if not sheet_name:
            logger.error("❌ Лист ПРИЛОЖЕНИЕ 1 не найден")
            return False
        
        ws = self.wb[sheet_name]
        
        # Стили
        header_font = Font(name='Arial', size=10, bold=True)
        normal_font = Font(name='Arial', size=9)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Ищем начало таблицы (строку с "№ п/п")
        start_row = None
        for row_idx in range(1, 20):
            cell_val = ws.cell(row_idx, 1).value
            if cell_val and '№' in str(cell_val):
                start_row = row_idx + 1
                break
        
        if not start_row:
            logger.error("❌ Не найдена таблица в ПРИЛОЖЕНИЕ 1")
            return False
        
        # Очищаем старые данные
        for row in ws.iter_rows(min_row=start_row, max_row=ws.max_row):
            for cell in row:
                cell.value = None
                cell.border = None
        
        # Заполняем новыми данными
        current_row = start_row
        
        for idx, work in enumerate(data, start=1):
            ws.cell(current_row, 1).value = idx
            ws.cell(current_row, 2).value = work['address']
            ws.cell(current_row, 3).value = work['work_start'] or work['date_start']
            ws.cell(current_row, 4).value = work['date_end']
            ws.cell(current_row, 5).value = work['service']
            
            # Стили
            for col in range(1, 6):
                cell = ws.cell(current_row, col)
                cell.font = normal_font
                cell.border = border
                cell.alignment = Alignment(vertical='center', wrap_text=True)
            
            current_row += 1
        
        logger.info(f"✅ ПРИЛОЖЕНИЕ 1: {len(data)} записей")
        return True
    
    def update_prilozhenie_3(self, data: List[Dict], month: int, year: int) -> bool:
        """Обновление ПРИЛОЖЕНИЕ 3"""
        logger.info("📄 Обновление ПРИЛОЖЕНИЕ 3...")
        
        # Ищем лист
        sheet_name = None
        for name in self.wb.sheetnames:
            if 'прил_3' in name.lower() or 'ведомость' in name.lower():
                sheet_name = name
                break
        
        if not sheet_name:
            logger.error("❌ Лист ПРИЛОЖЕНИЕ 3 не найден")
            return False
        
        ws = self.wb[sheet_name]
        
        # Стили
        header_font = Font(name='Arial', size=10, bold=True)
        normal_font = Font(name='Arial', size=9)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Ищем начало таблицы
        start_row = None
        for row_idx in range(1, 20):
            cell_val = ws.cell(row_idx, 1).value
            if cell_val and '№' in str(cell_val):
                start_row = row_idx + 1
                break
        
        if not start_row:
            logger.error("❌ Не найдена таблица в ПРИЛОЖЕНИЕ 3")
            return False
        
        # Очищаем старые данные
        for row in ws.iter_rows(min_row=start_row, max_row=ws.max_row):
            for cell in row:
                cell.value = None
                cell.border = None
        
        # Заполняем новыми данными
        current_row = start_row
        total_sum = 0
        
        for idx, work in enumerate(data, start=1):
            ws.cell(current_row, 1).value = idx
            ws.cell(current_row, 2).value = work['address']
            ws.cell(current_row, 3).value = work['service']
            
            # Стоимость
            price = work['price']
            if price:
                try:
                    price_val = float(price) if isinstance(price, (int, float)) else float(str(price).replace(' ', ''))
                    ws.cell(current_row, 4).value = price_val
                    total_sum += price_val
                except:
                    ws.cell(current_row, 4).value = 0
            else:
                ws.cell(current_row, 4).value = 0
            
            # Стили
            for col in range(1, 5):
                cell = ws.cell(current_row, col)
                cell.font = normal_font
                cell.border = border
                cell.alignment = Alignment(vertical='center', wrap_text=True)
            
            ws.cell(current_row, 4).alignment = Alignment(horizontal='right', vertical='center')
            
            current_row += 1
        
        # ИТОГО
        ws.cell(current_row, 1).value = "ИТОГО:"
        ws.cell(current_row, 1).font = header_font
        ws.cell(current_row, 4).value = total_sum
        ws.cell(current_row, 4).font = header_font
        
        for col in range(1, 5):
            ws.cell(current_row, col).border = border
        
        logger.info(f"✅ ПРИЛОЖЕНИЕ 3: {len(data)} записей, сумма: {total_sum:.2f} руб.")
        return True
    
    def save(self) -> bool:
        """Сохранение"""
        try:
            logger.info(f"💾 Сохранение...")
            self.wb.save(self.excel_file)
            logger.info("✅ Сохранено")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")
            return False


def generate_monthly_reports(excel_file: str, month: int, year: int) -> bool:
    """
    Генерация отчётов за месяц
    
    Args:
        excel_file: Путь к Excel файлу
        month: Месяц (1-12)
        year: Год
        
    Returns:
        True если успешно
    """
    logger.info("=" * 80)
    logger.info("📊 ГЕНЕРАЦИЯ ОТЧЁТОВ")
    logger.info("=" * 80)
    logger.info(f"Файл: {excel_file}")
    logger.info(f"Период: {month:02d}.{year}")
    logger.info("")
    
    try:
        # Создаём генератор
        generator = ReportGeneratorV2(excel_file)
        
        # Загружаем файл
        if not generator.load_workbook():
            return False
        
        # Извлекаем данные
        data = generator.extract_data_for_month(month, year)
        
        if not data:
            logger.warning("⚠️ Нет данных за указанный период")
            return False
        
        # Обновляем отчёты
        success1 = generator.update_prilozhenie_1(data, month, year)
        success2 = generator.update_prilozhenie_3(data, month, year)
        
        if not (success1 and success2):
            logger.error("❌ Ошибка обновления отчётов")
            return False
        
        # Сохраняем
        if not generator.save():
            return False
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ОТЧЁТЫ УСПЕШНО СФОРМИРОВАНЫ")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Генератор отчётов')
    parser.add_argument('--file', required=True, help='Путь к Excel файлу')
    parser.add_argument('--month', type=int, required=True, help='Месяц (1-12)')
    parser.add_argument('--year', type=int, required=True, help='Год')
    
    args = parser.parse_args()
    
    success = generate_monthly_reports(args.file, args.month, args.year)
    sys.exit(0 if success else 1)
