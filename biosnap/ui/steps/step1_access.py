# -*- coding: utf-8 -*-
import os
import sys
plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy
)
from qgis.PyQt.QtCore import Qt
from core.i18n import tr
from ui.widgets.mode_card import ModeCard
class Step1Access(QWidget):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self._state = state
        self._cards = {}
        self._selected_card = None
        self._build_ui()
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)
        self._title = QLabel(tr("step1_title"))
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setStyleSheet("font-size:16px; font-weight:bold; color:#212121;")
        root.addWidget(self._title)
        self._subtitle = QLabel(tr("step1_subtitle"))
        self._subtitle.setAlignment(Qt.AlignCenter)
        self._subtitle.setStyleSheet("font-size:11px; color:#757575;")
        self._subtitle.setWordWrap(True)
        root.addWidget(self._subtitle)
        root.addSpacing(8)
        card_defs = [
            (
                "gbif",
                "GBIF",
                [
                    ("search",   "GBIF Search API"),
                    ("download", "GBIF Download API"),
                ]
            ),
            (
                "inat",
                "iNaturalist",
                [
                    ("public", "Without token"),
                    ("token",  "With API token"),
                ]
            ),
            (
                "combined",
                "GBIF + iNat",
                [
                    ("combined_search",   "GBIF API + iNat"),
                    ("combined_download", "GBIF Download + iNat"),
                ]
            ),
        ]
        for card_id, title, modes in card_defs:
            card = ModeCard(card_id, title, modes, parent=self)
            card.selected.connect(self._on_card_selected)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self._cards[card_id] = card
            root.addWidget(card)
        root.addStretch()
    def _on_card_selected(self, card_id):
        self._selected_card = card_id
        for cid, card in self._cards.items():
            card.set_selected(cid == card_id)
        self._save_to_state()
    def _save_to_state(self):
        if self._selected_card is None:
            return
        card = self._cards[self._selected_card]
        mode = card.get_selected_mode()
        if self._selected_card == "gbif":
            self._state.download_mode = "B" if mode == "download" else "A"
            self._state.data_source   = "gbif"
        elif self._selected_card == "inat":
            self._state.download_mode = "inat_token" if mode == "token" else "inat_public"
            self._state.data_source   = "inat"
        elif self._selected_card == "combined":
            self._state.download_mode = mode
            self._state.data_source   = "combined"
    def is_valid(self):
        return self._selected_card is not None
    def retranslate_ui(self):
        self._title.setText(tr("step1_title"))
        self._subtitle.setText(tr("step1_subtitle"))
