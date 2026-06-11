#!/usr/bin/env python3
"""
RSI + Z-score + Relative Performance соотношения двух монет.
Использование: python3 ratio_rsi.py <coin1> <coin2> [rsi_period]
Пример:        python3 ratio_rsi.py W ROSE
               python3 ratio_rsi.py ETH BTC 14
"""

import sys
import time
import urllib.request
import json
import math

GATE_FALLBACK = {"XCH"}


def fetch_closes_binance(symbol, limit=500):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=1d&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return [float(k[4]) for k in json.loads(r.read())]


def fetch_closes_gate(symbol, limit=500):
    url = f"https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair={symbol}_USDT&interval=1d&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return [float(k[2]) for k in json.loads(r.read())]


def fetch_closes(symbol, limit=500):
    sym = symbol.upper()
    if sym in GATE_FALLBACK:
        print(f"  (Gate.io)")
        return fetch_closes_gate(sym, limit)
    try:
        return fetch_closes_binance(sym, limit)
    except Exception:
        print(f"  (Binance недоступен, пробую Gate.io)")
        return fetch_closes_gate(sym, limit)


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


def calc_zscore(series, window=180):
    w = min(window, len(series))
    if w < 10:
        return None
    recent = series[-w:]
    mean = sum(recent) / w
    std = math.sqrt(sum((x - mean) ** 2 for x in recent) / w)
    if std == 0:
        return 0.0
    return (series[-1] - mean) / std


def rel_perf(prices, days):
    if len(prices) <= days:
        return None
    return (prices[-1] / prices[-days - 1] - 1) * 100


def to_weekly(daily):
    return [daily[i] for i in range(6, len(daily), 7)]


def fmt_z(z):
    if z is None:
        return "н/д"
    arrow = "▲" if z > 0 else "▼"
    if abs(z) >= 2.0:
        return f"{z:+.2f} {arrow} ЭКСТРЕМ"
    if abs(z) >= 1.5:
        return f"{z:+.2f} {arrow} сильное"
    if abs(z) >= 1.0:
        return f"{z:+.2f} {arrow} умеренное"
    return f"{z:+.2f} {arrow} норма"


def interpret_rsi(rsi):
    if rsi is None:
        return "н/д"
    if rsi >= 70:
        return "ПЕРЕКУПЛ"
    if rsi <= 30:
        return "ПЕРЕПРОД"
    if rsi >= 60:
        return "бычья"
    if rsi <= 40:
        return "медвежья"
    return "нейтр"


def run(coin1, coin2, period=14):
    c1, c2 = coin1.upper(), coin2.upper()
    print(f"Загружаю {c1}...")
    p1 = fetch_closes(c1)
    print(f"Загружаю {c2}...")
    p2 = fetch_closes(c2)

    n = min(len(p1), len(p2))
    p1, p2 = p1[-n:], p2[-n:]

    ratio = [p1[i] / p2[i] for i in range(n)]
    weekly = to_weekly(ratio)

    rsi_d  = calc_rsi(ratio, period)
    rsi_w  = calc_rsi(weekly, period)
    z90    = calc_zscore(ratio, 90)
    z180   = calc_zscore(ratio, 180)

    # Relative performance отдельных монет vs BTC-baseline (7/30/90д)
    rp1_7   = rel_perf(p1, 7)
    rp1_30  = rel_perf(p1, 30)
    rp1_90  = rel_perf(p1, 90)
    rp2_7   = rel_perf(p2, 7)
    rp2_30  = rel_perf(p2, 30)
    rp2_90  = rel_perf(p2, 90)

    # RS = разница производительности (coin1 - coin2)
    rs_7  = (rp1_7  - rp2_7)  if rp1_7  is not None and rp2_7  is not None else None
    rs_30 = (rp1_30 - rp2_30) if rp1_30 is not None and rp2_30 is not None else None
    rs_90 = (rp1_90 - rp2_90) if rp1_90 is not None and rp2_90 is not None else None

    def pct(v):
        return f"{v:+.1f}%" if v is not None else "н/д"

    label = f"{c1}/{c2}"
    print(f"\n{'='*55}")
    print(f"Пара:   {label}")
    print(f"Ratio:  {ratio[-1]:.6f}  ({c1}={p1[-1]:.6f}  {c2}={p2[-1]:.6f})")
    print(f"Данных: {n} дней / {len(weekly)} недель")
    print(f"{'='*55}")

    print(f"\n--- RSI соотношения ---")
    print(f"  Daily  ({period}): {rsi_d:5.1f}  [{interpret_rsi(rsi_d)}]")
    print(f"  Weekly ({period}): {rsi_w:5.1f}  [{interpret_rsi(rsi_w)}]")

    print(f"\n--- Z-score ratio (насколько экстремален) ---")
    print(f"  Z-90д:   {fmt_z(z90)}")
    print(f"  Z-180д:  {fmt_z(z180)}")
    print(f"  Интерп:  {'Ratio аномально ВЫСОК -> ротация в {}'.format(c2) if (z90 or 0) > 1.5 else 'Ratio аномально НИЗОК -> ждать' if (z90 or 0) < -1.5 else 'В пределах нормы'}")

    print(f"\n--- Relative Performance ---")
    print(f"  {'':6}  {'7д':>7}  {'30д':>7}  {'90д':>7}")
    print(f"  {c1:<6}  {pct(rp1_7):>7}  {pct(rp1_30):>7}  {pct(rp1_90):>7}")
    print(f"  {c2:<6}  {pct(rp2_7):>7}  {pct(rp2_30):>7}  {pct(rp2_90):>7}")
    print(f"  {'RS':6}  {pct(rs_7):>7}  {pct(rs_30):>7}  {pct(rs_90):>7}  ({c1} vs {c2})")
    print(f"  Тренд RS: {'{} СИЛЬНЕЕ {}'.format(c1, c2) if (rs_30 or 0) > 5 else '{} СЛАБЕЕ {}'.format(c1, c2) if (rs_30 or 0) < -5 else 'сопоставимы'} за 30д")

    print(f"\n--- Динамика Daily RSI (7 дней) ---")
    for i in range(-7, 0):
        r = calc_rsi(ratio[:n + i + 1], period)
        if r:
            print(f"  [{i:+d}д] {r:5.1f}  {interpret_rsi(r)}")

    # Итоговый вывод
    print(f"\n{'='*55}")
    signals = []
    if (rsi_d or 0) > 60 or (rsi_w or 0) > 60:
        signals.append(f"RSI {'D+W' if (rsi_d or 0) > 60 and (rsi_w or 0) > 60 else 'D' if (rsi_d or 0) > 60 else 'W'} высокий")
    if (z90 or 0) > 1.5:
        signals.append(f"Z90 = {z90:.2f} (экстрем высокий)")
    if (rs_30 or 0) < -10:
        signals.append(f"RS30 = {rs_30:.1f}% ({c1} значительно слабее)")

    if signals:
        print(f"СИГНАЛ К РОТАЦИИ {c1} -> {c2}: {', '.join(signals)}")
    elif (rsi_d or 50) < 35 and (z90 or 0) < -1.0:
        print(f"ЖДАТЬ: {c1} исторически дёшев vs {c2}, не лучший момент для выхода")
    else:
        print("Чёткого сигнала нет")

    return rsi_d, rsi_w, z90, z180


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python3 ratio_rsi.py <coin1> <coin2> [period]")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 14)
