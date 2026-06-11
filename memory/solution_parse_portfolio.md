# Solution: парсинг портфеля dropstab

## Задача
Вытащить все активы портфеля со страницы `https://dropstab.com/p/po-moim-myslam-fjkjsebo6f` без браузера.

## Решение
Прямой запрос к внутреннему API `_gateway`:

```
GET https://dropstab.com/_gateway/api/portfolio/api/portfolioGroup/individualShare/{share_token}
Headers: Referer: https://dropstab.com/, Origin: https://dropstab.com/
```

- `share_token` - последняя часть URL после финального дефиса: `po-moim-myslam-fjkjsebo6f` -> `fjkjsebo6f`
- Ответ содержит `portfolios[]` (все позиции, 48 шт), `portfolioTotal` (сводные цифры)
- Не нужны куки, авторизация или браузер

## Как нашли
1. `__NEXT_DATA__` на странице содержит только 1 запись (SSR fallback частичный)
2. В JS бандле `/_next/static/chunks/pages/_app-203f912d500de44e.js` найден базовый URL: `https://dropstab.com/_gateway/api`
3. Там же найден эндпоинт: `/portfolio/api/portfolioGroup/individualShare/:token`

## Файлы
- `/home/masus/dropstab/parse_portfolio.py` - финальный скрипт
- Сохраняет снимок в `/home/masus/crypto_analysis/_portfolio_summary.md`
