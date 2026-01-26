[

Автоматическая синхронизация Trello → Excel → Акты СМР → Dropbox

🎯 Что делает
Ежедневно в 09:00 MSK:

📥 Скачивает data.xlsx из Dropbox

🔄 Синхронизирует с Trello (59 карточек, 38 активных работ)

📊 Генерирует output.xlsx с актами из template.xlsx

📤 Загружает файлы обратно в Dropbox

📝 Записывает логи в cron.log

✅ Статус: PRODUCTION READY
Компонент	Статус	Логи
Cron 09:00	✅ Работает	87KB cron.log
Trello API	✅ 38 обновлений	trello_sync.py
Excel	✅ pandas/openpyxl	generate_act.py
Dropbox API	✅ Автозагрузка	dropbox_sync.py
Watchtower	✅ Автообновления	Docker Hub
🚀 Быстрый старт
На VPS
bash
git clone https://github.com/Andreyhiitola/Rabota-document-generator.git severen-generator
cd severen-generator
cp .env.example .env  # Добавьте DROPBOX_TOKEN
docker-compose up -d watchtower
crontab -e  # 0 9 * * * ...
Локальное тестирование
bash
docker-compose run --rm severen-sync
tail -f cron.log
🏗️ Архитектура
text
graph LR
    A[Dropbox data.xlsx] --> B[full_sync.py]
    B --> C[Trello 59 карточек]
    C --> D[data.xlsx обновлен]
    B --> E[generate_act.py<br/>template.xlsx]
    E --> F[output.xlsx акты]
    D --> G[Dropbox]
    F --> G
    H[Cron 09:00] --> B
    I[Watchtower] --> B
📁 Структура проекта
text
severen-generator/
├── docker-compose.yml       # Docker + Watchtower
├── full_sync.py           # 🎯 Главный оркестратор (4 шага)
├── trello_sync.py         # Trello → Excel синхронизация
├── generate_act.py        # Генерация актов pandas
├── dropbox_sync.py        # Dropbox API upload/download
├── requirements_full.txt  # pandas openpyxl dropbox
├── template.xlsx          # Шаблон акта СМР
├── .env.example           # DROPBOX_TOKEN
└── cron.log              # ✅ Логи синхронизаций
📊 Результаты (26.01.2026)
text
✅ Обработано карточек: 59
✅ Активных работ: 38  
✅ Архивных: помечены [АРХИВНАЯ]
✅ Пропущено шаблонов: 21
✅ Файлы: data.xlsx + output.xlsx
✅ Лог: 87KB cron.log
🔍 Мониторинг
bash
# Логи синхронизации
tail -20 cron.log

# Статус Docker
docker-compose ps

# Последний успешный запуск
grep "СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА" cron.log | tail -1

# Размер логов
du -h cron.log
🛠️ Развертывание
1. VPS (Ubuntu/Debian)
bash
apt update && apt install docker.io docker-compose cron
systemctl enable --now docker cron
2. Клонирование
bash
cd /root
git clone https://github.com/Andreyhiitola/Rabota-document-generator.git severen-generator
cd severen-generator
3. Конфигурация
bash
cp .env.example .env
echo "DROPBOX_TOKEN=your_token_here" >> .env
4. Запуск
bash
docker-compose up -d watchtower
crontab -e  # Добавьте: 0 9 * * *
touch cron.log && chmod 666 cron.log
⚙️ Cron задача
bash
# /etc/crontab или crontab -e (root)
0 9 * * * root cd /root/severen-generator && /usr/bin/docker-compose run --rm severen-sync >> /root/severen-generator/cron.log 2>&1
🔄 Автообновления
Watchtower проверяет Docker Hub каждые 5 минут:

Новые коммиты → GitHub Actions → Docker Hub

Watchtower → автоматический docker pull

✅ Без downtime!

📈 Метрики (сегодня)
text
📊 Активных работ: 38
📦 Общий размер логов: 87KB
🔄 Запусков cron: 2+ тестовых
⏰ Следующий запуск: Завтра 09:00 MSK
🚀 Автор
Andrey Sagitov @andysag
VPS: unaccountable-hose.aeza.network
Дата запуска: 26.01.2026
Статус: 🟢 PRODUCTION 
