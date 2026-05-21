# -*- coding: utf-8 -*-
import os
import sys
plugin_dir = os.path.dirname(os.path.dirname(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QWidget,
    QSizePolicy, QLabel
)
from qgis.PyQt.QtCore import Qt
from core.i18n import tr, load_language, available_languages
from core.state import AppState
from ui.step_indicator import StepIndicator
from ui.steps.step1_access import Step1Access
from ui.steps.step2_taxon import Step2Taxon
class MainWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = AppState()
        self._current_step = 0
        self._total_steps = 5
        self._init_ui()
        self._update_nav_buttons()
    def _init_ui(self):
        self.setWindowTitle("BioSnap")
        self.setMinimumSize(680, 620)
        self.resize(760, 680)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet("background:#1565C0;")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(16, 0, 16, 0)
        title_lbl = QLabel("BioSnap")
        title_lbl.setStyleSheet("color:white; font-size:18px; font-weight:bold;")
        h_lay.addWidget(title_lbl)
        h_lay.addStretch()
        for lang in available_languages():
            btn = QPushButton(lang["flag"])
            btn.setFixedSize(36, 28)
            btn.setStyleSheet("QPushButton{color:white;background:transparent;border:1px solid rgba(255,255,255,0.4);border-radius:4px;font-size:11px;}QPushButton:hover{background:rgba(255,255,255,0.2);}")
            btn.clicked.connect(lambda checked, c=lang["code"]: self._on_lang_changed(c))
            h_lay.addWidget(btn)
        root.addWidget(header)
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._init_steps()
        root.addWidget(self.stack)
        bottom = QWidget()
        bottom.setFixedHeight(120)
        bottom.setStyleSheet("background:#F5F5F5;border-top:1px solid #E0E0E0;")
        b_lay = QVBoxLayout(bottom)
        b_lay.setContentsMargins(16, 6, 16, 6)
        b_lay.setSpacing(4)
        self.indicator = StepIndicator()
        b_lay.addWidget(self.indicator)
        nav = QHBoxLayout()
        nav.setSpacing(8)
        self.btn_back = QPushButton()
        self.btn_back.setFixedSize(120, 34)
        self.btn_back.setStyleSheet("QPushButton{background:white;border:1px solid #BDBDBD;border-radius:4px;font-size:13px;}QPushButton:hover{background:#EEEEEE;}QPushButton:disabled{color:#BDBDBD;}")
        self.btn_back.clicked.connect(self.on_back_clicked)
        self.btn_next = QPushButton()
        self.btn_next.setFixedSize(120, 34)
        self.btn_next.setStyleSheet("QPushButton{background:#1565C0;color:white;border:none;border-radius:4px;font-size:13px;}QPushButton:hover{background:#1976D2;}QPushButton:disabled{background:#BDBDBD;}")
        self.btn_next.clicked.connect(self.on_next_clicked)
        nav.addStretch()
        nav.addWidget(self.btn_back)
        nav.addWidget(self.btn_next)
        b_lay.addLayout(nav)
        root.addWidget(bottom)
        self.retranslate_ui()
    def _init_steps(self):
        self.steps = []
        self.step1 = Step1Access(self.state)
        self.steps.append(self.step1)
        self.stack.addWidget(self.step1)
        self.step2 = Step2Taxon(self.state)
        self.steps.append(self.step2)
        self.stack.addWidget(self.step2)
        for i in range(2, self._total_steps):
            w = QWidget()
            lay = QVBoxLayout(w)
            lay.setAlignment(Qt.AlignCenter)
            lbl = QLabel("Step {0}".format(i + 1))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size:24px;color:#9E9E9E;")
            lay.addWidget(lbl)
            self.steps.append(w)
            self.stack.addWidget(w)
    def go_to_step(self, index):
        if 0 <= index < self._total_steps:
            self._current_step = index
            self.stack.setCurrentIndex(index)
            self.indicator.set_current(index)
            self._update_nav_buttons()
    def on_next_clicked(self):
        if self._current_step == 0 and not self.step1.is_valid():
            return
        if self._current_step == 1 and not self.step2.is_valid():
            return
        if self._current_step < self._total_steps - 1:
            self.go_to_step(self._current_step + 1)
    def on_back_clicked(self):
        if self._current_step > 0:
            self.go_to_step(self._current_step - 1)
    def _update_nav_buttons(self):
        self.btn_back.setEnabled(self._current_step > 0)
        is_last = self._current_step == self._total_steps - 1
        self.btn_next.setText(tr("btn_finish") if is_last else tr("btn_next"))
    def _on_lang_changed(self, lang_code):
        load_language(lang_code)
        self.retranslate_ui()
    def retranslate_ui(self):
        self.setWindowTitle(tr("app_title"))
        self.btn_back.setText(tr("btn_back"))
        self._update_nav_buttons()
        self.indicator.retranslate_ui()
        if hasattr(self, 'step1'):
            self.step1.retranslate_ui()
        if hasattr(self, 'step2'):
            self.step2.retranslate_ui()
