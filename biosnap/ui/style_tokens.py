# -*- coding: utf-8 -*-
"""
BioSnap — централизованные токены дизайн-системы.
Единственный источник правды для цветов, шрифтов и отступов.
Версия 1.0 | 2026-05-27
"""

# ─────────────────────────────────────────────
#  ЦВЕТА
# ─────────────────────────────────────────────

# Зелёный (PRIMARY — Run, active toggles, GBIF, sliders)
GREEN_900 = "#1B5E20"   # pressed / dark accent
GREEN_700 = "#2E7D32"   # PRIMARY: Run BioSnap, active toggles, GBIF selected
GREEN_600 = "#388E3C"   # hover для primary-кнопок
GREEN_500 = "#4CAF50"   # GBIF brand, active track слайдеров
GREEN_200 = "#A5D6A7"   # border thumb слайдера
GREEN_100 = "#C8E6C9"   # selected bg (radio-группы)
GREEN_050 = "#F1F8E9"   # фон блока статистики

# Синий (INFORMATIONAL / NAVIGATION — Territory, iNat nav)
BLUE_800  = "#1565C0"   # иконки Territory, активный таб, навигация
BLUE_600  = "#1E88E5"   # hover синих элементов
BLUE_500  = "#2196F3"   # iNaturalist navigation
BLUE_100  = "#BBDEFB"   # hover bg Territory-кнопок
BLUE_050  = "#E3F2FD"   # фон информационных блоков, iNat selected bg

# Фиолетовый (SECONDARY / ADVANCED — Advanced settings)
PURPLE_800 = "#6A1B9A"  # заголовок Advanced, иконки
PURPLE_400 = "#AB47BC"  # hover для purple-элементов
PURPLE_100 = "#E1BEE7"  # hover bg
PURPLE_050 = "#F3E5F5"  # фон раскрытого Advanced блока

# Нейтральные
SURFACE        = "#FFFFFF"   # карточки, поля ввода
BACKGROUND     = "#F0F0F0"   # фон окна (системный QGIS)
BORDER         = "#D6D9D6"   # рамки элементов
BORDER_INPUT   = "#C8C8C8"   # рамки input-полей
BORDER_FOCUS   = "#2E7D32"   # рамка при фокусе
DIVIDER        = "#E8EAE8"   # разделители между секциями

# Текст
TEXT_PRIMARY     = "#1C2B1C"  # основной текст
TEXT_SECONDARY   = "#5C6B5C"  # лейблы секций, подсказки
TEXT_DISABLED    = "#9E9E9E"  # disabled-состояния
TEXT_PLACEHOLDER = "#AAAAAA"  # placeholder в полях
TEXT_ON_DARK     = "#FFFFFF"  # на тёмном фоне
TEXT_ON_PRIMARY  = "#FFFFFF"  # на primary-кнопках

# Семантические
COLOR_SUCCESS = "#2E7D32"   # = GREEN_700
COLOR_WARNING = "#F57F17"   # предупреждения
COLOR_ERROR   = "#C62828"   # ошибки
COLOR_INFO    = "#1565C0"   # = BLUE_800

# Бренды источников (ТОЛЬКО для иконок/бейджей)
BRAND_GBIF  = "#4CAF50"   # = GREEN_500
BRAND_INAT  = "#1BA798"   # оригинальный teal iNaturalist

# ─────────────────────────────────────────────
#  РАДИУСЫ
# ─────────────────────────────────────────────
RADIUS_XS   = 3   # мелкие элементы, badges
RADIUS_SM   = 4   # поля ввода, тогглы
RADIUS_MD   = 6   # кнопки, карточки (основной)
RADIUS_LG   = 8   # контейнеры
RADIUS_PILL = 20  # ТОЛЬКО Mode switcher

# ─────────────────────────────────────────────
#  ОТСТУПЫ (шаг 4px)
# ─────────────────────────────────────────────
SPACE_1 = 4
SPACE_2 = 8
SPACE_3 = 12
SPACE_4 = 16
SPACE_5 = 20
SPACE_6 = 24

WINDOW_PADDING   = 12
SECTION_GAP      = 12
SECTION_INNER_GAP = 8

# ─────────────────────────────────────────────
#  РАЗМЕРЫ КОМПОНЕНТОВ
# ─────────────────────────────────────────────
TOGGLE_W         = 34   # ширина трека тоггла
TOGGLE_H         = 20   # высота трека тоггла
TOGGLE_THUMB     = 14   # диаметр кружка
TOGGLE_TAP_W     = 44   # минимальная tap-зона (ширина)
TOGGLE_TAP_H     = 44   # минимальная tap-зона (высота)

RUN_BUTTON_H     = 44   # высота Run BioSnap
CHIP_H           = 28   # высота Mode-чипов
CHIP_W           = 80   # ширина Mode-чипов


# ─────────────────────────────────────────────
#  QSS — БАЗОВЫЕ СТИЛИ
# ─────────────────────────────────────────────

def get_base_stylesheet():
    """
    Возвращает QSS-строку с базовыми стилями всего плагина.
    Подключается один раз в BioSnapDialog.__init__:
        from ui.style_tokens import get_base_stylesheet
        self.setStyleSheet(get_base_stylesheet())
    """
    return f"""
/* ── Фон окна ───────────────────────────────── */
QDialog, QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "Inter", system-ui, sans-serif;
    font-size: 12px;
}}

/* ── PRIMARY-кнопка (Run BioSnap) ───────────── */
QPushButton[class="primary"] {{
    background-color: {GREEN_700};
    color: {TEXT_ON_PRIMARY};
    border: none;
    border-radius: {RADIUS_MD}px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    min-height: {RUN_BUTTON_H}px;
}}
QPushButton[class="primary"]:hover {{
    background-color: {GREEN_600};
}}
QPushButton[class="primary"]:pressed {{
    background-color: {GREEN_900};
}}
QPushButton[class="primary"]:disabled {{
    background-color: {BORDER};
    color: {TEXT_DISABLED};
}}

/* ── SECONDARY-кнопка ───────────────────────── */
QPushButton[class="secondary"] {{
    background-color: {SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD}px;
    padding: 6px 12px;
    font-size: 12px;
}}
QPushButton[class="secondary"]:hover {{
    background-color: {GREEN_100};
    border: 1px solid {GREEN_700};
}}
QPushButton[class="secondary"]:pressed {{
    background-color: {GREEN_100};
    border: 2px solid {GREEN_700};
}}
QPushButton[class="secondary"]:disabled {{
    background-color: {BACKGROUND};
    color: {TEXT_DISABLED};
    border-color: {BORDER};
}}

/* ── RADIO-чип: неактивный (Mode/Source/Format/Territory) */
QPushButton[class="chip"] {{
    background-color: {SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD}px;
    padding: 4px 10px;
    font-size: 12px;
}}
QPushButton[class="chip"]:hover {{
    background-color: rgba(46, 125, 50, 0.06);
    border: 1px solid {GREEN_200};
}}

/* ── RADIO-чип: активный ────────────────────── */
QPushButton[class="chip-active"] {{
    background-color: {GREEN_100};
    color: {GREEN_700};
    border: 2px solid {GREEN_700};
    border-radius: {RADIUS_MD}px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
}}

/* ── Mode-чип (pill) ────────────────────────── */
QPushButton[class="mode-chip"] {{
    background-color: {SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_PILL}px;
    min-width: {CHIP_W}px;
    max-width: {CHIP_W}px;
    min-height: {CHIP_H}px;
    max-height: {CHIP_H}px;
    font-size: 12px;
}}
QPushButton[class="mode-chip"]:hover {{
    background-color: rgba(46, 125, 50, 0.06);
    border-color: {GREEN_200};
}}
QPushButton[class="mode-chip-active"] {{
    background-color: {GREEN_100};
    color: {GREEN_700};
    border: 2px solid {GREEN_700};
    border-radius: {RADIUS_PILL}px;
    min-width: {CHIP_W}px;
    max-width: {CHIP_W}px;
    min-height: {CHIP_H}px;
    max-height: {CHIP_H}px;
    font-size: 12px;
    font-weight: 600;
}}

/* ── Input-поля ─────────────────────────────── */
QLineEdit {{
    background-color: {SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_INPUT};
    border-radius: {RADIUS_SM}px;
    padding: 5px 8px;
    font-size: 12px;
    selection-background-color: {GREEN_100};
}}
QLineEdit:focus {{
    border: 2px solid {BORDER_FOCUS};
    background-color: {SURFACE};
}}
QLineEdit:disabled {{
    background-color: {BACKGROUND};
    color: {TEXT_DISABLED};
    border-color: {BORDER};
}}
QLineEdit[class="error"] {{
    border: 2px solid {COLOR_ERROR};
    color: {TEXT_PRIMARY};
}}

/* ── Лейблы секций (UPPERCASE, small) ───────── */
QLabel[class="section-label"] {{
    color: {TEXT_SECONDARY};
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.06em;
}}

/* ── Read-only статистика ───────────────────── */
QLabel[class="stat-value"] {{
    color: {TEXT_PRIMARY};
    font-size: 16px;
    font-weight: 600;
    background-color: transparent;
}}
QLabel[class="stat-placeholder"] {{
    color: {TEXT_DISABLED};
    font-size: 16px;
    font-weight: 600;
    background-color: transparent;
}}
QLabel[class="stat-label"] {{
    color: {TEXT_SECONDARY};
    font-size: 11px;
    background-color: transparent;
}}

/* ── Предупреждение inline ──────────────────── */
QLabel[class="warning-inline"] {{
    color: {COLOR_WARNING};
    font-size: 11px;
}}
QLabel[class="error-inline"] {{
    color: {COLOR_ERROR};
    font-size: 11px;
}}

/* ── QMenu ──────────────────────────────────── */
QMenu {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD}px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 12px;
    border-radius: {RADIUS_SM}px;
    color: {TEXT_PRIMARY};
}}
QMenu::item:selected {{
    background-color: {GREEN_100};
    color: {GREEN_700};
}}

/* ── Разделители ────────────────────────────── */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {{
    color: {DIVIDER};
    border: none;
    background-color: {DIVIDER};
    max-height: 1px;
}}
"""


# ─────────────────────────────────────────────
#  QSS — СПЕЦИФИЧНЫЕ БЛОКИ (применяются точечно)
# ─────────────────────────────────────────────

def get_stats_block_style():
    """QSS для QFrame блока Records/Species/Families."""
    return f"""
    QFrame {{
        background-color: {GREEN_050};
        border: 1px solid {GREEN_100};
        border-radius: {RADIUS_LG}px;
        padding: {SPACE_3}px;
    }}
    """

def get_advanced_header_style():
    """QSS для QPushButton-заголовка Advanced settings."""
    return f"""
    QPushButton {{
        color: {PURPLE_800};
        background-color: transparent;
        border: none;
        text-align: left;
        font-size: 12px;
        font-weight: 500;
        padding: 6px 4px;
    }}
    QPushButton:hover {{
        color: {PURPLE_400};
    }}
    """

def get_advanced_body_style():
    """QSS для QFrame раскрытого Advanced settings."""
    return f"""
    QFrame {{
        background-color: {PURPLE_050};
        border-left: 3px solid {PURPLE_800};
        border-top: none;
        border-right: none;
        border-bottom: none;
        padding: {SPACE_2}px {SPACE_3}px;
    }}
    """

def get_territory_button_style(active=False):
    """QSS для кнопок Territory (Choose layer / Draw manually / Map extent)."""
    if active:
        return f"""
        QPushButton {{
            background-color: {BLUE_050};
            color: {BLUE_800};
            border: 2px solid {BLUE_800};
            border-radius: {RADIUS_MD}px;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: 600;
        }}
        """
    return f"""
    QPushButton {{
        background-color: {SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_MD}px;
        padding: 6px 10px;
        font-size: 12px;
    }}
    QPushButton:hover {{
        background-color: {BLUE_100};
        border-color: {BLUE_800};
        color: {BLUE_800};
    }}
    """

def get_source_chip_style(source=None, active=False):
    """
    QSS для чипов Source (GBIF / iNaturalist / Both).
    source: 'gbif' | 'inat' | 'both' | None
    """
    if not active:
        return f"""
        QPushButton {{
            background-color: {SURFACE};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            border-radius: {RADIUS_MD}px;
            padding: 5px 12px;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background-color: rgba(46, 125, 50, 0.06);
            border-color: {GREEN_200};
        }}
        """
    if source == 'gbif':
        return f"""
        QPushButton {{
            background-color: {GREEN_100};
            color: {GREEN_700};
            border: 2px solid {GREEN_700};
            border-radius: {RADIUS_MD}px;
            padding: 5px 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        """
    if source == 'inat':
        return f"""
        QPushButton {{
            background-color: {BLUE_050};
            color: {BLUE_800};
            border: 2px solid {BLUE_800};
            border-radius: {RADIUS_MD}px;
            padding: 5px 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        """
    # both
    return f"""
    QPushButton {{
        background-color: {BACKGROUND};
        color: {TEXT_PRIMARY};
        border: 2px solid {TEXT_PRIMARY};
        border-radius: {RADIUS_MD}px;
        padding: 5px 12px;
        font-size: 12px;
        font-weight: 600;
    }}
    """
