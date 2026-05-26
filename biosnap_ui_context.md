# BioSnap — состояние UI на 26.05.2026

## Среда
- Windows 7 64-bit
- QGIS 3.28.4 Firenze
- Python 3.9
- Репозиторий: C:/dev/biosnap-qgis
- Плагин: C:/Users/ACRIDIUM/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/biosnap

## Правила работы
- Файлы писать ТОЛЬКО целиком через консоль QGIS
- Проверять compile() перед копированием
- PowerShell обрезает длинные строки — не использовать
- Копировать через PowerShell Copy-Item

## Что готово
- ui/styles.py — палитра и QSS
- ui/main_window.py — Basic окно полностью

## Basic окно — все блоки готовы
- Шапка BioSnap (красная B + ioSnap + subtitle)
- Mode Single/Batch (чипы)
- Строка поиска: ранг QMenu + поле + история QMenu + лупа
- Territory: Choose layer / Draw manually / Map extent (иконки QGIS)
- Source: GBIF / iNaturalist / Both
- Year range + Accuracy
- Toggles: Has coordinates, Has taxonomy, Has media, Fossils only, No duplicates
- Preview панель (map + Records/Species/Families)
- Advanced settings кнопка
- Output layer поле
- Format chips: GeoPackage/Shapefile/CSV/Memory
- Run BioSnap кнопка

## Следующие шаги
1. Подключить biosnap.py — открытие по кнопке в QGIS
2. Advanced диалог (вкладки APIs/Sources/Lists/About)
3. Реальный поиск таксонов через GBIF API
4. История поиска — сохранение в QgsSettings

## Палитра
- brand_red: #D21C1C
- header_bg: #1A1A22
- window_bg: #F6F5F3
- gbif_green: #2D7D1F
- inat_teal: #0D9488
- coin_gold: #EAB308
