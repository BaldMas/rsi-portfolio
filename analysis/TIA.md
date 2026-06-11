# Celestia (TIA) - полный анализ

Дата: 2026-06-09
Источник данных: WebSearch (CoinGecko, CoinMarketCap, CryptoRank, Tokenomist, DefiLlama, Celestia docs, Cryptonomist, CoinDCX, Bitcoin Foundation)

---

## Позиция в портфеле
| Параметр | Значение |
|---|---|
| Invested | $599 |
| Current value | $41 |
| Unrealized P/L | -93.1% |
| Avg buy price | ~$6.50 (расчётный) |

---

## Базовые рыночные данные (июнь 2026)
| Метрика | Значение |
|---|---|
| Цена | ~$0.32 (диапазон $0.32-$0.34 по источникам) |
| Market Cap | ~$295-297M |
| 24h Volume | ~$31.6M |
| MC rank | #103-134 |
| ATH | $20.85 |
| От ATH | -98.5% |
| Circ supply | ~924M TIA |
| Total supply | ~1.17B TIA (1B genesis + инфляция) |
| Circ/FDV | ~79-80% |
| Следующий анлок | Ежемесячно ~9.7M TIA; крупный cliff 31.10.2026 (~175.66M TIA = ~17% supply) |
| OI деривативов | ~$68M (perps Binance/OKX/Bybit); funding +0.0042% (лонги платят) |
| Биржи | Binance, Coinbase, OKX, Bybit, KuCoin, Bitget, Gate, MEXC |

---

## Этап 1. Скрининг F1-F7
| Фильтр | Результат | Комментарий |
|---|---|---|
| F1. Ликвидность | PASS | 24h vol ~$31.6M > $20M; листинг Binance/Coinbase/OKX/Bybit; топ-4 CEX |
| F2. Market Cap | PASS | ~$295-297M > $200M (консервативный порог) |
| F3. Дилюция/анлоки | FAIL | Cliff 31.10.2026: ~175.66M TIA = ~17% supply - критический анлок в пределах 5 месяцев; ежемесячные анлоки ~9.7M TIA продолжаются |
| F4. Тренд HTF | FAIL | Цена ниже 200D MA ($0.85); нисходящий канал LH+LL на 1W с февраля 2024; -19.8% за 7 дней |
| F5. Нарратив | WARNING | RS к BTC отрицательный; есть катализаторы (Celestia Fibre 1Tb/s, V8 upgrade, Lazy Bridging), но "против ветра" unlocks |
| F6. Проект живой | PASS | 1500+ активных разработчиков; V8 Hibiscus на testnet; Vision 2.0 опубликован; активные коммиты |
| F7. Красные флаги | PASS | Хаков не было; активных регуляторных исков нет |

**Вердикт скрининга: FAIL.**
F3 FAIL (критический cliff 17% supply через 5 месяцев). F4 FAIL (явный downtrend, LH+LL на 1W). F4 + F5 суммарно >1 warning. Два hard fail - проект не проходит скрининг. Скоринг выполнен для информации по существующей позиции.

---

## Этап 2. Скоринг 29 пунктов

### S-тир (вес 50)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 1 | Ликвидность | 3 | 8 | 24 | Vol $31.6M/day - средне; на нижней границе; Vol/MCap ~0.10 нормальный |
| 3 | Нарратив | 3 | 7 | 21 | Модульная DA - пионер; но нарратив остыл; конкуренция EigenDA/Avail/EthDAS |
| 4 | ТА | 1 | 7 | 7 | Цена ниже 200D MA ($0.85); нисходящий 200D с октября 2024; descending channel; ATL $0.28 рядом |
| 2 | Токеномика | 1 | 7 | 7 | Cliff 175.66M TIA (17% supply) 31.10.2026; ежемесячные анлоки; инфляция 8% -> снижается на 10%/год |
| 24 | RS к сектору | 0 | 7 | 0 | TIA -98.5% от ATH; BTC около ATH; underperform массивный; RS отрицательный 60-90D |
| 13 | Деривативы | 2 | 7 | 14 | OI ~$68M (+14% в мае); funding +0.0042% (умеренный лонг-перекос); нет экстремумов |
| 16 | Катализаторы | 3 | 7 | 21 | Celestia Fibre (1Tb/s blockspace); V8 Hibiscus (ZK cross-chain); Lazy Bridging; $100M treasury; Blobstream для Ethereum L2 |
S-тир итого: **94**

### A-тир (вес 28)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 6 | On-chain | 3 | 4 | 12 | 1500+ разработчиков на Sovereign SDK/Rollkit; 160+ GB blob data опубликовано; 40% rollup data share в модульном пространстве |
| 25 | URPD | 1 | 4 | 4 | Огромный навес: большинство держателей купили в диапазоне $3-20; весь объём "под водой" |
| 23 | Value accrual | 1 | 4 | 4 | DA fees низкие; buyback/burn нет (только в proposal PoG); staking yield инфляционный; real yield ~0 |
| 26 | Exit liquidity | 2 | 4 | 8 | $31.6M daily vol достаточно для розницы; для крупных VC выходов после октябрьского cliff - проблема |
| 18 | Концентрация | 2 | 3 | 6 | 23 валидатора держат ~50% делегированного TIA; всё ещё VC-tilted распределение |
| 5 | Фундаментал | 3 | 3 | 9 | Реальный продукт: 55-64% дешевле Ethereum blobs; dozens rollups интегрированы |
| 21 | Стейблы | 1 | 3 | 3 | Celestia - DA layer; нет нативного DeFi; TIA не используется как залог для стейблов |
| 27 | Прошлые циклы | 2 | 3 | 6 | Новый токен (2023); один bull-run до ATH $20.85; потом -98.5%; аналогия с другими DA-токенами неблагоприятная |
A-тир итого: **52**

### B-тир (вес 16)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 12 | Макро | 2 | 2 | 4 | BTC around ATH (бычий фон), но alt-season не транслируется в vest-heavy токены |
| 15 | Real yield | 1 | 2 | 2 | Staking yield = 10-16% инфляционный (Matcha снизил до 0.25%); real yield около нуля |
| 8 | Конкуренция | 2 | 2 | 4 | EigenDA, Avail, NEAR DA, EthDAS; Celestia первопроходец, но теряет Ethereum-aligned долю |
| 9 | Безопасность | 4 | 2 | 8 | Хаков нет; CometBFT consensus проверен; ZK proofs аудитированы |
| 17 | Dev activity | 4 | 2 | 8 | 1500+ разработчиков; V8 Hibiscus; Fibre; Lazy Bridging - активная разработка |
| 20 | Реакция новости | 1 | 2 | 2 | Buyback Polychain ($62.5M) дал краткий отскок затем продажу; upgrades не двигают цену |
| 11 | Регуляторика | 3 | 2 | 6 | Нет активных исков; utility token (gas+staking); листинг Coinbase/Binance в США |
| 7 | Команда | 3 | 2 | 6 | Mustafa Al-Bassam (LazyLedger paper); сильный технический бэкграунд; нет конфликтов |
B-тир итого: **40**

### C-тир (вес 6)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 14 | Корреляции | 3 | 1 | 3 | Высокая корреляция с L1/DA-сектором и альт-индексом |
| 19 | Казна | 4 | 1 | 4 | $100M treasury (Celestia Foundation) - достаточно для долгосрочного развития |
| 10 | Соцметрики | 2 | 1 | 2 | Retail внимание ослабло после ATH 2024; хайп ушёл |
| 22 | Интеграции | 4 | 1 | 4 | Manta, Eclipse, Astria, Dymension RollApps; Arbitrum Orbit/OP Stack/Polygon CDK; Blobstream для Ethereum L2 |
| 28 | Key person | 3 | 1 | 3 | Mustafa Al-Bassam - известен в сообществе; зависимость средняя |
| 29 | Off-ramp | 4 | 1 | 4 | Binance/Coinbase/OKX/Bybit - все основные off-ramp; USDT/USDC пары |
C-тир итого: **20**

---

## Этап 3. Итоговый Score
**Score = 94 + 52 + 40 + 20 = 206 / 500**

Категория: **Skip** (<300)

---

## Решение по позиции
**Для новых денег:** FAIL (скрининг не пройден). Новый вход не рекомендован.

**Для существующей позиции:**
| Решение | За | Против |
|---|---|---|
| HOLD | Позиция $41 - психологически уже "dust"; возможный отскок 2-3x до $0.7-1.0 перед cliff | Cliff 175.66M TIA 31.10.2026; нисходящий тренд; RS нулевой; value accrual отсутствует |
| ADD | н/а - скрининг FAIL | Критически опасно: усреднение с приближающимся 17%-supply cliff |
| CUT | Фиксация убытка $557 для налоговой оптимизации; переаллокация в более сильный актив | Сумма $41 мала; психологически сложно |

### Рекомендация: HOLD с жёсткими условиями выхода (не усреднять)
1. Позиция -93.1% ($599 -> $41) - сумма мала, downside ограничен ($0-41).
2. Не докупать: F3 и F4 FAIL, cliff 17% supply через 5 месяцев - любое усреднение против тренда.
3. Возможный отскок на катализаторах (Fibre, V8, Lazy Bridging) до $0.55-0.65 до октября.
4. Стратегический выход до 15 октября 2026 - выйти полностью перед cliff unlock.
5. Re-entry рассматривать не раньше Q1 2027: после прохождения cliff + 2 месяца консолидации + higher low на 1W + цена выше 200D MA.

### Триггеры на выход
- Пробой $0.25 (ATL зона) - капитуляция, выход немедленно
- Отскок к $0.55-0.65 (200D EMA) - выход 70% позиции
- 15 октября 2026 - выход 100% перед cliff unlock 31.10.2026
- Рост конкурента EigenDA/Avail, вытесняющий Celestia из топ-rollup интеграций

---

## Источники
- [CoinGecko - Celestia](https://www.coingecko.com/en/coins/celestia)
- [CoinMarketCap - Celestia](https://coinmarketcap.com/currencies/celestia/)
- [CryptoRank - TIA Vesting](https://cryptorank.io/price/celestia/vesting)
- [Tokenomist - Celestia](https://tokenomist.ai/celestia)
- [DefiLlama - Celestia Unlocks](https://defillama.com/unlocks/celestia)
- [Celestia docs - Supply](https://docs.celestia.org/learn/TIA/staking-governance-supply/)
- [Cryptonomist - TIA token unlock](https://en.cryptonomist.ch/2026/04/01/tia-token-unlock-market/)
- [CoinDCX - Celestia 30x potential](https://coindcx.com/blog/crypto-news-global/can-celestia-be-the-next-30x-crypto-tia-shows-strength/)
- [Bitcoin Foundation - Celestia 2026](https://bitcoinfoundation.org/news/altcoins/celestia-price-prediction-2026-is-tia-the-future-of-modular-blockchains/)
