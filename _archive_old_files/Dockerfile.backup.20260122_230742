# Базовый образ Python
FROM python:3.11-slim

# Метаданные
LABEL maintainer="Severen Team"
LABEL description="Document Generator with Trello integration + GUI"
LABEL version="2.1"

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    # Для работы с GUI (Tkinter)
    python3-tk \
    tk-dev \
    # Для работы с Excel (openpyxl может требовать)
    libxml2-dev \
    libxslt1-dev \
    # Утилиты
    curl \
    wget \
    # Очистка кеша
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements_full.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_full.txt

# Копируем весь проект
COPY . .

# Создаем необходимые папки
RUN mkdir -p /app/output \
    /app/email_templates \
    /app/data \
    /app/excel_files

# Создаем шаблоны писем при сборке образа
RUN python -c "from email_generator import EmailTemplateGenerator; gen = EmailTemplateGenerator(); gen.create_default_templates()" || true

# Порт для веб-версии
EXPOSE 5000

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0
ENV TZ=Europe/Moscow

# Точка входа по умолчанию - веб-интерфейс
# Можно переопределить:
# - docker run app python sync_trello_severen.py (синхронизация)
# - docker run app python gui_app_with_trello.py (GUI)
CMD ["python", "web_app.py"]
