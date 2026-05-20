# -*- coding: utf-8 -*-
import os
import sys
plugin_dir = os.path.dirname(os.path.dirname(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)
from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtCore import Qt, QRect, QPoint
from qgis.PyQt.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QFontMetrics
from core.i18n import tr
CIRCLE_D = 36
LINE_H = 3
LABEL_H = 18
V_PAD = 8
TOTAL_H = V_PAD + CIRCLE_D + 6 + LABEL_H + V_PAD
COLOR_DONE = QColor("#4CAF50")
COLOR_ACTIVE = QColor("#2196F3")
COLOR_PENDING = QColor("#9E9E9E")
COLOR_LINE_ON = QColor("#4CAF50")
COLOR_LINE_OFF = QColor("#BDBDBD")
COLOR_WHITE = QColor("#FFFFFF")
COLOR_LABEL = QColor("#212121")
COLOR_LABEL_OFF = QColor("#9E9E9E")
STEP_KEYS = ["step1_name","step2_name","step3_name","step4_name","step5_name"]
class StepIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._total = 5
        self._current = 0
        self._icons = [None] * self._total
        self.setMinimumHeight(TOTAL_H)
        self.setMaximumHeight(TOTAL_H)
        self._load_icons()
    def set_current(self, index):
        self._current = index
        self.update()
    def retranslate_ui(self):
        self.update()
    def _load_icons(self):
        base = os.path.dirname(os.path.dirname(__file__))
        for i in range(self._total):
            path = os.path.join(base, "icons", "steps", "step{0}.png".format(i+1))
            if os.path.exists(path):
                px = QPixmap(path)
                if not px.isNull():
                    self._icons[i] = px.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        n = self._total
        w = self.width()
        r = CIRCLE_D // 2
        margin = 40
        step_w = (w - 2 * margin) / (n - 1)
        cx = [int(margin + i * step_w) for i in range(n)]
        cy = V_PAD + r
        for i in range(n - 1):
            done = i < self._current
            color = COLOR_LINE_ON if done else COLOR_LINE_OFF
            painter.setPen(QPen(color, LINE_H))
            painter.drawLine(cx[i] + r, cy, cx[i+1] - r, cy)
        for i in range(n):
            if i < self._current:
                color = COLOR_DONE
            elif i == self._current:
                color = COLOR_ACTIVE
            else:
                color = COLOR_PENDING
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(QPoint(cx[i], cy), r, r)
            icon = self._icons[i]
            if icon:
                painter.drawPixmap(cx[i] - 12, cy - 12, icon)
            else:
                font = QFont("Arial", 11, QFont.Bold)
                painter.setFont(font)
                painter.setPen(QPen(COLOR_WHITE))
                painter.drawText(QRect(cx[i]-r, cy-r, CIRCLE_D, CIRCLE_D), Qt.AlignCenter, str(i+1))
        font = QFont("Arial", 8)
        painter.setFont(font)
        fm = QFontMetrics(font)
        for i in range(n):
            label = tr(STEP_KEYS[i])
            lw = fm.width(label)
            lx = cx[i] - lw // 2
            ly = cy + r + 6
            if lx < 2:
                lx = 2
            if lx + lw > w - 2:
                lx = w - lw - 2
            if i <= self._current:
                painter.setPen(QPen(COLOR_LABEL))
            else:
                painter.setPen(QPen(COLOR_LABEL_OFF))
            painter.drawText(lx, ly + fm.ascent(), label)
        painter.end()
