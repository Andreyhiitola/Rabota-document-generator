#!/usr/bin/env python3
"""
Веб-приложение для генерации документов
Запуск: python web_app.py
Откройте в браузере: http://localhost:5000
"""

from flask import Flask, render_template_string, request, send_file, jsonify, session
import os
from werkzeug.utils import secure_filename
from document_generator import DocumentGenerator
from database import DocumentDatabase
from datetime import datetime
import tempfile
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

db = DocumentDatabase()

# HTML шаблон
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Генератор документов</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content { padding: 40px; }
        .section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            border-left: 4px solid #667eea;
        }
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
        }
        input[type="text"], input[type="date"], input[type="file"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .service-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            transition: all 0.3s;
        }
        .service-item:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
        }
        .service-item input[type="checkbox"] {
            width: auto;
            margin-right: 10px;
        }
        .service-item label {
            display: inline;
            margin: 0;
            font-weight: normal;
            cursor: pointer;
        }
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background: #5a6268;
        }
        .log {
            background: #1e1e1e;
            color: #00ff00;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            max-height: 300px;
            overflow-y: auto;
            margin-top: 20px;
        }
        .log-entry {
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        .timestamp {
            color: #888;
        }
        .success { color: #00ff00; }
        .error { color: #ff4444; }
        .info { color: #4444ff; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .stat-card h3 {
            color: #667eea;
            font-size: 2em;
            margin-bottom: 5px;
        }
        .stat-card p {
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 Генератор документов</h1>
            <p>Автоматическое создание заданий, отчетов и актов</p>
        </div>
        
        <div class="content">
            <!-- Загрузка файла -->
            <div class="section">
                <h2>1️⃣ Загрузка исходного файла</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="file">Выберите Excel файл:</label>
                        <input type="file" id="file" name="file" accept=".xlsx" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Загрузить файл</button>
                </form>
            </div>
            
            <!-- Параметры -->
            <div class="section">
                <h2>2️⃣ Параметры документа</h2>
                <form id="paramsForm">
                    <div class="form-group">
                        <label for="taskNumber">Номер задания:</label>
                        <input type="text" id="taskNumber" name="taskNumber" value="11-1" required>
                    </div>
                    <div class="form-group">
                        <label for="startDate">Дата начала:</label>
                        <input type="date" id="startDate" name="startDate" required>
                    </div>
                    <div class="form-group">
                        <label for="endDate">Дата окончания:</label>
                        <input type="date" id="endDate" name="endDate" required>
                    </div>
                </form>
            </div>
            
            <!-- Услуги -->
            <div class="section">
                <h2>3️⃣ Выбор услуг</h2>
                <div class="services-grid">
                    <div class="service-item">
                        <input type="checkbox" id="service1" value="1">
                        <label for="service1">Консультации по размещению кабелей ВОК - 1850₽</label>
                    </div>
                    <div class="service-item">
                        <input type="checkbox" id="service2" value="2">
                        <label for="service2">Согласование с Жилкомсервис/ГУПРЭП - 5250₽</label>
                    </div>
                    <div class="service-item">
                        <input type="checkbox" id="service3" value="3">
                        <label for="service3">Согласование с ТСЖ/ТСН/ЖСК/УК - 7050₽</label>
                    </div>
                    <div class="service-item">
                        <input type="checkbox" id="service4" value="4">
                        <label for="service4">Согласование транзитных линий - 8600₽</label>
                    </div>
                    <div class="service-item">
                        <input type="checkbox" id="service5" value="5">
                        <label for="service5">Содействие в монтаже по фасадам - 1850₽</label>
                    </div>
                    <div class="service-item">
                        <input type="checkbox" id="service6" value="6">
                        <label for="service6">Доступ в технические помещения - 5250₽</label>
                    </div>
                    <div class="service-item">
                        <input type="checkbox" id="service7" value="7">
                        <label for="service7">Доступ в паркинги/ТЦ/БЦ - 8600₽</label>
                    </div>
                </div>
            </div>
            
            <!-- Кнопки генерации -->
            <div class="section">
                <h2>4️⃣ Генерация документов</h2>
                <button onclick="generateAll()" class="btn btn-primary">Создать все документы</button>
                <button onclick="generate('zadanie')" class="btn btn-secondary">Только задание</button>
                <button onclick="generate('otchet')" class="btn btn-secondary">Только отчет</button>
                <button onclick="generate('akt')" class="btn btn-secondary">Только акт</button>
            </div>
            
            <!-- Лог -->
            <div class="section">
                <h2>📊 Журнал операций</h2>
                <div id="log" class="log">
                    <div class="log-entry info"><span class="timestamp">[--:--:--]</span> Система готова к работе</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function log(message, type = 'info') {
            const logDiv = document.getElementById('log');
            const time = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            entry.innerHTML = `<span class="timestamp">[${time}]</span> ${message}`;
            logDiv.appendChild(entry);
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        // Установка текущей даты
        document.getElementById('startDate').valueAsDate = new Date();
        document.getElementById('endDate').valueAsDate = new Date();
        
        // Загрузка файла
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            log('Загрузка файла...', 'info');
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    log(`✓ Файл загружен: ${result.filename}`, 'success');
                    log(`  Найдено заданий: ${result.tasks_count}`, 'info');
                    log(`  Загружено услуг: ${result.services_count}`, 'info');
                } else {
                    log(`✗ Ошибка: ${result.error}`, 'error');
                }
            } catch (error) {
                log(`✗ Ошибка загрузки: ${error}`, 'error');
            }
        });
        
        function getSelectedServices() {
            const services = [];
            for (let i = 1; i <= 7; i++) {
                const checkbox = document.getElementById(`service${i}`);
                if (checkbox.checked) {
                    services.push(parseInt(checkbox.value));
                }
            }
            return services;
        }
        
        async function generate(docType) {
            const services = getSelectedServices();
            if (services.length === 0 && docType !== 'zadanie') {
                log('✗ Выберите хотя бы одну услугу', 'error');
                return;
            }
            
            const data = {
                taskNumber: document.getElementById('taskNumber').value,
                startDate: document.getElementById('startDate').value,
                endDate: document.getElementById('endDate').value,
                services: services,
                docType: docType
            };
            
            log(`Генерация документа: ${docType}...`, 'info');
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = response.headers.get('Content-Disposition').split('filename=')[1];
                    a.click();
                    
                    log(`✓ Документ создан и загружен`, 'success');
                } else {
                    const error = await response.json();
                    log(`✗ Ошибка: ${error.error}`, 'error');
                }
            } catch (error) {
                log(`✗ Ошибка генерации: ${error}`, 'error');
            }
        }
        
        async function generateAll() {
            const services = getSelectedServices();
            if (services.length === 0) {
                log('✗ Выберите хотя бы одну услугу', 'error');
                return;
            }
            
            log('Генерация всех документов...', 'info');
            
            await generate('zadanie');
            await new Promise(resolve => setTimeout(resolve, 500));
            await generate('otchet');
            await new Promise(resolve => setTimeout(resolve, 500));
            await generate('akt');
            
            log('✓ Все документы созданы', 'success');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Главная страница"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Загрузка Excel файла"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не выбран'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Файл не выбран'})
    
    if file and file.filename.endswith('.xlsx'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            generator = DocumentGenerator(filepath)
            session['current_file'] = filepath
            
            return jsonify({
                'success': True,
                'filename': filename,
                'tasks_count': len(generator.tasks_data),
                'services_count': len(generator.prices)
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Неподдерживаемый формат файла'})

@app.route('/generate', methods=['POST'])
def generate_document():
    """Генерация документа"""
    data = request.json
    
    if 'current_file' not in session:
        return jsonify({'error': 'Сначала загрузите файл'}), 400
    
    try:
        generator = DocumentGenerator(session['current_file'])
        
        task_number = data['taskNumber']
        start_date = data['startDate']
        end_date = data['endDate']
        service_types = data['services']
        doc_type = data['docType']
        
        # Формирование списка услуг
        services = []
        for service_type in service_types:
            if service_type in generator.prices:
                services.append({
                    'type': service_type,
                    'start_date': start_date,
                    'end_date': end_date,
                    'price': generator.prices[service_type]['price'],
                    'description': generator.prices[service_type]['description']
                })
        
        # Генерация документа
        output_folder = tempfile.gettempdir()
        
        if doc_type == 'zadanie':
            filepath = generator.generate_zadanie(task_number, output_folder)
        elif doc_type == 'otchet':
            filepath = generator.generate_otchet(task_number, services, output_folder)
        elif doc_type == 'akt':
            filepath = generator.generate_akt(task_number, services, output_folder)
        else:
            return jsonify({'error': 'Неизвестный тип документа'}), 400
        
        # Сохранение в базу данных
        db.save_document(task_number, doc_type, start_date, end_date, services, filepath)
        
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/statistics')
def statistics():
    """Получение статистики"""
    stats = db.get_statistics()
    return jsonify(stats)

if __name__ == '__main__':
    print("=" * 50)
    print(" Веб-приложение для генерации документов")
    print("=" * 50)
    print("\n🌐 Откройте в браузере: http://localhost:5000")
    print("\n📝 Загрузите Excel файл и создавайте документы!\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
