# -*- coding: utf-8 -*-
import os
import sys
plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QAbstractItemView, QCheckBox,
    QSpinBox, QComboBox, QFrame, QSizePolicy,
    QLineEdit
)
from qgis.PyQt.QtCore import Qt
from core.i18n import tr

LIMIT_MODES = ("A", "inat_public", "combined_search")  # тільки без download API

LIMIT_MODE_LABELS = {
    "A":               "GBIF Search — max 100,000",
    "inat_public":     "iNat Public — max 10,000",
    "combined_search": "GBIF Search + iNat — max 100,000",
}

GBIF_MODES    = ("A", "B")
INAT_MODES    = ("inat_public", "inat_token")
COMBINED_MODES = ("combined_search", "combined_download")


class Step3Filters(QWidget):

    BASIS_MAP = [
        ("Human observation",    "HUMAN_OBSERVATION"),
        ("Machine observation",  "MACHINE_OBSERVATION"),
        ("Preserved specimen",   "PRESERVED_SPECIMEN"),
        ("Living specimen",      "LIVING_SPECIMEN"),
        ("Fossil specimen",      "FOSSIL_SPECIMEN"),
        ("Material citation",    "MATERIAL_CITATION"),
        ("Material sample",      "MATERIAL_SAMPLE"),
        ("Any type (no filter)", None),
    ]

    ACCURACY_OPTIONS = [
        ("Any",       None),
        ("≤ 100 m",   100),
        ("≤ 500 m",   500),
        ("≤ 1000 m",  1000),
        ("≤ 5000 m",  5000),
        ("≤ 10000 m", 10000),
    ]

    QUALITY_OPTIONS = [
        ("Any (no filter)",  ""),
        ("Research grade",   "research"),
        ("Needs ID",         "needs_id"),
        ("Casual",           "casual"),
    ]

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self._state = state
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.setSpacing(10)

        # Заголовок
        self._title = QLabel(tr("step3_title"))
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setStyleSheet("font-size:16px; font-weight:bold; color:#212121;")
        root.addWidget(self._title)

        # ════════════════════════════════════════
        # БЛОК GBIF
        # ════════════════════════════════════════
        self._gbif_block = QWidget()
        gbif_lay = QVBoxLayout(self._gbif_block)
        gbif_lay.setContentsMargins(0, 0, 0, 0)
        gbif_lay.setSpacing(8)

        # Заголовок GBIF блоку
        self._lbl_gbif_header = QLabel("GBIF filters")
        self._lbl_gbif_header.setStyleSheet("font-size:12px; font-weight:bold; color:#43A047;")
        gbif_lay.addWidget(self._lbl_gbif_header)

        # Basis of record
        self._lbl_basis = QLabel(tr("filter_basis"))
        self._lbl_basis.setStyleSheet("font-size:11px; font-weight:bold; color:#424242;")
        gbif_lay.addWidget(self._lbl_basis)

        self._list_basis = QListWidget()
        self._list_basis.setSelectionMode(QAbstractItemView.MultiSelection)
        self._list_basis.setFixedHeight(130)
        self._list_basis.setStyleSheet(
            "QListWidget { border:1px solid #BDBDBD; border-radius:4px; font-size:11px; }"
            "QListWidget::item:selected { background:#E3F2FD; color:#1565C0; }"
        )
        for label, _ in self.BASIS_MAP:
            self._list_basis.addItem(label)
        self._list_basis.item(0).setSelected(True)
        gbif_lay.addWidget(self._list_basis)

        # Виключити iNat (тільки для чистого GBIF)
        self._chk_inat = QCheckBox(tr("filter_inat"))
        self._chk_inat.setStyleSheet("font-size:11px;")
        self._chk_inat.setChecked(False)
        gbif_lay.addWidget(self._chk_inat)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("color:#E0E0E0;")
        gbif_lay.addWidget(sep1)

        # Діапазон років GBIF
        yr = QHBoxLayout()
        self._lbl_years_gbif = QLabel(tr("filter_years"))
        self._lbl_years_gbif.setStyleSheet("font-size:11px; font-weight:bold; color:#424242;")
        yr.addWidget(self._lbl_years_gbif)
        yr.addStretch()
        self._spin_year_from = QSpinBox()
        self._spin_year_from.setRange(1753, 2026)
        self._spin_year_from.setValue(2000)
        self._spin_year_from.setFixedWidth(70)
        self._spin_year_from.setStyleSheet("font-size:11px;")
        yr.addWidget(self._spin_year_from)
        lbl_d1 = QLabel("—")
        lbl_d1.setStyleSheet("font-size:11px; color:#757575;")
        yr.addWidget(lbl_d1)
        self._spin_year_to = QSpinBox()
        self._spin_year_to.setRange(1753, 2026)
        self._spin_year_to.setValue(2026)
        self._spin_year_to.setFixedWidth(70)
        self._spin_year_to.setStyleSheet("font-size:11px;")
        yr.addWidget(self._spin_year_to)
        gbif_lay.addLayout(yr)

        # Точність координат
        acc = QHBoxLayout()
        self._lbl_accuracy = QLabel(tr("filter_accuracy"))
        self._lbl_accuracy.setStyleSheet("font-size:11px; font-weight:bold; color:#424242;")
        acc.addWidget(self._lbl_accuracy)
        acc.addStretch()
        self._dd_accuracy = QComboBox()
        self._dd_accuracy.setFixedWidth(120)
        self._dd_accuracy.setStyleSheet("font-size:11px;")
        for label, val in self.ACCURACY_OPTIONS:
            self._dd_accuracy.addItem(label, val)
        acc.addWidget(self._dd_accuracy)
        gbif_lay.addLayout(acc)

        # Якість координат
        self._chk_coords = QCheckBox(tr("filter_coords"))
        self._chk_coords.setStyleSheet("font-size:11px;")
        self._chk_coords.setChecked(True)
        gbif_lay.addWidget(self._chk_coords)

        self._chk_geo_issues = QCheckBox(tr("filter_geo_issues"))
        self._chk_geo_issues.setStyleSheet("font-size:11px;")
        self._chk_geo_issues.setChecked(True)
        gbif_lay.addWidget(self._chk_geo_issues)

        # Ліміт записів
        lim = QHBoxLayout()
        self._lbl_limit = QLabel()
        self._lbl_limit.setStyleSheet("font-size:11px; font-weight:bold; color:#424242;")
        lim.addWidget(self._lbl_limit)
        lim.addStretch()
        self._spin_limit = QSpinBox()
        self._spin_limit.setRange(1, 100000)
        self._spin_limit.setValue(10000)
        self._spin_limit.setSingleStep(1000)
        self._spin_limit.setFixedWidth(90)
        self._spin_limit.setStyleSheet("font-size:11px;")
        lim.addWidget(self._spin_limit)
        self._limit_row = QWidget()
        self._limit_row.setLayout(lim)
        gbif_lay.addWidget(self._limit_row)

        root.addWidget(self._gbif_block)

        # ════════════════════════════════════════
        # РОЗДІЛЬНИК між блоками (для combined)
        # ════════════════════════════════════════
        self._sep_combined = QFrame()
        self._sep_combined.setFrameShape(QFrame.HLine)
        self._sep_combined.setStyleSheet("color:#BDBDBD;")
        root.addWidget(self._sep_combined)

        # ════════════════════════════════════════
        # БЛОК iNAT
        # ════════════════════════════════════════
        self._inat_block = QWidget()
        inat_lay = QVBoxLayout(self._inat_block)
        inat_lay.setContentsMargins(0, 0, 0, 0)
        inat_lay.setSpacing(8)

        self._lbl_inat_header = QLabel("iNaturalist filters")
        self._lbl_inat_header.setStyleSheet("font-size:12px; font-weight:bold; color:#1565C0;")
        inat_lay.addWidget(self._lbl_inat_header)

        # Quality grade
        qg = QHBoxLayout()
        self._lbl_quality = QLabel("Quality grade")
        self._lbl_quality.setStyleSheet("font-size:11px; font-weight:bold; color:#424242;")
        qg.addWidget(self._lbl_quality)
        qg.addStretch()
        self._dd_quality = QComboBox()
        self._dd_quality.setFixedWidth(150)
        self._dd_quality.setStyleSheet("font-size:11px;")
        for label, val in self.QUALITY_OPTIONS:
            self._dd_quality.addItem(label, val)
        self._dd_quality.setCurrentIndex(0)  # Any за дефолтом
        qg.addWidget(self._dd_quality)
        inat_lay.addLayout(qg)

        # Діапазон років iNat
        yr2 = QHBoxLayout()
        self._lbl_years_inat = QLabel(tr("filter_years"))
        self._lbl_years_inat.setStyleSheet("font-size:11px; font-weight:bold; color:#424242;")
        yr2.addWidget(self._lbl_years_inat)
        yr2.addStretch()
        self._spin_inat_year_from = QSpinBox()
        self._spin_inat_year_from.setRange(1753, 2026)
        self._spin_inat_year_from.setValue(2000)
        self._spin_inat_year_from.setFixedWidth(70)
        self._spin_inat_year_from.setStyleSheet("font-size:11px;")
        yr2.addWidget(self._spin_inat_year_from)
        lbl_d2 = QLabel("—")
        lbl_d2.setStyleSheet("font-size:11px; color:#757575;")
        yr2.addWidget(lbl_d2)
        self._spin_inat_year_to = QSpinBox()
        self._spin_inat_year_to.setRange(1753, 2026)
        self._spin_inat_year_to.setValue(2026)
        self._spin_inat_year_to.setFixedWidth(70)
        self._spin_inat_year_to.setStyleSheet("font-size:11px;")
        yr2.addWidget(self._spin_inat_year_to)
        inat_lay.addLayout(yr2)

        # Project ID
        proj = QHBoxLayout()
        self._lbl_project = QLabel("Project ID (optional)")
        self._lbl_project.setStyleSheet("font-size:11px; font-weight:bold; color:#424242;")
        proj.addWidget(self._lbl_project)
        proj.addStretch()
        self._txt_project = QLineEdit()
        self._txt_project.setPlaceholderText("e.g. 12345")
        self._txt_project.setFixedWidth(120)
        self._txt_project.setFixedHeight(24)
        self._txt_project.setStyleSheet("font-size:11px; padding:2px 6px; border:1px solid #BDBDBD; border-radius:4px;")
        proj.addWidget(self._txt_project)
        inat_lay.addLayout(proj)

        root.addWidget(self._inat_block)
        root.addStretch()

    def _update_blocks(self):
        mode = self._state.download_mode
        show_gbif   = mode in GBIF_MODES or mode in COMBINED_MODES or mode is None
        show_inat   = mode in INAT_MODES or mode in COMBINED_MODES
        show_inat_chk = mode in GBIF_MODES
        show_combined_sep = mode in COMBINED_MODES

        self._gbif_block.setVisible(show_gbif)
        self._inat_block.setVisible(show_inat)
        self._chk_inat.setVisible(show_inat_chk)
        self._sep_combined.setVisible(show_combined_sep)

        # Ліміт
        show_limit = mode in LIMIT_MODES
        self._limit_row.setVisible(show_limit)
        if show_limit:
            label = tr("filter_limit") + " — " + LIMIT_MODE_LABELS.get(mode, "max 100,000")
            self._lbl_limit.setText(label)

    def showEvent(self, event):
        super().showEvent(event)
        self._update_blocks()

    def save_to_state(self):
        mode = self._state.download_mode
        selected = [
            self.BASIS_MAP[i][1]
            for i in range(self._list_basis.count())
            if self._list_basis.item(i).isSelected()
        ]
        basis_vals = [v for v in selected if v is not None]

        self._state.query_params = {
            "basis_of_record"   : basis_vals or None,
            "exclude_inat"      : self._chk_inat.isChecked() if mode in GBIF_MODES else False,
            "year_from"         : self._spin_year_from.value(),
            "year_to"           : self._spin_year_to.value(),
            "coord_uncertainty" : self._dd_accuracy.currentData(),
            "has_coordinate"    : self._chk_coords.isChecked(),
            "no_geo_issues"     : self._chk_geo_issues.isChecked(),
            "max_records"       : self._spin_limit.value(),
            "exclude_datasets"  : [],
            "inat_quality_grade": self._dd_quality.currentData(),
            "inat_year_from"    : self._spin_inat_year_from.value(),
            "inat_year_to"      : self._spin_inat_year_to.value(),
            "inat_project_id"   : self._txt_project.text().strip() or None,
        }

    def is_valid(self):
        return True

    def retranslate_ui(self):
        self._title.setText(tr("step3_title"))
        self._lbl_basis.setText(tr("filter_basis"))
        self._chk_inat.setText(tr("filter_inat"))
        self._lbl_years_gbif.setText(tr("filter_years"))
        self._lbl_years_inat.setText(tr("filter_years"))
        self._lbl_accuracy.setText(tr("filter_accuracy"))
        self._chk_coords.setText(tr("filter_coords"))
        self._chk_geo_issues.setText(tr("filter_geo_issues"))
        self._update_blocks()
