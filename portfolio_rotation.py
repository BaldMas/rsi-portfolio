#!/usr/bin/env python3
"""
Сканер ротации для всего портфеля.
RSI + Z-score + RS + Funding rates + BTC Dominance + Fear&Greed + 200MA + OI
Использование: python3 portfolio_rotation.py
"""

import time
import urllib.request
import json
import math

GATE_FALLBACK = {"XCH"}
GATE_FUNDING = {"ROSE", "FLOW", "HFT"}  # фьючерсы есть на Gate.io, не на Binance

PORTFOLIO = {
    "STRK": 3, "OP": 3, "DOT": 3, "ETH": 1, "XRP": 2,
    "HBAR": 2, "ARB": 3, "LDO": 3, "IMX": 4, "ICP": 3,
    "PYTH": 4, "W": 5, "JUP": 2, "XCH": 4, "FLOW": 5,
    "WLD": 3, "CFX": 4, "ZK": 4, "RENDER": 2, "TIA": 4,
    "COMP": 4, "APT": 4, "GRT": 4, "FIL": 3, "ONDO": 2,
    "HFT": 5, "ROSE": 5, "BTC": 1,
}

INVESTED = {
    "STRK": 20377, "OP": 17857, "DOT": 11198, "ETH": 10695,
    "XRP": 9921, "HBAR": 5996, "ARB": 1696, "LDO": 1527,
    "IMX": 1354, "ICP": 1350, "PYTH": 1250, "W": 1174,
    "JUP": 1113, "XCH": 800, "FLOW": 770, "WLD": 745,
    "CFX": 617, "ZK": 601, "RENDER": 600, "TIA": 599,
    "TON": 594, "COMP": 500, "APT": 500, "GRT": 400,
    "FIL": 380, "ONDO": 300, "HFT": 212, "ROSE": 168,
}

# Монеты без перпов нигде
NO_PERP = {"XCH"}


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


def fetch_closes(symbol):
    sym = symbol.upper()
    if sym in GATE_FALLBACK:
        return fetch_closes_gate(sym)
    try:
        return fetch_closes_binance(sym)
    except Exception:
        return fetch_closes_gate(sym)


def fetch_funding_history_gate(symbol, limit=30):
    """История funding rates с Gate.io futures."""
    url = f"https://api.gateio.ws/api/v4/futures/usdt/funding_rate?contract={symbol.upper()}_USDT&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        if not isinstance(data, list) or not data:
            return []
        return [float(d["r"]) * 100 for d in data]
    except Exception:
        return []


def fetch_funding_history(symbol, limit=30):
    """История funding rates за N периодов. Binance приоритет, Gate.io fallback."""
    sym = symbol.upper()
    if sym in NO_PERP:
        return []
    if sym in GATE_FUNDING:
        return fetch_funding_history_gate(sym, limit)
    url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}USDT&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        return [float(d["fundingRate"]) * 100 for d in data]
    except Exception:
        return []


def fetch_funding(symbol):
    """Текущий funding rate. None если нет перпа нигде."""
    history = fetch_funding_history(symbol, limit=1)
    return history[-1] if history else None


def fetch_oi_history(symbol, limit=8):
    """История Open Interest ($ value) с Binance futures, дневные свечи."""
    sym = symbol.upper()
    if sym in NO_PERP or sym in GATE_FUNDING:
        return []
    url = f"https://fapi.binance.com/futures/data/openInterestHist?symbol={sym}USDT&period=1d&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        return [float(d["sumOpenInterestValue"]) for d in data]
    except Exception:
        return []


def calc_oi_change(history):
    """Изменение OI за период в %."""
    if len(history) < 2:
        return None
    return (history[-1] / history[0] - 1) * 100


def calc_ma200(prices):
    """Отклонение текущей цены от 200MA в %."""
    n = min(200, len(prices))
    if n < 50:
        return None
    ma = sum(prices[-n:]) / n
    return (prices[-1] / ma - 1) * 100


def fetch_macro():
    """BTC dominance (CoinPaprika) + Fear&Greed (alternative.me)."""
    result = {"dominance": None, "fg": None, "fg_label": None}
    try:
        url = "https://api.coinpaprika.com/v1/global"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        result["dominance"] = float(data["bitcoin_dominance_percentage"])
    except Exception:
        pass
    try:
        url = "https://api.alternative.me/fng/?limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        result["fg"] = int(data["data"][0]["value"])
        result["fg_label"] = data["data"][0]["value_classification"]
    except Exception:
        pass
    return result


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


def calc_zscore(series, window=90):
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


def funding_signal(rates_history):
    """
    Возвращает строку-сигнал по фандингу.
    Положительный средний = лонги платят = перегрев.
    Отрицательный = шорты платят = возможен сквиз.
    """
    if not rates_history:
        return None, "н/д"
    avg = sum(rates_history) / len(rates_history)
    last = rates_history[-1]
    if last > 0.05:
        return last, "ПЕРЕГРЕВ (лонги платят)"
    if last < -0.05:
        return last, "ШОРТЫ ДОМИНИРУЮТ"
    if avg > 0.02:
        return last, "умерен. бычий"
    if avg < -0.02:
        return last, "умерен. медвежий"
    return last, "нейтральный"


def score_signal(rsi_d, rsi_w, z90, rs_30, funding_last, dist_200=None, oi_chg=None):
    s = 0
    if rsi_d is not None:
        s += (rsi_d - 50) / 10
    if rsi_w is not None:
        s += (rsi_w - 50) / 10 * 1.5
    if z90 is not None:
        s += z90 * 2
    if rs_30 is not None:
        s += -rs_30 / 10
    if funding_last is not None:
        if funding_last > 0.05:
            s += 1.5
        elif funding_last > 0.02:
            s += 0.5
        elif funding_last < -0.05:
            s -= 1.5
    # Выше 200MA = тренд подтверждён, ниже = давление продавцов
    if dist_200 is not None:
        if dist_200 > 0:
            s += 0.3
        else:
            s -= 0.5
    # Рост OI = позиции набираются, сигнал сильнее; падение OI = выход
    if oi_chg is not None:
        if oi_chg > 30:
            s += 1.0
        elif oi_chg > 10:
            s += 0.5
        elif oi_chg < -30:
            s -= 1.0
        elif oi_chg < -10:
            s -= 0.5
    return s


def main():
    print("Загружаю макро данные...", flush=True)
    macro = fetch_macro()
    dom = macro["dominance"]
    fg  = macro["fg"]
    fg_label = macro["fg_label"]

    # Макрофильтр: если доминанс BTC растёт и F&G < 25 - не время для ротации в альты
    macro_ok = True
    macro_warn = []
    if dom is not None and dom > 57:
        macro_warn.append(f"BTC доминанс {dom:.1f}% - высокий, альты под давлением")
        macro_ok = False
    if fg is not None and fg < 25:
        macro_warn.append(f"Fear&Greed {fg} ({fg_label}) - рынок в страхе")

    print(f"Загружаю цены...", flush=True)
    prices = {}
    all_coins = list(PORTFOLIO.keys()) + ["TON"]
    for i, coin in enumerate(all_coins):
        try:
            prices[coin] = fetch_closes(coin)
            print(f"  {coin} OK", flush=True)
        except Exception as e:
            print(f"  {coin} ERR: {e}", flush=True)
        if i < len(all_coins) - 1:
            time.sleep(0.25)

    print("Загружаю funding rates...", flush=True)
    fundings = {}
    funding_hist = {}
    for coin in PORTFOLIO:
        if coin in NO_PERP or coin == "BTC" or coin == "ETH":
            continue
        fh = fetch_funding_history(coin, 30)
        funding_hist[coin] = fh
        fundings[coin] = fh[-1] if fh else None
        time.sleep(0.1)

    print("Загружаю Open Interest...", flush=True)
    oi_changes = {}
    for coin in PORTFOLIO:
        if coin in NO_PERP or coin in GATE_FUNDING or coin in ("BTC", "ETH"):
            continue
        hist = fetch_oi_history(coin, 8)
        oi_changes[coin] = calc_oi_change(hist)
        time.sleep(0.1)

    btc = prices.get("BTC", [])
    eth = prices.get("ETH", [])

    results = []
    for coin, grp in PORTFOLIO.items():
        if coin in ("BTC", "ETH") or coin not in prices:
            continue
        p = prices[coin]
        f_last, f_sig = funding_signal(funding_hist.get(coin, []))
        dist_200 = calc_ma200(p)
        oi_chg = oi_changes.get(coin)

        for ref_name, ref_p, ref_g in [("BTC", btc, 1), ("ETH", eth, 1)]:
            if not ref_p:
                continue
            n = min(len(p), len(ref_p))
            ratio = [p[-n + i] / ref_p[-n + i] for i in range(n)]
            weekly = to_weekly(ratio)

            rsi_d = calc_rsi(ratio)
            rsi_w = calc_rsi(weekly)
            z90   = calc_zscore(ratio, 90)

            rp_coin_30 = rel_perf(p, 30)
            rp_ref_30  = rel_perf(ref_p, 30)
            rs_30 = (rp_coin_30 - rp_ref_30) if rp_coin_30 is not None and rp_ref_30 is not None else None

            rp_coin_7 = rel_perf(p, 7)
            rp_ref_7  = rel_perf(ref_p, 7)
            rs_7 = (rp_coin_7 - rp_ref_7) if rp_coin_7 is not None and rp_ref_7 is not None else None

            sig = score_signal(rsi_d, rsi_w, z90, rs_30, f_last, dist_200, oi_chg)

            results.append({
                "coin": coin, "ref": ref_name,
                "grp": grp, "ref_g": ref_g,
                "rsi_d": rsi_d, "rsi_w": rsi_w,
                "z90": z90,
                "rs_7": rs_7, "rs_30": rs_30,
                "funding": f_last,
                "funding_sig": f_sig,
                "dist_200": dist_200,
                "oi_chg": oi_chg,
                "sig": sig,
                "invested": INVESTED.get(coin, 0),
            })

    results.sort(key=lambda x: x["sig"], reverse=True)

    def f(v, fmt=".1f"):
        return f"{v:{fmt}}" if v is not None else " н/д"

    def zi(z):
        if z is None: return "  н/д"
        if z >= 2.0:  return f"{z:+.2f}!!"
        if z >= 1.5:  return f"{z:+.2f}! "
        if z <= -2.0: return f"{z:+.2f}!!"
        if z <= -1.5: return f"{z:+.2f}! "
        return f"{z:+.2f}  "

    def fi(v):
        if v is None: return "  н/д"
        if v > 0.05:  return f"{v:+.3f}▲▲"
        if v > 0.02:  return f"{v:+.3f}▲ "
        if v < -0.05: return f"{v:+.3f}▼▼"
        if v < -0.02: return f"{v:+.3f}▼ "
        return f"{v:+.3f}  "

    def d200(v):
        if v is None: return "  н/д"
        if v > 20:  return f"{v:+.0f}%▲▲"
        if v > 0:   return f"{v:+.0f}%▲ "
        if v > -20: return f"{v:+.0f}%▼ "
        return f"{v:+.0f}%▼▼"

    def oif(v):
        if v is None: return "  н/д"
        if v > 30:  return f"{v:+.0f}%▲▲"
        if v > 10:  return f"{v:+.0f}%▲ "
        if v < -30: return f"{v:+.0f}%▼▼"
        if v < -10: return f"{v:+.0f}%▼ "
        return f"{v:+.0f}%  "

    # --- ЗАГОЛОВОК ---
    W = 115
    print(f"\n{'='*W}")
    print(f"МАКРО КОНТЕКСТ")
    print(f"  BTC Dominance: {dom:.2f}%  {'⚠ ВЫСОКИЙ - альты под давлением' if dom and dom > 57 else '✓ норма'}" if dom else "  BTC Dominance: н/д")
    print(f"  Fear & Greed:  {fg} ({fg_label})  {'⚠ ЭКСТРЕМ СТРАХА' if fg and fg < 20 else '⚠ СТРАХ' if fg and fg < 40 else ''}" if fg else "  Fear & Greed:  н/д")
    if macro_warn:
        print(f"\n  ⚠ МАКРОФИЛЬТР: {' | '.join(macro_warn)}")
        print(f"  Ротация в альты преждевременна до разворота доминанса")
    print(f"{'='*W}")

    # --- ТАБЛИЦА ---
    print(f"\n{'Монета/ref':<12} {'Г':>2}  {'RSI_D':>5} {'RSI_W':>5}  {'Z90':>7}  {'RS_30':>6}  {'Funding':>8}  {'MA200':>7}  {'OI_7d':>7}  {'СИГНАЛ':>6}  Инвест")
    print(f"{'-'*W}")

    for r in results:
        tag = ""
        if not macro_ok and r["grp"] > 1 and r["ref"] in ("BTC","ETH"):
            tag = "⚠макро"
        elif r["sig"] > 4:    tag = "▶ РОТИРОВАТЬ"
        elif r["sig"] > 2:    tag = "▷ смотреть"
        elif r["sig"] < -3:   tag = "◀ ждать"

        print(
            f"{r['coin']}/{r['ref']:<4} {r['grp']:>2}->{r['ref_g']}  "
            f"{f(r['rsi_d']):>5} {f(r['rsi_w']):>5}  "
            f"{zi(r['z90']):>7}  "
            f"{f(r['rs_30']):>6}  "
            f"{fi(r['funding']):>8}  "
            f"{d200(r['dist_200']):>7}  "
            f"{oif(r['oi_chg']):>7}  "
            f"{r['sig']:>+6.2f}  "
            f"${r['invested']:>6,}  {tag}"
        )

    # --- ТОП СИГНАЛЫ ---
    print(f"\n{'='*W}")
    print("ТОП СИГНАЛЫ К РОТАЦИИ:")
    top = [r for r in results if r["sig"] > 2]
    for r in top[:10]:
        reasons = []
        if (r["rsi_d"] or 0) > 60:    reasons.append(f"RSI_D={r['rsi_d']:.0f}")
        if (r["rsi_w"] or 0) > 60:    reasons.append(f"RSI_W={r['rsi_w']:.0f}")
        if (r["z90"] or 0) > 1.5:     reasons.append(f"Z90={r['z90']:.2f}")
        if (r["rs_30"] or 0) < -10:   reasons.append(f"RS30={r['rs_30']:.0f}%")
        if (r["funding"] or 0) > 0.05: reasons.append(f"funding={r['funding']:.3f}% перегрев")
        macro_tag = " ⚠МАКРО" if not macro_ok else ""
        oi_tag = f"  OI:{oif(r['oi_chg'])}" if r['oi_chg'] is not None else ""
        print(f"  {r['coin']:6} -> {r['ref']}  г{r['grp']}->г{r['ref_g']}  сигнал={r['sig']:+.2f}  [{', '.join(reasons)}]  funding:{r['funding_sig']}  MA200:{d200(r['dist_200'])}{oi_tag}  ${r['invested']:,}{macro_tag}")

    print(f"\nЖДАТЬ (исторически дёшевы vs цели):")
    wait = [r for r in results if r["sig"] < -3 and r["ref"] == "BTC"]
    for r in sorted(wait, key=lambda x: x["sig"])[:8]:
        print(f"  {r['coin']:6} vs BTC  сигнал={r['sig']:+.2f}  Z90={f(r['z90'])}  RS30={f(r['rs_30'])}%  MA200:{d200(r['dist_200'])}  OI:{oif(r['oi_chg'])}")


if __name__ == "__main__":
    main()
