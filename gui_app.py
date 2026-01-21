#!/usr/bin/env python3
"""
GUI приложение для генерации документов
Простой и удобный интерфейс для создания заданий, отчетов и актов
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import os
from document_generator import DocumentGenerator


class DocumentGeneratorGUI:
    """Графический интерфейс для генератора документов"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор документов - Задание/Отчет/Акт")
        self.root.geometry("900x700")
        
        self.generator = None
        self.input_file = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        
        # Фрейм для выбора файла
        file_frame = ttk.LabelFrame(self.root, text="1. Выбор исходного файла", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_label = ttk.Label(file_frame, text="Файл не выбран")
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(file_frame, text="Выбрать файл Excel", command=self.load_file).pack(side=tk.RIGHT, padx=5)
        
        # Фрейм для выбора задания
        task_frame = ttk.LabelFrame(self.root, text="2. Параметры задания", padding=10)
        task_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Номер задания
        ttk.Label(task_frame, text="Номер задания:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.task_number_var = tk.StringVar(value="11-1")
        ttk.Entry(task_frame, textvariable=self.task_number_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Даты
        ttk.Label(task_frame, text="Дата начала:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.start_date_var = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        ttk.Entry(task_frame, textvariable=self.start_date_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(task_frame, text="Дата окончания:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        ttk.Entry(task_frame, textvariable=self.end_date_var, width=20).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Фрейм для выбора услуг
        services_frame = ttk.LabelFrame(self.root, text="3. Выбор оказанных услуг", padding=10)
        services_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Список доступных услуг
        ttk.Label(services_frame, text="Доступные услуги:").pack(anchor=tk.W)
        
        # Создаем список с чекбоксами
        self.services_list = ttk.Frame(services_frame)
        self.services_list.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.service_vars = []
        self.create_services_list()
        
        # Фрейм для выбора папки вывода
        output_frame = ttk.LabelFrame(self.root, text="4. Папка для сохранения", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.output_label = ttk.Label(output_frame, text="output/")
        self.output_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(output_frame, text="Выбрать папку", command=self.select_output_folder).pack(side=tk.RIGHT, padx=5)
        
        self.output_folder = "output"
        
        # Кнопки действий
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Создать все документы", command=self.generate_all, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Только задание", command=lambda: self.generate_single('zadanie')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Только отчет", command=lambda: self.generate_single('otchet')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Только акт", command=lambda: self.generate_single('akt')).pack(side=tk.LEFT, padx=5)
        
        # Лог
        log_frame = ttk.LabelFrame(self.root, text="Журнал операций", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = ScrolledText(log_frame, height=8, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("Программа готова к работе")
    
    def create_services_list(self):
        """Создание списка услуг с чекбоксами"""
        services = [
            (1, "Консультации по размещению кабелей ВОК - 1850 руб."),
            (2, "Согласование с Жилкомсервис или ГУПРЭП - 5250 руб."),
            (3, "Согласование с ТСЖ, ТСН, ЖСК, УК - 7050 руб."),
            (4, "Согласование транзитных воздушных линий - 8600 руб."),
            (5, "Содействие в монтажных работах по фасадам - 1850 руб."),
            (6, "Доступ в технические помещения - 5250 руб."),
            (7, "Доступ в паркинги/ТЦ/БЦ - 8600 руб."),
        ]
        
        for service_id, service_desc in services:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.services_list, text=service_desc, variable=var)
            cb.pack(anchor=tk.W, pady=2)
            self.service_vars.append((service_id, var))
    
    def load_file(self):
        """Загрузка Excel файла"""
        filename = filedialog.askopenfilename(
            title="Выберите Excel файл",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.input_file = filename
                self.generator = DocumentGenerator(filename)
                self.file_label.config(text=os.path.basename(filename))
                self.log(f"Файл загружен: {os.path.basename(filename)}")
                self.log(f"Найдено заданий: {len(self.generator.tasks_data)}")
                self.log(f"Загружено услуг: {len(self.generator.prices)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
                self.log(f"Ошибка загрузки: {str(e)}")
    
    def select_output_folder(self):
        """Выбор папки для сохранения"""
        folder = filedialog.askdirectory(title="Выберите папку для сохранения")
        if folder:
            self.output_folder = folder
            self.output_label.config(text=folder)
            self.log(f"Папка сохранения: {folder}")
    
    def get_selected_services(self):
        """Получение списка выбранных услуг"""
        services = []
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        
        for service_id, var in self.service_vars:
            if var.get():
                services.append({
                    'type': service_id,
                    'start_date': start_date,
                    'end_date': end_date
                })
        
        return services
    
    def generate_all(self):
        """Генерация всех документов"""
        if not self.generator:
            messagebox.showwarning("Внимание", "Сначала загрузите Excel файл")
            return
        
        services = self.get_selected_services()
        if not services:
            messagebox.showwarning("Внимание", "Выберите хотя бы одну услугу")
            return
        
        try:
            task_number = self.task_number_var.get()
            self.log(f"\n--- Генерация документов для задания {task_number} ---")
            
            files = self.generator.generate_all_documents(task_number, services, self.output_folder)
            
            self.log(f"✓ Задание: {os.path.basename(files['zadanie'])}")
            self.log(f"✓ Отчет: {os.path.basename(files['otchet'])}")
            self.log(f"✓ Акт: {os.path.basename(files['akt'])}")
            self.log(f"Всего услуг: {len(services)}")
            
            total = sum(self.generator.prices[s['type']]['price'] for s in services if s['type'] in self.generator.prices)
            self.log(f"Общая сумма: {total:,.2f} руб.")
            
            messagebox.showinfo("Успех", f"Все документы созданы!\n\nПапка: {self.output_folder}")
            
            # Открываем папку с результатами
            os.startfile(self.output_folder) if os.name == 'nt' else os.system(f'xdg-open "{self.output_folder}"')
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации: {str(e)}")
            self.log(f"✗ Ошибка: {str(e)}")
    
    def generate_single(self, doc_type):
        """Генерация одного типа документа"""
        if not self.generator:
            messagebox.showwarning("Внимание", "Сначала загрузите Excel файл")
            return
        
        services = self.get_selected_services()
        if not services and doc_type != 'zadanie':
            messagebox.showwarning("Внимание", "Выберите хотя бы одну услугу")
            return
        
        try:
            task_number = self.task_number_var.get()
            
            if doc_type == 'zadanie':
                filename = self.generator.generate_zadanie(task_number, self.output_folder)
            elif doc_type == 'otchet':
                filename = self.generator.generate_otchet(task_number, services, self.output_folder)
            else:  # akt
                filename = self.generator.generate_akt(task_number, services, self.output_folder)
            
            self.log(f"✓ Создан: {os.path.basename(filename)}")
            messagebox.showinfo("Успех", f"Документ создан!\n\n{os.path.basename(filename)}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации: {str(e)}")
            self.log(f"✗ Ошибка: {str(e)}")
    
    def log(self, message):
        """Вывод сообщения в лог"""
        self.log_text.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')


if __name__ == '__main__':
    root = tk.Tk()
    app = DocumentGeneratorGUI(root)
    root.mainloop()
