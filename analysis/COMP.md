# Compound (COMP) - полный анализ

Дата: 2026-06-09
Источник данных: WebSearch (CoinMarketCap, CoinGecko, DefiLlama, Tokenomist, Blockchain Magazine, Compound Finance, Messari, Bitget)

---

## Позиция в портфеле
| Параметр | Значение |
|---|---|
| Invested | $500 |
| Current value | $162 |
| Unrealized P/L | -67.7% |
| Avg buy price | ~$51 (расчётный) |

---

## Базовые рыночные данных (июнь 2026)
| Метрика | Значение |
|---|---|
| Цена | ~$17.74 (CMC) / диапазон $16-22 по источникам |
| Market Cap | ~$177M (CMC) / ~$163M по Stock Observer 05.06.2026 |
| 24h Volume | ~$35M |
| MC rank | ~#145 |
| ATH | $911.25 (май 2021) |
| От ATH | -98.1% |
| Circ supply | ~9.97M COMP |
| Total supply | 10.0M COMP |
| Circ/FDV | ~99.8% (полностью разлочен с 2024) |
| Следующий анлок | Нет - schedule завершён в 2024 |
| OI деривативов | Низкий; фьючерсы на Binance/OKX/Bybit; конкретный OI н/д |
| Биржи | Binance, Coinbase, OKX, Bybit, Gate, Binance.US |

TVL (DefiLlama): Compound V3 (Comet) ~$2.7B (апр 2026); V2+V3 combined ~$1.54B. Деплои: Ethereum (~$1.4B), Base, Arbitrum, Polygon, Optimism, Scroll.

---

## Этап 1. Скрининг F1-F7
| Фильтр | Результат | Комментарий |
|---|---|---|
| F1. Ликвидность | PASS | 24h vol ~$35M > $20M; листинг Binance/Coinbase/OKX/Bybit; спред <0.5% на топ-парах |
| F2. Market Cap | FAIL | MC ~$163-177M < $200M (консервативный порог); большинство свежих источников подтверждают < $200M |
| F3. Дилюция/анлоки | PASS | Circ/FDV ~99.8%; unlock schedule завершён в 2024; нет предстоящих анлоков - наилучший возможный результат |
| F4. Тренд HTF | FAIL | 200D MA нисходит с апреля 2026; цена ниже 200D MA; структура LH+LL на 1W; ATL $15.21 в феврале 2026 |
| F5. Нарратив | WARNING | RS к BTC отрицательный; катализатор (fee switch 30% reserves -> stakers) предложен, но не активирован |
| F6. Проект живой | PASS | Comet репо обновлён 29.05.2026; compound-finance.github.io обновлён 03.06.2026; DAO активен |
| F7. Красные флаги | PASS | Хаков core-контрактов нет; website phishing июль 2024 (>12M назад, не контракты); активных исков SEC нет |

**Вердикт скрининга: FAIL.**
F2 FAIL (MC < $200M). F4 FAIL (bear-структура: цена ниже падающего 200D MA, LH+LL на 1W). Два hard fail. Скоринг выполнен для информации по существующей позиции.

---

## Этап 2. Скоринг 29 пунктов

### S-тир (вес 50)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 1 | Ликвидность | 3 | 8 | 24 | $35M/день - на нижней границе; топ-4 биржи; глубина стакана средняя для MC ~$177M |
| 3 | Нарратив | 1 | 7 | 7 | DeFi-лендинг как нарратив есть; но Compound - "вчерашний день"; Aave/Morpho забрали внимание |
| 4 | ТА | 1 | 7 | 7 | Bear-структура: LH+LL на 1W; цена под падающим 200D MA; ATL $15.21 (фев 2026) рядом |
| 2 | Токеномика | 3 | 7 | 21 | Полностью разлочен (+); нет эмиссионного давления (+); нет sink/burn/value accrual (-) |
| 24 | RS к сектору | 1 | 7 | 7 | RS к BTC отрицательный; COMP underperform vs BTC, ETH и DeFi-конкурентов |
| 13 | Деривативы | 2 | 7 | 14 | Фьючерсы на Binance/OKX/Bybit; OI низкий относительно топов; ограниченный интерес |
| 16 | Катализаторы | 2 | 7 | 14 | Fee switch (30% reserves -> stakers) предложен; Treasury Mgmt RFP до 24.06.2026; без on-chain активации - слабые катализаторы |
S-тир итого: **94**

### A-тир (вес 28)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 6 | On-chain | 2 | 4 | 8 | TVL стагнирует/снижается с 2021; borrow APR 2-12%; active users есть, но рост остановлен |
| 25 | URPD | 2 | 4 | 8 | Большой объём держателей с ценой выше текущей (купили дороже); накопление в $15-25 формируется |
| 23 | Value accrual | 1 | 4 | 4 | COMP - чистый governance token без cashflow; fee switch предложен, но не работает |
| 26 | Exit liquidity | 3 | 4 | 12 | $35M/24h позволяет выйти с позицией $500 без удара по цене |
| 18 | Концентрация | 3 | 3 | 9 | Распределённый governance; активные делегаты; но Golden Boys 2024 показал риск концентрации власти |
| 5 | Фундаментал | 3 | 3 | 9 | Работающий протокол; $2.7B TVL Comet; реальный продукт; но рост стагнирует |
| 21 | Стейблы | 4 | 3 | 12 | USDC Comet - основной маркет на Ethereum + 5 L2; прямая интеграция со стейблами как базовый продукт |
| 27 | Прошлые циклы | 2 | 3 | 6 | ATH $911 в 2021; не восстановился в 2024 bull run; AAVE и Morpho опередили; аналоги неблагоприятны |
A-тир итого: **68**

### B-тир (вес 16)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 12 | Макро | 2 | 2 | 4 | DeFi-лендинг чувствителен к ставкам; COMP не отвечает на рост DeFi-сектора |
| 15 | Real yield | 1 | 2 | 2 | COMP-холдер не получает yield на текущий момент; fee switch ещё не live |
| 8 | Конкуренция | 1 | 2 | 2 | Жёсткая: Aave $25B TVL (48% сектора); Morpho $7-10B; Euler v2; Compound теряет долю |
| 9 | Безопасность | 4 | 2 | 8 | Аудиты Trail of Bits/OpenZeppelin/Certora; core-контракты не взламывались |
| 17 | Dev activity | 2 | 2 | 4 | 13 коммитов; ранг 99 по активности; Comet репо обновлён 29.05.2026; скромно |
| 20 | Реакция новости | 1 | 2 | 2 | Новости (новые сети, fee switch обсуждения) практически не двигают цену |
| 11 | Регуляторика | 3 | 2 | 6 | Нет активных исков SEC; благоприятный климат для DeFi в 2025-2026; class action против founders (не токен) |
| 7 | Команда | 3 | 2 | 6 | Compound Labs; Robert Leshner переключился на Superstate; бренд держится на DAO |
B-тир итого: **34**

### C-тир (вес 6)
| # | Пункт | Балл | Вес | × | Обоснование |
|---|---|---|---|---|---|
| 14 | Корреляции | 3 | 1 | 3 | Высокая корреляция с DeFi-сектором и ETH; не диверсифицирует портфель |
| 19 | Казна | 3 | 1 | 3 | DAO treasury существует; RFP на профессиональное управление ($20-25M аллокация) |
| 10 | Соцметрики | 1 | 1 | 1 | Социальный интерес к COMP низкий; забывается комьюнити; аутсайдер новостного фона |
| 22 | Интеграции | 3 | 1 | 3 | Деплои на 6 EVM-сетях; USDC/ETH/USDT маркеты; Chainlink oracles v4 (фев 2026) |
| 28 | Key person | 2 | 1 | 2 | Leshner вышел из активной роли; бренд держится на DAO; нет харизматичного лидера |
| 29 | Off-ramp | 4 | 1 | 4 | Coinbase listing -> прямой fiat off-ramp в США; Binance/Bybit для остального мира |
C-тир итого: **16**

---

## Этап 3. Итоговый Score
**Score = 94 + 68 + 34 + 16 = 212 / 500**

Категория: **Skip** (<300)

---

## Решение по позиции
**Для новых денег:** FAIL (скрининг не пройден). Новый вход не рекомендован.

**Для существующей позиции:**
| Решение | За | Против |
|---|---|---|
| HOLD | ATL $15.21 рядом (снизу ограничен); fee switch может дать краткосрочный импульс | Score 212; скрининг FAIL (F2+F4); Aave/Morpho дадут лучший risk/reward на тот же DeFi-сценарий |
| ADD | н/а - скрининг FAIL | F2 FAIL (MC); F4 FAIL (bear); COMP underperform даже в bull DeFi - не усреднять |
| CUT | Освобождение $162 для ротации в лидеров сектора (AAVE); sunk cost $338 уже зафиксирован | Психологически сложно; текущая цена у ATL |

### Рекомендация: CUT при отскоке к $22-28
1. Score 212/500 - значительно ниже порога Skip (<300); проект объективно не соответствует критериям удержания.
2. F2 FAIL (MC < $200M) и F4 FAIL (bear-структура) - два hard fail; проект не проходит скрининг.
3. AAVE ($25B TVL, value accrual работает, buybacks) и Morpho (рост TVL) дадут лучший risk/reward на DeFi-лендинг сценарий.
4. Тактика: дождаться отскока к $22-28 (тест 200D MA снизу + сопротивление); закрыть 70-100% позиции.
5. Если держать часть как "лотерею fee switch" - не более 20-30% ($30-50); стоп $13.

### Триггеры на пересмотр (для возможного повторного входа позже)
- Fee switch активирован on-chain (30% reserves -> stakers) + TVL Comet возобновляет рост >$3.5B
- MC восстанавливается выше $300M + цена выше 200D MA
- До этих условий - не рассматривать

---

## Источники
- [CoinMarketCap - Compound](https://coinmarketcap.com/currencies/compound/)
- [CoinGecko - Compound](https://www.coingecko.com/en/coins/compound)
- [DefiLlama - Compound V3](https://defillama.com/protocol/compound-v3)
- [DefiLlama - Compound Finance](https://defillama.com/protocol/compound-finance)
- [Tokenomist - Compound](https://tokenomist.ai/compound-governance-token)
- [Blockchain Magazine - COMP 10% rally](https://blockchainmagazine.net/compounds-10-rally-signals-defi-lending-revival-amid-market-reset/)
- [Compound Finance Governance](https://compound.finance/governance/comp)
- [Bitget - DeFi Fee Switch 2026](https://www.bitget.com/news/detail/12560604635816)
- [Messari - Compound](https://messari.io/project/compound)
