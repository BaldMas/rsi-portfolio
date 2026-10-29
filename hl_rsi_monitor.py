#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyperliquid: монитор RSI по акциям и товарам (HIP-3 биржи builder-ов).

Что делает:
  1. Через публичный API (api.hyperliquid.xyz/info) находит все HIP-3 биржи (perpDexs),
     забирает их рынки (metaAndAssetCtxs) и оставляет акции и товары.
  2. Определяет страну эмитента (на бирже её нет): встроенный справочник -> ваш файл
     data/country_overrides.json -> Yahoo Finance (yfinance, если установлен) -> "Не определена".
  3. Считает RSI(14) по Уайлдеру на 4h, 1D, 1W.
  4. Пишет HTML-отчёт (сортировка по любому столбцу, фильтры, цветовые зоны RSI)
     и assets.csv со списком активов и стран.
  5. Шлёт в Telegram алерты, когда RSI заходит в экстремальную зону или углубляется в неё.

Запуск:
  pip install requests            (желательно ещё: pip install yfinance)
  export TG_BOT_TOKEN="123:ABC"   export TG_CHAT_ID="123456789"
  python hl_rsi_monitor.py                 # бесконечный цикл
  python hl_rsi_monitor.py --once          # один проход (для cron)
  python hl_rsi_monitor.py --list-assets   # только список активов -> assets.csv
  python hl_rsi_monitor.py --test-telegram # проверка отправки в Telegram

Первый запуск медленный: свечи грузятся один раз (лимит API 1200 weight/мин на IP),
дальше они кэшируются в data/candles_cache.json и обновляются только по мере
закрытия свечей. Живая цена берётся из metaAndAssetCtxs (одним запросом на биржу).
"""
import argparse
import csv
import html
import json
import logging
import math
import os
import sys
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

# ============================== НАСТРОЙКИ ==============================
API_URL = "https://api.hyperliquid.xyz/info"

RSI_PERIOD = 14
# (интервал API, подпись столбца, длительность свечи в мс)
TIMEFRAMES = [
    ("4h", "RSI 4h", 4 * 3600 * 1000),
    ("1d", "RSI 1D", 24 * 3600 * 1000),
    ("1w", "RSI 1W", 7 * 24 * 3600 * 1000),
]
CANDLES_HISTORY = 250          # сколько свечей грузить на старте (для сглаживания Уайлдера)
CYCLE_SECONDS = 300            # период опроса, сек
RATE_BUDGET_PER_MIN = 1000     # наш бюджет weight/мин (лимит биржи 1200 на IP)
MIN_REFRESH_GAP_MS = 10 * 60 * 1000   # не перезапрашивать один и тот же ряд чаще, чем раз в 10 мин

# Какие категории показывать. Доступны: "Акция", "Товар", "ETF", "Индекс", "Валюта",
# "Облигация", "Не определён", "Другое" (крипта, pre-IPO и т.п. на не-TradFi биржах).
INCLUDE_CATEGORIES = {"Акция", "Товар", "ETF", "Не определён"}

# Пороги цветовых зон RSI (по возрастанию «глубины»)
LOW_LEVELS = (30, 20, 10)      # < 30, < 20, < 10
HIGH_LEVELS = (70, 80, 90)     # > 70, > 80, > 90

# Алерты: 1 = от 30/70, 2 = от 20/80, 3 = только 10/90
ALERT_MIN_ZONE = 2
ALERT_HYSTERESIS = 5           # RSI должен отойти от границы на 5 пунктов, чтобы зона сбросилась

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
HTML_FILE = Path("/home/masus/rsi-portfolio") / "rsi_report.html"
ASSETS_CSV = Path("/home/masus/rsi-portfolio") / "assets.csv"
CANDLES_FILE = DATA_DIR / "candles_cache.json"
STATE_FILE = DATA_DIR / "state.json"
YAHOO_CACHE_FILE = DATA_DIR / "country_cache.json"
YAHOO_FAILED_FILE = DATA_DIR / "yahoo_failed.json"
OVERRIDES_FILE = Path("/home/masus/rsi-portfolio") / "country_overrides.json"

# Биржи, где листингов-акций/товаров можно ждать. На остальных (крипта, pre-IPO)
# неизвестные тикеры получают категорию "Другое" и по умолчанию скрыты.
TRADFI_DEXES = {"xyz", "cash", "flx", "km"}
YAHOO_DEXES = {"xyz", "cash", "flx"}       # где допустим поиск страны через Yahoo

NO_COUNTRY = "Без страны (товар)"
UNKNOWN_COUNTRY = "Не определена"

# ============================== СПРАВОЧНИКИ ==============================
# Страна = страна головного офиса эмитента.
# Строки, помеченные [src], сверены со списком рынков trade.xyz (DefiLlama, октябрь 2026);
# остальные - общеизвестные факты. Всё, чего здесь нет, ищется через Yahoo или помечается
# "Не определена" - ничего не додумывается.
US, KR, CN, TW, NL, GB, CA = "США", "Южная Корея", "Китай", "Тайвань", "Нидерланды", "Великобритания", "Канада"
SEED: Dict[str, Tuple[str, str, str]] = {
    # тикер: (название, страна, категория)
    "NVDA": ("NVIDIA", US, "Акция"),                      # [src]
    "MRVL": ("Marvell Technology", US, "Акция"),          # [src]
    "GOOGL": ("Alphabet", US, "Акция"),                   # [src]
    "INTC": ("Intel", US, "Акция"),                       # [src]
    "ORCL": ("Oracle", US, "Акция"),                      # [src]
    "SNDK": ("Sandisk", US, "Акция"),                     # [src]
    "CRCL": ("Circle Internet Group", US, "Акция"),       # [src]
    "CBRS": ("Cerebras Systems", US, "Акция"),            # [src]
    "MSFT": ("Microsoft", US, "Акция"),                   # [src]
    "META": ("Meta Platforms", US, "Акция"),              # [src]
    "AAPL": ("Apple", US, "Акция"),                       # [src]
    "TSLA": ("Tesla", US, "Акция"),                       # [src]
    "MSTR": ("Strategy", US, "Акция"),                    # [src]
    "PLTR": ("Palantir Technologies", US, "Акция"),       # [src]
    "LITE": ("Lumentum Holdings", US, "Акция"),           # [src]
    "MU": ("Micron Technology", US, "Акция"),             # [src]
    "SPCX": ("Space Exploration Technologies (SpaceX)", US, "Акция"),  # [src]
    "BB": ("BlackBerry", CA, "Акция"),                    # [src]
    "ARM": ("Arm Holdings", GB, "Акция"),                 # [src]
    "NBIS": ("Nebius Group", NL, "Акция"),                # [src]
    "SKHX": ("SK hynix", KR, "Акция"),                    # [src]
    "SKHY": ("SK hynix ADR", KR, "Акция"),                # [src]
    "SMSN": ("Samsung Electronics", KR, "Акция"),         # [src]
    "CXMT": ("ChangXin Memory Technologies", CN, "Акция"),  # [src]
    "DRAM": ("Roundhill Memory ETF", US, "ETF"),          # [src]
    "AMZN": ("Amazon", US, "Акция"),
    "AMD": ("Advanced Micro Devices", US, "Акция"),
    "NFLX": ("Netflix", US, "Акция"),
    "COIN": ("Coinbase", US, "Акция"),
    "HOOD": ("Robinhood", US, "Акция"),
    "AVGO": ("Broadcom", US, "Акция"),
    "TSM": ("TSMC", TW, "Акция"),
    "BABA": ("Alibaba", CN, "Акция"),
    "ASML": ("ASML", NL, "Акция"),
}

# Товары. Названия подтверждены для GOLD/SILVER/CL/BRENTOIL [src]; остальное - по тикеру.
COMMODITIES: Dict[str, str] = {
    "GOLD": "Золото", "SILVER": "Серебро", "CL": "Нефть WTI", "BRENTOIL": "Нефть Brent",
    "OIL": "Нефть", "NATGAS": "Природный газ", "WHEAT": "Пшеница", "CORN": "Кукуруза",
    "COPPER": "Медь", "PLATINUM": "Платина", "PALLADIUM": "Палладий",
    "URANIUM": "Уран", "ALUMINIUM": "Алюминий", "ALUMINUM": "Алюминий",
}
INDICES: Dict[str, str] = {"SP500": "S&P 500", "XYZ100": "Nasdaq-100", "JP225": "Nikkei 225", "KR200": "KOSPI 200"}
FX: Dict[str, str] = {"EUR": "EUR/USD", "JPY": "USD/JPY", "DXY": "Индекс доллара", "GBP": "GBP/USD"}

COUNTRY_RU = {
    "United States": "США", "South Korea": "Южная Корея", "China": "Китай", "Taiwan": "Тайвань",
    "Japan": "Япония", "Canada": "Канада", "United Kingdom": "Великобритания", "Netherlands": "Нидерланды",
    "Germany": "Германия", "France": "Франция", "Switzerland": "Швейцария", "Ireland": "Ирландия",
    "Israel": "Израиль", "Singapore": "Сингапур", "Hong Kong": "Гонконг", "India": "Индия",
    "Brazil": "Бразилия", "Australia": "Австралия", "Denmark": "Дания", "Sweden": "Швеция",
    "Italy": "Италия", "Spain": "Испания", "Argentina": "Аргентина", "Luxembourg": "Люксембург",
    "Cayman Islands": "Каймановы острова", "Bermuda": "Бермуды", "Finland": "Финляндия",
    "Norway": "Норвегия", "Belgium": "Бельгия", "Mexico": "Мексика", "Uruguay": "Уругвай",
}

# Если тикер на бирже отличается от символа Yahoo - добавьте сюда (или в country_overrides.json).
YAHOO_ALIASES = {"SKHX": "000660.KS", "SMSN": "005930.KS"}

log = logging.getLogger("hl_rsi")


# ============================== УТИЛИТЫ ==============================
def load_json(path: Path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json_atomic(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)


def write_text_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


# ============================== RSI ==============================
def wilder_rsi(closes: List[float], period: int = RSI_PERIOD) -> Optional[float]:
    """RSI по Уайлдеру (как в TradingView/StockCharts). Нужно минимум period+1 цен."""
    if len(closes) < period + 1:
        return None
    gains = losses = 0.0
    for i in range(1, period + 1):
        d = closes[i] - closes[i - 1]
        gains += max(d, 0.0)
        losses += max(-d, 0.0)
    avg_g, avg_l = gains / period, losses / period
    for i in range(period + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        avg_g = (avg_g * (period - 1) + max(d, 0.0)) / period
        avg_l = (avg_l * (period - 1) + max(-d, 0.0)) / period
    if avg_l == 0:
        return 100.0 if avg_g > 0 else 50.0
    return 100.0 - 100.0 / (1.0 + avg_g / avg_l)


def zone(rsi: Optional[float]) -> int:
    """-3..-1 перепроданность (<10/<20/<30), 0 норма, 1..3 перекупленность (>70/>80/>90)."""
    if rsi is None:
        return 0
    if rsi < LOW_LEVELS[2]:
        return -3
    if rsi < LOW_LEVELS[1]:
        return -2
    if rsi < LOW_LEVELS[0]:
        return -1
    if rsi > HIGH_LEVELS[2]:
        return 3
    if rsi > HIGH_LEVELS[1]:
        return 2
    if rsi > HIGH_LEVELS[0]:
        return 1
    return 0


def next_alert_state(last: int, rsi: Optional[float]) -> Tuple[int, bool]:
    """Возвращает (новое состояние, слать ли алерт). Состояние хранит максимальную достигнутую зону."""
    if rsi is None:
        return last, False
    z = zone(rsi)
    if z == 0:
        if last < 0 and rsi < LOW_LEVELS[0] + ALERT_HYSTERESIS:
            return last, False          # у границы: не сбрасываем, чтобы не мигало
        if last > 0 and rsi > HIGH_LEVELS[0] - ALERT_HYSTERESIS:
            return last, False
        return 0, False
    same_side = last != 0 and (z > 0) == (last > 0)
    deeper = (not same_side) or abs(z) > abs(last)
    fire = abs(z) >= ALERT_MIN_ZONE and deeper
    new_state = z if deeper else last
    return new_state, fire


# ============================== API ==============================
class RateLimiter:
    """Скользящее окно 60 сек по суммарному weight."""

    def __init__(self, budget_per_min: int):
        self.budget = budget_per_min
        self.events: deque = deque()

    def acquire(self, weight: int) -> None:
        while True:
            now = time.monotonic()
            while self.events and now - self.events[0][0] >= 60:
                self.events.popleft()
            used = sum(w for _, w in self.events)
            if used + weight <= self.budget:
                self.events.append((now, weight))
                return
            time.sleep(max(60 - (now - self.events[0][0]) + 0.05, 0.1))


class HyperliquidClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.limiter = RateLimiter(RATE_BUDGET_PER_MIN)

    def post(self, payload: dict, weight: int = 20, retries: int = 5):
        last_err = None
        for attempt in range(retries):
            self.limiter.acquire(weight)
            try:
                r = self.session.post(API_URL, json=payload, timeout=30)
                if r.status_code == 429:
                    wait = 15 * (attempt + 1)
                    log.warning("429 от API, жду %s с", wait)
                    time.sleep(wait)
                    continue
                r.raise_for_status()
                return r.json()
            except (requests.RequestException, ValueError) as e:
                last_err = e
                log.warning("Ошибка запроса (%s/%s): %s", attempt + 1, retries, e)
                time.sleep(2 ** attempt)
        raise RuntimeError(f"API недоступен: {last_err}")

    def perp_dexs(self) -> List[str]:
        data = self.post({"type": "perpDexs"})
        # элемент 0 = null (основная биржа Hyperliquid), дальше HIP-3 биржи
        return [d["name"] for d in data if d and d.get("name")]

    def meta_and_ctxs(self, dex: str):
        return self.post({"type": "metaAndAssetCtxs", "dex": dex})

    def candles(self, coin: str, interval: str, start_ms: int, end_ms: int, interval_ms: int) -> List[list]:
        n_est = int((end_ms - start_ms) // interval_ms) + 1
        weight = 20 + n_est // 60 + 1          # 20 + 1 за каждые 60 свечей в ответе
        data = self.post(
            {"type": "candleSnapshot",
             "req": {"coin": coin, "interval": interval, "startTime": int(start_ms), "endTime": int(end_ms)}},
            weight=weight,
        )
        out = []
        for c in data or []:
            try:
                out.append([int(c["t"]), int(c["T"]), float(c["c"])])
            except (KeyError, TypeError, ValueError):
                continue
        return out


# ============================== АКТИВЫ И СТРАНЫ ==============================
@dataclass
class Asset:
    coin: str            # как в API: "xyz:TSLA"
    dex: str
    ticker: str          # "TSLA"
    name: str
    category: str
    country: str
    price: Optional[float]
    volume24h: Optional[float]


class Resolver:
    """Название / категория / страна для тикера."""

    def __init__(self):
        self.overrides: dict = load_json(OVERRIDES_FILE, {})
        self.yahoo_cache: dict = load_json(YAHOO_CACHE_FILE, {})
        self.yahoo_failed: set = set(load_json(YAHOO_FAILED_FILE, []))
        self.dirty = False
        self.unresolved: set = set()

    def _yahoo(self, ticker: str) -> Optional[dict]:
        if ticker in self.yahoo_cache:
            return self.yahoo_cache[ticker]
        if ticker in self.yahoo_failed:
            return None
        try:
            import yfinance as yf
        except ImportError:
            self.yahoo_failed.add(ticker)
            return None
        try:
            info = yf.Ticker(YAHOO_ALIASES.get(ticker, ticker)).info or {}
            country = info.get("country")
            qt = (info.get("quoteType") or "").upper()
            if not country and qt != "ETF":
                raise ValueError("нет country в профиле")
            res = {
                "name": info.get("longName") or info.get("shortName") or ticker,
                "country": COUNTRY_RU.get(country, country) if country else None,
                "category": "ETF" if qt == "ETF" else "Акция",
            }
            self.yahoo_cache[ticker] = res
            self.dirty = True
            return res
        except Exception as e:  # yfinance бросает разное
            log.info("Yahoo не знает %s: %s", ticker, e)
            self.yahoo_failed.add(ticker)
            return None

    def resolve(self, coin: str, dex: str, ticker: str) -> Tuple[str, str, str]:
        t = ticker.upper()
        if t in SEED:
            name, country, cat = SEED[t]
        elif t in COMMODITIES:
            name, country, cat = COMMODITIES[t], NO_COUNTRY, "Товар"
        elif t in INDICES:
            name, country, cat = INDICES[t], NO_COUNTRY, "Индекс"
        elif t in FX:
            name, country, cat = FX[t], NO_COUNTRY, "Валюта"
        elif dex not in TRADFI_DEXES:
            name, country, cat = ticker, UNKNOWN_COUNTRY, "Другое"
        else:
            y = self._yahoo(t) if dex in YAHOO_DEXES else None
            if y:
                name, country, cat = y["name"], y["country"] or UNKNOWN_COUNTRY, y["category"]
            else:
                name, country, cat = ticker, UNKNOWN_COUNTRY, "Не определён"
        ov = self.overrides.get(coin) or self.overrides.get(t)
        if isinstance(ov, dict):
            name = ov.get("name", name)
            country = ov.get("country", country)
            cat = ov.get("category", cat)
        if country == UNKNOWN_COUNTRY and cat in ("Акция", "ETF", "Не определён"):
            self.unresolved.add(coin)
        return name, cat, country

    def flush(self):
        if self.dirty:
            save_json_atomic(YAHOO_CACHE_FILE, self.yahoo_cache)
            self.dirty = False
        save_json_atomic(YAHOO_FAILED_FILE, list(self.yahoo_failed))


def to_float(x) -> Optional[float]:
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def discover_assets(hl: HyperliquidClient, resolver: Resolver) -> List[Asset]:
    assets: List[Asset] = []
    for dex in hl.perp_dexs():
        try:
            data = hl.meta_and_ctxs(dex)
            meta, ctxs = data[0], data[1]
        except Exception as e:
            log.warning("Биржа %s пропущена: %s", dex, e)
            continue
        for u, c in zip(meta.get("universe", []), ctxs):
            if u.get("isDelisted"):
                continue
            raw = u["name"]
            coin = raw if ":" in raw else f"{dex}:{raw}"
            ticker = coin.split(":", 1)[1]
            name, cat, country = resolver.resolve(coin, dex, ticker)
            if cat not in INCLUDE_CATEGORIES:
                continue
            price = to_float(c.get("markPx")) or to_float(c.get("midPx"))
            assets.append(Asset(coin, dex, ticker, name, cat, country, price, to_float(c.get("dayNtlVlm"))))
    resolver.flush()
    assets.sort(key=lambda a: (a.category, a.country, a.ticker, a.dex))
    return assets


def write_assets_csv(assets: List[Asset]) -> None:
    with open(ASSETS_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Биржа", "Монета (API)", "Тикер", "Название", "Категория", "Страна", "Цена", "Объём 24ч, $"])
        for a in sorted(assets, key=lambda a: (a.country, a.category, a.ticker)):
            w.writerow([a.dex, a.coin, a.ticker, a.name, a.category, a.country, a.price, a.volume24h])


# ============================== СВЕЧИ И RSI ==============================
class CandleStore:
    def __init__(self):
        self.data: Dict[str, List[list]] = load_json(CANDLES_FILE, {})
        self.last_refresh: Dict[str, int] = {}
        self.changed = False

    @staticmethod
    def key(coin: str, tf: str) -> str:
        return f"{coin}|{tf}"

    def refresh(self, hl: HyperliquidClient, assets: List[Asset], now_ms: int) -> None:
        todo = []
        for a in assets:
            for tf, _, ims in TIMEFRAMES:
                k = self.key(a.coin, tf)
                cs = self.data.get(k)
                rolled = (not cs) or now_ms > cs[-1][1]
                if rolled and now_ms - self.last_refresh.get(k, 0) > MIN_REFRESH_GAP_MS:
                    start = (now_ms - CANDLES_HISTORY * ims) if not cs else cs[-1][0]
                    todo.append((a.coin, tf, ims, k, start))
        if not todo:
            return
        log.info("Обновляю свечи: %s рядов (первый запуск может идти несколько минут)", len(todo))
        for i, (coin, tf, ims, k, start) in enumerate(todo, 1):
            try:
                new = hl.candles(coin, tf, start, now_ms, ims)
            except Exception as e:
                log.warning("Свечи %s %s не получены: %s", coin, tf, e)
                continue
            self.last_refresh[k] = now_ms
            merged = {c[0]: c for c in self.data.get(k, [])}
            for c in new:
                merged[c[0]] = c
            self.data[k] = [merged[t] for t in sorted(merged)][-(CANDLES_HISTORY + 20):]
            self.changed = True
            if i % 50 == 0:
                log.info("  %s/%s", i, len(todo))
                self.save()
        self.save()

    def save(self) -> None:
        if self.changed:
            save_json_atomic(CANDLES_FILE, self.data)
            self.changed = False

    def closes_live(self, coin: str, tf: str, price: Optional[float], now_ms: int) -> List[float]:
        """Закрытия + живая цена: последняя свеча обновляется ценой, а если она уже закрыта - добавляется новая."""
        cs = self.data.get(self.key(coin, tf)) or []
        closes = [c[2] for c in cs]
        if price is None or not closes:
            return closes
        if now_ms > cs[-1][1]:
            closes.append(price)
        else:
            closes[-1] = price
        return closes


def compute_rsi(store: CandleStore, a: Asset, now_ms: int) -> Dict[str, Tuple[Optional[float], Optional[float]]]:
    """{tf: (RSI сейчас, изменение к RSI на закрытии предыдущей свечи)}"""
    out = {}
    for tf, _, _ in TIMEFRAMES:
        closes = store.closes_live(a.coin, tf, a.price, now_ms)
        cur = wilder_rsi(closes)
        prev = wilder_rsi(closes[:-1]) if len(closes) > 1 else None
        delta = (cur - prev) if (cur is not None and prev is not None) else None
        out[tf] = (cur, delta)
    return out


# ============================== HTML ==============================
def fmt_price(p: Optional[float]) -> str:
    if p is None:
        return "—"
    return f"{p:,.2f}" if p >= 1 else f"{p:.6g}"


def fmt_vol(v: Optional[float]) -> str:
    if v is None:
        return "—"
    for lim, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if v >= lim:
            return f"{v / lim:.1f}{suf}"
    return f"{v:.0f}"


ZONE_CLASS = {-3: "lo3", -2: "lo2", -1: "lo1", 0: "", 1: "hi1", 2: "hi2", 3: "hi3"}

HTML_TEMPLATE = """<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="__REFRESH__">
<title>RSI: акции и товары на Hyperliquid</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--tx:#1b1f24;--mut:#6a737d;--line:#e3e6ea;--head:#eef0f3;
--lo1:#d7f0dc;--lo2:#8fd6a0;--lo3:#2f9e55;--hi1:#fadada;--hi2:#f08a8a;--hi3:#c92a2a}
@media (prefers-color-scheme:dark){:root{--bg:#14171a;--card:#1c2024;--tx:#e6e9ec;--mut:#98a1ab;--line:#2d3339;--head:#242a30;
--lo1:#1f4a2e;--lo2:#2b7a47;--lo3:#2f9e55;--hi1:#5a2626;--hi2:#9c3b3b;--hi3:#c92a2a}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);font:14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-variant-numeric:tabular-nums}
main{max-width:1280px;margin:0 auto;padding:20px 16px 40px}
h1{font-size:20px;margin:0 0 4px}
.sub{color:var(--mut);margin:0 0 14px}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px}
input,select{background:var(--card);color:var(--tx);border:1px solid var(--line);border-radius:6px;padding:6px 9px;font:inherit}
input{min-width:240px}
.legend{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 12px;color:var(--mut)}
.legend span{padding:2px 8px;border-radius:4px;color:var(--tx)}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card)}
table{border-collapse:collapse;width:100%}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);white-space:nowrap;text-align:left}
th{background:var(--head);cursor:pointer;user-select:none;position:sticky;top:0;font-weight:600}
th:hover{text-decoration:underline}
th.asc::after{content:" ▲";color:var(--mut)} th.desc::after{content:" ▼";color:var(--mut)}
td.n,th.n{text-align:right}
tbody tr:hover td{background:var(--head)}
td small{color:var(--mut);margin-left:6px;font-size:11px}
td.lo1{background:var(--lo1)} td.lo2{background:var(--lo2)} td.lo3{background:var(--lo3);color:#fff;font-weight:600}
td.hi1{background:var(--hi1)} td.hi2{background:var(--hi2)} td.hi3{background:var(--hi3);color:#fff;font-weight:600}
td.lo3 small,td.hi3 small{color:#fff;opacity:.85}
.tk{font-weight:600}
.warn{margin-top:12px;color:var(--mut);font-size:12px}
</style></head><body><main>
<h1>RSI: акции и товары на Hyperliquid (HIP-3)</h1>
<p class="sub">Обновлено __UPDATED__ · активов: <b id="cnt">__TOTAL__</b> из __TOTAL__ · RSI(__PERIOD__) по Уайлдеру, учитывает текущую свечу · Δ — изменение к закрытию предыдущей свечи</p>
<div class="bar" style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px">
<input id="q" type="search" placeholder="Тикер, название, страна">
<select id="fcat"><option value="">Все типы</option>__CATS__</select>
<select id="fcountry"><option value="">Все страны</option>__COUNTRIES__</select>
<select id="fdex"><option value="">Все биржи</option>__DEXES__</select>
<div class="legend" style="margin:0;display:flex;flex-wrap:wrap;gap:6px;color:var(--mut)">
<span style="background:var(--lo3);color:#fff">&lt;10</span><span style="background:var(--lo2)">&lt;20</span><span style="background:var(--lo1)">&lt;30</span>
<span style="background:var(--hi1)">&gt;70</span><span style="background:var(--hi2)">&gt;80</span><span style="background:var(--hi3);color:#fff">&gt;90</span>
</div>
<div class="wrap"><table id="tbl"><thead><tr>__HEAD__</tr></thead><tbody>
__ROWS__
</tbody></table></div>
<p class="warn">__WARN__</p>
</main>
<script>
const table=document.getElementById('tbl'),tbody=table?table.tBodies[0]:null,ths=table?[...table.tHead.rows[0].cells]:[];
const q=document.getElementById('q'),fcat=document.getElementById('fcat'),fcountry=document.getElementById('fcountry'),fdex=document.getElementById('fdex'),cnt=document.getElementById('cnt');
let col=-1,dir=1;
function val(td,num){const v=td?td.dataset.v:undefined;if(num){const n=parseFloat(v);return isNaN(n)?null:n}return(v||'').toLowerCase()}
function sortBy(i,d){if(i>=ths.length)return;
  const num=ths[i].dataset.type==='num';
  const rows=[...tbody.rows];
  rows.sort((a,b)=>{const x=val(a.cells[i],num),y=val(b.cells[i],num);
    if(x===null&&y===null)return 0;if(x===null)return 1;if(y===null)return -1;
    return(num?(x<y?-1:x>y?1:0):x.localeCompare(y,'ru'))*d});
  rows.forEach(r=>tbody.appendChild(r));
  ths.forEach(h=>h.classList.remove('asc','desc'));
  ths[i].classList.add(d===1?'asc':'desc');
}
function save(){try{localStorage.setItem('hlrsi',JSON.stringify({col,dir,q:q.value,c:fcat.value,k:fcountry.value,d:fdex.value}))}catch(e){}}
function applyFilter(){
  const s=q.value.trim().toLowerCase();let n=0;
  for(const r of tbody.rows){
    const ok=(!s||r.dataset.s.includes(s))&&(!fcat.value||r.dataset.cat===fcat.value)&&(!fcountry.value||r.dataset.country===fcountry.value)&&(!fdex.value||r.dataset.dex===fdex.value);
    r.style.display=ok?'':'none';if(ok)n++;
  }
  cnt.textContent=n;save();
}
if(ths&&ths.length){
ths.forEach((th,i)=>th.addEventListener('click',()=>{dir=(col===i)?-dir:1;col=i;sortBy(i,dir);save()}));
}
[q,fcat,fcountry,fdex].forEach(el=>el&&el.addEventListener('input',applyFilter));
try{const s=JSON.parse(localStorage.getItem('hlrsi')||'null');
  if(s&&table&&ths&&ths.length){q.value=s.q||'';fcat.value=s.c||'';fcountry.value=s.k||'';fdex.value=s.d||'';
    if(s.col>=0&&s.col<ths.length){col=s.col;dir=s.dir||1;sortBy(col,dir)}}}catch(e){}
if(typeof applyFilter==='function')applyFilter();
/* HW: fetch history + click popup */
let HISTORY={};
function loadHistory(){fetch('history.json').then(r=>r.json()).then(d=>{HISTORY=d;}).catch(()=>{});}
loadHistory();
function showPopup(td){
  const ticker=td.closest('tr').querySelector('td.tk').dataset.v||'';
  const idx=Array.from(td.parentNode.children).indexOf(td);
  const hdr=document.querySelector('#tbl thead tr').children[idx].textContent.trim();
  const key=hdr.replace(/\s+/g,'_').toLowerCase();
  const items=(HISTORY[ticker]||{})[key]||(HISTORY[ticker]||{})[hdr]||[];
  const html='<h3 style=\'margin:0 0 8px;padding:6px 8px;background:#4a4e55;border-radius:4px;color:#fff;font-size:15px;\'>\'+ticker+' · '+hdr+'</h3><table><tr><th>t</th><th>v</th></tr>'+items.map(it=>'<tr style="border-bottom:1px solid #444;"><td style="padding:3px 4px;">'+it.t+'</td><td style="padding:3px 4px;text-align:right;">'+it.v+'</td></tr>').join('')+'</table><button onclick="this.parentElement.remove()" style="margin-top:10px;padding:6px 12px;background:#555;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:12px;">close</button>';
  const d=document.createElement('div');
  d.style.cssText='position:fixed;top:10%;left:10%;width:320px;background:#2b2d31;border:2px solid #555;padding:14px;z-index:9999;border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,.6);font-family:sans-serif;font-size:13px;color:#e8e8e8';
  d.innerHTML=html; d.querySelector('button').onclick=()=>d.remove(); document.body.appendChild(d);
}
if(document.querySelectorAll){
document.querySelectorAll('td.n').forEach(td=>{
  td.style.cursor='pointer';
  td.addEventListener('click',()=>showPopup(td));
});
}
</script></body></html>
"""


def opts(values) -> str:
    return "".join(f'<option value="{html.escape(v)}">{html.escape(v)}</option>' for v in sorted(set(values)))


def build_html(assets: List[Asset], rsi: dict, unresolved: set) -> str:
    # z-score по 1D RSI для всей выборки
    rsi_1d = [rsi.get(a.coin, {}).get("1d", (None, None))[0] for a in assets]
    rsi_1d = [v for v in rsi_1d if v is not None]
    mean_1d = sum(rsi_1d) / len(rsi_1d) if rsi_1d else 0.0
    std_1d = (sum((v - mean_1d) ** 2 for v in rsi_1d) / len(rsi_1d)) ** 0.5 if rsi_1d else 0.0
    cols = [("Тикер", "t"), ("Биржа", "t"), ("Название", "t"), ("Тип", "t"), ("Страна", "t"),
            ("Цена", "n"), ("Объём 24ч", "n"), ("Z 1D", "n")] + [(lbl, "n") for _, lbl, _ in TIMEFRAMES]
    head = "".join(
        f'<th data-type="{"num" if t == "n" else "txt"}"{" class=n" if t == "n" else ""}>{html.escape(n)}</th>'
        for n, t in cols
    )
    rows = []
    for a in assets:
        r = rsi.get(a.coin, {})
        cells = [
            f'<td class="tk" data-v="{html.escape(a.ticker)}"><a style="color:#fff;text-decoration:none;" href="https://app.hyperliquid.xyz/trade/{html.escape(a.coin)}" target="_blank">{html.escape(a.ticker)}</a></td>',
            f'<td data-v="{html.escape(a.dex)}">{html.escape(a.dex)}</td>',
            f'<td data-v="{html.escape(a.name)}">{html.escape(a.name)}</td>',
            f'<td data-v="{html.escape(a.category)}">{html.escape(a.category)}</td>',
            f'<td data-v="{html.escape(a.country)}">{html.escape(a.country)}</td>',
            f'<td class="n" data-v="{a.price if a.price is not None else ""}">{fmt_price(a.price)}</td>',
            f'<td class="n" data-v="{a.volume24h if a.volume24h is not None else ""}">{fmt_vol(a.volume24h)}</td>',
        ]
        r_1d = rsi.get(a.coin, {}).get("1d", (None, None))[0]
        z_cell = f'<td class="n" data-v="{(r_1d - mean_1d) / std_1d if std_1d > 0 and r_1d is not None else ""}">{(r_1d - mean_1d) / std_1d:.2f}</td>' if r_1d is not None and std_1d > 0 else '<td class="n" data-v="">—</td>'
        cells.append(z_cell)
        for tf, _, _ in TIMEFRAMES:
            cur, delta = r.get(tf, (None, None))
            if cur is None:
                cells.append('<td class="n" data-v="">—</td>')
                continue
            arrow = ""
            if delta is not None and abs(delta) >= 0.05:
                arrow = f"<small>{'▲' if delta > 0 else '▼'}{abs(delta):.1f}</small>"
            cells.append(f'<td class="n {ZONE_CLASS[zone(cur)]}" data-v="{cur:.2f}">{cur:.1f}{arrow}</td>')
        search = f"{a.ticker} {a.name} {a.country} {a.coin}".lower()
        rows.append(
            f'<tr data-s="{html.escape(search)}" data-cat="{html.escape(a.category)}" '
            f'data-country="{html.escape(a.country)}" data-dex="{html.escape(a.dex)}">{"".join(cells)}</tr>'
        )
    warn = ""
    if unresolved:
        warn = ("Страна не определена для: " + ", ".join(sorted(unresolved)) +
                ". Добавьте их в data/country_overrides.json, например "
                '{"xyz:TICKER": {"country": "Япония", "category": "Акция"}}.')
    return (HTML_TEMPLATE
            .replace("__REFRESH__", str(CYCLE_SECONDS))
            .replace("__UPDATED__", datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC"))
            .replace("__TOTAL__", str(len(assets)))
            .replace("__PERIOD__", str(RSI_PERIOD))
            .replace("__CATS__", opts(a.category for a in assets))
            .replace("__COUNTRIES__", opts(a.country for a in assets))
            .replace("__DEXES__", opts(a.dex for a in assets))
            .replace("__HEAD__", head)
            .replace("__ROWS__", "\n".join(rows))
            .replace("__WARN__", html.escape(warn)))


# ============================== TELEGRAM ==============================
def tg_send(text: str) -> bool:
    if not (TG_BOT_TOKEN and TG_CHAT_ID):
        log.info("Telegram не настроен (TG_BOT_TOKEN / TG_CHAT_ID) — сообщение пропущено")
        return False
    chunks, cur = [], ""
    for line in text.split("\n"):
        if len(cur) + len(line) + 1 > 3800:
            chunks.append(cur)
            cur = ""
        cur += line + "\n"
    if cur.strip():
        chunks.append(cur)
    ok = True
    for ch in chunks:
        try:
            payload = {"chat_id": TG_CHAT_ID, "text": ch, "parse_mode": "HTML", "disable_web_page_preview": True}
            if os.getenv("TG_THREAD_ID"):
                payload["message_thread_id"] = int(os.getenv("TG_THREAD_ID"))
            r = requests.post(
                f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
                json=payload,
                timeout=20,
            )
            if r.status_code != 200:
                log.warning("Telegram ответил %s: %s", r.status_code, r.text[:200])
                ok = False
        except requests.RequestException as e:
            log.warning("Telegram недоступен: %s", e)
            ok = False
        time.sleep(0.4)
    return ok


def alert_line(a: Asset, label: str, cur: float, delta: Optional[float]) -> str:
    z = zone(cur)
    icon = "🟢" if z < 0 else "🔴"
    level = f"&lt;{LOW_LEVELS[abs(z) - 1]}" if z < 0 else f"&gt;{HIGH_LEVELS[z - 1]}"
    d = f" ({'▲' if delta > 0 else '▼'}{abs(delta):.1f})" if delta is not None and abs(delta) >= 0.05 else ""
    return (f"{icon} <b>{html.escape(a.coin)}</b> · {html.escape(a.category)} · {html.escape(a.country)}\n"
            f"    {label}: <b>{cur:.1f}</b>{d} — зона {level}, цена {fmt_price(a.price)}")


def process_alerts(assets: List[Asset], rsi: dict, state: dict, silent: bool) -> List[str]:
    alerts_state = state.setdefault("alerts", {})
    lines = []
    for a in assets:
        for tf, label, _ in TIMEFRAMES:
            cur, delta = rsi.get(a.coin, {}).get(tf, (None, None))
            k = f"{a.coin}|{tf}"
            new, fire = next_alert_state(alerts_state.get(k, 0), cur)
            alerts_state[k] = new
            if fire and not silent:
                lines.append(alert_line(a, label, cur, delta))
    return lines


# ============================== ЦИКЛ ==============================
def run_cycle(hl: HyperliquidClient, resolver: Resolver, store: CandleStore, state: dict,
              use_telegram: bool, first_run: bool) -> None:
    now_ms = int(time.time() * 1000)
    assets = discover_assets(hl, resolver)
    write_assets_csv(assets)
    store.refresh(hl, assets, now_ms)
    rsi = {a.coin: compute_rsi(store, a, now_ms) for a in assets}

    write_text_atomic(HTML_FILE, build_html(assets, rsi, resolver.unresolved))
    # VARIANT 3: write current measurement to data/history.json (create/fill)
    hist_path = DATA_DIR / "history.json"
    hist = {}
    try:
        with open(hist_path, "r", encoding="utf-8") as f:
            hist = json.load(f)
    except Exception:
        hist = {}
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for a in assets:
        coin = a.coin
        ticker = a.ticker
        hist.setdefault(ticker, {})
        def last_val(key):
            arr = hist[ticker].get(key, [])
            return arr[-1]["v"] if arr else None
        def should_append(key, cur, rel=0.01, abs_off=0.0):
            prev = last_val(key)
            if prev is None: return True
            if abs_off and abs(cur - prev) >= abs_off: return True
            if prev != 0 and abs(cur - prev) / abs(prev) >= rel: return True
            if prev == 0 and abs(cur) > rel: return True
            return False
        # price
        if should_append("price", a.price or 0, rel=0.005):
            hist[ticker].setdefault("price", []).append({"t": now_str, "v": round(a.price or 0, 2)})
        # volume
        if should_append("volume24h", a.volume24h or 0, rel=0.10):
            hist[ticker].setdefault("volume24h", []).append({"t": now_str, "v": round(a.volume24h or 0, 2)})
        # rsi values
        r = rsi.get(coin, {})
        for tf, lbl, _ in TIMEFRAMES:
            cur, _ = r.get(tf, (None, None))
            if cur is not None:
                key = lbl.replace(" ", "_")
                if should_append(key, cur, rel=0, abs_off=2.0 if "rsi" in key.lower() else 0.2):
                    hist[ticker].setdefault(key, []).append({"t": now_str, "v": round(cur, 2)})
        # trim to 150 last per param
        for k in list(hist[ticker]):
            if isinstance(hist[ticker][k], list) and len(hist[ticker][k]) > 150:
                hist[ticker][k] = hist[ticker][k][-150:]
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)
    # also write to rsi-portfolio for git push
    portfolio_hist = Path("/home/masus/rsi-portfolio") / "history.json"
    with open(portfolio_hist, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)
    lines = process_alerts(assets, rsi, state, silent=first_run)
    save_json_atomic(STATE_FILE, state)

    n_ext = sum(1 for a in assets for tf, _, _ in TIMEFRAMES if zone(rsi[a.coin][tf][0]) != 0)
    log.info("Активов: %s · RSI в цветовых зонах: %s · новых алертов: %s", len(assets), n_ext, len(lines))
    if use_telegram:
        if first_run:
            tg_send(f"✅ Монитор RSI запущен. Активов: {len(assets)}, "
                    f"значений RSI в зонах &lt;30 / &gt;70: {n_ext}. Алерты — от зон "
                    f"&lt;{LOW_LEVELS[ALERT_MIN_ZONE - 1]} / &gt;{HIGH_LEVELS[ALERT_MIN_ZONE - 1]}.")
        elif lines:
            stamp = datetime.now(timezone.utc).strftime("%d.%m %H:%M UTC")
            tg_send(f"<b>RSI-алерты Hyperliquid · {stamp}</b>\n\n" + "\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description="RSI-монитор акций и товаров Hyperliquid (HIP-3)")
    ap.add_argument("--once", action="store_true", help="один проход и выход")
    ap.add_argument("--no-telegram", action="store_true", help="не отправлять в Telegram")
    ap.add_argument("--list-assets", action="store_true", help="только список активов и стран -> assets.csv")
    ap.add_argument("--test-telegram", action="store_true", help="отправить тестовое сообщение")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.test_telegram:
        ok = tg_send("Тест: монитор RSI Hyperliquid подключён ✅")
        print("OK" if ok else "Не отправлено — проверьте TG_BOT_TOKEN и TG_CHAT_ID")
        return 0 if ok else 1

    hl, resolver = HyperliquidClient(), Resolver()
    if args.list_assets:
        assets = discover_assets(hl, resolver)
        write_assets_csv(assets)
        print(f"Активов: {len(assets)} -> {ASSETS_CSV}")
        if resolver.unresolved:
            print("Страна не определена:", ", ".join(sorted(resolver.unresolved)))
        return 0

    store = CandleStore()
    first_run = not STATE_FILE.exists()
    state = load_json(STATE_FILE, {})
    use_tg = not args.no_telegram

    while True:
        try:
            run_cycle(hl, resolver, store, state, use_tg, first_run)
            first_run = False
        except KeyboardInterrupt:
            raise
        except Exception:
            log.exception("Сбой цикла, повторю через %s с", CYCLE_SECONDS)
        if args.once:
            return 0
        try:
            time.sleep(CYCLE_SECONDS)
        except KeyboardInterrupt:
            break
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
