# Hedera (HBAR) - полный анализ

Дата: 2026-06-09
Источник данных: WebSearch (CoinGecko, CoinMarketCap, SEC EDGAR, Hedera Council, Disruption Banking, AInvest)

---

## Позиция в портфеле

| Параметр | Значение |
|---|---|
| Куплено | 76 729,65 HBAR |
| Avg buy price | $0,0781 |
| Дата покупки | **2026-06-03** (6 дней назад, тот же день что и XRP) |
| Invested | $5 996 |
| Текущая цена | $0,0806 |
| Current value | $6 184 |
| Realized P/L | $0 |
| Unrealized P/L | **+$188 (+3,1%)** |

**Ключевой факт:** покупка ровно на ключевом support зоне $0,078-$0,088. Сейчас цена в нижней трети консолидации.

---

## Базовые рыночные данные (июнь 2026)

| Метрика | Значение |
|---|---|
| Цена | $0,0818 |
| Market Cap | $3,54B |
| Circ supply | 43B |
| Max supply | 50B |
| Circ/Max | **86%** (хорошо) |
| Rank (CoinGecko) | #29 |
| 24h Volume | $53M (умеренный для топ-30) |
| 7d change | -11,9% (но лучше альтов: -14,2% по smart contracts) |
| ETF | **Canary HBAR ETF (HBR) на Nasdaq**, $93M AUM, держит 549M HBAR |

---

## Этап 1. Скрининг F1-F7

| Фильтр | Результат | Комментарий |
|---|---|---|
| **F1. Ликвидность** | PASS | $53M спот, листинг Coinbase/Binance/Kraken/Bybit + **ETF на Nasdaq** |
| **F2. Market Cap** | PASS strong | $3,54B, топ-30 |
| **F3. Дилюция** | PASS strong | 86% уже в обращении, прозрачные квартальные релизы Council, нет дискретных cliffs |
| **F4. Тренд HTF** | **FAIL** | Ниже всех 5 EMA (10/20/50/100/200), MACD negative, RSI 41 нейтрально-bearish |
| **F5. Нарратив сектора** | PASS | RWA + Enterprise AI + ETF - все хайповые темы 2026, Accenture вошёл в Council апр 2026 |
| **F6. Проект живой** | PASS strong | Council расширен (Accenture, McLaren, FedEx, Halborn), Lloyds/Aberdeen UK use case, Australian Digital Dollar |
| **F7. Красные флаги** | PASS | Нет хаков, нет регуляторных issue, есть ETF |

**Вердикт скрининга: PASS (с 1 warning на F4).**
F4 единственный fail, укладывается в правило "1 warning". Актив проходит на скоринг.

---

## Этап 2. Скоринг 29 пунктов

### S-тир (вес 50)

| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 1 | Ликвидность | **3** | 8 | 24 | $53M ок для топ-30, ETF плюс. Не tier-1 объёмы как у топ-10 |
| 3 | Нарратив | **4** | 7 | 28 | RWA + Enterprise AI (Accenture), Council expansion = горячие темы |
| 4 | ТА | **2** | 7 | 14 | Bearish HTF, но **купил ровно на support зоне** $0,078-$0,088 |
| 2 | Токеномика | **4** | 7 | 28 | 86% циркуляция, прозрачные квартальные релизы, нет cliff'ов |
| 24 | RS к сектору | **3** | 7 | 21 | Outperform smart contracts (-11,9% vs -14,2% сектор) |
| 13 | Деривативы | **2** | 7 | 14 | Perpetuals есть, но OI меньше топ-10 |
| 16 | Катализаторы | **4** | 7 | 28 | ETF expansion, Council adds, Australian CBDC, Lloyds intgration |

S-тир итого: **157**

### A-тир (вес 28)

| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 6 | On-chain метрики | **3** | 4 | 12 | Реальные enterprise tx, но многое в private chains - не виден весь трафик |
| 25 | URPD | **3** | 4 | 12 | На уровне ключевого cost basis cluster - типичный паттерн "support из бэгхолдеров" |
| 23 | Value accrual | **2** | 4 | 8 | HBAR оплачивает tx fees, но нет buyback/burn механизма |
| 26 | Exit liquidity | **3** | 4 | 12 | $53M/день позволяет выйти $5-10K позицию без слиппеджа |
| 18 | Концентрация | **3** | 3 | 9 | Treasury 7B HBAR, Council distributed = умеренная централизация |
| 5 | Фундаментал | **4** | 3 | 12 | Lloyds/Aberdeen FX, Australian Digital Dollar, Google/IBM/Boeing/DT/Accenture - реальная adoption |
| 21 | Стейблы | **2** | 3 | 6 | Есть стейблы на Hedera, но экосистема мала |
| 27 | Аналоги прошлых циклов | **3** | 3 | 9 | HBAR показывал паттерн "длинная консолидация на дне → парабола", повторяемо |

A-тир итого: **80**

### B-тир (вес 16)

| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 12 | Макро | **2** | 2 | 4 | Текущий risk-off бьёт по альтам, но enterprise story частично insulates |
| 15 | Real yield | **2** | 2 | 4 | Staking yield есть, небольшой |
| 8 | Конкуренция / moat | **3** | 2 | 6 | aBFT консенсус уникальный, Council governance differentiator |
| 9 | Безопасность | **5** | 2 | 10 | **Лучшие в классе** - aBFT mathematically proven, no hacks, enterprise-grade |
| 17 | Dev activity | **4** | 2 | 8 | Активная разработка, HBAR Foundation финансирует ecosystem |
| 20 | Реакция на новости | **3** | 2 | 6 | Council adds запускают локальные ралли +5-10% |
| 11 | Регуляторика | **4** | 2 | 8 | Coinbase listed, ETF на Nasdaq, чисто |
| 7 | Команда | **4** | 2 | 8 | Leemon Baird (создатель Hashgraph), Mance Harmon, сильный Council |

B-тир итого: **54**

### C-тир (вес 6)

| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 14 | Корреляции | **2** | 1 | 2 | Бета к BTC умеренная, движения коррелированы |
| 19 | Казна | **4** | 1 | 4 | Treasury 7B HBAR, прозрачная отчётность Council |
| 10 | Соцметрики | **2** | 1 | 2 | Enterprise-leaning, retail mindshare меньше |
| 22 | Интеграции | **5** | 1 | 5 | Google, IBM, Boeing, DT, FedEx, McLaren, Accenture - топ enterprise |
| 28 | Key person | **4** | 1 | 4 | Распределённая команда + Council = низкий риск ключевого лица |
| 29 | Off-ramp | **4** | 1 | 4 | Coinbase, Binance, ETF на Nasdaq |

C-тир итого: **21**

---

## Этап 3. Итоговый Score

**Score = 157 + 80 + 54 + 21 = 312 / 500**

**Процент от максимума: 62,4%**

По шкале интерпретации:
- 450+ Top-pick
- 380-449 Хорошо
- **300-379 Средне, только под катализатор** ← **HBAR здесь (312)**
- < 300 Пропуск

HBAR попадает в зону "под катализатор". Катализаторы есть: ETF expansion (potential), Accenture AI initiative, Australian Digital Dollar adoption.

---

## Решение по позиции (+3,1%, купил на support)

### Контекст
Позиция набрана 6 дней назад **прямо на ключевом support** $0,078-$0,088. Это:
- Не случайность - ты явно купил в зоне технической поддержки
- Asymmetric setup: stop близко ($0,075), upside до $0,103-$0,118

### Решение: HOLD с конкретными уровнями

| Уровень | Действие | Логика |
|---|---|---|
| **Stop loss: $0,075** | Закрыть всю позицию | Пробой ключевого support = тезис сломался, переход в lower trading range |
| **Take Profit 1: $0,103** | Продать 30-40% (~25-30K HBAR) | Верх текущей консолидации, рост +28% от entry |
| **Take Profit 2: $0,118** | Продать ещё 30% | Прошлая резистанс зона, рост +51% |
| **Take Profit 3: $0,20-$0,25** | Закрыть остаток | Зона "reclaim" - подтверждение реверсии |
| **Add trigger: $0,10 пробой с объёмом** | Усреднить вверх на 30-50% | Только при подтверждённом пробое + объём > 30D avg |

### Почему HOLD a не cut

1. **Купил на правильном уровне** - не на хайпе как с STRK/OP, а на support
2. **Реальные катализаторы**: Accenture AI, ETF растёт ($93M AUM), Lloyds/Aberdeen UK
3. **Score 312** попадает в "под катализатор" зону - именно для такого случая
4. **Tight risk**: stop -7% при upside +28-51% = R/R 4-7x

### Почему не ADD сейчас

1. **F4 fail** - тренд ещё не подтвердил разворот
2. **Ниже всех EMA** - бычий сетап технически не подтверждён
3. **Сектор макро слабый** - risk-off режим
4. **Лучше купить на пробое $0,10 с подтверждением**, чем угадывать дно

### Триггеры экстренного выхода

- Пробой $0,075 вниз с объёмом
- Утечка из ETF (отток > $20M за неделю)
- Council member покидает (репутационный риск)
- Major hack или регуляторное действие

---

## Контраст с другими позициями

| Параметр | OP (-93%) | XRP (+131%) | HBAR (+3%) |
|---|---|---|---|
| Когда куплен | На хайпе $1,43 | На дипе $0,50 | На support $0,078 |
| Catalyst-driven? | Технологический хайп | ETF + CLARITY конкретные даты | Накопительная enterprise adoption |
| Score | 276 | 367 | 312 |
| Решение | HOLD без add | TRIM 50% + runner | HOLD с tight stop |
| Risk/Reward сейчас | Низкое (структурные проблемы) | Хорошее (катализатор близко) | **Хорошее (купил на support)** |

---

## Главный урок

**HBAR это пример "правильной покупки на support после фундаментальной работы".** Что хорошего сделано:
1. Не покупал на параболе, а ждал консолидации
2. Тезис: enterprise adoption растёт (Accenture, FedEx, McLaren в 2026)
3. Tight risk через близкий stop
4. Asymmetric reward через близкие resistance уровни

Если HBAR пройдёт скрининг и поднимется до score 380+ (например, на новостях о расширении ETF или новых Council members) - можно увеличивать позицию.

---

## Источники

- [HBAR - CoinGecko](https://www.coingecko.com/en/coins/hedera)
- [HBAR - CoinMarketCap](https://coinmarketcap.com/currencies/hedera/)
- [Canary HBAR ETF - SEC EDGAR](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0002039458)
- [Accenture joins Hedera Council - PR Newswire](https://www.prnewswire.com/news-releases/hedera-council-welcomes-accenture-to-advance-trusted-infrastructure-for-enterprise-ai-302759356.html)
- [FedEx joins Hedera Council - Disruption Banking](https://www.disruptionbanking.com/2026/02/17/fedex-joins-hedera-council-amid-rising-hbar-momentum/)
- [Hedera Council members](https://hederacouncil.org/)
- [HBAR Tokenomics - MEXC](https://www.mexc.com/price/HBAR/tokenomics)
- [Hedera RWA AI - AInvest](https://www.ainvest.com/news/hedera-institutional-grade-infrastructure-2026-launchpad-rwa-ai-driven-finance-2601/)
