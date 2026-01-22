FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements_full.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements_full.txt

# Копируем все Python файлы
COPY *.py .

# Копируем Markdown документацию
COPY *.md .

# Создаем необходимые директории
RUN mkdir -p /app/files /app/output /app/logs /app/templates /app/static

# Права на выполнение для всех Python скриптов
RUN chmod +x *.py

# Переменная окружения для Python
ENV PYTHONUNBUFFERED=1

# По умолчанию запускаем bash
CMD ["/bin/bash"]
