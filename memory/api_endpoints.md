# API эндпоинты Dropstab

## Что исследовалось (find_api*.py, find_bff*.py)

### Next.js API routes (/portfolio/api/...)
Все возвращают 401 или 403 без авторизации:
- `/portfolio/api/portfolioGroup/currencies`
- `/portfolio/api/portfolioGroup/totalPortfolio/holdings`
- `/portfolio/api/portfolioGroup/totalPortfolio`
- `/portfolio/api/portfolioGroup/individualShare/{shareToken}`
- `/portfolio/api/portfolioGroup/{groupId}`

Заголовки пробовались: User-Agent, Referer, Origin, X-Requested-With - не помогают.

### BFF (Backend For Frontend) 
Искались в JS бандлах Next.js (`/_next/static/chunks/pages/_app-*.js`).
Модуль 54930 содержит конфигурацию API - требует изучения актуального бандла.

### Публичный __NEXT_DATA__ (РАБОТАЕТ)
Единственный надёжный путь без авторизации - данные в HTML через __NEXT_DATA__.
Подробнее: [[parsing_architecture]]

## Структура авторизации (из кода)

- `shareToken` - токен доступа к общему портфелю (из URL /p/<slug>)
- `groupId` - числовой ID группы портфелей
- Для авторизованных запросов нужны cookies сессии

## Итог

Для неавторизованного доступа к публичным портфелям - только __NEXT_DATA__.
REST API без сессионных cookies недоступен.
