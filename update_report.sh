#!/bin/bash
# Обновляет HTML отчёт, собирает новости, публикует на GitHub Pages

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$SCRIPT_DIR/update.log"
MINUTE=$(date '+%M')

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Запуск обновления..." >> "$LOG"

cd "$SCRIPT_DIR"

# Генерируем отчёт (каждые 15 минут)
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

# Сбор новостей: каждые 60 минут (когда минуты 00 или 15 → каждый час в :00)
if [ "$MINUTE" = "00" ] || [ "$MINUTE" = "15" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Сбор новостей..." >> "$LOG"
    python3 news_fetcher.py >> "$LOG" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Новости обновлены" >> "$LOG"
fi

# Рекомендации: 3 раза в день в 09:00, 15:00, 21:00 MNE (= 07:00, 13:00, 19:00 UTC)
HOUR_UTC=$(date -u '+%H')
if [ "$MINUTE" = "00" ] && { [ "$HOUR_UTC" = "07" ] || [ "$HOUR_UTC" = "13" ] || [ "$HOUR_UTC" = "19" ]; }; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Генерация рекомендаций..." >> "$LOG"
    python3 recommendations.py >> "$LOG" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Рекомендации отправлены" >> "$LOG"
fi
