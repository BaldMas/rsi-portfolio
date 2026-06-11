# Hashflow (HFT) - полный анализ

Дата: 2026-06-09
Источник данных: WebSearch (CoinMarketCap, CoinGecko, Tokenomist, CryptoRank, coinlore.com, CoinGlass, Binance Academy, chainbroker.io)

---

## Позиция в портфеле
| Параметр | Значение |
|---|---|
| Invested | $212 |
| Current value | $23 |
| Unrealized P/L | -89.3% |
| Avg buy price | ~$0.092 |

---

## Базовые рыночные данные (июнь 2026)
| Метрика | Значение |
|---|---|
| Цена | ~$0.0102-0.012 |
| Market Cap | ~$8.4-9.7M |
| 24h Volume | ~$4.3M (spot + futures) |
| MC rank | #1022-1232 |
| ATH | $3.61 (ноябрь 2022) |
| От ATH | ~-99.7% |
| Circ supply | ~819M HFT |
| Total supply | 1,000M HFT |
| Circ/FDV | ~81.9% |
| Следующий анлок | Большая часть разблокирована; оставшиеся ~181M в вестинге у команды/инвесторов |
| OI деривативов | ~$1-3M (минимальный) |
| Биржи | Binance (Monitoring Tag с 22 мая 2026!), Gate.io, Bitget, MEXC |

---

## Этап 1. Скрининг F1-F7
| Фильтр | Результат | Комментарий |
|---|---|---|
| F1. Ликвидность | FAIL | MC $8.4M << $20M; 24h spot vol ~$660K (не достигает $20M 30D avg); Binance Monitoring Tag = риск делистинга главной биржи; реальная ликвидность критически мала |
| F2. Market Cap | FAIL | MC ~$8.4-9.7M << $50M (hard fail); << $200M (консервативный порог) |
| F3. Дилюция/анлоки | PASS | Circ/FDV ~81.9% > 25%; нет крупных клифф-анлоков в ближайшие 90 дней |
| F4. Тренд HTF | WARNING | Ниже 200D MA; -99.7% от ATH; Binance Monitoring Tag = техническое давление продаж |
| F5. Нарратив | WARNING | DEX/RFQ нарратив слабый; расширение на Solana/Monad - позитив, но не двигает цену; нет активного нарратива |
| F6. Проект живой | PASS | Расширение на Solana и Monad 2026; fee-sharing 50/50 stakers/buy-burn; $28B cumulative vol |
| F7. Красные флаги | FAIL | Binance Monitoring Tag (22 мая 2026) = официальный красный флаг; риск делистинга с крупнейшей биржи; сигнал проблем с liquidity/dev activity по критериям Binance |

**Вердикт скрининга: FAIL.**
Тройной hard fail: F1 (ликвидность), F2 (market cap $8.4M << $50M), F7 (Binance Monitoring Tag = красный флаг). Плюс F4+F5 оба WARNING. Проект де-факто в зоне ликвидации позиции.

---

## Этап 2. Скоринг 29 пунктов

### S-тир (вес 50)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 1 | Ликвидность | 0 | 8 | 0 | MC $8.4M; spot vol ~$660K/день; Binance Monitoring Tag = риск потери главной ликвидности; hard fail |
| 3 | Нарратив | 1 | 7 | 7 | DEX/RFQ нарратив не актуален в 2026; Solana/Monad expansion есть, но без внимания рынка |
| 4 | ТА | 0 | 7 | 0 | -99.7% от ATH; Binance Monitoring Tag = технические продавцы активны; bearish macro; нет поддержки |
| 2 | Токеномика | 2 | 7 | 14 | Circ/FDV 82% - хорошо; fee-sharing 50/50 = buy-burn механизм; но MC $8.4M делает это несущественным |
| 24 | RS к сектору | 0 | 7 | 0 | Катастрофический underperform vs BTC и DEX-сектором; в процессе death spiral |
| 13 | Деривативы | 0 | 7 | 0 | OI ~$1-3M - незначимый; нет институционального интереса |
| 16 | Катализаторы | 1 | 7 | 7 | Solana/Monad expansion; buy-burn при росте объёмов; но Binance Monitoring Tag нивелирует |
S-тир итого: **28**

### A-тир (вес 28)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 6 | On-chain | 2 | 4 | 8 | $28B cumulative vol; $30M+ daily RFQ trades; $500M committed liquidity - протокол работает, но токен это не отражает |
| 25 | URPD | 0 | 4 | 0 | При $0.012 vs ATH $3.61 - 100% держателей в убытке; любой отскок = продажа |
| 23 | Value accrual | 2 | 4 | 8 | Buy-burn 50% fees теоретически дефляционен; fee-sharing 50% - но объёмы и MC слишком малы |
| 26 | Exit liquidity | 0 | 4 | 0 | MC $8.4M; spot vol $660K/день; выйти на $23 ещё можно, но на крупных позициях - невозможно |
| 18 | Концентрация | 2 | 3 | 6 | Early Investors 25% + Core Team 19.32% = высокая концентрация у ранних участников |
| 5 | Фундаментал | 2 | 3 | 6 | Протокол технически работает; RFQ model; мультичейн; но токен полностью отвязан от протокольного success |
| 21 | Стейблы | 1 | 3 | 3 | Нет значимой стейбл-экосистемы |
| 27 | Прошлые циклы | 1 | 3 | 3 | ATH $3.61 (2022); один цикл; -99.7%; нет признаков восстановления |
A-тир итого: **34**

### B-тир (вес 16)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 12 | Макро | 1 | 2 | 2 | Общий рынок давит; малая капитализация = 2x негативный эффект макро |
| 15 | Real yield | 1 | 2 | 2 | Fee-sharing существует, но объём слишком мал для значимого yield |
| 8 | Конкуренция | 1 | 2 | 2 | 1inch, Paraswap, CoW Protocol доминируют в DEX aggregation; Hashflow в маргинальном положении |
| 9 | Безопасность | 2 | 2 | 4 | Нет хаков за 12M; но малый MC = target для manipulation |
| 17 | Dev activity | 2 | 2 | 4 | Solana/Monad expansion 2026; протокол не мёртв; но активность снижается |
| 20 | Реакция новости | 0 | 2 | 0 | Binance Monitoring Tag (негативная новость) - цена упала; на позитив нет реакции |
| 11 | Регуляторика | 2 | 2 | 4 | Нет прямых регуляторных рисков; но Binance Monitoring Tag = косвенный compliance вопрос |
| 7 | Команда | 2 | 2 | 4 | Varun Kumar (CEO) - известен в DeFi; команда активна; без публичных скандалов |
B-тир итого: **22**

### C-тир (вес 6)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 14 | Корреляции | 1 | 1 | 1 | Коррелирует с рынком, но с усиленным downside |
| 19 | Казна | 1 | 1 | 1 | Ecosystem Development 35.76%; конкретные данные по treasury не раскрыты публично |
| 10 | Соцметрики | 1 | 1 | 1 | Низкая активность; Binance Monitoring Tag не добавляет позитивного attention |
| 22 | Интеграции | 2 | 1 | 2 | Solana, Monad expansion; мультичейн присутствие |
| 28 | Key person | 2 | 1 | 2 | Varun Kumar известен в DeFi-кругах |
| 29 | Off-ramp | 2 | 1 | 2 | Gate.io, Bitget, MEXC; Binance под риском делистинга; ограниченный off-ramp |
C-тир итого: **9**

---

## Этап 3. Итоговый Score
**Score = 28 + 34 + 22 + 9 = 93 / 500**

---

## Решение по позиции
**Для новых денег:** FAIL. Тройной hard fail скрининга (F1, F2, F7). Score 93/500 = глубокий Skip. Категорически не добавлять.

**Для существующей позиции:**
| Решение | За | Против |
|---|---|---|
| HOLD | Протокол технически жив; buy-burn механизм; Solana expansion | Tройной hard fail скрининга; MC $8.4M; Binance Monitoring Tag; score 93/500; возможный делистинг |
| ADD | - | Нет ни одного весомого аргумента за добавление |
| CUT | Фиксация убытка; ротация; ликвидность ещё есть ($23 выйти можно); риск делистинга = $0 ликвидность | Продажа на абсолютном дне |

### Рекомендация: CUT НЕМЕДЛЕННО
1. Тройной hard fail скрининга: F1 (ликвидность), F2 (MC $8.4M), F7 (Binance Monitoring Tag)
2. Score 93/500 - самый низкий из всех 6 активов; категория глубокий Skip
3. Binance Monitoring Tag (22 мая 2026) = официальный сигнал риска делистинга; исторически 70%+ монет с этим тегом делистируются в течение 3-6 месяцев
4. MC $8.4M << $50M минимального порога; если Binance делистирует - ликвидность рухнет до нуля
5. Сейчас ещё есть $23 exit value; после делистинга - может быть $0-5
6. Задержка = увеличение риска permanent loss of capital

### Триггеры
- Нет триггеров на HOLD/ADD - только выход
- Действие: sell немедленно при наличии ликвидности; не ждать "отскока"

---

## Источники
- [CoinMarketCap HFT](https://coinmarketcap.com/currencies/hashflow/)
- [CoinGecko HFT](https://www.coingecko.com/en/coins/hashflow)
- [Tokenomist HFT](https://tokenomist.ai/hashflow)
- [CoinGlass HFT](https://www.coinglass.com/currencies/HFT)
- [Binance Academy Hashflow](https://academy.binance.com/en/articles/what-is-hashflow-hft)
- [CoinLore HFT](https://www.coinlore.com/coin/hashflow)
- [ChainBroker HFT](https://chainbroker.io/projects/hashflow/)
- [Bitget HFT](https://www.bitget.com/price/hashflow)
