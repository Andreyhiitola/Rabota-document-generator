from flask import Flask, render_template_string, request, send_file, jsonify
from datetime import datetime
import os
from report_generator_v2 import ReportGenerator

app = Flask(__name__)

# HTML шаблон
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Генератор отчётов - Северный</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.2em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.95;
        }

        .content {
            padding: 40px 30px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            color: #333;
            font-weight: 600;
            font-size: 1em;
        }

        input[type="date"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            transition: all 0.3s;
            font-family: inherit;
        }

        input[type="date"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: 500;
            display: none;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .status.loading {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }

        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 3px solid rgba(0,0,0,0.1);
            border-radius: 50%;
            border-top-color: #0c5460;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .info-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 25px;
            border-left: 4px solid #667eea;
        }

        .info-box h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }

        .info-box ul {
            list-style: none;
            color: #666;
        }

        .info-box li {
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }

        .info-box li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Генератор отчётов</h1>
            <p>Северный - система отчётности</p>
        </div>

        <div class="content">
            <form id="reportForm">
                <div class="form-group">
                    <label for="startDate">📅 Дата начала периода:</label>
                    <input type="date" id="startDate" name="startDate" required>
                </div>

                <div class="form-group">
                    <label for="endDate">📅 Дата окончания периода:</label>
                    <input type="date" id="endDate" name="endDate" required>
                </div>

                <button type="submit" class="btn" id="generateBtn">
                    Сгенерировать отчёт
                </button>
            </form>

            <div id="status" class="status"></div>

            <div class="info-box">
                <h3>ℹ️ Информация</h3>
                <ul>
                    <li>Данные загружаются из Google Sheets</li>
                    <li>Автоматический подсчёт итогов</li>
                    <li>Выгрузка в формате Excel</li>
                    <li>Фильтрация по выбранному периоду</li>
                </ul>
            </div>
        </div>
    </div>

    <script>
        // Установка текущей даты
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);

        document.getElementById('startDate').valueAsDate = firstDay;
        document.getElementById('endDate').valueAsDate = today;

        // Обработка формы
        document.getElementById('reportForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const btn = document.getElementById('generateBtn');
            const status = document.getElementById('status');
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;

            // Валидация дат
            if (new Date(startDate) > new Date(endDate)) {
                showStatus('error', 'Дата начала не может быть позже даты окончания');
                return;
            }

            // Показать загрузку
            btn.disabled = true;
            btn.textContent = 'Генерация...';
            showStatus('loading', '<span class="spinner"></span>Генерация отчёта...');

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ startDate, endDate })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `Отчет_${startDate}_${endDate}.xlsx`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);

                    showStatus('success', '✓ Отчёт успешно сгенерирован и загружен!');
                } else {
                    const error = await response.json();
                    showStatus('error', `Ошибка: ${error.error}`);
                }
            } catch (error) {
                showStatus('error', `Ошибка сети: ${error.message}`);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Сгенерировать отчёт';
            }
        });

        function showStatus(type, message) {
            const status = document.getElementById('status');
            status.className = `status ${type}`;
            status.innerHTML = message;
            status.style.display = 'block';

            if (type === 'success') {
                setTimeout(() => {
                    status.style.display = 'none';
                }, 5000);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Главная страница"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'report-generator'})

@app.route('/generate', methods=['POST'])
def generate_report():
    """Генерация отчёта"""
    try:
        data = request.get_json()
        start_date = data.get('startDate')
        end_date = data.get('endDate')

        if not start_date or not end_date:
            return jsonify({'error': 'Не указаны даты'}), 400

        # Создаём генератор отчётов
        generator = ReportGenerator()

        # Генерируем отчёт
        output_file = generator.generate_report(start_date, end_date)

        if not output_file or not os.path.exists(output_file):
            return jsonify({'error': 'Ошибка генерации отчёта'}), 500

        # Отправляем файл
        return send_file(
            output_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'Отчет_{start_date}_{end_date}.xlsx'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print(" Генератор отчётов - Северный")
    print("=" * 50)
    print()
    print("🌐 Откройте в браузере: http://localhost:5000")
    print()
    print("📊 Выберите период и создавайте отчёты!")
    print()

    app.run(host='0.0.0.0', port=5000, debug=True)
