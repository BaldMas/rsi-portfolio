#!/usr/bin/env python3
"""
Генерирует рекомендации по портфелю на основе:
  - Технических сигналов (signals.json от generate_html.py)
  - Сентимента новостей (news.db от news_fetcher.py)
  - Текущих данных портфеля (portfolio_live.py)

Отправляет в Telegram и сохраняет в recommendations.log
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))

SIGNALS_FILE = os.path.join(os.path.dirname(__file__), "signals.json")
NEWS_DB      = os.path.join(os.path.dirname(__file__), "news.db")
RECS_LOG     = os.path.join(os.path.dirname(__file__), "recommendations.log")


def _mne_now():
    mne = timezone(timedelta(hours=2))
    return datetime.now(tz=mne).strftime("%Y-%m-%d %H:%M")


def load_signals():
    """Загружает сигналы из signals.json. Возвращает dict {coin: best_signal_data}."""
    if not os.path.exists(SIGNALS_FILE):
        return {}
    with open(SIGNALS_FILE) as f:
        data = json.load(f)

    # Агрегируем по монете: берём лучший сигнал (vs BTC или наивысший sig)
    per_coin = {}
    for r in data.get("signals", []):
        coin = r["coin"]
        sig  = r.get("sig", 0)
        # Предпочитаем сигнал vs BTC, иначе наивысший
        existing = per_coin.get(coin)
        if existing is None or sig > existing["sig"] or r.get("ref") == "BTC":
            per_coin[coin] = r
    return per_coin


def load_news_sentiment(hours=48):
    """Загружает сентимент новостей из SQLite. Возвращает {coin: {pos, neg, neu, items}}."""
    if not os.path.exists(NEWS_DB):
        return {}
    conn = sqlite3.connect(NEWS_DB)
    cur = conn.execute("""
        SELECT coin, sentiment, title, source, published, lang FROM news
        WHERE fetched >= datetime('now', ?)
        ORDER BY fetched DESC
    """, (f"-{hours} hours",))
    rows = cur.fetchall()
    conn.close()

    result = {}
    for coin, sentiment, title, source, published, lang in rows:
        if coin not in result:
            result[coin] = {"pos": 0, "neg": 0, "neu": 0, "items": []}
        d = result[coin]
        if sentiment == 1:
            d["pos"] += 1
        elif sentiment == -1:
            d["neg"] += 1
        else:
            d["neu"] += 1
        if len(d["items"]) < 5:
            d["items"].append({"title": title, "source": source, "lang": lang})
    return result


def combined_score(sig, news_pos, news_neg):
    """Итоговый скор: технический + новостной."""
    news_adj = 0
    total = news_pos + news_neg
    if total >= 3:
        ratio = (news_pos - news_neg) / total
        if ratio > 0.5:
            news_adj = 1.5
        elif ratio < -0.5:
            news_adj = -1.5
        elif ratio > 0.2:
            news_adj = 0.7
        elif ratio < -0.2:
            news_adj = -0.7
    return sig + news_adj


def build_recommendations():
    try:
        from portfolio_live import get_dynamic_portfolio
        PORTFOLIO, INVESTED, pv, new_coins, changes = get_dynamic_portfolio()
    except Exception as e:
        print(f"Ошибка загрузки портфеля: {e}")
        return []

    signals  = load_signals()
    news_map = load_news_sentiment(48)

    recs = []
    for coin, grp in PORTFOLIO.items():
        val     = pv.get(coin, {}).get("value", 0)
        pnl     = pv.get(coin, {}).get("pnl", 0)
        invested = INVESTED.get(coin, 0)

        sig_data = signals.get(coin, {})
        sig      = sig_data.get("sig", 0)
        rsi_d    = sig_data.get("rsi_d")
        z90      = sig_data.get("z90")
        rs_30    = sig_data.get("rs_30")
        dist_200 = sig_data.get("dist_200")
        funding  = sig_data.get("funding")

        news = news_map.get(coin, {"pos": 0, "neg": 0, "neu": 0, "items": []})
        pos, neg, neu = news["pos"], news["neg"], news["neu"]
        total_news = pos + neg + neu

        cscore = combined_score(sig, pos, neg)

        recs.append({
            "coin":     coin,
            "grp":      grp,
            "val":      val,
            "pnl":      pnl,
            "invested": invested,
            "sig":      sig,
            "cscore":   cscore,
            "rsi_d":    rsi_d,
            "z90":      z90,
            "rs_30":    rs_30,
            "dist_200": dist_200,
            "funding":  funding,
            "pos":      pos,
            "neg":      neg,
            "neu":      neu,
            "total_news": total_news,
            "news_items": news["items"],
            "changes": changes,
        })

    recs.sort(key=lambda x: x["cscore"], reverse=True)
    return recs


def fmt_num(v, decimals=1):
    if v is None:
        return "н/д"
    return f"{v:+.{decimals}f}"


def format_telegram(recs):
    ts = _mne_now() + " (MNE)"

    urgent    = [r for r in recs if r["neg"] >= 3 or r["sig"] < -4]
    positive  = [r for r in recs if r["cscore"] > 4 and r not in urgent]
    watch     = [r for r in recs if 2 < r["cscore"] <= 4 and r not in urgent]
    no_news   = [r["coin"] for r in recs if r["total_news"] == 0 and r["coin"] not in ("BTC", "ETH")]

    lines = [f"<b>📊 Рекомендации по портфелю</b>"]
    lines.append(f"<i>{ts}</i>")

    # Изменения портфеля
    changes = recs[0]["changes"] if recs and recs[0].get("changes") else []
    if changes:
        lines.append("")
        lines.append("<b>🔄 Изменения портфеля:</b>")
        for c in changes[-5:]:
            lines.append(f"  • {c}")

    # Тревога
    if urgent:
        lines.append("")
        lines.append("<b>🔴 Внимание:</b>")
        for r in urgent[:5]:
            news_note = f" | новости: {r['pos']}+ / {r['neg']}-" if r["total_news"] else ""
            lines.append(
                f"  <b>{r['coin']}</b> G{r['grp']} | "
                f"sig={fmt_num(r['sig'])} | "
                f"RSI={fmt_num(r['rsi_d'],'0') if r['rsi_d'] else 'н/д'} | "
                f"P/L {r['pnl']:+.0f}%"
                f"{news_note}"
            )
            for item in r["news_items"][:2]:
                lines.append(f"    ↳ [{item['lang']}] {item['title'][:90]}")

    # Позитивные сигналы
    if positive:
        lines.append("")
        lines.append("<b>🟢 Сигналы на ротацию:</b>")
        for r in positive[:5]:
            news_note = f" | {r['pos']}+ новостей" if r["pos"] else ""
            lines.append(
                f"  <b>{r['coin']}</b> G{r['grp']} | "
                f"sig={fmt_num(r['sig'])} | "
                f"Z={fmt_num(r['z90'])} | "
                f"MA200={fmt_num(r['dist_200'])}%"
                f"{news_note}"
            )

    # Смотреть
    if watch:
        lines.append("")
        lines.append("<b>🟡 Смотреть:</b>")
        coins_watch = ", ".join(
            f"{r['coin']}(sig={fmt_num(r['sig'])})" for r in watch[:8]
        )
        lines.append(f"  {coins_watch}")

    # Общий срез портфеля
    total_val     = sum(r["val"] for r in recs)
    total_invested = sum(r["invested"] for r in recs if r["invested"] > 0)
    total_pnl     = ((total_val / total_invested - 1) * 100) if total_invested else 0
    lines.append("")
    lines.append(
        f"<b>💼 Портфель:</b> ${total_val:,.0f} "
        f"(вложено ${total_invested:,.0f}, {total_pnl:+.1f}%)"
    )

    if no_news:
        lines.append(f"<i>⚪ Нет новостей: {', '.join(no_news[:10])}</i>")

    return "\n".join(lines)


def save_log(text):
    ts = _mne_now() + " (MNE)"
    with open(RECS_LOG, "a") as f:
        f.write(f"\n{'='*60}\n[{ts}]\n{text}\n")


def run():
    print("Портфель и сигналы...", flush=True)
    recs = build_recommendations()
    if not recs:
        print("Нет данных для рекомендаций")
        return

    print(f"  Монет: {len(recs)}", flush=True)
    text = format_telegram(recs)
    save_log(text)

    from notify_telegram import send
    ok = send(text)
    if ok:
        print("✓ Рекомендации отправлены в Telegram")
    else:
        print("✗ Telegram не настроен, рекомендации сохранены в recommendations.log")
        # Печатаем в консоль
        import re
        plain = re.sub(r"<[^>]+>", "", text)
        print("\n" + plain)


if __name__ == "__main__":
    run()
