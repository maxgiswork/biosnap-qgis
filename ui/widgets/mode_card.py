# -*- coding: utf-8 -*-
import os
import sys
plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)
from qgis.PyQt.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QRadioButton, QButtonGroup, QSizePolicy
)
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QPainter, QBrush, QFont, QPixmap, QPen
class ModeCard(QWidget):
    selected = pyqtSignal(str)
    COLORS = {
        "gbif":     "#43A047",
        "inat":     "#81C784",
        "combined": "#1565C0",
    }
    def __init__(self, card_id, title, modes, parent=None):
        super().__init__(parent)
        self._card_id  = card_id
        self._title    = title
        self._modes    = modes
        self._selected = False
        self._color    = self.COLORS.get(card_id, "#1565C0")
        self.setMinimumHeight(90)
        self.setMaximumHeight(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self._build_ui()
        self._set_idle()
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self._frame = QFrame(self)
        self._frame.setObjectName("cardFrame")
        self._frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        outer.addWidget(self._frame)
        row = QHBoxLayout(self._frame)
        row.setContentsMargins(16, 12, 16, 12)
        row.setSpacing(16)
        self._logo_label = QLabel()
        self._logo_label.setAlignment(Qt.AlignCenter)
        self._logo_label.setFixedSize(56, 56)
        self._logo_label.setStyleSheet("border: none; background: transparent;")
        self._set_logo_placeholder()
        row.addWidget(self._logo_label)
        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(6)
        self._title_label = QLabel(self._title)
        self._title_label.setStyleSheet("border: none; background: transparent;")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self._title_label.setFont(font)
        text_col.addWidget(self._title_label)
        self._radio_group   = QButtonGroup(self)
        self._radio_widgets = []
        for i, (mode_id, mode_label) in enumerate(self._modes):
            rb = QRadioButton(mode_label)
            rb.setVisible(False)
            rb.setStyleSheet("QRadioButton { font-size: 11px; border: none; background: transparent; }")
            self._radio_group.addButton(rb, i)
            text_col.addWidget(rb)
            self._radio_widgets.append(rb)
        if self._radio_widgets:
            self._radio_widgets[0].setChecked(True)
        text_col.addStretch()
        row.addLayout(text_col)
        row.addStretch()
    def _set_logo_placeholder(self):
        size = 48
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(QColor(self._color)))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(2, 2, size-4, size-4, 8, 8)
        p.setPen(QPen(QColor("white")))
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        p.setFont(font)
        fm = p.fontMetrics()
        text = self._card_id.upper()[:4]
        tw = fm.width(text)
        p.drawText((size - tw) // 2, size // 2 + 4, text)
        p.end()
        self._logo_label.setPixmap(pix)
    def _set_idle(self):
        self._frame.setStyleSheet(
            "#cardFrame { background:#EEEEEE; border:2px solid #BDBDBD; border-radius:10px; }"
        )
    def _set_hover(self):
        self._frame.setStyleSheet(
            "#cardFrame {{ background:#F5F5F5; border:2px solid {c}; border-radius:10px; }}".format(c=self._color)
        )
    def _set_selected(self):
        self._frame.setStyleSheet(
            "#cardFrame {{ background:#FAFAFA; border:3px solid {c}; border-radius:10px; }}".format(c=self._color)
        )
    def set_selected(self, selected: bool):
        self._selected = selected
        for rb in self._radio_widgets:
            rb.setVisible(selected)
        if selected:
            self._set_selected()
            self.setMaximumHeight(140)
        else:
            self._set_idle()
            self.setMaximumHeight(120)
    def get_selected_mode(self):
        idx = self._radio_group.checkedId()
        if idx >= 0:
            return self._modes[idx][0]
        return None
    def enterEvent(self, event):
        if not self._selected:
            self._set_hover()
        super().enterEvent(event)
    def leaveEvent(self, event):
        if not self._selected:
            self._set_idle()
        super().leaveEvent(event)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self._card_id)
        super().mousePressEvent(event)
