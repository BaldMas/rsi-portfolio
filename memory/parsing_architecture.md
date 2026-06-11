# Архитектура парсинга Dropstab

## Основной метод: __NEXT_DATA__

Dropstab - Next.js приложение. Данные вшиты в HTML страницы в теге:
```html
<script id="__NEXT_DATA__" type="application/json">{...}</script>
```

Это работает без браузера, Selenium, Playwright - чистый urllib.request.

### Код извлечения:
```python
import re, json, urllib.request

def fetch_page(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8")

def extract_next_data(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not m:
        raise ValueError("__NEXT_DATA__ not found")
    return json.loads(m.group(1))
```

## Путь к данным портфеля (публичная страница)

URL формат: `https://dropstab.com/p/<slug>`

```
data["props"]["pageProps"]["fallbackBody"]
  ├── name           - название портфеля
  ├── portfolioTotal - сводные цифры
  │     ├── initialCap  - вложено (dict по валютам)
  │     └── totalCap    - текущая стоимость (dict по валютам)
  └── portfolios     - список позиций (см. data_structure.md)
```

## Ограничения

- Работает только для публичных страниц (портфели с shareToken или публичные ссылки /p/...)
- Данные реального времени - при каждом запросе актуальные
- Нет пагинации - всё в одном __NEXT_DATA__
- User-Agent должен быть реалистичным (Mozilla/5.0 достаточно)

## Рабочий скрипт

`/home/masus/dropstab/parse_portfolio.py` - полный парсер с выводом и сохранением снимка.
