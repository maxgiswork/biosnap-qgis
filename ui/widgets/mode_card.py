# -*- coding: utf-8 -*-
import os
import sys
import base64
plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)
from qgis.PyQt.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QLineEdit
)
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QPainter, QBrush, QFont, QPixmap, QPen
from qgis.core import QgsSettings

MODE_DESCRIPTIONS = {
    "search":             "Quick search via REST API. No registration needed. Up to 100k records.",
    "download":           "Full export via Download API. Requires GBIF login. No record limit.",
    "public":             "Access all public observations. Sensitive species show obscured coordinates.",
    "token":              "Use iNat API token. Access precise coordinates for sensitive species.",
    "combined_search":    "GBIF Search API + iNat public. No registration needed.",
    "combined_download":  "GBIF Download API + iNat token. Requires GBIF login and iNat token.",
}

MODE_LABELS = {
    "search":             "GBIF Search",
    "download":           "GBIF Download",
    "public":             "iNat Public",
    "token":              "iNat Token",
    "combined_search":    "GBIF Search + iNat",
    "combined_download":  "GBIF Download + iNat Token",
}

def _encode(s):
    return base64.b64encode(s.encode("utf-8")).decode("ascii") if s else ""

def _decode(s):
    try:
        return base64.b64decode(s.encode("ascii")).decode("utf-8") if s else ""
    except Exception:
        return ""


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
        self._desc.setFixedWidth(150)
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


class AuthBlock(QWidget):
    def __init__(self, block_type, parent=None):
        super().__init__(parent)
        self._type    = block_type
        self._loading = False
        self._settings = QgsSettings()
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 4, 4, 4)
        layout.setSpacing(4)
        if self._type == "gbif":
            lbl = QLabel("GBIF Login")
            lbl.setStyleSheet("font-size:10px; font-weight:bold; color:#424242; border:none; background:transparent;")
            layout.addWidget(lbl)
            self._login = QLineEdit()
            self._login.setPlaceholderText("GBIF username")
            self._login.setFixedHeight(24)
            self._login.setMinimumWidth(140)
            self._login.setStyleSheet("font-size:11px; padding:2px 6px; border:1px solid #BDBDBD; border-radius:4px;")
            self._login.textChanged.connect(self._save)
            layout.addWidget(self._login)
            self._password = QLineEdit()
            self._password.setPlaceholderText("GBIF password")
            self._password.setEchoMode(QLineEdit.Password)
            self._password.setFixedHeight(24)
            self._password.setMinimumWidth(140)
            self._password.setStyleSheet("font-size:11px; padding:2px 6px; border:1px solid #BDBDBD; border-radius:4px;")
            self._password.textChanged.connect(self._save)
            layout.addWidget(self._password)
        elif self._type == "inat":
            lbl = QLabel("iNat Token")
            lbl.setStyleSheet("font-size:10px; font-weight:bold; color:#424242; border:none; background:transparent;")
            layout.addWidget(lbl)
            self._token = QLineEdit()
            self._token.setPlaceholderText("iNaturalist API token")
            self._token.setEchoMode(QLineEdit.Password)
            self._token.setFixedHeight(24)
            self._token.setMinimumWidth(140)
            self._token.setStyleSheet("font-size:11px; padding:2px 6px; border:1px solid #BDBDBD; border-radius:4px;")
            self._token.textChanged.connect(self._save)
            layout.addWidget(self._token)
        self._warn = QLabel("")
        self._warn.setStyleSheet("font-size:10px; color:#F57F17; border:none; background:transparent;")
        self._warn.setWordWrap(True)
        self._warn.hide()
        layout.addWidget(self._warn)
        layout.addStretch()

    def _load(self):
        self._loading = True
        s = self._settings
        if self._type == "gbif":
            self._login.setText(s.value("biosnap/gbif_user", "", str))
            self._password.setText(_decode(s.value("biosnap/gbif_pass_b64", "", str)))
        elif self._type == "inat":
            self._token.setText(_decode(s.value("biosnap/inat_token_b64", "", str)))
        self._loading = False

    def _save(self):
        if self._loading:
            return
        s = self._settings
        if self._type == "gbif":
            s.setValue("biosnap/gbif_user", self._login.text().strip())
            s.setValue("biosnap/gbif_pass_b64", _encode(self._password.text()))
        elif self._type == "inat":
            s.setValue("biosnap/inat_token_b64", _encode(self._token.text()))

    def get_login(self):
        return self._login.text().strip() if self._type == "gbif" else ""

    def get_password(self):
        return self._password.text().strip() if self._type == "gbif" else ""

    def get_token(self):
        return self._token.text().strip() if self._type == "inat" else ""

    def check_warn(self):
        if self._type == "gbif":
            if not self.get_login() or not self.get_password():
                self._warn.setText("Login and password required for Download API")
                self._warn.show()
                return False
        elif self._type == "inat":
            if not self.get_token():
                self._warn.setText("Token required for iNat Token mode")
                self._warn.show()
                return False
        self._warn.hide()
        return True

    def clear_warn(self):
        self._warn.hide()


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
        self._auth_blocks = {}
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
        for mode_id, _ in self._modes:
            label = MODE_LABELS.get(mode_id, mode_id)
            mb = ModeButton(mode_id, label, self._color)
            mb.setVisible(False)
            mb.clicked.connect(self._on_mode_clicked)
            self._mode_btns[mode_id] = mb
            self._btns_row.addWidget(mb)
        self._btns_row.addStretch()
        right_col.addLayout(self._btns_row)
        right_col.addStretch()
        row.addLayout(right_col)
        if self._card_id == "gbif":
            ab = AuthBlock("gbif")
            ab.setVisible(False)
            self._auth_blocks["gbif"] = ab
            row.addWidget(ab)
        elif self._card_id == "inat":
            ab = AuthBlock("inat")
            ab.setVisible(False)
            self._auth_blocks["inat"] = ab
            row.addWidget(ab)
        elif self._card_id == "combined":
            ab_gbif = AuthBlock("gbif")
            ab_gbif.setVisible(False)
            self._auth_blocks["gbif"] = ab_gbif
            row.addWidget(ab_gbif)
            ab_inat = AuthBlock("inat")
            ab_inat.setVisible(False)
            self._auth_blocks["inat"] = ab_inat
            row.addWidget(ab_inat)
        row.addStretch()

    def _update_auth_visibility(self):
        mode = self._active_mode
        needs_gbif = mode in ("download", "combined_download")
        needs_inat = mode in ("token", "combined_download")
        if "gbif" in self._auth_blocks:
            self._auth_blocks["gbif"].setVisible(self._selected and needs_gbif)
        if "inat" in self._auth_blocks:
            self._auth_blocks["inat"].setVisible(self._selected and needs_inat)

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
        self._update_auth_visibility()
        for ab in self._auth_blocks.values():
            ab.clear_warn()

    def set_selected(self, selected):
        self._selected = selected
        for mb in self._mode_btns.values():
            mb.setVisible(selected)
        if selected:
            self._set_selected()
            if self._active_mode:
                self._mode_btns[self._active_mode].set_active(True)
            self._update_auth_visibility()
        else:
            self._set_idle()
            for mb in self._mode_btns.values():
                mb.set_active(False)
            for ab in self._auth_blocks.values():
                ab.setVisible(False)

    def get_selected_mode(self):
        return self._active_mode

    def get_gbif_credentials(self):
        if "gbif" in self._auth_blocks:
            ab = self._auth_blocks["gbif"]
            return ab.get_login(), ab.get_password()
        return "", ""

    def get_inat_token(self):
        if "inat" in self._auth_blocks:
            return self._auth_blocks["inat"].get_token()
        return ""

    def check_auth_warnings(self):
        mode = self._active_mode
        ok = True
        if mode in ("download", "combined_download") and "gbif" in self._auth_blocks:
            if not self._auth_blocks["gbif"].check_warn():
                ok = False
        if mode in ("token", "combined_download") and "inat" in self._auth_blocks:
            if not self._auth_blocks["inat"].check_warn():
                ok = False
        return ok

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
