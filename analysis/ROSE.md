# Oasis Network (ROSE) - полный анализ

Дата: 2026-06-09
Источник данных: WebSearch (CoinMarketCap, CoinGecko, Coinbase, Binance, Tokenomist, CryptoRank, ainvest.com, simplystaking.com, themarketsdaily.com, oasis.net)

---

## Позиция в портфеле
| Параметр | Значение |
|---|---|
| Invested | $168 |
| Current value | $40 |
| Unrealized P/L | -75.9% |
| Avg buy price | ~$0.026 |

---

## Базовые рыночные данные (июнь 2026)
| Метрика | Значение |
|---|---|
| Цена | ~$0.00633-0.00653 |
| Market Cap | ~$48.5-50.8M |
| 24h Volume | ~$3.2-5.7M |
| MC rank | ~#300-400 (оценочно) |
| ATH | ~$0.586 (февраль 2022) |
| От ATH | ~-98.9% |
| Circ supply | ~6.5B ROSE |
| Total supply | 10,000M ROSE |
| Circ/FDV | ~65% |
| Следующий анлок | Февраль 2026 (56M ROSE = 0.56%); стейкинг-эмиссия продолжается; ~1.12B ROSE ещё заблокировано |
| OI деривативов | ~$1-3M (минимальный) |
| Биржи | Binance, Gate.io, Bybit, MEXC; Upbit/Bithumb/Coinone делистировали в марте 2025 |

---

## Этап 1. Скрининг F1-F7
| Фильтр | Результат | Комментарий |
|---|---|---|
| F1. Ликвидность | FAIL | 24h vol $3.2-5.7M << $20M порог 30D avg; Korean CEX делистировали в 2025, потеря ликвидности; спред на малых биржах может превышать 0.5% |
| F2. Market Cap | FAIL | MC ~$48.5-50.8M - пограничная зона: ниже $50M = hard fail (базовый порог); даже при $50.8M - ниже $200M консервативного порога |
| F3. Дилюция/анлоки | PASS | Circ/FDV ~65% > 25%; анлок февраль 0.56% - незначительный; предсказуемая стейкинг-эмиссия |
| F4. Тренд HTF | WARNING | -28.1% за 7 дней (июнь 2026); Korean CEX делистинг марта 2025 сломал структуру; ниже 200D MA |
| F5. Нарратив | WARNING | Privacy/AI Confidential Computing нарратив есть; +105% на Privacy AI surge январь 2026; но sector RS vs BTC за 60-90D отрицательный; нарратив отыгран |
| F6. Проект живой | PASS | ROFL mainnet июль 2025; Sapphire EVM активна; GitHub commits есть; нет тишины >60D |
| F7. Красные флаги | PASS | Нет хаков за 12M; Korean delisting - ликвидность проблема, но не хак/фрод; нет регуляторных действий |

**Вердикт скрининга: FAIL.**
Двойной hard fail: F1 (ликвидность <$20M) и F2 (MC ~$48.5M < $50M). Плюс F4+F5 оба WARNING (max 1 допускается). Тройная причина для FAIL.

---

## Этап 2. Скоринг 29 пунктов

### S-тир (вес 50)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 1 | Ликвидность | 0 | 8 | 0 | MC $48.5M; 24h vol $3.2-5.7M << $20M; Korean CEX делистинг разрушил ликвидность; hard fail |
| 3 | Нарратив | 2 | 7 | 14 | Privacy/Confidential AI нарратив есть (ROFL, Sapphire); но +105% в январе уже отыгран; sector RS отрицательный 60-90D |
| 4 | ТА | 0 | 7 | 0 | -28.1% за 7D; -98.9% от ATH; ниже 200D MA; bearish macro; Korean delisting сломал chart |
| 2 | Токеномика | 2 | 7 | 14 | Circ/FDV 65% - хорошо; нет крупных анлоков; но MC $48.5M делает всё несущественным |
| 24 | RS к сектору | 0 | 7 | 0 | Катастрофический underperform: Korean delisting + -28.1% за неделю; нет sector outperformance |
| 13 | Деривативы | 0 | 7 | 0 | OI $1-3M - незначимый; нет институционального интереса к деривативам |
| 16 | Катализаторы | 2 | 7 | 14 | ROFL mainnet (июль 2025) уже запущен; post-quantum prep; Personal AI партнёрство; но рынок не реагирует |
S-тир итого: **42**

### A-тир (вес 28)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 6 | On-chain | 2 | 4 | 8 | Sapphire EVM работает; ROFL для private AI; реальное использование есть, но данные по объёмам невысокие |
| 25 | URPD | 0 | 4 | 0 | При $0.006 vs ATH $0.586 - 100% держателей в убытке; любой отскок = продажа |
| 23 | Value accrual | 1 | 4 | 4 | Стейкинг-вознаграждения; нет burn/buyback; токен не захватывает ценность протокола |
| 26 | Exit liquidity | 1 | 4 | 4 | MC $48.5M; vol $3-5M/день; на позиции $40 выйти можно, но на $1000+ - заметный слиппаж |
| 18 | Концентрация | 2 | 3 | 6 | Backers 23% + Core Contributors 20% = 43%; умеренная концентрация |
| 5 | Фундаментал | 2 | 3 | 6 | Sapphire - первый production EVM с конфиденциальностью; ROFL - реальная инновация; но adoption слабый |
| 21 | Стейблы | 1 | 3 | 3 | Минимальная стейбл-экосистема |
| 27 | Прошлые циклы | 1 | 3 | 3 | ATH $0.586 (2022); два цикла; -98.9%; нет восстановления после Korean delisting |
A-тир итого: **34**

### B-тир (вес 16)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 12 | Макро | 1 | 2 | 2 | Общий рынок под давлением; малая капа = усиленный негатив |
| 15 | Real yield | 1 | 2 | 2 | Стейкинг есть; но реального протокольного yield нет для holders |
| 8 | Конкуренция | 2 | 2 | 4 | Privacy L1 конкуренты: Secret Network, Aztec, Penumbra; ROSE уникален с EVM Sapphire, но adoption не доказан |
| 9 | Безопасность | 3 | 2 | 6 | Нет хаков за 12M; TEE + ZK технология; Korean delisting - compliance, не security |
| 17 | Dev activity | 3 | 2 | 6 | ROFL mainnet запущен; Sapphire активна; post-quantum разработка; GitHub активен |
| 20 | Реакция новости | 1 | 2 | 2 | +105% на Privacy AI surge (январь) уже отыгран; на дальнейший позитив реакции нет |
| 11 | Регуляторика | 2 | 2 | 4 | Privacy token = потенциальный регуляторный риск; Korean delisting как пример compliance pressure |
| 7 | Команда | 3 | 2 | 6 | Dawn Song (основатель) - профессор Berkeley, известная фигура в privacy/security; команда академически сильная |
B-тир итого: **32**

### C-тир (вес 6)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 14 | Корреляции | 1 | 1 | 1 | Высокая корреляция с BTC с усиленным downside |
| 19 | Казна | 2 | 1 | 2 | Foundation Endowment 10%; ресурсы ограничены при MC $48.5M |
| 10 | Соцметрики | 2 | 1 | 2 | Умеренная активность; privacy AI тема поддерживает интерес |
| 22 | Интеграции | 2 | 1 | 2 | Personal AI партнёрство; Sapphire для dApps; ROFL framework |
| 28 | Key person | 3 | 1 | 3 | Dawn Song - академически известна; UC Berkeley профессор |
| 29 | Off-ramp | 2 | 1 | 2 | Binance, Bybit, Gate.io; Korean CEX ушли; ограниченный off-ramp |
C-тир итого: **12**

---

## Этап 3. Итоговый Score
**Score = 42 + 34 + 32 + 12 = 120 / 500**

---

## Решение по позиции
**Для новых денег:** FAIL. Двойной hard fail скрининга (F1, F2) + F4+F5 оба WARNING. Score 120/500 = глубокий Skip. Категорически не добавлять.

**Для существующей позиции:**
| Решение | За | Против |
|---|---|---|
| HOLD | Протокол технически инновационный; ROFL + Sapphire реальные продукты; Dawn Song известна | Двойной hard fail скрининга; MC $48.5M < $50M; F4+F5 оба WARNING; Korean delisting разрушил ликвидность; score 120 |
| ADD | - | Нет аргументов; ловля ножа при критическом провале фильтров |
| CUT | Ротация; ликвидность ещё есть ($40); избежать риска дальнейшего падения MC ниже $30M | Продажа на -98.9% от ATH |

### Рекомендация: CUT
1. Двойной hard fail: F1 (ликвидность $3-5M << $20M) и F2 (MC $48.5M < $50M)
2. F4+F5 оба WARNING = тройная причина для FAIL скрининга
3. Score 120/500 - второй снизу из 6 активов после HFT
4. Korean CEX делистинг (март 2025) - структурная потеря ликвидности без возврата
5. Privacy токены имеют растущий регуляторный риск как asset class (compliance давление)
6. Privacy AI нарратив (+105% январь) отыгран; нет нового катализатора
7. $40 остаток - ротация разумнее удержания; риск дальнейшего снижения MC под $30M = критически низкая ликвидность

### Триггеры на пересмотр (если держать)
- MC устойчиво выше $100M
- Korean CEX re-listing (маловероятно)
- Новый крупный privacy AI catalyst с реальной on-chain adoption

---

## Источники
- [CoinMarketCap ROSE](https://coinmarketcap.com/currencies/oasis-network/)
- [CoinGecko ROSE](https://www.coingecko.com/en/coins/oasis)
- [Binance ROSE](https://www.binance.com/en/price/oasis-network)
- [Tokenomist ROSE](https://tokenomist.ai/oasis-network)
- [Oasis Tokenomics - oasis.net](https://oasis.net/rose-and-tokenomics)
- [Oasis Privacy AI - ainvest](https://www.ainvest.com/news/oasis-rose-gains-relevance-privacy-focused-crypto-ecosystem-2601/)
- [Oasis ROFL + Privacy AI - simplystaking](https://simplystaking.com/oasis-where-privacy-meets-web3-ai)
- [ROSE 24h Volume - themarketsdaily](https://www.themarketsdaily.com/2026/06/05/oasis-network-rose-24-hour-trading-volume-hits-5-67-million.html)
- [CryptoRank ROSE](https://cryptorank.io/price/oasis-network)
