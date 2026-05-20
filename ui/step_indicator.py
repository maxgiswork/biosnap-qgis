# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtCore import Qt, QRect, QPoint
from qgis.PyQt.QtGui import (QPainter, QColor, QPen, QFont,
                              QPixmap, QFontMetrics)
from core.i18n import tr

CIRCLE_D  = 36    # діаметр кружка px
LINE_H    = 3     # товщина лінії
LABEL_H   = 18    # висота підпису
V_PAD     = 8     # відступ зверху
TOTAL_H   = V_PAD + CIRCLE_D + 6 + LABEL_H + V_PAD

COLOR_DONE    = QColor("#4CAF50")
COLOR_ACTIVE  = QColor("#2196F3")
COLOR_PENDING = QColor("#9E9E9E")
COLOR_LINE_ON = QColor("#4CAF50")
COLOR_LINE_OFF= QColor("#BDBDBD")
COLOR_WHITE   = QColor("#FFFFFF")
COLOR_LABEL   = QColor("#212121")
COLOR_LABEL_OFF = QColor("#9E9E9E")

STEP_KEYS = [
    "step1_name",
    "step2_name",
    "step3_name",
    "step4_name",
    "step5_name",
]


class StepIndicator(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._total   = 5
        self._current = 0       # 0-based
        self._done    = set()
        self._icons   = [None] * self._total
        self.setMinimumHeight(TOTAL_H)
        self.setMaximumHeight(TOTAL_H)
        self._load_icons()

    # ── public API ────────────────────────────────────────────

    def set_step(self, index: int):
        self._current = index
        self.update()

    def set_step_completed(self, index: int):
        self._done.add(index)
        self.update()

    def retranslate_ui(self):
        self.update()

    # ── icons ─────────────────────────────────────────────────

    def _load_icons(self):
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        for i in range(self._total):
            path = os.path.join(plugin_dir, "icons", "steps",
                                f"step{i+1}.png")
            if os.path.exists(path):
                px = QPixmap(path)
                if not px.isNull():
                    self._icons[i] = px.scaled(
                        24, 24,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )

    # ── painting ──────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        n   = self._total
        w   = self.width()
        r   = CIRCLE_D // 2

        # Центри кружків по X
        step_w = (w - 2 * 24) / (n - 1)
        cx = [int(24 + i * step_w) for i in range(n)]
        cy = V_PAD + r

        # ── лінії між кружками ───────────────────────────────
        for i in range(n - 1):
            x1 = cx[i] + r
            x2 = cx[i+1] - r
            y  = cy
            done = (i in self._done and i+1 in self._done) or \
                   (i in self._done and i+1 == self._current) or \
                   (i < self._current)
            color = COLOR_LINE_ON if done else COLOR_LINE_OFF
            painter.setPen(QPen(color, LINE_H))
            painter.drawLine(x1, y, x2, y)

        # ── кружки ───────────────────────────────────────────
        for i in range(n):
            if i in self._done:
                color = COLOR_DONE
            elif i == self._current:
                color = COLOR_ACTIVE
            else:
                color = COLOR_PENDING

            # кружок
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(
                QPoint(cx[i], cy), r, r
            )

            # іконка або цифра
            icon = self._icons[i]
            if icon:
                ix = cx[i] - 12
                iy = cy - 12
                painter.drawPixmap(ix, iy, icon)
            else:
                # заглушка — цифра
                font = QFont("Arial", 11, QFont.Bold)
                painter.setFont(font)
                painter.setPen(QPen(COLOR_WHITE))
                painter.drawText(
                    QRect(cx[i]-r, cy-r, CIRCLE_D, CIRCLE_D),
                    Qt.AlignCenter,
                    str(i + 1)
                )

        # ── підписи ───────────────────────────────────────────
        font = QFont("Arial", 8)
        painter.setFont(font)
        fm = QFontMetrics(font)

        for i in range(n):
            label = tr(STEP_KEYS[i])
            lw    = fm.width(label)
            lx    = cx[i] - lw // 2
            ly    = cy + r + 6

            if i == self._current or i in self._done:
                painter.setPen(QPen(COLOR_LABEL))
            else:
                painter.setPen(QPen(COLOR_LABEL_OFF))

            painter.drawText(lx, ly + fm.ascent(), label)

        painter.end()