#!/usr/bin/env python3
"""
Сбор новостей по монетам портфеля из Google News RSS (en, ru, zh, ko).
Хранит в SQLite, дедуплицирует по hash(coin+title).
"""

import os
import re
import time
import sqlite3
import hashlib
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

DB_FILE  = os.path.join(os.path.dirname(__file__), "news.db")
ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")

# Монеты - подгружаем динамически, fallback список
DEFAULT_COINS = [
    "BTC", "ETH", "XRP", "ONDO", "RENDER", "HBAR", "TON", "JUP",
    "OP", "WLD", "LDO", "FIL", "DOT", "ICP", "ARB", "STRK",
    "PYTH", "CFX", "COMP", "TIA", "APT", "GRT", "IMX", "ZK",
    "XCH", "W", "ROSE", "HFT", "FLOW",
]

# Полные названия для лучшего поиска
COIN_NAMES = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "XRP": "Ripple XRP",
    "ONDO": "Ondo Finance", "RENDER": "Render Network RNDR",
    "HBAR": "Hedera HBAR", "TON": "Toncoin", "JUP": "Jupiter Solana",
    "OP": "Optimism crypto", "WLD": "Worldcoin", "LDO": "Lido DAO",
    "FIL": "Filecoin", "DOT": "Polkadot", "ICP": "Internet Computer",
    "ARB": "Arbitrum", "STRK": "Starknet", "PYTH": "Pyth Network",
    "CFX": "Conflux Network", "COMP": "Compound crypto",
    "TIA": "Celestia crypto", "APT": "Aptos crypto",
    "GRT": "The Graph crypto", "IMX": "Immutable X",
    "ZK": "ZKsync", "XCH": "Chia Network",
    "W": "Wormhole crypto", "ROSE": "Oasis Network",
    "HFT": "Hashflow crypto", "FLOW": "Flow blockchain",
}

LANG_CONFIGS = {
    "en": {"suffix": "cryptocurrency",     "hl": "en-US", "gl": "US", "ceid": "US:en"},
    "ru": {"suffix": "криптовалюта",        "hl": "ru-RU", "gl": "RU", "ceid": "RU:ru"},
    "zh": {"suffix": "加密货币",             "hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"},
    "ko": {"suffix": "암호화폐",             "hl": "ko-KR", "gl": "KR", "ceid": "KR:ko"},
}

# Ключевые слова для сентимента
POS_KW = {
    "listing", "partnership", "upgrade", "launch", "mainnet", "adoption",
    "institutional", "etf", "approval", "bullish", "accumulate",
    "breakout", "integration", "milestone", "record", "rally", "surge",
    "grant", "invest", "expand", "deploy", "achieve", "soar", "gain",
    "листинг", "партнёрство", "обновление", "принятие", "бычий",
    "интеграция", "рекорд", "ралли", "рост", "инвестиции", "запуск",
    "上市", "合作", "升级", "采用", "涨", "突破", "里程碑",
    "상장", "파트너십", "업그레이드", "채택", "급등", "돌파",
}

NEG_KW = {
    "hack", "exploit", "sec", "lawsuit", "ban", "dump", "bearish", "fud",
    "delist", "vulnerability", "crash", "scandal", "fraud", "investigation",
    "sanction", "fine", "arrest", "collapse", "rug", "ponzi", "attack",
    "хак", "взлом", "иск", "запрет", "обвал", "медвежий", "уязвимость",
    "мошенничество", "расследование", "санкции", "арест", "крах",
    "黑客", "漏洞", "禁止", "崩溃", "欺诈", "调查", "制裁",
    "해킹", "취약점", "금지", "폭락", "사기", "조사", "제재",
}


def init_db(conn=None):
    close = conn is None
    if conn is None:
        conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            coin      TEXT NOT NULL,
            title     TEXT NOT NULL,
            url       TEXT,
            published TEXT,
            source    TEXT,
            lang      TEXT,
            sentiment INTEGER DEFAULT 0,
            hash      TEXT UNIQUE,
            fetched   TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_coin ON news(coin)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_fetched ON news(fetched)")
    conn.commit()
    if close:
        conn.close()
    else:
        return conn


def score_sentiment(title):
    t = title.lower()
    pos = sum(1 for kw in POS_KW if kw in t)
    neg = sum(1 for kw in NEG_KW if kw in t)
    if pos > neg:
        return 1
    if neg > pos:
        return -1
    return 0


def fetch_gnews(coin, lang="en", limit=8):
    cfg = LANG_CONFIGS.get(lang, LANG_CONFIGS["en"])
    name = COIN_NAMES.get(coin, coin)
    query = f"{name} {cfg['suffix']}"
    url = (
        f"https://news.google.com/rss/search"
        f"?q={urllib.parse.quote(query)}"
        f"&hl={cfg['hl']}&gl={cfg['gl']}&ceid={cfg['ceid']}"
    )
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Accept": "application/rss+xml,application/xml,text/xml",
    })
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            xml_data = r.read()
        root = ET.fromstring(xml_data)
        items = root.findall(".//item")[:limit]
        results = []
        for item in items:
            title  = (item.findtext("title") or "").strip()
            link   = (item.findtext("link") or "").strip()
            pub    = (item.findtext("pubDate") or "").strip()
            src_el = item.find("source")
            source = src_el.text.strip() if src_el is not None and src_el.text else ""
            if not title:
                continue
            h = hashlib.md5(f"{coin}:{title}".encode()).hexdigest()
            results.append({
                "coin": coin, "title": title, "url": link,
                "published": pub, "source": source, "lang": lang,
                "sentiment": score_sentiment(title), "hash": h,
            })
        return results
    except Exception as e:
        return []


def save_news(conn, items):
    saved = 0
    before = conn.total_changes
    for item in items:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO news
                  (coin, title, url, published, source, lang, sentiment, hash)
                VALUES
                  (:coin, :title, :url, :published, :source, :lang, :sentiment, :hash)
            """, item)
        except Exception:
            pass
    conn.commit()
    return conn.total_changes - before


def get_recent_sentiment(coin, hours=24, conn=None):
    """Возвращает (pos, neg, neu, rows) за последние N часов."""
    close = conn is None
    if conn is None:
        conn = sqlite3.connect(DB_FILE)
        init_db(conn)
    cur = conn.execute("""
        SELECT sentiment, title, source, published, lang FROM news
        WHERE coin = ?
          AND fetched >= datetime('now', ?)
        ORDER BY fetched DESC
    """, (coin, f"-{hours} hours"))
    rows = cur.fetchall()
    pos = sum(1 for r in rows if r[0] == 1)
    neg = sum(1 for r in rows if r[0] == -1)
    neu = sum(1 for r in rows if r[0] == 0)
    if close:
        conn.close()
    return pos, neg, neu, rows


def fetch_all(coins=None, langs=("en", "ru", "zh", "ko"), verbose=True):
    if coins is None:
        try:
            import sys
            sys.path.insert(0, os.path.dirname(__file__))
            from portfolio_live import get_dynamic_portfolio
            PORTFOLIO, *_ = get_dynamic_portfolio()
            coins = [c for c in PORTFOLIO if c not in ("BTC", "ETH")] + ["BTC", "ETH"]
        except Exception:
            coins = DEFAULT_COINS

    conn = sqlite3.connect(DB_FILE)
    init_db(conn)
    total_saved = 0

    for coin in coins:
        coin_saved = 0
        for lang in langs:
            items = fetch_gnews(coin, lang)
            n = save_news(conn, items)
            coin_saved += n
            time.sleep(0.4)
        total_saved += coin_saved
        if verbose:
            print(f"  {coin}: +{coin_saved} новых", flush=True)

    conn.close()
    return total_saved


def cleanup_old(days=14):
    """Удаляет новости старше N дней."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM news WHERE fetched < datetime('now', ?)", (f"-{days} days",))
    n = conn.total_changes
    conn.commit()
    conn.close()
    return n


if __name__ == "__main__":
    print("Загрузка новостей...", flush=True)
    n = fetch_all()
    print(f"\nВсего новых записей: {n}")
    cleanup_old()
