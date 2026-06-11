#!/usr/bin/env python3
"""
Модуль динамического портфеля из Dropstab API.
Заменяет хардкод PORTFOLIO / INVESTED в generate_html.py
"""

import os
import re
import json
import urllib.request

GROUPS_FILE  = "/home/masus/crypto_analysis/_portfolio_groups.md"
ENV_FILE     = os.path.join(os.path.dirname(__file__), ".env")
MIN_VALUE_USD = 5.0  # минимальная стоимость позиции чтобы попасть в список


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


def fetch_dropstab_holdings():
    """
    Возвращает {symbol: {value, invested, pnl, qty}} для активных позиций.
    """
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
    """
    Парсит _portfolio_groups.md.
    Возвращает {symbol: {group, score}}.
    """
    groups = {}
    if not os.path.exists(GROUPS_FILE):
        return groups
    with open(GROUPS_FILE) as f:
        for line in f:
            # | **1** | BTC | 413 | ...
            m = re.match(r'\|\s*\*\*(\d)\*\*\s*\|\s*([A-Z0-9]+)\s*\|\s*(\w+)', line)
            if m:
                g         = int(m.group(1))
                sym       = m.group(2)
                score_str = m.group(3)
                score     = int(score_str) if score_str.isdigit() else 0
                groups[sym] = {"group": g, "score": score}
    return groups


def get_dynamic_portfolio():
    """
    Основная функция модуля.
    Возвращает (PORTFOLIO, INVESTED, portfolio_values, new_coins).

    PORTFOLIO        : {sym: group_int}
    INVESTED         : {sym: invested_usd}
    portfolio_values : {sym: {value, pnl}}
    new_coins        : [sym, ...] - монеты без анализа в _portfolio_groups.md
    """
    holdings     = fetch_dropstab_holdings()
    known_groups = parse_known_groups()

    PORTFOLIO = {}
    INVESTED  = {}
    pv        = {}
    new_coins = []

    for sym, data in holdings.items():
        if sym in known_groups:
            grp = known_groups[sym]["group"]
        else:
            grp = 3  # временно нейтральная группа до анализа
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

    return PORTFOLIO, INVESTED, pv, new_coins


if __name__ == "__main__":
    PORTFOLIO, INVESTED, pv, new_coins = get_dynamic_portfolio()
    print(f"Активных позиций: {len(PORTFOLIO)}")
    print(f"Новые монеты (без анализа): {new_coins}")
    for sym, grp in sorted(PORTFOLIO.items(), key=lambda x: x[1]):
        val  = pv.get(sym, {}).get("value", 0)
        pnl  = pv.get(sym, {}).get("pnl", 0)
        flag = " *** НОВАЯ ***" if sym in new_coins else ""
        print(f"  {sym:8} г{grp}  ${val:>8,.0f}  {pnl:+.1f}%{flag}")
