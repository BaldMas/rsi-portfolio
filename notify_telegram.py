#!/usr/bin/env python3
"""
Отправка сообщений в Telegram.
Читает TELEGRAM_TOKEN и TELEGRAM_CHAT_ID из .env
"""

import os
import json
import urllib.request
import urllib.parse

ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")


def _read_env(key):
    if not os.path.exists(ENV_FILE):
        return ""
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    return ""


def send(text, parse_mode="HTML"):
    token   = _read_env("TELEGRAM_TOKEN")
    chat_id = _read_env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("  [Telegram] не настроен — добавь TELEGRAM_TOKEN и TELEGRAM_CHAT_ID в .env")
        return False

    # Разбиваем на части если сообщение длиннее 4096 символов
    parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
    ok = True
    for part in parts:
        data = urllib.parse.urlencode({
            "chat_id":                  chat_id,
            "text":                     part,
            "parse_mode":               parse_mode,
            "disable_web_page_preview": "true",
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data, method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                result = json.loads(r.read())
                if not result.get("ok"):
                    print(f"  [Telegram] ошибка: {result}")
                    ok = False
        except Exception as e:
            print(f"  [Telegram] исключение: {e}")
            ok = False
    return ok


def get_chat_id(token):
    """Помощник для получения chat_id: отправь боту любое сообщение и вызови это."""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        updates = data.get("result", [])
        if not updates:
            print("Нет сообщений. Отправь боту любое сообщение в Telegram и повтори.")
            return None
        chat_id = updates[-1]["message"]["chat"]["id"]
        print(f"Твой chat_id: {chat_id}")
        return chat_id
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "get_chat_id":
        token = _read_env("TELEGRAM_TOKEN")
        if token:
            get_chat_id(token)
        else:
            print("Добавь TELEGRAM_TOKEN в .env")
    else:
        ok = send("✅ Тест: бот настроен и работает")
        print("OK" if ok else "FAIL")
