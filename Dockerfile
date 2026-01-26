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

# Копирование всех файлов проекта
COPY *.py ./
COPY template.xlsx ./

# Создание необходимых папок с правами
RUN mkdir -p /app/excel_files /app/output /app/logs /app/templates && \
    chmod -R 777 /app/excel_files /app/output /app/logs /app/templates

# Права на выполнение
RUN chmod +x *.py

CMD ["python3", "full_sync.py"]
