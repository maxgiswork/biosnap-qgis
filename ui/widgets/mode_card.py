# -*- coding: utf-8 -*-
import os
import sys
plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)
from qgis.PyQt.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy
)
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QPainter, QBrush, QFont, QPixmap, QPen
MODE_DESCRIPTIONS = {
    "search":            "Quick search via REST API. No registration needed. Up to 100k records per query.",
    "download":          "Full export via Download API. Requires GBIF login. No record limit.",
    "public":            "Access all public observations. Sensitive species show obscured coordinates (~28km).",
    "token":             "Use iNat API token. Access precise coordinates for sensitive species.",
    "combined_search":   "GBIF Search API + iNat. No registration needed. Duplicates removed automatically.",
    "combined_download": "GBIF Download API + iNat. Requires GBIF login. Full dataset, no limits.",
}
class ModeButton(QWidget):
    clicked = pyqtSignal(str)
    def __init__(self, mode_id, label, color, parent=None):
        super().__init__(parent)
        self._mode_id = mode_id
        self._color   = color
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._btn = QPushButton(label)
        self._btn.setFixedHeight(28)
        self._btn.setMinimumWidth(120)
        self._btn.setCursor(Qt.PointingHandCursor)
        self._btn.clicked.connect(lambda: self.clicked.emit(self._mode_id))
        layout.addWidget(self._btn)
        desc = MODE_DESCRIPTIONS.get(mode_id, "")
        self._desc = QLabel(desc)
        self._desc.setStyleSheet("color:#9E9E9E; font-size:10px; border:none; background:transparent;")
        self._desc.setWordWrap(True)
        self._desc.setFixedWidth(130)
        layout.addWidget(self._desc)
        self.set_active(False)
    def set_active(self, active):
        if active:
            self._btn.setStyleSheet(
                "QPushButton {{ background:{c}; color:white; border:none; border-radius:6px; font-size:11px; font-weight:bold; padding:2px 12px; }}".format(c=self._color)
            )
        else:
            self._btn.setStyleSheet(
                "QPushButton { background:#E0E0E0; color:#616161; border:none; border-radius:6px; font-size:11px; padding:2px 12px; }"
            )
class ModeCard(QWidget):
    selected = pyqtSignal(str)
    COLORS = {
        "gbif":     "#43A047",
        "inat":     "#81C784",
        "combined": "#1565C0",
    }
    def __init__(self, card_id, title, modes, parent=None):
        super().__init__(parent)
        self._card_id     = card_id
        self._title       = title
        self._modes       = modes
        self._selected    = False
        self._color       = self.COLORS.get(card_id, "#1565C0")
        self._mode_btns   = {}
        self._active_mode = modes[0][0] if modes else None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self._build_ui()
        self._set_idle()
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self._frame = QFrame(self)
        self._frame.setObjectName("cardFrame")
        self._frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        outer.addWidget(self._frame)
        row = QHBoxLayout(self._frame)
        row.setContentsMargins(16, 12, 16, 12)
        row.setSpacing(16)
        self._logo_label = QLabel()
        self._logo_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self._logo_label.setFixedSize(56, 56)
        self._logo_label.setStyleSheet("border:none; background:transparent;")
        self._set_logo_placeholder()
        row.addWidget(self._logo_label)
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(8)
        self._title_label = QLabel(self._title)
        self._title_label.setStyleSheet("border:none; background:transparent; font-weight:bold; font-size:12px;")
        right_col.addWidget(self._title_label)
        self._btns_row = QHBoxLayout()
        self._btns_row.setSpacing(16)
        self._btns_row.setContentsMargins(0, 0, 0, 0)
        for mode_id, mode_label in self._modes:
            mb = ModeButton(mode_id, mode_label, self._color)
            mb.setVisible(False)
            mb.clicked.connect(self._on_mode_clicked)
            self._mode_btns[mode_id] = mb
            self._btns_row.addWidget(mb)
        self._btns_row.addStretch()
        right_col.addLayout(self._btns_row)
        right_col.addStretch()
        row.addLayout(right_col)
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
    def _on_mode_clicked(self, mode_id):
        self._active_mode = mode_id
        for mid, mb in self._mode_btns.items():
            mb.set_active(mid == mode_id)
    def set_selected(self, selected: bool):
        self._selected = selected
        for mb in self._mode_btns.values():
            mb.setVisible(selected)
        if selected:
            self._set_selected()
            if self._active_mode:
                self._mode_btns[self._active_mode].set_active(True)
        else:
            self._set_idle()
            for mb in self._mode_btns.values():
                mb.set_active(False)
    def get_selected_mode(self):
        return self._active_mode
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
