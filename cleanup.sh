#!/bin/bash
# Скрипт очистки мусорных файлов

echo "🗑️  Начинаю очистку мусорных файлов..."

# Backup old files
mkdir -p _archive_old_files
mv -v Dockerfile.backup.* _archive_old_files/ 2>/dev/null
mv -v report_generator_v2.py _archive_old_files/ 2>/dev/null
mv -v enhanced_generator.py _archive_old_files/ 2>/dev/null
mv -v requirements_full.txt _archive_old_files/ 2>/dev/null

# Remove old sync scripts
rm -v sync_excel_to_trello.py 2>/dev/null
rm -v sync_excel_trello.py 2>/dev/null
rm -v sync_trello_severen.py 2>/dev/null
rm -v full_sync.py 2>/dev/null
rm -v dropbox_upload_initial.py 2>/dev/null

# Remove GUI apps (if not needed)
rm -v gui_app.py 2>/dev/null
rm -v gui_app_with_trello.py 2>/dev/null
rm -v web_app.py 2>/dev/null

# Remove installation scripts
rm -v install.sh 2>/dev/null
rm -v get_dropbox_refresh_token.py 2>/dev/null
rm -v generate_report.sh 2>/dev/null

# Archive documentation
mkdir -p _archive_docs
mv -v *.txt _archive_docs/ 2>/dev/null
mv -v *.md _archive_docs/ 2>/dev/null

# Remove duplicate Excel (with spaces in name)
rm -v "Рабочие табл. СМР v2.xlsx" 2>/dev/null

echo "✅ Очистка завершена!"
echo "📦 Старые файлы перемещены в _archive_old_files/"
echo "📄 Документация перемещена в _archive_docs/"
