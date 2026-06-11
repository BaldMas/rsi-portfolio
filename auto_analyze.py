#!/usr/bin/env python3
"""
Автоматический скоринг новых монет по 29-пунктному фреймворку.
Заполняет то, что можно по API (CoinPaprika + Binance).
Остальное - n/a = 0 (строгий подход, нужен ручной анализ).

Использование:
  python3 auto_analyze.py              # анализ всех новых монет из Dropstab
  python3 auto_analyze.py SOL PENDLE   # анализ конкретных монет
"""

import sys
import os
import json
import math
import time
import urllib.request
from datetime import datetime, timezone, timedelta

ANALYSIS_DIR = "/home/masus/crypto_analysis"
ENV_FILE     = os.path.join(os.path.dirname(__file__), ".env")

# Веса по 29 критериям (из фреймворка)
WEIGHTS = {
    1: 8,   # Ликвидность
    2: 7,   # Токеномика и анлоки
    3: 7,   # Нарратив и фаза цикла
    4: 7,   # Технический анализ
    5: 3,   # Фундаментал (TVL, revenue)
    6: 4,   # On-chain метрики
    7: 2,   # Команда, инвесторы, vesting
    8: 2,   # Конкуренция и moat
    9: 2,   # Безопасность
    10: 1,  # Социальные метрики
    11: 2,  # Регуляторные риски
    12: 2,  # Макро-контекст
    13: 7,  # Деривативы и позиционирование
    14: 1,  # Корреляции и бета
    15: 2,  # Реальная доходность
    16: 7,  # Катализаторы и roadmap
    17: 2,  # Активность разработки
    18: 3,  # Концентрация холдеров / smart money
    19: 1,  # Казна и runway
    20: 2,  # Качество реакции на новости
    21: 3,  # Стейблкоины и потоки в экосистеме
    22: 1,  # Интеграции и BD
    23: 4,  # Value accrual
    24: 7,  # RS к сектору
    25: 4,  # Cost basis distribution (URPD)
    26: 4,  # Exit liquidity
    27: 3,  # Поведение в аналогичных сетапах прошлых циклов
    28: 1,  # Key person risk
    29: 1,  # Off-ramp и конвертируемость
}

MNE = timezone(timedelta(hours=2))


def fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {}


def fetch_closes_binance(symbol, limit=250):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=1d&limit={limit}"
    data = fetch_json(url)
    if not data or not isinstance(data, list):
        return []
    return [float(k[4]) for k in data]


def calc_rsi(series, period=14):
    if len(series) < period + 2:
        return None
    gains, losses = [], []
    for i in range(1, len(series)):
        d = series[i] - series[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    ag = sum(gains[:period]) / period
    al = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        ag = (ag * (period - 1) + gains[i]) / period
        al = (al * (period - 1) + losses[i]) / period
    if al == 0:
        return 100.0
    return 100 - 100 / (1 + ag / al)


def search_paprika(symbol):
    """Находит CoinPaprika ID по тикеру."""
    data = fetch_json(f"https://api.coinpaprika.com/v1/search?q={symbol}&c=currencies&limit=10")
    currencies = data.get("currencies", [])
    matches = [c for c in currencies if c.get("symbol", "").upper() == symbol.upper()]
    if not matches:
        return None
    matches.sort(key=lambda x: x.get("rank", 9999))
    return matches[0].get("id"), matches[0].get("name", symbol)


def fetch_paprika_ticker(coin_id):
    return fetch_json(f"https://api.coinpaprika.com/v1/tickers/{coin_id}?quotes=USD")


def fetch_paprika_coin(coin_id):
    return fetch_json(f"https://api.coinpaprika.com/v1/coins/{coin_id}")


def analyze_coin(symbol):
    """
    Полный автоматический анализ монеты.
    Возвращает dict с данными и предварительным score.
    """
    sym = symbol.upper()
    print(f"  Анализ {sym}...", flush=True)

    # ── CoinPaprika ──
    paprika_result = search_paprika(sym)
    if not paprika_result:
        print(f"    {sym}: не найден в CoinPaprika")
        return None
    coin_id, coin_name = paprika_result
    print(f"    CoinPaprika: {coin_id} ({coin_name})", flush=True)

    ticker = fetch_paprika_ticker(coin_id)
    time.sleep(0.5)
    coin_info = fetch_paprika_coin(coin_id)

    q = ticker.get("quotes", {}).get("USD", {})
    price        = float(q.get("price", 0) or 0)
    market_cap   = float(q.get("market_cap", 0) or 0)
    volume_24h   = float(q.get("volume_24h", 0) or 0)
    ath_price    = float(q.get("ath_price", 0) or 0)
    pct_from_ath = float(q.get("percent_from_price_ath", 0) or 0)

    circ_supply  = float(ticker.get("circulating_supply", 0) or 0)
    total_supply = float(ticker.get("total_supply", 0) or 0)
    max_supply   = float(ticker.get("max_supply", 0) or 0)
    rank         = int(ticker.get("rank", 9999) or 9999)
    beta         = float(ticker.get("beta_value", 0) or 0)

    # FDV
    effective_supply = max_supply if max_supply > 0 else total_supply
    fdv = price * effective_supply if effective_supply > 0 else 0
    circ_fdv_ratio = (circ_supply / effective_supply * 100) if effective_supply > 0 else 0

    # ── Binance - цена и MA200 ──
    closes = fetch_closes_binance(sym)
    if not closes:
        print(f"    Нет данных Binance для {sym}")
        price_vs_ma200 = None
        rsi_d = None
        rs_30 = None
    else:
        n200 = min(200, len(closes))
        ma200 = sum(closes[-n200:]) / n200
        price_vs_ma200 = (closes[-1] / ma200 - 1) * 100

        # RSI daily
        rsi_d = calc_rsi(closes)

        # RS vs BTC за 30 дней
        btc_closes = fetch_closes_binance("BTC")
        if btc_closes and len(closes) >= 31 and len(btc_closes) >= 31:
            coin_ret = (closes[-1] / closes[-31] - 1) * 100
            btc_ret  = (btc_closes[-1] / btc_closes[-31] - 1) * 100
            rs_30 = coin_ret - btc_ret
        else:
            rs_30 = None

    # ── Скрининг F1-F7 ──
    screening = {}

    # F1 - Ликвидность
    screening["F1"] = "PASS" if volume_24h >= 20_000_000 else "FAIL" if volume_24h < 5_000_000 else "WARN"

    # F2 - Размер рынка
    screening["F2"] = "PASS" if market_cap >= 200_000_000 else "WARN" if market_cap >= 50_000_000 else "FAIL"

    # F3 - Дилюция
    if circ_fdv_ratio >= 25:
        screening["F3"] = "PASS"
    elif circ_fdv_ratio >= 10:
        screening["F3"] = "WARN"
    else:
        screening["F3"] = "FAIL"

    # F4 - Тренд HTF
    if price_vs_ma200 is None:
        screening["F4"] = "N/A"
    elif price_vs_ma200 > 0:
        screening["F4"] = "PASS"
    else:
        screening["F4"] = "FAIL"

    # F5 - Нарратив / RS
    if rs_30 is None:
        screening["F5"] = "N/A"
    elif rs_30 > 5:
        screening["F5"] = "PASS"
    elif rs_30 > -10:
        screening["F5"] = "WARN"
    else:
        screening["F5"] = "FAIL"

    # F6, F7 - требуют ручной проверки
    screening["F6"] = "MANUAL"
    screening["F7"] = "MANUAL"

    fail_count = sum(1 for v in screening.values() if v == "FAIL")
    warn_count = sum(1 for v in screening.values() if v == "WARN")

    # ── Автоскоринг 29 критериев ──
    scores = {i: 0 for i in range(1, 30)}

    # #1 Ликвидность (вес 8)
    if volume_24h >= 500_000_000:  scores[1] = 5
    elif volume_24h >= 100_000_000: scores[1] = 4
    elif volume_24h >= 50_000_000:  scores[1] = 3
    elif volume_24h >= 20_000_000:  scores[1] = 2
    elif volume_24h >= 5_000_000:   scores[1] = 1
    else:                           scores[1] = 0

    # #2 Токеномика / анлоки (вес 7) - частично по circ/FDV
    if circ_fdv_ratio >= 70:    scores[2] = 4
    elif circ_fdv_ratio >= 50:  scores[2] = 3
    elif circ_fdv_ratio >= 25:  scores[2] = 2
    elif circ_fdv_ratio >= 10:  scores[2] = 1
    else:                       scores[2] = 0

    # #4 TA - цена vs MA200, RSI (вес 7)
    if price_vs_ma200 is not None:
        if price_vs_ma200 > 20:   scores[4] = 4
        elif price_vs_ma200 > 0:  scores[4] = 3
        elif price_vs_ma200 > -20: scores[4] = 2
        elif price_vs_ma200 > -50: scores[4] = 1
        else:                      scores[4] = 0

    # #12 Макро-контекст (вес 2) - фиксированный средний балл
    scores[12] = 2

    # #14 Корреляции и бета (вес 1)
    if beta > 0:
        if 0.5 <= beta <= 1.5:    scores[14] = 4
        elif 1.5 < beta <= 2.5:   scores[14] = 3
        elif beta > 2.5:          scores[14] = 2
        else:                     scores[14] = 3

    # #24 RS к сектору (вес 7)
    if rs_30 is not None:
        if rs_30 > 30:    scores[24] = 5
        elif rs_30 > 10:  scores[24] = 4
        elif rs_30 > 0:   scores[24] = 3
        elif rs_30 > -15: scores[24] = 2
        else:             scores[24] = 1

    # #29 Off-ramp (листинг) (вес 1)
    if rank <= 50:   scores[29] = 5
    elif rank <= 200: scores[29] = 4
    elif rank <= 500: scores[29] = 3
    elif rank <= 999: scores[29] = 2
    else:             scores[29] = 1

    raw_score = sum(scores[i] * WEIGHTS[i] for i in range(1, 30))

    # Группа
    fails_hard = sum(1 for k in ["F1","F2","F3","F7"] if screening.get(k) == "FAIL")
    if fails_hard >= 2 or screening.get("F7") == "FAIL":
        group = 5
    elif raw_score >= 380:
        group = 1
    elif raw_score >= 300:
        group = 2
    elif raw_score >= 220:
        group = 3
    elif raw_score >= 140:
        group = 4
    else:
        group = 5

    return {
        "symbol": sym,
        "name": coin_name,
        "coin_id": coin_id,
        "rank": rank,
        "price": price,
        "market_cap": market_cap,
        "volume_24h": volume_24h,
        "circ_supply": circ_supply,
        "total_supply": total_supply,
        "fdv": fdv,
        "circ_fdv_ratio": circ_fdv_ratio,
        "ath_price": ath_price,
        "pct_from_ath": pct_from_ath,
        "beta": beta,
        "price_vs_ma200": price_vs_ma200,
        "rsi_d": rsi_d,
        "rs_30": rs_30,
        "screening": screening,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "scores": scores,
        "raw_score": raw_score,
        "group": group,
    }


def save_analysis(d):
    """Сохраняет предварительный анализ в /home/masus/crypto_analysis/{SYM}.md"""
    sym  = d["symbol"]
    now  = datetime.now(tz=MNE).strftime("%Y-%m-%d %H:%M (MNE)")
    path = os.path.join(ANALYSIS_DIR, f"{sym}.md")

    mc_str  = f"${d['market_cap']/1e6:.0f}M" if d['market_cap'] else "н/д"
    fdv_str = f"${d['fdv']/1e6:.0f}M" if d['fdv'] else "н/д"
    vol_str = f"${d['volume_24h']/1e6:.1f}M" if d['volume_24h'] else "н/д"

    screening_lines = "\n".join(
        f"- **{k}**: {v}" for k, v in d["screening"].items()
    )
    fail_warn = ""
    if d["fail_count"] > 0 or d["warn_count"] > 0:
        fail_warn = f"\n⚠ FAILs: {d['fail_count']} | WARNs: {d['warn_count']}"

    auto_scores_lines = []
    auto_items = {1: "Ликвидность", 2: "Токеномика/анлоки", 4: "Технический анализ",
                  12: "Макро-контекст", 14: "Корреляции/бета", 24: "RS к сектору", 29: "Off-ramp"}
    for i, name in auto_items.items():
        s = d["scores"][i]
        auto_scores_lines.append(f"- [{i}] {name} (вес {WEIGHTS[i]}): **{s}/5**")

    manual_items = [i for i in range(1, 30) if i not in auto_items]
    manual_lines = ", ".join(f"[{i}]" for i in manual_items)

    content = f"""# {sym} - {d['name']} (AUTO)

> Автоматический предварительный анализ от {now}
> **Требует ручной проверки и дополнения по пунктам {manual_lines}**

---

## Рыночные данные

| Параметр | Значение |
|---|---|
| Цена | ${d['price']:,.4f} |
| Market Cap | {mc_str} |
| FDV | {fdv_str} |
| Circ/FDV | {d['circ_fdv_ratio']:.1f}% |
| Объём 24h | {vol_str} |
| CoinPaprika Rank | #{d['rank']} |
| ATH | ${d['ath_price']:,.4f} ({d['pct_from_ath']:.1f}% от ATH) |
| Цена vs MA200 | {f"{d['price_vs_ma200']:+.1f}%" if d['price_vs_ma200'] is not None else "н/д"} |
| RSI (daily) | {f"{d['rsi_d']:.1f}" if d['rsi_d'] else "н/д"} |
| RS vs BTC 30д | {f"{d['rs_30']:+.1f}%" if d['rs_30'] is not None else "н/д"} |
| Beta vs BTC | {d['beta']:.2f} |

---

## Скрининг F1-F7

{screening_lines}{fail_warn}

> F6 (Проект живой) и F7 (Красные флаги) - требуют ручной проверки.

---

## Автоскоринг (частичный)

Автоматически рассчитаны только количественные критерии:

{chr(10).join(auto_scores_lines)}

**Автосумма (частичная):** {d['raw_score']} / 500

> ⚠ Пункты {manual_lines} = 0 (n/a, требуют ручного анализа).
> Реальный score будет значительно выше после дополнения.

---

## Предварительная группа

**Группа {d['group']}** (на основе автоскоринга {d['raw_score']}/500 + {d['fail_count']} FAIL)

> Это предварительная оценка. После ручного скоринга группа может измениться.

---

## TODO - ручной анализ

- [ ] F6: Активность GitHub, коммиты за 30 дней
- [ ] F7: Хаки, эксплойты, регуляторные иски
- [ ] [2] Детальный vesting schedule, команда и инвесторы
- [ ] [3] Нарратив сектора, фаза цикла
- [ ] [5] TVL, revenue, active users
- [ ] [6] On-chain метрики (hodlers, whale activity)
- [ ] [7] Команда: доксированность, опыт, красные флаги
- [ ] [8] Конкуренты, moat
- [ ] [9] Аудиты, безопасность кода
- [ ] [13] OI, funding, ликвидации
- [ ] [16] Roadmap, катализаторы ближайшие 3-6 мес
- [ ] [17] GitHub активность
- [ ] [18] Whale holders, smart money
- [ ] [23] Value accrual механизм токена
- [ ] [25] URPD / cost basis distribution
- [ ] [26] Exit liquidity при нужном размере позиции
"""

    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"    Сохранено: {path}")
    return path


def update_groups_file(sym, group, score):
    """Добавляет новую монету в _portfolio_groups.md если её там нет."""
    groups_path = "/home/masus/crypto_analysis/_portfolio_groups.md"
    if not os.path.exists(groups_path):
        return
    with open(groups_path) as f:
        content = f.read()
    if f"| **{group}** | {sym} |" in content or f"| {sym} |" in content:
        return  # уже есть
    # Добавляем в конец таблицы группы
    insert = f"| **{group}** | {sym} | {score} | AUTO (нужен анализ) | н/д | н/д | HOLD* |\n"
    # Вставляем после последней строки таблицы с нужной группой
    lines = content.split("\n")
    insert_idx = len(lines) - 1
    for i, line in enumerate(lines):
        if f"| **{group}** |" in line:
            insert_idx = i + 1
    lines.insert(insert_idx, insert.rstrip())
    with open(groups_path, "w") as f:
        f.write("\n".join(lines))
    print(f"    Добавлен в _portfolio_groups.md: {sym} г{group}")


def main():
    from portfolio_live import get_dynamic_portfolio

    # Определяем список монет для анализа
    if len(sys.argv) > 1:
        coins = [s.upper() for s in sys.argv[1:]]
    else:
        _, _, _, new_coins = get_dynamic_portfolio()
        coins = new_coins

    if not coins:
        print("Нет новых монет для анализа.")
        return

    print(f"Монет для анализа: {len(coins)}: {coins}")

    for sym in coins:
        # Пропускаем если уже есть полный анализ
        analysis_path = os.path.join(ANALYSIS_DIR, f"{sym}.md")
        if os.path.exists(analysis_path):
            with open(analysis_path) as f:
                first_line = f.read(200)
            if "AUTO" not in first_line:
                print(f"  {sym}: уже есть полный анализ, пропускаем")
                continue

        data = analyze_coin(sym)
        if not data:
            continue

        save_analysis(data)
        update_groups_file(sym, data["group"], data["raw_score"])

        print(f"    Score: {data['raw_score']}/500 | Группа {data['group']} | "
              f"MC: ${data['market_cap']/1e6:.0f}M | "
              f"Circ/FDV: {data['circ_fdv_ratio']:.0f}% | "
              f"Screening: {data['fail_count']} FAIL {data['warn_count']} WARN")
        time.sleep(1)


if __name__ == "__main__":
    main()
