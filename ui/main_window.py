import os, sys
plugin_dir = os.path.dirname(os.path.dirname(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QSizePolicy, QWidget, QPushButton,
    QLineEdit, QScrollArea, QCheckBox, QMenu
)
from qgis.PyQt.QtCore import Qt, QSize, QPoint, QTimer
from qgis.core import QgsApplication, QgsSettings
from ui.styles import MAIN_STYLE

CHIP_ON  = ("background-color:#1A1A22; color:#FFFFFF; border:none;"
            "border-radius:13px; padding:4px 18px;"
            "font-size:13px; font-weight:bold;")
CHIP_OFF = ("background-color:#ECECF0; color:#1A1A22; border:none;"
            "border-radius:13px; padding:4px 18px; font-size:13px;")
CHIP_SM_ON  = ("background-color:#1A1A22; color:#FFFFFF; border:none;"
               "border-radius:10px; padding:3px 12px; font-size:11px;")
CHIP_SM_OFF = ("background-color:#ECECF0; color:#1A1A22; border:none;"
               "border-radius:10px; padding:3px 12px; font-size:11px;")
SECTION_LBL = ("font-size:10px; color:#6B7280; font-weight:bold;"
               "background:transparent; margin-bottom:2px;")
BTN_GBIF    = ("background-color:#2D7D1F; color:#FFFFFF; border:none;"
               "border-radius:13px; padding:4px 14px;"
               "font-size:12px; font-weight:bold;")
BTN_INAT    = ("background-color:#0D9488; color:#FFFFFF; border:none;"
               "border-radius:13px; padding:4px 14px;"
               "font-size:12px; font-weight:bold;")
BTN_BOTH_ON  = ("background-color:#1A1A22; color:#FFFFFF; border:none;"
                "border-radius:13px; padding:4px 14px; font-size:12px;")
BTN_BOTH_OFF = ("background-color:#ECECF0; color:#1A1A22; border:none;"
                "border-radius:13px; padding:4px 14px; font-size:12px;")
FIELD = ("border:1px solid #E5E7EB; border-radius:6px;"
         "padding:4px 8px; background:#FFFFFF; font-size:12px;")
TOGGLE_ON  = ("QCheckBox { font-size:12px; color:#1A1A22;"
              "background:transparent; spacing:8px; }"
              "QCheckBox::indicator { width:38px; height:22px;"
              "border-radius:11px; background-color:#1A1A22; border:none; }"
              "QCheckBox::indicator:unchecked { background-color:#D1D5DB; }")
TOGGLE_OFF = ("QCheckBox { font-size:12px; color:#9CA3AF;"
              "background:transparent; spacing:8px; }"
              "QCheckBox::indicator { width:38px; height:22px;"
              "border-radius:11px; background-color:#D1D5DB; border:none; }"
              "QCheckBox::indicator:checked { background-color:#1A1A22; }")
SEARCH_FRAME_NORMAL = ("QFrame { background:#FFFFFF; border:1.5px solid #E5E7EB;"
                       "border-radius:8px; }")
SEARCH_FRAME_FOCUS  = ("QFrame { background:#FFFFFF; border:1.5px solid #1A1A22;"
                       "border-radius:8px; }")
RANK_BTN  = ("background-color:#ECECF0; color:#1A1A22; border:none;"
             "border-radius:6px; padding:0 8px; font-size:11px;")
RANK_MENU = ("QMenu { background:#FFFFFF; border:1px solid #E5E7EB;"
             "font-size:11px; padding:2px; }"
             "QMenu::item { padding:5px 16px; color:#1A1A22; }"
             "QMenu::item:selected { background:#1A1A22; color:#FFFFFF; }")
RANKS = ["Kingdom","Phylum","Class","Order",
         "Family","Subfamily","Tribe",
         "Genus","Subgenus","Species","Subspecies"]


class BioSnapDialog(QDialog):

    def __init__(self, iface=None, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("BioSnap")
        self.setMinimumWidth(440)
        self.setMinimumHeight(620)
        self.resize(460, 760)
        self.setStyleSheet(MAIN_STYLE)
        self._mode   = "single"
        self._source = "both"
        self._format = "gpkg"
        self._rank   = "Species"

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:#F6F5F3;")

        body = QWidget()
        body.setStyleSheet("background:#F6F5F3;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(16, 14, 16, 16)
        bl.setSpacing(8)

        bl.addWidget(self._build_mode_switcher())
        bl.addWidget(self._build_search_block())
        bl.addWidget(self._divider())
        bl.addWidget(self._build_territory_block())
        bl.addWidget(self._divider())
        bl.addWidget(self._build_source_block())
        bl.addWidget(self._divider())
        bl.addWidget(self._build_year_accuracy_block())
        bl.addWidget(self._build_toggles_block())
        bl.addWidget(self._divider())
        bl.addWidget(self._build_preview_block())
        bl.addWidget(self._build_advanced_btn())
        bl.addWidget(self._divider())
        bl.addWidget(self._build_output_block())
        bl.addWidget(self._build_format_block())
        bl.addSpacing(4)
        bl.addWidget(self._build_run_btn())

        scroll.setWidget(body)
        root.addWidget(scroll)

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(
            "color:#E5E7EB; background:#E5E7EB; border:none; max-height:1px;")
        return line

    def _slbl(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(SECTION_LBL)
        return lbl

    def _build_header(self):
        header = QFrame()
        header.setObjectName("header")
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header.setFixedHeight(58)
        outer = QHBoxLayout(header)
        outer.setContentsMargins(16, 0, 16, 0)
        outer.setSpacing(0)
        outer.setAlignment(Qt.AlignVCenter)
        logo_w = QWidget()
        logo_w.setStyleSheet("background:transparent;")
        logo_v = QVBoxLayout(logo_w)
        logo_v.setContentsMargins(0, 0, 0, 0)
        logo_v.setSpacing(1)
        logo_v.setAlignment(Qt.AlignVCenter)
        lbl_name = QLabel()
        lbl_name.setText(
            '<span style="font-family:Segoe UI;font-size:17pt;font-weight:bold;">'
            '<span style="color:#D21C1C;font-style:italic;">B</span>'
            '<span style="color:#FFFFFF;">ioSnap</span></span>'
        )
        lbl_name.setStyleSheet("background:transparent;")
        lbl_name.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        lbl_sub = QLabel("Quick occurrence loader")
        lbl_sub.setStyleSheet(
            "color:#9CA3AF; font-size:10px; background:transparent;")
        lbl_sub.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        logo_v.addWidget(lbl_name)
        logo_v.addWidget(lbl_sub)
        outer.addWidget(logo_w)
        outer.addStretch()
        return header

    def _build_mode_switcher(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        lbl = QLabel("Mode")
        lbl.setStyleSheet(SECTION_LBL)
        h.addWidget(lbl)
        h.addSpacing(4)
        self._btn_single = QPushButton("Single")
        self._btn_single.setFixedHeight(28)
        self._btn_single.setStyleSheet(CHIP_ON)
        self._btn_single.clicked.connect(lambda: self._set_mode("single"))
        self._btn_batch = QPushButton("Batch")
        self._btn_batch.setFixedHeight(28)
        self._btn_batch.setStyleSheet(CHIP_OFF)
        self._btn_batch.clicked.connect(lambda: self._set_mode("batch"))
        h.addWidget(self._btn_single)
        h.addWidget(self._btn_batch)
        h.addStretch()
        return w

    def _set_mode(self, mode):
        self._mode = mode
        self._btn_single.setStyleSheet(CHIP_ON if mode == "single" else CHIP_OFF)
        self._btn_batch.setStyleSheet(CHIP_ON if mode == "batch" else CHIP_OFF)
        self._search_block.setVisible(mode == "single")

    def _set_rank(self, rank):
        self._rank = rank
        self._rank_btn.setText(rank + "  ▾")

    def _add_to_history(self, name, rank):
        settings = QgsSettings()
        raw = settings.value("biosnap/taxon_history", "")
        items = [x for x in raw.split("||") if x] if raw else []
        entry = name + "::" + rank
        if entry in items:
            items.remove(entry)
        items.insert(0, entry)
        items = items[:10]
        settings.setValue("biosnap/taxon_history", "||".join(items))

    def _build_search_block(self):
        self._search_block = QWidget()
        self._search_block.setStyleSheet("background:transparent;")
        v = QVBoxLayout(self._search_block)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.addWidget(self._slbl("Taxon"))

        self._search_frame = QFrame()
        self._search_frame.setFixedHeight(38)
        self._search_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._search_frame.setStyleSheet(SEARCH_FRAME_NORMAL)

        h = QHBoxLayout(self._search_frame)
        h.setContentsMargins(6, 0, 4, 0)
        h.setSpacing(4)

        # Кнопка ранга
        self._rank_btn = QPushButton("Species  ▾")
        self._rank_btn.setFixedHeight(28)
        self._rank_btn.setFixedWidth(92)
        self._rank_btn.setStyleSheet(RANK_BTN)

        rank_menu = QMenu(self)
        rank_menu.setStyleSheet(RANK_MENU)
        for rank in RANKS:
            action = rank_menu.addAction(rank)
            action.triggered.connect(lambda chk, r=rank: self._set_rank(r))

        self._rank_menu_open = False

        def show_rank_menu():
            if self._rank_menu_open:
                return
            self._rank_menu_open = True
            pos = self._rank_btn.mapToGlobal(QPoint(0, self._rank_btn.height()))
            rank_menu.exec_(pos)
            QTimer.singleShot(200, lambda: setattr(self, "_rank_menu_open", False))

        self._rank_btn.clicked.connect(show_rank_menu)

        # Поле ввода
        self._search_field = QLineEdit()
        self._search_field.setStyleSheet(
            "QLineEdit { border:none; background:transparent;"
            "font-size:12px; color:#1A1A22; }"
            "QLineEdit:focus { border:none; }")
        self._search_field.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Placeholder
        self._ph_label = QLabel("Type name...  e.g. Chrysis ignita")
        self._ph_label.setStyleSheet(
            "color:#9CA3AF; font-size:12px; background:transparent;"
            "border:none; padding-left:2px;")
        self._ph_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._ph_label.setParent(self._search_field)
        self._ph_label.move(2, 0)
        self._ph_label.resize(300, 34)
        self._ph_label.show()
        self._search_field.textChanged.connect(
            lambda: self._ph_label.setVisible(not self._search_field.text()))

        # Кнопка истории
        self._hist_menu_open = False
        btn_history = QPushButton("⌛")
        btn_history.setFixedSize(28, 28)
        btn_history.setStyleSheet(
            "background-color:#ECECF0; color:#1A1A22; border:none;"
            "border-radius:6px; font-size:13px;")

        def show_history():
            if self._hist_menu_open:
                return
            settings = QgsSettings()
            raw = settings.value("biosnap/taxon_history", "")
            items = [x for x in raw.split("||") if x][:3] if raw else []
            if not items:
                return
            self._hist_menu_open = True
            hist_menu = QMenu(self)
            hist_menu.setStyleSheet(RANK_MENU)
            for item in items:
                parts = item.split("::")
                name = parts[0]
                rank = parts[1] if len(parts) > 1 else "Species"
                action = hist_menu.addAction(rank + "  —  " + name)
                action.triggered.connect(
                    lambda chk, n=name, r=rank: (
                        self._search_field.setText(n),
                        self._set_rank(r)
                    ))
            pos = btn_history.mapToGlobal(QPoint(0, btn_history.height()))
            hist_menu.exec_(pos)
            QTimer.singleShot(200, lambda: setattr(self, "_hist_menu_open", False))

        btn_history.clicked.connect(show_history)

        # Кнопка поиска
        btn_search = QPushButton("🔍")
        btn_search.setFixedSize(28, 28)
        btn_search.setStyleSheet(
            "background-color:#1A1A22; color:#FFFFFF; border:none;"
            "border-radius:6px; font-size:15px;")

        h.addWidget(self._rank_btn)
        h.addWidget(self._search_field)
        h.addWidget(btn_history)
        h.addWidget(btn_search)

        v.addWidget(self._search_frame)
        return self._search_block

    def _build_territory_block(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.addWidget(self._slbl("Territory"))
        frame = QFrame()
        frame.setFixedHeight(36)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setStyleSheet(
            "QFrame { background:#FFFFFF; border:1.5px solid #E5E7EB;"
            "border-radius:8px; }")
        h = QHBoxLayout(frame)
        h.setContentsMargins(2, 2, 2, 2)
        h.setSpacing(0)
        btn_layer = QPushButton(
            QgsApplication.getThemeIcon("mActionAddMap.svg"), "  Choose layer")
        btn_layer.setIconSize(QSize(16, 16))
        btn_layer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn_layer.setStyleSheet(
            "background-color:rgba(45,125,31,0.12); color:#2D7D1F;"
            "border:none; border-radius:6px; font-size:12px; font-weight:bold;")
        btn_draw = QPushButton(
            QgsApplication.getThemeIcon("mActionDigitizeWithCurve.svg"), "  Draw manually")
        btn_draw.setIconSize(QSize(16, 16))
        btn_draw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn_draw.setStyleSheet(
            "background-color:rgba(13,148,136,0.12); color:#0D9488;"
            "border:none; border-radius:6px; font-size:12px; font-weight:bold;")
        btn_extent = QPushButton(
            QgsApplication.getThemeIcon("mActionMapIdentification.svg"), "  Map extent")
        btn_extent.setIconSize(QSize(16, 16))
        btn_extent.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn_extent.setStyleSheet(
            "background-color:rgba(26,26,34,0.07); color:#1A1A22;"
            "border:none; border-radius:6px; font-size:12px; font-weight:bold;")
        h.addWidget(btn_layer)
        h.addWidget(btn_draw)
        h.addWidget(btn_extent)
        v.addWidget(frame)
        return w

    def _build_source_block(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.addWidget(self._slbl("Source"))
        row = QWidget()
        row.setStyleSheet("background:transparent;")
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        self._btn_gbif = QPushButton("GBIF ▾")
        self._btn_gbif.setFixedHeight(28)
        self._btn_gbif.setStyleSheet(BTN_GBIF)
        self._btn_gbif.clicked.connect(lambda: self._set_source("gbif"))
        self._btn_inat = QPushButton("iNaturalist ▾")
        self._btn_inat.setFixedHeight(28)
        self._btn_inat.setStyleSheet(BTN_INAT)
        self._btn_inat.clicked.connect(lambda: self._set_source("inat"))
        self._btn_both = QPushButton("Both")
        self._btn_both.setFixedHeight(28)
        self._btn_both.setStyleSheet(BTN_BOTH_ON)
        self._btn_both.clicked.connect(lambda: self._set_source("both"))
        h.addWidget(self._btn_gbif)
        h.addWidget(self._btn_inat)
        h.addWidget(self._btn_both)
        h.addStretch()
        v.addWidget(row)
        return w

    def _set_source(self, source):
        self._source = source
        self._btn_both.setStyleSheet(
            BTN_BOTH_ON if source == "both" else BTN_BOTH_OFF)

    def _build_year_accuracy_block(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(20)
        yw = QWidget()
        yw.setStyleSheet("background:transparent;")
        yv = QVBoxLayout(yw)
        yv.setContentsMargins(0, 0, 0, 0)
        yv.setSpacing(4)
        yv.addWidget(self._slbl("Year range"))
        yr = QWidget()
        yr.setStyleSheet("background:transparent;")
        yh = QHBoxLayout(yr)
        yh.setContentsMargins(0, 0, 0, 0)
        yh.setSpacing(6)
        self._year_from = QLineEdit("2000")
        self._year_from.setFixedSize(58, 30)
        self._year_from.setStyleSheet(FIELD)
        dash = QLabel("—")
        dash.setStyleSheet("color:#6B7280; background:transparent;")
        self._year_to = QLineEdit("2025")
        self._year_to.setFixedSize(58, 30)
        self._year_to.setStyleSheet(FIELD)
        yh.addWidget(self._year_from)
        yh.addWidget(dash)
        yh.addWidget(self._year_to)
        yv.addWidget(yr)
        aw = QWidget()
        aw.setStyleSheet("background:transparent;")
        av = QVBoxLayout(aw)
        av.setContentsMargins(0, 0, 0, 0)
        av.setSpacing(4)
        av.addWidget(self._slbl("Accuracy ≤"))
        self._accuracy = QLineEdit("10 000 m")
        self._accuracy.setFixedSize(88, 30)
        self._accuracy.setStyleSheet(FIELD)
        av.addWidget(self._accuracy)
        h.addWidget(yw)
        h.addWidget(aw)
        h.addStretch()
        return w

    def _build_toggles_block(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 4, 0, 0)
        v.setSpacing(6)

        def tog(label, checked=False):
            cb = QCheckBox(label)
            cb.setChecked(checked)
            cb.setStyleSheet(TOGGLE_ON if checked else TOGGLE_OFF)
            cb.stateChanged.connect(
                lambda s, c=cb: c.setStyleSheet(
                    TOGGLE_ON if c.isChecked() else TOGGLE_OFF))
            return cb

        for pairs in [
            [("Has coordinates", True),  ("Has taxonomy",  True)],
            [("Has media",       False), ("Fossils only",  False)],
            [("No duplicates",   True)],
        ]:
            row = QWidget()
            row.setStyleSheet("background:transparent;")
            rh = QHBoxLayout(row)
            rh.setContentsMargins(0, 0, 0, 0)
            rh.setSpacing(20)
            for label, checked in pairs:
                rh.addWidget(tog(label, checked))
            rh.addStretch()
            v.addWidget(row)
        return w

    def _build_preview_block(self):
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background:#FFFFFF; border:1px solid #E5E7EB;"
            "border-radius:8px; }")
        h = QHBoxLayout(frame)
        h.setContentsMargins(14, 10, 14, 10)
        h.setSpacing(0)
        map_box = QFrame()
        map_box.setFixedSize(58, 46)
        map_box.setStyleSheet(
            "background:#E5E7EB; border-radius:6px; border:none;")
        ml = QVBoxLayout(map_box)
        ml.setContentsMargins(0, 0, 0, 0)
        lm = QLabel("map")
        lm.setAlignment(Qt.AlignCenter)
        lm.setStyleSheet("color:#9CA3AF; font-size:10px; background:transparent;")
        ml.addWidget(lm)
        h.addWidget(map_box)
        h.addSpacing(16)
        for number, label in [("--","Records"),("--","Species"),("--","Families")]:
            col = QWidget()
            col.setStyleSheet("background:transparent;")
            cv = QVBoxLayout(col)
            cv.setContentsMargins(0, 0, 0, 0)
            cv.setSpacing(1)
            n = QLabel(number)
            n.setStyleSheet(
                "font-size:20px; font-weight:bold;"
                "color:#1A1A22; background:transparent;")
            lb = QLabel(label)
            lb.setStyleSheet(
                "font-size:10px; color:#6B7280; background:transparent;")
            cv.addWidget(n)
            cv.addWidget(lb)
            h.addWidget(col)
            h.addSpacing(24)
        h.addStretch()
        return frame

    def _build_advanced_btn(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        btn = QPushButton("⚙  Advanced settings")
        btn.setFixedHeight(28)
        btn.setStyleSheet(
            "background-color:#F3F4F6; color:#6B7280;"
            "border:1px solid #E5E7EB; border-radius:6px;"
            "padding:0 12px; font-size:11px;")
        h.addWidget(btn)
        h.addStretch()
        return w

    def _build_output_block(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.addWidget(self._slbl("Output layer"))
        self._output_field = QLineEdit("biosnap_results")
        self._output_field.setFixedHeight(30)
        self._output_field.setStyleSheet(FIELD)
        v.addWidget(self._output_field)
        return w

    def _build_format_block(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.addWidget(self._slbl("Format"))
        row = QWidget()
        row.setStyleSheet("background:transparent;")
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        self._fmt_btns = {}
        for fmt, label in [("gpkg","GeoPackage"),("shp","Shapefile"),
                            ("csv","CSV"),("mem","Memory")]:
            btn = QPushButton(label)
            btn.setFixedHeight(26)
            btn.setStyleSheet(CHIP_SM_ON if fmt == "gpkg" else CHIP_SM_OFF)
            btn.clicked.connect(lambda c, f=fmt: self._set_format(f))
            self._fmt_btns[fmt] = btn
            h.addWidget(btn)
        h.addStretch()
        v.addWidget(row)
        return w

    def _set_format(self, fmt):
        self._format = fmt
        for f, btn in self._fmt_btns.items():
            btn.setStyleSheet(CHIP_SM_ON if f == fmt else CHIP_SM_OFF)

    def _build_run_btn(self):
        btn = QPushButton("  Run BioSnap")
        btn.setFixedHeight(48)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setStyleSheet(
            "background-color:#D21C1C; color:#FFFFFF; border:none;"
            "border-radius:10px; font-size:14px; font-weight:bold;")
        return btn
