FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements_full.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements_full.txt

# Копирование скриптов из КОРНЯ
COPY full_sync.py .
COPY sync_trello_severen.py .
COPY dropbox_sync.py .

# Создание необходимых папок
RUN mkdir -p /app/data /app/logs && \
    chmod -R 777 /app/data /app/logs

# Права на выполнение
RUN chmod +x *.py

CMD ["python3", "full_sync.py"]
