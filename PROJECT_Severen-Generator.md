Автоматическая синхронизация Trello → Excel → Акты → Dropbox

Что делает система
Ежедневно в 09:00 MSK автоматически:

Скачивает data.xlsx из Dropbox

Синхронизирует данные с Trello (38+ активных работ)

Генерирует output.xlsx с актами из template.xlsx

Загружает обновленные файлы обратно в Dropbox

Статус: ✅ ПРОДАКШЕН РАБОТАЕТ
Компонент	✅ Статус
Cron 09:00	Работает
Trello Sync	38 обновлений
Pandas/Excel	✅ generate_act.py
Dropbox	Автозагрузка
Watchtower	Автообновления
Логи	/root/severen-generator/cron.log
Архитектура
text
graph TD
    A[Dropbox<br/>data.xlsx] --> B[Docker<br/>severen-sync]
    B --> C[Trello API<br/>59 карточек]
    B --> D[generate_act.py<br/>template.xlsx]
    D --> E[output.xlsx]
    B --> F[Dropbox<br/>data.xlsx + output.xlsx]
    G[Cron 09:00] --> B
    H[Watchtower] --> B
Структура проекта
text
severen-generator/
├── docker-compose.yml      # Docker + Watchtower
├── full_sync.py           # 🎯 Основной оркестратор
├── trello_sync.py         # Trello → Excel
├── generate_act.py        # Акты из template.xlsx
├── dropbox_sync.py        # Dropbox API
├── requirements_full.txt  # pandas, openpyxl, dropbox
├── template.xlsx          # Шаблон актов
├── cron.log              # ✅ 87KB логов
└── .env                  # DROPBOX_TOKEN
Развертывание
VPS: unaccountable-hose.aeza.network

bash
cd /root/severen-generator
docker-compose up -d watchtower
crontab -e  # 0 9 * * *
Локально:

bash
git push origin main  # → GitHub Actions → Docker Hub
Мониторинг
bash
# Логи синхронизации
tail -f cron.log

# Статус контейнеров
docker-compose ps

# Последний запуск
grep "ЗАПУСК ПОЛНОЙ" cron.log | tail -1
Результаты (26.01.2026)
text
✅ Обработано карточек: 59
✅ Обновлено строк: 38
✅ Архивных: [АРХИВНАЯ]
✅ Пропущено шаблонов: 21
✅ Файл: /tmp/data.xlsx
Следующие шаги
 Добавить email-уведомления об ошибках

 Rate limit защита Dropbox

 Telegram бот уведомления

 Бэкап template.xlsx
