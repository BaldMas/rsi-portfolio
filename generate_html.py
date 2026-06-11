#!/usr/bin/env python3
"""
Генерирует HTML отчёт ротации портфеля в стиле rsi_portfolio_auto.
Использование: python3 generate_html.py [output.html]
"""

import sys
import time
import json
import math
import os
import urllib.request
from datetime import datetime

# ──────────────────────────────────────────────
# Справочники

GATE_FALLBACK = {"XCH"}
GATE_FUNDING  = {"ROSE", "FLOW", "HFT"}
NO_PERP       = {"XCH"}

PORTFOLIO = {
    "STRK": 3, "OP": 3, "DOT": 3, "ETH": 1, "XRP": 2,
    "HBAR": 2, "ARB": 3, "LDO": 3, "IMX": 4, "ICP": 3,
    "PYTH": 4, "W": 5, "JUP": 2, "XCH": 4, "FLOW": 5,
    "WLD": 3, "CFX": 4, "ZK": 4, "RENDER": 2, "TIA": 4,
    "COMP": 4, "APT": 4, "GRT": 4, "FIL": 3, "ONDO": 2,
    "HFT": 5, "ROSE": 5, "BTC": 1,
}

SCORES = {
    "BTC": 413, "ETH": 396, "XRP": 367, "ONDO": 340, "RENDER": 314,
    "HBAR": 312, "TON": 311, "JUP": 311, "OP": 276, "WLD": 266,
    "LDO": 257, "FIL": 249, "DOT": 246, "ICP": 234, "ARB": 232,
    "STRK": 226, "PYTH": 220, "CFX": 215, "COMP": 212, "TIA": 206,
    "APT": 205, "GRT": 193, "IMX": 176, "ZK": 171, "XCH": 147,
    "W": 146, "ROSE": 120, "HFT": 93, "FLOW": 47,
}

INVESTED = {
    "STRK": 20377, "OP": 17857, "DOT": 11198, "ETH": 10695,
    "XRP": 9921, "HBAR": 5996, "ARB": 1696, "LDO": 1527,
    "IMX": 1354, "ICP": 1350, "PYTH": 1250, "W": 1174,
    "JUP": 1113, "XCH": 800, "FLOW": 770, "WLD": 745,
    "CFX": 617, "ZK": 601, "RENDER": 600, "TIA": 599,
    "COMP": 500, "APT": 500, "GRT": 400, "FIL": 380,
    "ONDO": 300, "HFT": 212, "ROSE": 168,
}

# ──────────────────────────────────────────────
# Загрузка данных

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def fetch_portfolio_values():
    """Текущие стоимости и P/L с Dropstab API."""
    result = {}
    try:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        token = ""
        with open(env_path) as f:
            for line in f:
                if "DROPSTAB_TOKEN" in line:
                    token = line.split("=", 1)[1].strip()
        if not token:
            return result
        data = fetch_json(f"https://dropstab.com/_gateway/api/portfolio/api/portfolioGroup/individualShare/{token}")
        for item in data.get("portfolios", []):
            sym = item.get("symbol", "").upper()
            total = item.get("totalCap", {})
            pnl   = item.get("unrealizedProfitPercent", {})
            value = float(total.get("USD", 0) or 0) if isinstance(total, dict) else 0
            pnl_p = float(pnl.get("USD", 0) or 0) if isinstance(pnl, dict) else 0
            if sym and value > 0:
                result[sym] = {"value": value, "pnl": pnl_p}
    except Exception:
        pass
    return result


def fetch_closes_binance(symbol, limit=500):
    data = fetch_json(f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=1d&limit={limit}")
    return [float(k[4]) for k in data]


def fetch_closes_gate(symbol, limit=500):
    data = fetch_json(f"https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair={symbol}_USDT&interval=1d&limit={limit}")
    return [float(k[2]) for k in data]


def fetch_closes(symbol):
    sym = symbol.upper()
    if sym in GATE_FALLBACK:
        return fetch_closes_gate(sym)
    try:
        return fetch_closes_binance(sym)
    except Exception:
        return fetch_closes_gate(sym)


def fetch_funding_history_gate(symbol, limit=30):
    try:
        data = fetch_json(f"https://api.gateio.ws/api/v4/futures/usdt/funding_rate?contract={symbol}_USDT&limit={limit}")
        return [float(d["r"]) * 100 for d in data] if isinstance(data, list) else []
    except Exception:
        return []


def fetch_funding_history(symbol, limit=30):
    sym = symbol.upper()
    if sym in NO_PERP:
        return []
    if sym in GATE_FUNDING:
        return fetch_funding_history_gate(sym, limit)
    try:
        data = fetch_json(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}USDT&limit={limit}")
        return [float(d["fundingRate"]) * 100 for d in data]
    except Exception:
        return []


def fetch_oi_history(symbol, limit=8):
    sym = symbol.upper()
    if sym in NO_PERP or sym in GATE_FUNDING:
        return []
    try:
        data = fetch_json(f"https://fapi.binance.com/futures/data/openInterestHist?symbol={sym}USDT&period=1d&limit={limit}")
        return [float(d["sumOpenInterestValue"]) for d in data]
    except Exception:
        return []


def fetch_macro():
    result = {"dominance": None, "fg": None, "fg_label": None}
    try:
        d = fetch_json("https://api.coinpaprika.com/v1/global")
        result["dominance"] = float(d["bitcoin_dominance_percentage"])
    except Exception:
        pass
    try:
        d = fetch_json("https://api.alternative.me/fng/?limit=1")
        result["fg"] = int(d["data"][0]["value"])
        result["fg_label"] = d["data"][0]["value_classification"]
    except Exception:
        pass
    return result

# ──────────────────────────────────────────────
# Вычисления

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
    return 0.0 if std == 0 else (series[-1] - mean) / std


def calc_ma200(prices):
    n = min(200, len(prices))
    if n < 50:
        return None
    ma = sum(prices[-n:]) / n
    return (prices[-1] / ma - 1) * 100


def rel_perf(prices, days):
    if len(prices) <= days:
        return None
    return (prices[-1] / prices[-days - 1] - 1) * 100


def to_weekly(daily):
    return [daily[i] for i in range(6, len(daily), 7)]


def calc_oi_change(history):
    if len(history) < 2:
        return None
    return (history[-1] / history[0] - 1) * 100


def funding_label(rates):
    if not rates:
        return None, "н/д"
    avg = sum(rates) / len(rates)
    last = rates[-1]
    if last > 0.05:  return last, "ПЕРЕГРЕВ"
    if last < -0.05: return last, "ШОРТЫ"
    if avg > 0.02:   return last, "бычий"
    if avg < -0.02:  return last, "медвежий"
    return last, "нейтр"


def score_signal(rsi_d, rsi_w, z90, rs_30, funding_last, dist_200=None, oi_chg=None):
    s = 0
    if rsi_d is not None:    s += (rsi_d - 50) / 10
    if rsi_w is not None:    s += (rsi_w - 50) / 10 * 1.5
    if z90 is not None:      s += z90 * 2
    if rs_30 is not None:    s += -rs_30 / 10
    if funding_last is not None:
        if funding_last > 0.05:   s += 1.5
        elif funding_last > 0.02: s += 0.5
        elif funding_last < -0.05: s -= 1.5
    if dist_200 is not None:
        s += 0.3 if dist_200 > 0 else -0.5
    if oi_chg is not None:
        if oi_chg > 30:    s += 1.0
        elif oi_chg > 10:  s += 0.5
        elif oi_chg < -30: s -= 1.0
        elif oi_chg < -10: s -= 0.5
    return s

# ──────────────────────────────────────────────
# HTML

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #e6edf3; padding: 20px; }
h1 { font-size: 1.4em; margin-bottom: 4px; color: #58a6ff; }
.subtitle { color: #8b949e; font-size: 0.85em; margin-bottom: 16px; }
.macro { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; display: flex; gap: 32px; flex-wrap: wrap; }
.macro-item { font-size: 0.9em; }
.macro-item .label { color: #8b949e; }
.macro-item .value { font-weight: 600; }
.warn { color: #f85149; }
.ok   { color: #3fb950; }
.caution { color: #d29922; }
table { width: 100%; border-collapse: collapse; font-size: 0.82em; }
th { background: #161b22; color: #8b949e; padding: 8px 10px; text-align: left; border-bottom: 2px solid #30363d; white-space: nowrap; cursor: pointer; user-select: none; }
th:hover { color: #58a6ff; }
td { padding: 7px 10px; border-bottom: 1px solid #21262d; white-space: nowrap; vertical-align: middle; }
tr:hover td { background: #1c2128; }
.medal { font-size: 1.1em; }
.pair { font-weight: 600; }
.coin-tag { display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 0.78em; margin-left: 3px; }
.g1 { background: #1f3a24; color: #3fb950; }
.g2 { background: #1a2e4a; color: #58a6ff; }
.g3 { background: #2d2a1e; color: #d29922; }
.g4 { background: #2d1f1f; color: #f0883e; }
.g5 { background: #3d1a1a; color: #f85149; }
.score-bar { display: inline-block; height: 6px; border-radius: 3px; vertical-align: middle; margin-right: 4px; }
.sig-rotate  { color: #3fb950; font-weight: 700; }
.sig-watch   { color: #d29922; font-weight: 600; }
.sig-wait    { color: #f85149; }
.sig-neutral { color: #8b949e; }
.tag-rotate  { background: #1f3a24; color: #3fb950; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 700; }
.tag-watch   { background: #2d2a1e; color: #d29922; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
.tag-wait    { background: #3d1a1a; color: #f85149; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
.z-hi  { color: #f85149; }
.z-lo  { color: #3fb950; }
.z-mid { color: #8b949e; }
.ma-up { color: #3fb950; }
.ma-dn { color: #f85149; }
.oi-up { color: #3fb950; }
.oi-dn { color: #f85149; }
.fn-hot { color: #f85149; }
.fn-neg { color: #58a6ff; }
.fn-neu { color: #8b949e; }
.macro-warn { background: #2d1f1f; border: 1px solid #f85149; border-radius: 6px; padding: 8px 14px; margin-bottom: 12px; color: #f85149; font-size: 0.88em; }
.filter-bar { margin-bottom: 12px; display: flex; gap: 8px; flex-wrap: wrap; }
.filter-btn { padding: 4px 12px; border-radius: 4px; border: 1px solid #30363d; background: #161b22; color: #8b949e; cursor: pointer; font-size: 0.82em; }
.filter-btn.active { border-color: #58a6ff; color: #58a6ff; }
.timestamp { color: #8b949e; font-size: 0.78em; }
"""

JS = """
function sortTable(col) {
  const tb = document.getElementById('main-table');
  const rows = Array.from(tb.tBodies[0].rows);
  const asc = tb.dataset.sortCol == col && tb.dataset.sortDir == 'asc';
  rows.sort((a,b) => {
    let av = a.cells[col].dataset.val || a.cells[col].textContent;
    let bv = b.cells[col].dataset.val || b.cells[col].textContent;
    let an = parseFloat(av), bn = parseFloat(bv);
    if (!isNaN(an) && !isNaN(bn)) return asc ? an-bn : bn-an;
    return asc ? av.localeCompare(bv) : bv.localeCompare(av);
  });
  rows.forEach(r => tb.tBodies[0].appendChild(r));
  tb.dataset.sortCol = col;
  tb.dataset.sortDir = asc ? 'desc' : 'asc';
}

function filterRows(type) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  document.querySelector('[data-filter="'+type+'"]').classList.add('active');
  document.querySelectorAll('#main-table tbody tr').forEach(r => {
    r.style.display = (type == 'all' || r.dataset.sig == type) ? '' : 'none';
  });
}
"""

def grp_class(g):
    return f"g{g}"

def score_bar(score, maxscore=500):
    pct = min(100, score / maxscore * 100)
    color = "#3fb950" if pct > 60 else "#d29922" if pct > 40 else "#f85149"
    return f'<span class="score-bar" style="width:{pct * 0.6:.0f}px;background:{color}"></span>'

def rsi_color(v):
    if v is None: return '<span style="color:#8b949e">н/д</span>'
    cls = "warn" if v >= 70 else "ok" if v <= 30 else "caution" if v >= 60 else "ok" if v <= 40 else ""
    return f'<span class="{cls}">{v:.1f}</span>'

def z_fmt(v):
    if v is None: return '<span class="z-mid">н/д</span>'
    cls = "z-hi" if v >= 1.5 else "z-lo" if v <= -1.5 else "z-mid"
    mark = "!!" if abs(v) >= 2 else "!" if abs(v) >= 1.5 else ""
    return f'<span class="{cls}" data-val="{v:.2f}">{v:+.2f}{mark}</span>'

def ma_fmt(v):
    if v is None: return '<span style="color:#8b949e">н/д</span>'
    cls = "ma-up" if v > 0 else "ma-dn"
    arrow = "▲" if v > 0 else "▼"
    return f'<span class="{cls}" data-val="{v:.1f}">{v:+.0f}% {arrow}</span>'

def oi_fmt(v):
    if v is None: return '<span style="color:#8b949e">н/д</span>'
    cls = "oi-up" if v > 10 else "oi-dn" if v < -10 else "z-mid"
    arrow = "▲▲" if v > 30 else "▲" if v > 10 else "▼▼" if v < -30 else "▼" if v < -10 else ""
    return f'<span class="{cls}" data-val="{v:.0f}">{v:+.0f}%{arrow}</span>'

def fn_fmt(v, label):
    if v is None: return '<span class="fn-neu">н/д</span>'
    cls = "fn-hot" if v > 0.05 else "fn-neg" if v < -0.02 else "fn-neu"
    return f'<span class="{cls}" title="{label}" data-val="{v:.4f}">{v:+.3f}%</span>'

def pnl_fmt(coin, pv):
    if coin not in pv:
        return '<span style="color:#8b949e">-</span>'
    val  = pv[coin]["value"]
    pnl  = pv[coin]["pnl"]
    cls  = "ok" if pnl >= 0 else "warn"
    pnl_str = f'{pnl:+.1f}%'
    return f'<span data-val="{val:.0f}">${val:,.0f} <span class="{cls}">({pnl_str})</span></span>'

def rs_fmt(v):
    if v is None: return '<span style="color:#8b949e">н/д</span>'
    cls = "warn" if v > 30 else "ok" if v < -10 else ""
    return f'<span class="{cls}" data-val="{v:.1f}">{v:+.1f}%</span>'

def sig_class(sig):
    if sig > 4:   return "rotate"
    if sig > 2:   return "watch"
    if sig < -3:  return "wait"
    return "neutral"

MEDALS = ["🥇", "🥈", "🥉"]

def build_html(results, macro, generated_at, total=0, cnt_rotate=0, cnt_watch=0, cnt_wait=0, portfolio_values=None):
    dom  = macro.get("dominance")
    fg   = macro.get("fg")
    fglb = macro.get("fg_label", "")

    dom_cls = "warn" if dom and dom > 57 else "ok"
    fg_cls  = "warn" if fg and fg < 20 else "caution" if fg and fg < 40 else "ok"

    macro_warn = []
    if dom and dom > 57:
        macro_warn.append(f"BTC доминанс {dom:.1f}% — альты под давлением")
    if fg and fg < 25:
        macro_warn.append(f"Fear & Greed {fg} ({fglb}) — рынок в страхе")

    warn_html = ""
    if macro_warn:
        warn_html = f'<div class="macro-warn">⚠ МАКРОФИЛЬТР: {" | ".join(macro_warn)}</div>'

    pv = portfolio_values or {}

    rows_html = ""
    rank = 0
    for i, r in enumerate(results):
        sig = r["sig"]
        sc  = sig_class(sig)
        rank += 1

        medal = MEDALS[i] if i < 3 else f"{rank}"
        coin  = r["coin"]
        ref   = r["ref"]
        grp   = r["grp"]
        ref_g = r["ref_g"]

        cscore = SCORES.get(coin, 0)
        rscore = SCORES.get(ref, 0)

        tag_html = {
            "rotate":  '<span class="tag-rotate">▶ РОТИРОВАТЬ</span>',
            "watch":   '<span class="tag-watch">▷ смотреть</span>',
            "wait":    '<span class="tag-wait">◀ ждать</span>',
            "neutral": "",
        }[sc]

        rows_html += f"""
<tr data-sig="{sc}">
  <td class="medal">{medal}</td>
  <td class="pair">
    {coin}<span class="coin-tag {grp_class(grp)}" title="Score: {cscore}/500">г{grp} ★{cscore}</span>
    →
    {ref}<span class="coin-tag {grp_class(ref_g)}" title="Score: {rscore}/500">г{ref_g} ★{rscore}</span>
  </td>
  <td data-val="{r['rsi_d'] or 0:.1f}">{rsi_color(r['rsi_d'])}</td>
  <td data-val="{r['rsi_w'] or 0:.1f}">{rsi_color(r['rsi_w'])}</td>
  <td>{z_fmt(r['z90'])}</td>
  <td>{rs_fmt(r['rs_30'])}</td>
  <td>{ma_fmt(r['dist_200'])}</td>
  <td>{oi_fmt(r['oi_chg'])}</td>
  <td>{fn_fmt(r['funding'], r['funding_sig'])}</td>
  <td data-val="{sig:.2f}"><span class="sig-{sc}">{sig:+.2f}</span></td>
  <td>${r['invested']:,}</td>
  <td>{pnl_fmt(coin, pv)}</td>
  <td>{tag_html}</td>
</tr>"""

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RSI Portfolio Rotation</title>
<style>{CSS}</style>
</head>
<body>
<h1>RSI Portfolio Rotation Monitor</h1>
<p class="subtitle timestamp">Обновлено: {generated_at}</p>

<div class="macro">
  <div class="macro-item">
    <span class="label">BTC Dominance: </span>
    <span class="value {dom_cls}">{f"{dom:.2f}%" if dom else "н/д"}</span>
  </div>
  <div class="macro-item">
    <span class="label">Fear & Greed: </span>
    <span class="value {fg_cls}">{f"{fg} ({fglb})" if fg else "н/д"}</span>
  </div>
</div>

{warn_html}

<div class="filter-bar">
  <button class="filter-btn active" data-filter="all" onclick="filterRows('all')">Все ({total})</button>
  <button class="filter-btn" data-filter="rotate" onclick="filterRows('rotate')">▶ Ротировать ({cnt_rotate})</button>
  <button class="filter-btn" data-filter="watch" onclick="filterRows('watch')">▷ Смотреть ({cnt_watch})</button>
  <button class="filter-btn" data-filter="wait" onclick="filterRows('wait')">◀ Ждать ({cnt_wait})</button>
</div>

<table id="main-table" data-sort-col="-1" data-sort-dir="desc">
<thead>
<tr>
  <th onclick="sortTable(0)">#</th>
  <th onclick="sortTable(1)">Из → В</th>
  <th onclick="sortTable(2)">RSI 1D</th>
  <th onclick="sortTable(3)">RSI 1W</th>
  <th onclick="sortTable(4)">Z-score 90д</th>
  <th onclick="sortTable(5)">RS 30д</th>
  <th onclick="sortTable(6)">MA200</th>
  <th onclick="sortTable(7)">OI 7д</th>
  <th onclick="sortTable(8)">Funding</th>
  <th onclick="sortTable(9)">Сигнал</th>
  <th onclick="sortTable(10)">Инвест</th>
  <th onclick="sortTable(11)">Сейчас (P/L)</th>
  <th>Статус</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>

<script>{JS}</script>
</body>
</html>"""


def main():
    out_file = sys.argv[1] if len(sys.argv) > 1 else "/home/masus/dropstab/report.html"

    print("Макро...", flush=True)
    macro = fetch_macro()

    print("Текущие стоимости (Dropstab)...", flush=True)
    portfolio_values = fetch_portfolio_values()
    print(f"  Получено {len(portfolio_values)} позиций", flush=True)

    print("Цены...", flush=True)
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

    print("Funding...", flush=True)
    funding_hist = {}
    for coin in PORTFOLIO:
        if coin in NO_PERP:
            continue
        fh = fetch_funding_history(coin, 30)
        funding_hist[coin] = fh
        time.sleep(0.1)

    print("OI...", flush=True)
    oi_changes = {}
    for coin in PORTFOLIO:
        if coin in NO_PERP or coin in GATE_FUNDING:
            continue
        hist = fetch_oi_history(coin, 8)
        oi_changes[coin] = calc_oi_change(hist)
        time.sleep(0.1)

    results = []
    for coin, grp in PORTFOLIO.items():
        if coin not in prices:
            continue
        p = prices[coin]
        f_last, f_sig = funding_label(funding_hist.get(coin, []))
        dist_200 = calc_ma200(p)
        oi_chg   = oi_changes.get(coin)

        for ref_coin, ref_grp in PORTFOLIO.items():
            if ref_coin == coin or ref_grp > grp:
                continue
            ref_p = prices.get(ref_coin, [])
            if not ref_p:
                continue
            n = min(len(p), len(ref_p))
            ratio  = [p[-n + i] / ref_p[-n + i] for i in range(n)]
            weekly = to_weekly(ratio)

            rsi_d = calc_rsi(ratio)
            rsi_w = calc_rsi(weekly)
            z90   = calc_zscore(ratio, 90)

            rp_c30 = rel_perf(p, 30)
            rp_r30 = rel_perf(ref_p, 30)
            rs_30  = (rp_c30 - rp_r30) if rp_c30 is not None and rp_r30 is not None else None

            sig = score_signal(rsi_d, rsi_w, z90, rs_30, f_last, dist_200, oi_chg)

            results.append({
                "coin": coin, "ref": ref_coin,
                "grp": grp, "ref_g": ref_grp,
                "rsi_d": rsi_d, "rsi_w": rsi_w,
                "z90": z90, "rs_30": rs_30,
                "funding": f_last, "funding_sig": f_sig,
                "dist_200": dist_200, "oi_chg": oi_chg,
                "sig": sig,
                "invested": INVESTED.get(coin, 0),
            })

    results.sort(key=lambda x: x["sig"], reverse=True)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    total      = len(results)
    cnt_rotate = sum(1 for r in results if r["sig"] > 4)
    cnt_watch  = sum(1 for r in results if 2 < r["sig"] <= 4)
    cnt_wait   = sum(1 for r in results if r["sig"] < -3)
    html = build_html(results, macro, generated_at, total, cnt_rotate, cnt_watch, cnt_wait, portfolio_values)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✓ Сохранено: {out_file}")


if __name__ == "__main__":
    main()
