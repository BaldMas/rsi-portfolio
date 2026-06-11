#!/usr/bin/env python3
"""
Парсер портфеля Dropstab через API _gateway.
Использование: python3 parse_portfolio.py [share_token_or_url]
Токен берётся из .env (DROPSTAB_TOKEN) или передаётся аргументом.
"""

import sys
import json
import re
import os
import urllib.request
from datetime import datetime

API_BASE = "https://dropstab.com/_gateway/api"
OUTPUT_DIR = "/home/masus/crypto_analysis"

def _load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

_load_env()
DEFAULT_TOKEN = os.environ.get("DROPSTAB_TOKEN", "")


def fetch_json(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://dropstab.com/",
        "Origin": "https://dropstab.com",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


def extract_token(arg):
    # принимаем URL вида .../p/po-moim-myslam-fjkjsebo6f или просто токен
    m = re.search(r"/p/[^/]+-([a-z0-9]{10})$", arg)
    return m.group(1) if m else arg


def fmt_usd(val):
    v = float(val)
    sign = "+" if v > 0 else ""
    return f"{sign}${v:,.0f}"


def fmt_pct(val):
    v = float(val)
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.1f}%"


def usd(field, default=0.0):
    if field is None:
        return default
    if isinstance(field, dict):
        return float(field.get("USD") or default)
    try:
        return float(field)
    except (TypeError, ValueError):
        return default


def parse_portfolio(token=DEFAULT_TOKEN):
    data = fetch_json(f"{API_BASE}/portfolio/api/portfolioGroup/individualShare/{token}")

    name = data["name"]
    date_str = datetime.now().strftime("%Y-%m-%d")

    total = data["portfolioTotal"]
    invested = usd(total.get("initialCap"))
    current = usd(total.get("totalCap"))
    pnl = current - invested
    pnl_pct = pnl / invested * 100 if invested else 0

    active = []
    closed = []

    for p in data.get("portfolios", []):
        sym = p["symbol"]
        pname = p["name"]
        qty = float(p.get("quantity") or 0)
        inv = usd(p.get("initialCap"))
        cur = usd(p.get("totalCap"))
        realized = usd(p.get("realizedProfit"))
        unrealized = usd(p.get("unrealizedProfit"))

        if qty == 0 and inv == 0:
            if abs(realized) > 0:
                closed.append({"sym": sym, "realized": realized})
        else:
            pct = (unrealized / inv * 100) if inv else 0
            active.append({
                "sym": sym,
                "name": pname,
                "inv": inv,
                "cur": cur,
                "pnl": cur - inv,
                "pct": pct,
            })

    active.sort(key=lambda x: x["inv"], reverse=True)
    closed.sort(key=lambda x: x["realized"], reverse=True)

    print(f"\n{'='*65}")
    print(f"Портфель: {name}")
    print(f"Дата: {date_str}")
    print(f"{'='*65}")
    print(f"Invested:    ${invested:>12,.0f}")
    print(f"Current:     ${current:>12,.0f}")
    print(f"P/L:         {fmt_usd(pnl):>13}  ({fmt_pct(pnl_pct)})")
    print(f"\nАктивные позиции ({len(active)}):")
    print(f"{'#':<4}{'Тикер':<10}{'Invested':>12}{'Current':>12}{'P/L $':>12}{'P/L %':>9}")
    print("-"*60)
    for i, p in enumerate(active, 1):
        print(f"{i:<4}{p['sym']:<10}{fmt_usd(p['inv']):>12}{fmt_usd(p['cur']):>12}{fmt_usd(p['pnl']):>12}{fmt_pct(p['pct']):>9}")

    if closed:
        print(f"\nЗакрытые позиции ({len(closed)}):")
        for p in closed:
            print(f"  {p['sym']:<12}{fmt_usd(p['realized'])}")

    save_snapshot(name, date_str, invested, current, pnl, pnl_pct, active, closed)

    return active, closed


def save_snapshot(name, date_str, invested, current, pnl, pnl_pct, active, closed):
    sign = "+" if pnl >= 0 else ""
    lines = [
        f"# Портфель \"{name}\" - сводка",
        "",
        f"Дата снимка: {date_str}",
        "",
        "## Сводные цифры",
        "",
        "| Параметр | Значение |",
        "|---|---|",
        f"| Total invested | ${invested:,.0f} |",
        f"| Current value | ${current:,.0f} |",
        f"| **Total P/L** | **{sign}${pnl:,.0f} ({sign}{pnl_pct:.1f}%)** |",
        "",
        f"## Активные позиции ({len(active)} шт)",
        "",
        "| # | Тикер | Название | Invested | Current | P/L $ | P/L % |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, p in enumerate(active, 1):
        s = "+" if p["pnl"] >= 0 else ""
        pcts = "+" if p["pct"] >= 0 else ""
        lines.append(
            f"| {i} | {p['sym']} | {p['name']} | ${p['inv']:,.0f} | ${p['cur']:,.0f} "
            f"| {s}${p['pnl']:,.0f} | {pcts}{p['pct']:.1f}% |"
        )

    if closed:
        lines += ["", "## Закрытые позиции (realized P/L)", "", "| Тикер | Realized P/L |", "|---|---|"]
        for p in closed:
            s = "+" if p["realized"] >= 0 else ""
            lines.append(f"| {p['sym']} | {s}${p['realized']:,.0f} |")

    out = f"{OUTPUT_DIR}/_portfolio_summary.md"
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nСнимок сохранён: {out}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TOKEN
    token = extract_token(arg)
    parse_portfolio(token)
