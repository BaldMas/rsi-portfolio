# Структура данных портфеля Dropstab

## Мультивалютные поля

ВАЖНО: большинство числовых полей - это словари `{USD, BTC, ETH, BNB, SOL}`, не числа.

```python
# НЕПРАВИЛЬНО:
unrealized = float(p.get("unrealizedProfit", 0))  # TypeError: dict

# ПРАВИЛЬНО:
def usd(field, default=0):
    if field is None:
        return default
    if isinstance(field, dict):
        return float(field.get("USD", default) or default)
    try:
        return float(field)
    except (TypeError, ValueError):
        return default
```

## Поля позиции (portfolios[i])

```
id, name, slug, symbol, rank, image
quantity          - количество монет (float или None)
initialCap        - вложено {USD: ..., BTC: ..., ETH: ..., BNB: ..., SOL: ...}
totalCap          - текущая стоимость (мультивалютный dict)
averageBuyPrice   - средняя цена покупки (мультивалютный dict)
price             - текущая цена (мультивалютный dict)
realizedProfit    - реализованный P/L (мультивалютный dict)
unrealizedProfit  - нереализованный P/L (мультивалютный dict)
unrealizedProfitPercent - % нереализованного P/L (мультивалютный dict)
netChange         - {1H, 1D, 1W, 1M, 3M}
netChangePercent  - {1H, 4H, 12H, 1D, 1W}
totalChange       - мультивалютный dict
change            - {1H, 1D, 1W, 1M, 3M}
share             - доля в портфеле (мультивалютный dict)
transactions      - список сделок []
x                 - иксы от покупки (мультивалютный dict)
xfromIco          - иксы от ICO (мультивалютный dict)
icoPrice          - цена ICO (мультивалютный dict)
priceRange        - {from, to}
marketCap         - рыночная капа (мультивалютный dict)
volume            - объём {1H, 1D, 1W, 1M, 3M}
tags              - список тегов
category          - категория
groupId           - ID группы портфеля
```

## Поля portfolioTotal

```
initialCap   - общая сумма вложений (мультивалютный dict)
totalCap     - текущая стоимость портфеля (мультивалютный dict)
```

## Определение активных/закрытых позиций

Позиция считается закрытой если `quantity == 0`. 
Но `quantity` может быть None если она вообще не заполнена - проверять через `or 0`.
