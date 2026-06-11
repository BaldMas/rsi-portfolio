#!/usr/bin/env python3
"""
Модуль динамического портфеля из Dropstab API.
Заменяет хардкод PORTFOLIO / INVESTED в generate_html.py
"""

import os
import re
import json
import urllib.request
from datetime import datetime, timezone, timedelta

GROUPS_FILE    = "/home/masus/crypto_analysis/_portfolio_groups.md"
ENV_FILE       = os.path.join(os.path.dirname(__file__), ".env")
SNAPSHOT_FILE  = os.path.join(os.path.dirname(__file__), "portfolio_snapshot.json")
CHANGES_LOG    = os.path.join(os.path.dirname(__file__), "changes.log")
MIN_VALUE_USD  = 5.0


def _read_token():
    if not os.path.exists(ENV_FILE):
        return ""
    with open(ENV_FILE) as f:
        for line in f:
            if "DROPSTAB_TOKEN" in line:
                return line.split("=", 1)[1].strip()
    return ""


def _fetch_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://dropstab.com/",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def _mne_now():
    mne = timezone(timedelta(hours=2))
    return datetime.now(tz=mne).strftime("%Y-%m-%d %H:%M")


def fetch_dropstab_holdings():
    """Возвращает {symbol: {value, invested, pnl, qty}} для активных позиций."""
    token = _read_token()
    if not token:
        return {}
    data = _fetch_json(
        f"https://dropstab.com/_gateway/api/portfolio/api/portfolioGroup/individualShare/{token}"
    )
    result = {}
    for item in data.get("portfolios", []):
        sym   = item.get("symbol", "").upper()
        total = item.get("totalCap", {})
        init  = item.get("initialCap", {})
        pnl   = item.get("unrealizedProfitPercent", {})
        value    = float(total.get("USD", 0) or 0) if isinstance(total, dict) else 0
        invested = float(init.get("USD", 0) or 0)  if isinstance(init, dict) else 0
        pnl_p    = float(pnl.get("USD", 0) or 0)   if isinstance(pnl, dict) else 0
        qty      = float(item.get("quantity", 0) or 0)
        if not sym or value < MIN_VALUE_USD:
            continue
        result[sym] = {
            "value":    round(value, 2),
            "invested": round(invested, 2),
            "pnl":      round(pnl_p, 2),
            "qty":      qty,
        }
    return result


def parse_known_groups():
    """Парсит _portfolio_groups.md. Возвращает {symbol: {group, score}}."""
    groups = {}
    if not os.path.exists(GROUPS_FILE):
        return groups
    with open(GROUPS_FILE) as f:
        for line in f:
            m = re.match(r'\|\s*\*\*(\d)\*\*\s*\|\s*([A-Z0-9]+)\s*\|\s*(\w+)', line)
            if m:
                g         = int(m.group(1))
                sym       = m.group(2)
                score_str = m.group(3)
                score     = int(score_str) if score_str.isdigit() else 0
                groups[sym] = {"group": g, "score": score}
    return groups


def _load_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        return {}
    try:
        with open(SNAPSHOT_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_snapshot(holdings):
    snap = {
        "timestamp": _mne_now(),
        "holdings": {sym: {"value": d["value"], "invested": d["invested"], "pnl": d["pnl"]}
                     for sym, d in holdings.items()},
    }
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snap, f, indent=2)


def _log_changes(changes):
    """Дописывает изменения в changes.log."""
    if not changes:
        return
    ts = _mne_now() + " (MNE)"
    with open(CHANGES_LOG, "a") as f:
        for c in changes:
            f.write(f"[{ts}] {c}\n")


def detect_changes(current_holdings, prev_snapshot):
    """
    Сравнивает текущий портфель со снапшотом.
    Возвращает список строк с описанием изменений.
    """
    changes = []
    prev = prev_snapshot.get("holdings", {})

    # Новые монеты
    for sym in current_holdings:
        if sym not in prev:
            val = current_holdings[sym]["value"]
            inv = current_holdings[sym]["invested"]
            changes.append(f"КУПЛЕНО {sym}: вложено ${inv:,.0f}, текущая стоимость ${val:,.0f}")

    # Проданные монеты
    for sym in prev:
        if sym not in current_holdings:
            changes.append(f"ПРОДАНО {sym}: позиция закрыта (была ${prev[sym]['value']:,.0f})")

    # Существенные изменения P/L (>= 5 п.п. относительно предыдущего снапшота)
    for sym in current_holdings:
        if sym not in prev:
            continue
        old_pnl = prev[sym].get("pnl", 0)
        new_pnl = current_holdings[sym]["pnl"]
        delta = new_pnl - old_pnl
        if abs(delta) >= 5:
            direction = "выросло" if delta > 0 else "упало"
            changes.append(
                f"P/L {sym} {direction} на {delta:+.1f}% "
                f"(было {old_pnl:+.1f}%, стало {new_pnl:+.1f}%)"
            )

    # Существенное изменение стоимости позиции без смены состава (>= $500)
    for sym in current_holdings:
        if sym not in prev:
            continue
        old_val = prev[sym].get("value", 0)
        new_val = current_holdings[sym]["value"]
        delta_usd = new_val - old_val
        # Пропускаем если это просто движение рынка без явного пополнения/частичной продажи
        old_inv = prev[sym].get("invested", 0)
        new_inv = current_holdings[sym]["invested"]
        inv_delta = abs(new_inv - old_inv)
        if inv_delta >= 200:  # изменение вложений >= $200
            direction = "пополнена" if new_inv > old_inv else "частично продана"
            changes.append(
                f"ПОЗИЦИЯ {sym} {direction}: вложено ${old_inv:,.0f} -> ${new_inv:,.0f} "
                f"(${inv_delta:+,.0f})"
            )

    return changes


def load_recent_changes(n=20):
    """Читает последние n строк из changes.log."""
    if not os.path.exists(CHANGES_LOG):
        return []
    with open(CHANGES_LOG) as f:
        lines = [l.rstrip() for l in f if l.strip()]
    return lines[-n:]


def get_dynamic_portfolio():
    """
    Основная функция модуля.
    Возвращает (PORTFOLIO, INVESTED, portfolio_values, new_coins, changes).

    PORTFOLIO        : {sym: group_int}
    INVESTED         : {sym: invested_usd}
    portfolio_values : {sym: {value, pnl}}
    new_coins        : [sym, ...] - монеты без анализа в _portfolio_groups.md
    changes          : [str, ...] - изменения с прошлого запуска
    """
    holdings     = fetch_dropstab_holdings()
    known_groups = parse_known_groups()

    # Обнаружение изменений
    prev_snapshot = _load_snapshot()
    changes = detect_changes(holdings, prev_snapshot)
    if changes:
        _log_changes(changes)
    _save_snapshot(holdings)

    PORTFOLIO = {}
    INVESTED  = {}
    pv        = {}
    new_coins = []

    for sym, data in holdings.items():
        if sym in known_groups:
            grp = known_groups[sym]["group"]
        else:
            grp = 3
            new_coins.append(sym)

        PORTFOLIO[sym] = grp
        INVESTED[sym]  = round(data["invested"])
        pv[sym]        = {"value": data["value"], "pnl": data["pnl"]}

    # BTC и ETH всегда нужны как эталоны
    for anchor in ("BTC", "ETH"):
        if anchor not in PORTFOLIO:
            g = known_groups.get(anchor, {}).get("group", 1)
            PORTFOLIO[anchor] = g
            INVESTED[anchor]  = 0

    return PORTFOLIO, INVESTED, pv, new_coins, changes


if __name__ == "__main__":
    PORTFOLIO, INVESTED, pv, new_coins, changes = get_dynamic_portfolio()
    print(f"Активных позиций: {len(PORTFOLIO)}")
    print(f"Новые монеты (без анализа): {new_coins}")
    if changes:
        print(f"\nИзменения ({len(changes)}):")
        for c in changes:
            print(f"  {c}")
    for sym, grp in sorted(PORTFOLIO.items(), key=lambda x: x[1]):
        val  = pv.get(sym, {}).get("value", 0)
        pnl  = pv.get(sym, {}).get("pnl", 0)
        flag = " *** НОВАЯ ***" if sym in new_coins else ""
        print(f"  {sym:8} г{grp}  ${val:>8,.0f}  {pnl:+.1f}%{flag}")
