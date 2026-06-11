#!/bin/bash
# Обновляет HTML отчёт и публикует на GitHub Pages

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$SCRIPT_DIR/update.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Запуск обновления..." >> "$LOG"

cd "$SCRIPT_DIR"

# Генерируем отчёт
python3 generate_html.py >> "$LOG" 2>&1
cp report.html index.html

# Коммитим и пушим если есть изменения
if git diff --quiet index.html; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Нет изменений, пропускаем push" >> "$LOG"
else
    git add index.html
    git commit -m "auto: update report $(date '+%Y-%m-%d %H:%M')" >> "$LOG" 2>&1
    git push >> "$LOG" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Опубликовано" >> "$LOG"
fi
