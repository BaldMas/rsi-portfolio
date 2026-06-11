# Конфликт имён файлов в проекте

## Проблема

`inspect.py` в директории проекта конфликтует со стандартной библиотекой Python `inspect`.
При импорте `traceback` (который импортирует `inspect`) Python берёт локальный файл вместо stdlib.

Симптом:
```
AttributeError: module 'inspect' has no attribute 'signature'
(consider renaming '/home/masus/dropstab/inspect.py')
```

## Решение

Переименовать в `_inspect_dropstab.py` (с нижним подчёркиванием и суффиксом).
Это уже сделано: `inspect.py` -> `_inspect_dropstab.py`.

## Правило

Не называть файлы в проекте именами стандартных Python модулей:
- inspect, json, re, os, sys, io, time, math, random, copy, etc.
