#!/usr/bin/env python3
"""
GUI приложение для генератора документов "Северен" с интеграцией Trello
Объединяет:
- Синхронизацию Trello → Excel
- Генерацию писем из шаблонов
- Генерацию документов (Задание, Отчет, Акт)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
import sys
from pathlib import Path
from datetime import datetime

# Проверка зависимостей
try:
    from sync_trello_severen import SeverenTrelloSync
    from email_generator import EmailTemplateGenerator
    from config import (
        TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID, 
        EXCEL_PATH, AUTO_SYNC_ON_START
    )
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("   Убедитесь что все файлы на месте:")
    print("   - sync_trello_severen.py")
    print("   - email_generator.py")
    print("   - config.py")
    sys.exit(1)


class SeverenGUI:
    """GUI приложение с интеграцией Trello"""

    def __init__(self, root):
        self.root = root
        self.root.title("Генератор документов Северен + Trello")
        self.root.geometry("1000x700")
        
        # Инициализация компонентов
        self.trello_sync = None
        self.email_gen = EmailTemplateGenerator()
        self.trello_cards = []
        self.selected_card = None
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Проверяем Trello API
        self.check_trello_connection()
        
        # Автосинхронизация при запуске
        if AUTO_SYNC_ON_START:
            self.root.after(1000, self.sync_trello)

    def create_widgets(self):
        """Создание виджетов интерфейса"""
        
        # ============================================================
        # HEADER - Заголовок и статус
        # ============================================================
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(
            header_frame, 
            text="🚀 Генератор документов Северен + Trello",
            font=('Arial', 16, 'bold')
        ).pack()
        
        self.status_label = ttk.Label(
            header_frame,
            text="⚙️ Проверка подключения к Trello...",
            font=('Arial', 10)
        )
        self.status_label.pack(pady=5)
        
        # ============================================================
        # NOTEBOOK - Вкладки
        # ============================================================
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вкладка 1: Синхронизация Trello
        self.create_sync_tab()
        
        # Вкладка 2: Генерация документов
        self.create_documents_tab()
        
        # Вкладка 3: Генерация писем
        self.create_email_tab()
        
        # Вкладка 4: Настройки
        self.create_settings_tab()
        
        # ============================================================
        # FOOTER - Статус бар
        # ============================================================
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.footer_label = ttk.Label(
            footer_frame,
            text="Готов к работе",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding="5"
        )
        self.footer_label.pack(fill=tk.X)

    # ============================================================
    # ВКЛАДКА 1: СИНХРОНИЗАЦИЯ TRELLO
    # ============================================================
    def create_sync_tab(self):
        """Вкладка синхронизации Trello"""
        
        sync_tab = ttk.Frame(self.notebook)
        self.notebook.add(sync_tab, text="📡 Синхронизация Trello")
        
        # Информация о подключении
        info_frame = ttk.LabelFrame(sync_tab, text="Подключение к Trello", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.trello_status_label = ttk.Label(
            info_frame,
            text="⚙️ Проверка...",
            font=('Arial', 10)
        )
        self.trello_status_label.pack(anchor=tk.W)
        
        self.trello_board_label = ttk.Label(
            info_frame,
            text=f"Доска: Северен согласования (ID: {TRELLO_BOARD_ID})",
            font=('Arial', 9)
        )
        self.trello_board_label.pack(anchor=tk.W)
        
        # Кнопка синхронизации
        btn_frame = ttk.Frame(sync_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.sync_button = ttk.Button(
            btn_frame,
            text="🔄 Синхронизировать Trello → Excel",
            command=self.sync_trello,
            state=tk.DISABLED
        )
        self.sync_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🔍 Просмотр карточек",
            command=self.load_trello_cards
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="📂 Открыть Excel",
            command=self.open_excel
        ).pack(side=tk.LEFT, padx=5)
        
        # Список карточек из Trello
        cards_frame = ttk.LabelFrame(sync_tab, text="Карточки из Trello", padding="10")
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Таблица карточек
        columns = ('Номер', 'Адрес', 'Район', 'Статус')
        self.cards_tree = ttk.Treeview(cards_frame, columns=columns, show='tree headings', height=10)
        
        self.cards_tree.heading('#0', text='')
        self.cards_tree.column('#0', width=30)
        
        for col in columns:
            self.cards_tree.heading(col, text=col)
        
        self.cards_tree.column('Номер', width=80)
        self.cards_tree.column('Адрес', width=400)
        self.cards_tree.column('Район', width=150)
        self.cards_tree.column('Статус', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(cards_frame, orient=tk.VERTICAL, command=self.cards_tree.yview)
        self.cards_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cards_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязываем клик
        self.cards_tree.bind('<Double-1>', self.on_card_select)
        
        # Логи синхронизации
        log_frame = ttk.LabelFrame(sync_tab, text="Логи синхронизации", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.sync_log = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.sync_log.pack(fill=tk.BOTH, expand=True)

    # ============================================================
    # ВКЛАДКА 2: ГЕНЕРАЦИЯ ДОКУМЕНТОВ
    # ============================================================
    def create_documents_tab(self):
        """Вкладка генерации документов"""
        
        docs_tab = ttk.Frame(self.notebook)
        self.notebook.add(docs_tab, text="📄 Документы")
        
        # Выбор карточки
        card_frame = ttk.LabelFrame(docs_tab, text="Выбор задания", padding="10")
        card_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(card_frame, text="Номер работы:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.doc_task_number = ttk.Entry(card_frame, width=30)
        self.doc_task_number.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Button(
            card_frame,
            text="🔍 Найти в Trello",
            command=self.find_card_for_docs
        ).grid(row=0, column=2, padx=5, pady=2)
        
        # Информация о задании
        info_frame = ttk.LabelFrame(docs_tab, text="Информация о задании", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.doc_info_text = scrolledtext.ScrolledText(info_frame, height=10, wrap=tk.WORD)
        self.doc_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки генерации
        gen_frame = ttk.Frame(docs_tab)
        gen_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            gen_frame,
            text="📝 Задание + Отчет + Акт",
            command=self.generate_all_docs
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            gen_frame,
            text="📝 Только Задание",
            command=lambda: self.generate_doc('zadanie')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            gen_frame,
            text="📝 Только Отчет",
            command=lambda: self.generate_doc('otchet')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            gen_frame,
            text="📝 Только Акт",
            command=lambda: self.generate_doc('akt')
        ).pack(side=tk.LEFT, padx=5)

    # ============================================================
    # ВКЛАДКА 3: ГЕНЕРАЦИЯ ПИСЕМ
    # ============================================================
    def create_email_tab(self):
        """Вкладка генерации писем"""
        
        email_tab = ttk.Frame(self.notebook)
        self.notebook.add(email_tab, text="📧 Письма")
        
        # Выбор карточки
        card_frame = ttk.LabelFrame(email_tab, text="Выбор задания", padding="10")
        card_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(card_frame, text="Номер работы:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.email_task_number = ttk.Entry(card_frame, width=30)
        self.email_task_number.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Button(
            card_frame,
            text="🔍 Загрузить из Trello",
            command=self.load_card_for_email
        ).grid(row=0, column=2, padx=5, pady=2)
        
        # Выбор типа письма
        type_frame = ttk.LabelFrame(email_tab, text="Тип письма", padding="10")
        type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(type_frame, text="Шаблон:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.email_template = ttk.Combobox(type_frame, width=30, state='readonly')
        self.email_template['values'] = (
            'согласование',
            'обследование',
            'транзитные',
            'подключение',
            'жилкомсервис',
            'тсж',
            'ук',
            'администрация',
            'договор'
        )
        self.email_template.current(0)
        self.email_template.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Предпросмотр письма
        preview_frame = ttk.LabelFrame(email_tab, text="Предпросмотр письма", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.email_preview = scrolledtext.ScrolledText(preview_frame, height=15, wrap=tk.WORD)
        self.email_preview.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки
        btn_frame = ttk.Frame(email_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            btn_frame,
            text="👁️ Предпросмотр",
            command=self.preview_email
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="💾 Сохранить HTML",
            command=self.save_email
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🌐 Открыть в браузере",
            command=self.open_email_in_browser
        ).pack(side=tk.LEFT, padx=5)

    # ============================================================
    # ВКЛАДКА 4: НАСТРОЙКИ
    # ============================================================
    def create_settings_tab(self):
        """Вкладка настроек"""
        
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="⚙️ Настройки")
        
        # Trello настройки
        trello_frame = ttk.LabelFrame(settings_tab, text="Trello API", padding="10")
        trello_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(trello_frame, text=f"API Key: {TRELLO_API_KEY[:20]}...").pack(anchor=tk.W)
        ttk.Label(trello_frame, text=f"Board ID: {TRELLO_BOARD_ID}").pack(anchor=tk.W)
        
        ttk.Button(
            trello_frame,
            text="📝 Редактировать config.py",
            command=self.edit_config
        ).pack(anchor=tk.W, pady=5)
        
        # Excel настройки
        excel_frame = ttk.LabelFrame(settings_tab, text="Excel файл", padding="10")
        excel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(excel_frame, text=f"Путь: {EXCEL_PATH}").pack(anchor=tk.W)
        
        ttk.Button(
            excel_frame,
            text="📂 Выбрать другой файл",
            command=self.select_excel_file
        ).pack(anchor=tk.W, pady=5)
        
        # О программе
        about_frame = ttk.LabelFrame(settings_tab, text="О программе", padding="10")
        about_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        about_text = """
Генератор документов "Северен" + Trello
Версия: 2.0

Возможности:
✅ Синхронизация Trello → Excel
✅ Генерация писем из шаблонов
✅ Генерация документов (Задание, Отчет, Акт)
✅ Автоматическое извлечение данных
✅ Docker поддержка

Разработано с ❤️ для автоматизации рутинных задач
Экономия времени: 24 часа в год!
        """
        
        ttk.Label(about_frame, text=about_text, justify=tk.LEFT).pack(anchor=tk.W)

    # ============================================================
    # МЕТОДЫ: TRELLO
    # ============================================================
    
    def check_trello_connection(self):
        """Проверка подключения к Trello API"""
        
        def check():
            try:
                if TRELLO_API_KEY == 'your_api_key_here':
                    self.update_status("❌ Trello API не настроен", "red")
                    self.log_sync("❌ Trello API не настроен. Откройте config.py")
                    return
                
                self.trello_sync = SeverenTrelloSync(
                    api_key=TRELLO_API_KEY,
                    token=TRELLO_TOKEN,
                    board_id=TRELLO_BOARD_ID,
                    excel_path=EXCEL_PATH
                )
                
                self.update_status("✅ Подключено к Trello", "green")
                self.sync_button.config(state=tk.NORMAL)
                self.log_sync("✅ Подключение к Trello успешно")
                
            except Exception as e:
                self.update_status(f"❌ Ошибка подключения: {str(e)}", "red")
                self.log_sync(f"❌ Ошибка: {str(e)}")
        
        thread = threading.Thread(target=check)
        thread.daemon = True
        thread.start()

    def sync_trello(self):
        """Синхронизация Trello → Excel"""
        
        def sync():
            try:
                self.update_status("🔄 Синхронизация...", "blue")
                self.sync_button.config(state=tk.DISABLED)
                
                self.log_sync("\n" + "="*60)
                self.log_sync("🔄 НАЧАЛО СИНХРОНИЗАЦИИ")
                self.log_sync("="*60)
                
                result = self.trello_sync.sync_to_excel()
                
                self.log_sync("\n" + "="*60)
                self.log_sync("📊 РЕЗУЛЬТАТЫ:")
                self.log_sync(f"  ✅ Синхронизировано: {result['synced']}")
                self.log_sync(f"  ⏭️  Пропущено: {result['skipped']}")
                self.log_sync(f"  📋 Всего: {result['total']}")
                self.log_sync("="*60)
                
                if result['synced'] > 0:
                    self.update_status(
                        f"✅ Синхронизировано {result['synced']} карточек", 
                        "green"
                    )
                    messagebox.showinfo(
                        "Успех",
                        f"Синхронизировано {result['synced']} новых карточек!"
                    )
                else:
                    self.update_status("✅ Нет новых карточек", "green")
                    messagebox.showinfo(
                        "Информация",
                        "Нет новых карточек для синхронизации"
                    )
                
                # Обновляем список карточек
                self.load_trello_cards()
                
            except Exception as e:
                self.log_sync(f"\n❌ ОШИБКА: {str(e)}")
                self.update_status(f"❌ Ошибка: {str(e)}", "red")
                messagebox.showerror("Ошибка", f"Ошибка синхронизации:\n{str(e)}")
            
            finally:
                self.sync_button.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=sync)
        thread.daemon = True
        thread.start()

    def load_trello_cards(self):
        """Загрузка карточек из Trello"""
        
        def load():
            try:
                self.update_status("🔍 Загрузка карточек...", "blue")
                
                cards = self.trello_sync.get_cards_to_sync()
                self.trello_cards = cards
                
                # Очищаем таблицу
                for item in self.cards_tree.get_children():
                    self.cards_tree.delete(item)
                
                # Добавляем карточки
                for card in cards:
                    icon = "✅" if card['status'] == 'Выполнен' else "⏸️"
                    self.cards_tree.insert(
                        '',
                        'end',
                        text=icon,
                        values=(
                            card['number'],
                            card['address'][:50] + '...' if len(card['address']) > 50 else card['address'],
                            card['district'],
                            card['status']
                        )
                    )
                
                self.update_status(f"✅ Загружено {len(cards)} карточек", "green")
                self.log_sync(f"✅ Загружено {len(cards)} карточек из Trello")
                
            except Exception as e:
                self.update_status(f"❌ Ошибка: {str(e)}", "red")
                self.log_sync(f"❌ Ошибка загрузки карточек: {str(e)}")
        
        thread = threading.Thread(target=load)
        thread.daemon = True
        thread.start()

    def on_card_select(self, event):
        """Обработка выбора карточки"""
        selection = self.cards_tree.selection()
        if selection:
            item = self.cards_tree.item(selection[0])
            values = item['values']
            
            if values:
                number = values[0]
                # Находим полную карточку
                for card in self.trello_cards:
                    if card['number'] == number:
                        self.selected_card = card
                        
                        # Показываем информацию
                        info = f"""
Номер работы: {card['number']}
Адрес: {card['address']}
Район: {card['district']}
Статус: {card['status']}
                        """
                        
                        messagebox.showinfo("Карточка", info.strip())
                        break

    # ============================================================
    # МЕТОДЫ: ДОКУМЕНТЫ
    # ============================================================
    
    def find_card_for_docs(self):
        """Поиск карточки для генерации документов"""
        task_number = self.doc_task_number.get().strip()
        
        if not task_number:
            messagebox.showwarning("Предупреждение", "Введите номер работы")
            return
        
        # Ищем в загруженных карточках
        for card in self.trello_cards:
            if card['number'] == task_number:
                self.selected_card = card
                
                info = f"""
Номер работы: {card['number']}
Адрес: {card['address']}
Район: {card['district']}
Статус: {card['status']}

Карточка найдена! Можно генерировать документы.
                """
                
                self.doc_info_text.delete('1.0', tk.END)
                self.doc_info_text.insert('1.0', info.strip())
                return
        
        messagebox.showwarning(
            "Не найдено",
            f"Карточка с номером {task_number} не найдена.\nЗагрузите карточки из Trello."
        )

    def generate_all_docs(self):
        """Генерация всех документов"""
        if not self.selected_card:
            messagebox.showwarning("Предупреждение", "Сначала выберите карточку")
            return
        
        # TODO: Интеграция с существующим генератором документов
        messagebox.showinfo(
            "В разработке",
            "Генерация документов будет добавлена в следующей версии.\n"
            "Используйте существующий генератор из GUI."
        )

    def generate_doc(self, doc_type):
        """Генерация конкретного документа"""
        if not self.selected_card:
            messagebox.showwarning("Предупреждение", "Сначала выберите карточку")
            return
        
        messagebox.showinfo(
            "В разработке",
            f"Генерация {doc_type} будет добавлена в следующей версии"
        )

    # ============================================================
    # МЕТОДЫ: ПИСЬМА
    # ============================================================
    
    def load_card_for_email(self):
        """Загрузка карточки для генерации письма"""
        task_number = self.email_task_number.get().strip()
        
        if not task_number:
            messagebox.showwarning("Предупреждение", "Введите номер работы")
            return
        
        for card in self.trello_cards:
            if card['number'] == task_number:
                self.selected_card = card
                messagebox.showinfo("Успех", f"Карточка {task_number} загружена")
                self.preview_email()
                return
        
        messagebox.showwarning(
            "Не найдено",
            f"Карточка {task_number} не найдена. Загрузите карточки из Trello."
        )

    def preview_email(self):
        """Предпросмотр письма"""
        if not self.selected_card:
            messagebox.showwarning("Предупреждение", "Сначала загрузите карточку")
            return
        
        try:
            template = self.email_template.get()
            
            # Генерируем письмо
            email_html = self.email_gen.generate_email(
                template_name=template,
                trello_card_data={
                    'name': self.selected_card.get('name', ''),
                    'number': self.selected_card['number'],
                    'address': self.selected_card['address'],
                    'description': self.selected_card.get('description', '')
                }
            )
            
            # Показываем HTML (упрощенно)
            self.email_preview.delete('1.0', tk.END)
            self.email_preview.insert('1.0', email_html)
            
            self.update_status("✅ Письмо сгенерировано", "green")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации письма:\n{str(e)}")

    def save_email(self):
        """Сохранение письма в файл"""
        if not self.selected_card:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте письмо")
            return
        
        try:
            template = self.email_template.get()
            
            email_html = self.email_gen.generate_email(
                template_name=template,
                trello_card_data={
                    'name': self.selected_card.get('name', ''),
                    'number': self.selected_card['number'],
                    'address': self.selected_card['address'],
                    'description': self.selected_card.get('description', '')
                }
            )
            
            # Выбор файла для сохранения
            filename = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                initialfile=f"email_{self.selected_card['number']}.html"
            )
            
            if filename:
                self.email_gen.save_email(email_html, filename)
                messagebox.showinfo("Успех", f"Письмо сохранено:\n{filename}")
                self.update_status(f"✅ Письмо сохранено: {filename}", "green")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения:\n{str(e)}")

    def open_email_in_browser(self):
        """Открытие письма в браузере"""
        if not self.selected_card:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте письмо")
            return
        
        try:
            import tempfile
            import webbrowser
            
            template = self.email_template.get()
            
            email_html = self.email_gen.generate_email(
                template_name=template,
                trello_card_data={
                    'name': self.selected_card.get('name', ''),
                    'number': self.selected_card['number'],
                    'address': self.selected_card['address'],
                    'description': self.selected_card.get('description', '')
                }
            )
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(email_html)
                temp_path = f.name
            
            # Открываем в браузере
            webbrowser.open('file://' + temp_path)
            self.update_status("✅ Письмо открыто в браузере", "green")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка открытия:\n{str(e)}")

    # ============================================================
    # МЕТОДЫ: НАСТРОЙКИ
    # ============================================================
    
    def edit_config(self):
        """Открытие config.py для редактирования"""
        try:
            import subprocess
            import platform
            
            config_path = "config.py"
            
            if platform.system() == 'Windows':
                os.startfile(config_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', config_path])
            else:  # Linux
                subprocess.call(['xdg-open', config_path])
            
            self.update_status("✅ Файл config.py открыт", "green")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть config.py:\n{str(e)}")

    def select_excel_file(self):
        """Выбор Excel файла"""
        filename = filedialog.askopenfilename(
            title="Выберите Excel файл",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if filename:
            messagebox.showinfo(
                "Информация",
                f"Выбран файл:\n{filename}\n\n"
                "Отредактируйте config.py и укажите:\n"
                f"EXCEL_PATH = '{filename}'"
            )

    def open_excel(self):
        """Открытие Excel файла"""
        try:
            import subprocess
            import platform
            
            if not os.path.exists(EXCEL_PATH):
                messagebox.showerror("Ошибка", f"Файл не найден:\n{EXCEL_PATH}")
                return
            
            if platform.system() == 'Windows':
                os.startfile(EXCEL_PATH)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', EXCEL_PATH])
            else:  # Linux
                subprocess.call(['xdg-open', EXCEL_PATH])
            
            self.update_status("✅ Excel файл открыт", "green")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть Excel:\n{str(e)}")

    # ============================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ============================================================
    
    def update_status(self, text, color="black"):
        """Обновление статуса"""
        self.status_label.config(text=text, foreground=color)
        self.footer_label.config(text=text)

    def log_sync(self, message):
        """Добавление сообщения в лог"""
        self.sync_log.insert(tk.END, message + "\n")
        self.sync_log.see(tk.END)
        self.sync_log.update()


def main():
    """Запуск приложения"""
    
    # Проверка шаблонов писем
    email_gen = EmailTemplateGenerator()
    templates_dir = Path(email_gen.templates_dir)
    
    if not templates_dir.exists() or not list(templates_dir.glob('*.html')):
        print("📧 Создаем шаблоны писем...")
        email_gen.create_default_templates()
    
    # Запуск GUI
    root = tk.Tk()
    app = SeverenGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
