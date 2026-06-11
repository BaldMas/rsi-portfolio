# Toncoin (TON) - полный анализ

Дата: 2026-06-09
Источник данных: WebSearch (CoinMarketCap, CoinGecko, CryptoTimes, InvZZ, TradingView, DEXTools, CoinGlass, Glassnode)

---

## Позиция в портфеле
| Параметр | Значение |
|---|---|
| Invested | $594 |
| Current value | $239 |
| Unrealized P/L | -59.8% |
| Avg buy price | ~$4.20 (расчётный) |

---

## Базовые рыночные данные (июнь 2026)
| Метрика | Значение |
|---|---|
| Цена | ~$1.78 |
| Market Cap | ~$4.75B |
| 24h Volume | ~$200M |
| MC rank | ~#22 |
| ATH | $8.25 (июнь 2024) |
| От ATH | -78% |
| Circ supply | ~2.67B TON |
| Total supply | ~5.15B (max 5.2B) |
| Circ/FDV | ~52% |
| Следующий анлок | TON Believers Fund ~36.59M TON/месяц (до октября 2028); 23.10.2026 - ~0.72% supply |
| OI деривативов | ~$500-570M; фьюч объём ~$1B/день |
| Биржи | Binance, Coinbase, OKX, Bybit, KuCoin, Gate, MEXC, Bitget - 97+ бирж |

Ребрендинг: 8 июня 2026 community vote (81.22% за) одобрило переименование токена TON -> GRAM; активация 15 июня 2026 в 12:00 UTC. Блокчейн не меняется; миграции не требуется.

---

## Этап 1. Скрининг F1-F7
| Фильтр | Результат | Комментарий |
|---|---|---|
| F1. Ликвидность | PASS | 24h vol ~$200M spot + ~$1B фьючи; листинг на 97 биржах включая Binance/Coinbase/OKX/Bybit |
| F2. Market Cap | PASS | ~$4.75B - топ-25 по MC |
| F3. Дилюция/анлоки | PASS | Circ/FDV ~52%; ближайший крупный анлок 23.10.2026 (~0.72% supply) - в норме; TON Believers Fund равномерно |
| F4. Тренд HTF | WARNING | Цена $1.78 у 200D MA ($1.75); 200D MA нисходит с 26.04.2026; но есть higher low: $0.59 (окт 2025) -> $1.92 (май 2026) +120%; не LH+LL на 1W |
| F5. Нарратив | PASS | Конкретные катализаторы: Gram ребрендинг 15.06.2026; Telegram -> крупнейший валидатор (MTONGA step 4); шаги 5-7 не раскрыты; $400M treasury company через Kingsway |
| F6. Проект живой | PASS | Активные коммиты июнь 2026; 520-678 commits в 43 core repos; обновления ton-blockchain 1-8 июня |
| F7. Красные флаги | PASS | TAC Cross-Chain exploit $2.8M (май 2026) - экосистемный, не основной протокол; Durov под следствием во Франции (travel ban снят 13.11.2025); активных регуляторных исков против TON нет |

**Вердикт скрининга: PASS.**
Один WARNING по F4 (цена у 200D MA, нисходящий 200D); F5 = PASS через конкретный катализатор. Суммарно 1 warning - допустимо.

---

## Этап 2. Скоринг 29 пунктов

### S-тир (вес 50)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 1 | Ликвидность | 4 | 8 | 32 | $200M/день spot; $1B/день фьючи; 97 бирж; все топ-CEX; спред <0.5% |
| 3 | Нарратив | 4 | 7 | 28 | "Telegram L1 для 900M+ юзеров"; Gram ребрендинг; MTONGA roadmap; уникальный distribution через мессенджер |
| 4 | ТА | 2 | 7 | 14 | Цена у 200D MA ($1.75); 200D нисходит; но higher low от $0.59 сформирован; отскок +120% от лоу в мае |
| 2 | Токеномика | 3 | 7 | 21 | Circ/FDV 52% (норм); инфляция 0.6% низкая; 50% fees burn; max supply нет (post-genesis эмиссия) |
| 24 | RS к сектору | 2 | 7 | 14 | TON -41% за 12 месяцев (с $3.02 до $1.78); BTC за тот же период значительно лучше; RS слабый |
| 13 | Деривативы | 3 | 7 | 21 | OI $500-570M; рост OI +41% на катализаторах; funding нейтральный; здоровый рынок |
| 16 | Катализаторы | 5 | 7 | 35 | Gram ребрендинг 15.06.2026; MTONGA шаги 5-7 (нераскрыты); $400M treasury company Kingsway; Telegram = крупнейший валидатор; fees снижены в 6x |
S-тир итого: **165**

### A-тир (вес 28)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 6 | On-chain | 2 | 4 | 8 | ~1.5B транзакций Q1 2026; DAU ~500K адресов; TVL упал с $800M до ~$76M - существенный отток |
| 25 | URPD | 2 | 4 | 8 | Огромный навес bag-holders в зоне $2-8 (покупки 2024); точная URPD н/д |
| 23 | Value accrual | 3 | 4 | 12 | 50% fees burn + staking yield 3.5-5%; fees снижены в 6x (меньше burn); умеренное value accrual |
| 26 | Exit liquidity | 4 | 4 | 16 | $200M/день spot - выход из позиции $239 без импакта; хорошая exit liquidity |
| 18 | Концентрация | 2 | 3 | 6 | >68% supply у whale wallets; высокая концентрация - риск |
| 5 | Фундаментал | 3 | 3 | 9 | Уникальный distribution через Telegram; $770M стейблов на сети; но TVL DeFi упал в 10x |
| 21 | Стейблы | 4 | 3 | 12 | USDT $580M + USDe + др. = ~$770M стейблов на TON; значимо для L1 такого размера |
| 27 | Прошлые циклы | 3 | 3 | 9 | В 2024 показал ATH $8.25 (x14 от минимумов); Telegram-driven нарратив работал; аналог с мессенджером-монетой |
A-тир итого: **80**

### B-тир (вес 16)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 12 | Макро | 3 | 2 | 6 | Общий рынок в осторожной фазе; Telegram-экосистема частично декаплируется от macro |
| 15 | Real yield | 3 | 2 | 6 | Staking 3.5-5% + fees burn - реальный yield, не пустая инфляция |
| 8 | Конкуренция | 2 | 2 | 4 | Конкурирует с SOL/SUI/APT как L1; TON отстаёт по DeFi/TVL; уникален только Telegram-distribution |
| 9 | Безопасность | 3 | 2 | 6 | Основной блокчейн без хаков; TAC Cross-Chain exploit $2.8M (экосистемный, не core); scam через Telegram |
| 17 | Dev activity | 3 | 2 | 6 | 520-678 commits в 43 repos; 54-57 место по dev activity; активно, но не топ |
| 20 | Реакция новости | 4 | 2 | 8 | +19% на анонс Gram; +28% на отдельные новости; +120% от лоу за 2 месяца; сильная спекулятивная реакция |
| 11 | Регуляторика | 2 | 2 | 4 | Durov под следствием во Франции; US-биржи осторожны (тень SEC 2019-2020); travel ban снят, но дело идёт |
| 7 | Команда | 3 | 2 | 6 | TON Foundation заменяется Telegram как главным игроком; Durov - сильный key person, но и риск |
B-тир итого: **46**

### C-тир (вес 6)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 14 | Корреляции | 3 | 1 | 3 | Корреляция с топ-10 = 0.371 (низкая); частично декаплируется на Telegram-катализаторах |
| 19 | Казна | 3 | 1 | 3 | $400M treasury company через Kingsway в работе; ещё не оформлено |
| 10 | Соцметрики | 4 | 1 | 4 | Telegram 900M+ MAU - крупнейший social-asset в крипте; встроенный кошелёк |
| 22 | Интеграции | 4 | 1 | 4 | USDT on TON; Atomic Wallet; Lighter perpetuals в Telegram Wallet; Mini Apps 150-190M MAU |
| 28 | Key person | 2 | 1 | 2 | Durov - и сила, и риск; следствие во Франции; концентрация власти Telegram над TON растёт |
| 29 | Off-ramp | 4 | 1 | 4 | Binance/Coinbase/OKX - все основные fiat off-ramp поддерживают TON |
C-тир итого: **20**

---

## Этап 3. Итоговый Score
**Score = 165 + 80 + 46 + 20 = 311 / 500**

Категория: **Average/catalyst** (300-379)

---

## Решение по позиции
**Для новых денег:** PASS. Проект проходит скрининг; плотный поток катализаторов в июне 2026. Вход с жёстким стопом - только после подтверждения выше $2.00.

**Для существующей позиции:**
| Решение | За | Против |
|---|---|---|
| HOLD | Gram ребрендинг 15.06; MTONGA шаги 5-7; $400M treasury; сильная реакция на новости; unique Telegram distribution | -59.8%; цена у 200D MA нисходящего; TVL упал в 10x; Durov-риск; высокая концентрация whales |
| ADD | Катализаторный момент; возможность усреднения перед Gram launch | Score 311 = "под катализатор", не "хорошо"; до подтверждения разворота риск |
| CUT | Освобождение капитала для более сильных активов | Потеря потенциала на Gram-нарративе; продажа перед ключевым событием |

### Рекомендация: HOLD под катализатор с чёткими уровнями
1. Gram ребрендинг 15.06.2026 - ближайший катализатор; уже одобрен (81.22%); рынок знает о нём.
2. MTONGA шаги 5-7 нераскрыты - потенциальный сюрприз для рынка.
3. Технически цена у 200D MA ($1.75); пробой вверх + удержание даст сигнал на усиление позиции.
4. Стоп-лосс: закрытие дня ниже $1.40 (слом higher low структуры).
5. TP1 (30-40% позиции): $2.50-2.80 (~+50%); TP2 (30%): $3.50-4.00 (~+100%).
6. Если к 15 июля 2026 цена не закрепится выше $2.00 - сократить позицию на 50%.

### Триггеры на выход
- Закрытие дня ниже $1.40 (слом структуры)
- Ужесточение дела Дурова во Франции (новый арест / ограничения)
- MTONGA шаги 5-7 оказались разочаровывающими для рынка
- BTC широкий deleveraging ниже ключевых поддержек

---

## Источники
- [CoinMarketCap - Toncoin](https://coinmarketcap.com/currencies/toncoin/)
- [CoinGecko - Toncoin](https://www.coingecko.com/en/coins/toncoin)
- [CryptoTimes - Gram rebrand approved (09.06.2026)](https://www.cryptotimes.io/2026/06/09/gram-is-back-ton-community-approves-rebrand-with-81-support/)
- [CryptoTimes - Durov revives Gram (02.06.2026)](https://www.cryptotimes.io/2026/06/02/telegrams-durov-revives-gram-token-name-in-3-week-ton-rebrand/)
- [Invezz - TON rallies on Gram](https://invezz.com/news/2026/06/02/toncoin-jumps-as-durov-revives-gram-name-and-bulls-eye-major-breakout/)
- [TradingView - TON token unlock Oct 2026](https://www.tradingview.com/news/coinmarketcal:823b16bf7094b:0-toncoin-token-unlock-23-october-2026/)
- [DEXTools - TON Tokenomics 2026](https://www.dextools.io/tutorials/ton-tokenomics-toncoin-supply-distribution-inflation-guide-2026)
- [CoinGlass - TON Liquidations](https://www.coinglass.com/liquidations/TON)
- [Glassnode - TON Futures Leverage](https://studio.glassnode.com/charts/futures-leverage-ratio?a=TON)
