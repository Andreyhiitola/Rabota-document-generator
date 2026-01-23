#!/bin/bash
# Настройка cron для автозапуска severen-trello-sync

echo "⏰ Настройка cron для Trello → Excel синхронизации"

# Создаем скрипт запуска
cat > /root/severen-app/run_trello_sync.sh << 'SCRIPT'
#!/bin/bash
cd /root/severen-app
docker-compose up --no-deps severen-trello-sync
SCRIPT

chmod +x /root/severen-app/run_trello_sync.sh

# Добавляем в crontab
(crontab -l 2>/dev/null | grep -v "run_trello_sync.sh"; cat << CRON
# Синхронизация Trello → Excel (3 раза в день)
0 9 * * * /root/severen-app/run_trello_sync.sh >> /root/severen-app/logs/trello_sync_cron.log 2>&1
0 13 * * * /root/severen-app/run_trello_sync.sh >> /root/severen-app/logs/trello_sync_cron.log 2>&1
0 20 * * * /root/severen-app/run_trello_sync.sh >> /root/severen-app/logs/trello_sync_cron.log 2>&1
CRON
) | crontab -

echo "✅ Cron настроен!"
echo ""
echo "📋 Расписание:"
echo "  - 09:00 МСК — синхронизация Trello → Excel"
echo "  - 13:00 МСК — синхронизация Trello → Excel"
echo "  - 20:00 МСК — синхронизация Trello → Excel"
echo ""
echo "📂 Логи: /root/severen-app/logs/trello_sync_cron.log"
echo ""
echo "🔍 Проверить cron:"
echo "   crontab -l"
echo ""
echo "🧪 Тестовый запуск:"
echo "   /root/severen-app/run_trello_sync.sh"
