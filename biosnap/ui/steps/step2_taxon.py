# -*- coding: utf-8 -*-
import os
import sys
plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QListWidget, QSizePolicy,
    QFrame, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QCompleter,
    QStyledItemDelegate
)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal, QStringListModel, QSize, QTimer
from qgis.PyQt.QtGui import QColor, QFont, QPainter, QFontMetrics
from qgis.core import QgsSettings
from core.i18n import tr

MAX_HISTORY  = 10
SETTINGS_KEY = "biosnap/taxon_history"

RANKS = ["All", "Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species", "Subspecies"]

SOURCE_COLORS = {"gbif": "#43A047", "inat": "#81C784", "combined": "#1565C0"}

CARD_COLORS = {
    "gbif":     {"border": "#43A047", "bg": "#F1F8E9"},
    "inat":     {"border": "#81C784", "bg": "#F1F8E9"},
    "combined": {"border": "#1565C0", "bg": "#E3F2FD"},
}

STATUS_COLORS = {
    "accepted":            "#43A047",
    "synonym":             "#1565C0",
    "doubtful":            "#F57C00",
    "heterotypic synonym": "#1565C0",
    "homotypic synonym":   "#1565C0",
    "proparte synonym":    "#1565C0",
    "misapplied":          "#F57C00",
    "inactive":            "#F57C00",
}

def _status_color(status):
    if not status:
        return "#9E9E9E"
    s = status.lower()
    for key, color in STATUS_COLORS.items():
        if key in s:
            return color
    return "#9E9E9E"


class HistoryLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def _show_history(self):
        if self.completer() and self.completer().model():
            if self.completer().model().rowCount() > 0:
                self.completer().setCompletionPrefix("")
                self.completer().complete()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        QTimer.singleShot(150, self._show_history)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        QTimer.singleShot(150, self._show_history)


class TaxonDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        data = index.data(Qt.UserRole)
        if not data:
            super().paint(painter, option, index)
            return
        painter.save()
        is_selected = bool(option.state & 0x0002)
        if is_selected:
            painter.fillRect(option.rect, QColor("#E3F2FD"))
        else:
            painter.fillRect(option.rect, QColor("white"))
        name = data.get("name", "")
        auth = data.get("authorship", "")
        italic_font = QFont(option.font)
        italic_font.setItalic(True)
        italic_font.setPointSize(11)
        normal_font = QFont(option.font)
        normal_font.setItalic(False)
        normal_font.setPointSize(10)
        fm_italic = QFontMetrics(italic_font)
        fm_normal = QFontMetrics(normal_font)
        x  = option.rect.x() + 8
        cy = option.rect.y() + option.rect.height() // 2
        painter.setFont(italic_font)
        painter.setPen(QColor("#212121"))
        painter.drawText(x, cy + fm_italic.ascent() // 2, name)
        x += fm_italic.width(name) + 6
        if auth:
            painter.setFont(normal_font)
            painter.setPen(QColor("#9E9E9E"))
            painter.drawText(x, cy + fm_normal.ascent() // 2, auth)
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(200, 32)


class SearchWorker(QThread):
    results_ready = pyqtSignal(list)

    def __init__(self, query, source):
        super().__init__()
        self._query  = query
        self._source = source

    def run(self):
        from core.taxon_search import search_taxon
        self.results_ready.emit(search_taxon(self._query, self._source))


class DetailsWorker(QThread):
    details_ready = pyqtSignal(object)

    def __init__(self, key, source):
        super().__init__()
        self._key    = key
        self._source = source

    def run(self):
        from core.taxon_search import fetch_taxon_details
        self.details_ready.emit(fetch_taxon_details(self._key, self._source))


class TaxonCard(QFrame):
    def __init__(self, source, parent=None):
        super().__init__(parent)
        self._source = source
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        name_row = QHBoxLayout()
        self._icon_label = QLabel(u"\u2713")
        self._icon_label.setStyleSheet("font-size:14px; font-weight:bold; border:none; background:transparent;")
        name_row.addWidget(self._icon_label)
        self._name_label = QLabel("")
        self._name_label.setStyleSheet("font-size:13px; font-weight:bold; font-style:italic; border:none; background:transparent;")
        name_row.addWidget(self._name_label)
        self._auth_label = QLabel("")
        self._auth_label.setStyleSheet("font-size:11px; color:#616161; border:none; background:transparent;")
        name_row.addWidget(self._auth_label)
        self._rank_label = QLabel("")
        self._rank_label.setStyleSheet("font-size:10px; color:white; border-radius:4px; padding:1px 6px; border:none;")
        name_row.addWidget(self._rank_label)
        name_row.addStretch()
        layout.addLayout(name_row)
        self._meta_label = QLabel("")
        self._meta_label.setStyleSheet("font-size:11px; color:#424242; border:none; background:transparent;")
        layout.addWidget(self._meta_label)
        self._link_label = QLabel("")
        self._link_label.setStyleSheet("font-size:11px; color:#1565C0; border:none; background:transparent;")
        self._link_label.setOpenExternalLinks(True)
        layout.addWidget(self._link_label)
        self._ancestors_label = QLabel("")
        self._ancestors_label.setStyleSheet("font-size:10px; color:#757575; font-style:italic; border:none; background:transparent;")
        layout.addWidget(self._ancestors_label)
        self.set_source(source)

    def set_source(self, source):
        self._source = source
        colors = CARD_COLORS.get(source, CARD_COLORS["gbif"])
        self.setStyleSheet(
            "QFrame {{ background:{bg}; border-left:4px solid {border}; border-radius:6px; padding:4px; }}".format(
                bg=colors["bg"], border=colors["border"]
            )
        )
        self._icon_label.setStyleSheet("color:{c}; font-size:14px; font-weight:bold; border:none; background:transparent;".format(c=colors["border"]))
        self._rank_label.setStyleSheet("font-size:10px; color:white; background:{c}; border-radius:4px; padding:1px 6px; border:none;".format(c=colors["border"]))

    def update_details(self, details):
        if not details:
            return
        self._name_label.setText(details.get("name", ""))
        self._auth_label.setText(details.get("authorship", ""))
        self._rank_label.setText("[{0}]".format(details.get("rank", "").upper()))
        key    = details.get("key", "")
        status = details.get("status", "")
        meta   = "taxonKey: {0}".format(key)
        if status:
            meta += " | {0}".format(status)
        self._meta_label.setText(meta)
        url = details.get("url", "")
        if url:
            self._link_label.setText('<a href="{0}">-> {0}</a>'.format(url))
        ancestors = details.get("ancestors", [])
        if ancestors:
            self._ancestors_label.setText(" -> ".join(ancestors))


class Step2Taxon(QWidget):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self._state          = state
        self._worker         = None
        self._details_worker = None
        self._all_results    = []
        self._history        = []
        self._completer      = None
        self._load_history()
        self._build_ui()

    def _label_tag(self, text, color):
        lbl = QLabel(text)
        lbl.setFixedHeight(32)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFixedWidth(70)
        lbl.setStyleSheet(
            "QLabel {{ background:{c}; color:white; border-radius:6px; font-size:12px; font-weight:bold; padding:0 8px; }}".format(c=color)
        )
        return lbl

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)
        self._title = QLabel(tr("step2_title"))
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setStyleSheet("font-size:16px; font-weight:bold; color:#212121;")
        root.addWidget(self._title)
        self._source_label = QLabel("")
        self._source_label.setAlignment(Qt.AlignCenter)
        self._source_label.setStyleSheet("font-size:11px; color:#757575;")
        root.addWidget(self._source_label)
        root.addSpacing(4)
        color = SOURCE_COLORS.get(getattr(self._state, "data_source", "gbif"), "#43A047")
        rank_row = QHBoxLayout()
        rank_row.setSpacing(8)
        self._rank_lbl = self._label_tag("RANK", color)
        rank_row.addWidget(self._rank_lbl)
        self._rank_combo = QComboBox()
        self._rank_combo.addItems(RANKS)
        self._rank_combo.setFixedHeight(32)
        self._rank_combo.setStyleSheet(
            "QComboBox { border:1px solid #BDBDBD; border-radius:6px; padding:0 8px; font-size:12px; }"
            "QComboBox:focus { border:1px solid #1565C0; }"
            "QComboBox::drop-down { border:none; }"
        )
        self._rank_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._rank_combo.currentIndexChanged.connect(self._apply_rank_filter)
        rank_row.addWidget(self._rank_combo)
        root.addLayout(rank_row)
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        self._taxon_lbl = self._label_tag("TAXON", color)
        search_row.addWidget(self._taxon_lbl)
        self._search_field = HistoryLineEdit()
        self._search_field.setPlaceholderText("e.g. Chrysis ignita or taxon ID")
        self._search_field.setFixedHeight(32)
        self._search_field.setStyleSheet(
            "QLineEdit { border:1px solid #BDBDBD; border-radius:6px; padding:0 8px; font-size:12px; }"
            "QLineEdit:focus { border:1px solid #1565C0; }"
        )
        self._search_field.returnPressed.connect(self._do_search)
        self._search_field.focusInEvent = self._on_search_focus
        self._search_field.textEdited.connect(lambda t: self._history_popup.setVisible(False))
        self._search_field.leaveEvent = lambda e: self._hide_popup_if_not_hovered()
        self._search_field.leaveEvent = lambda e: self._hide_popup_if_not_hovered()
        search_row.addWidget(self._search_field)
        self._btn_search = QPushButton(tr("btn_search"))
        self._btn_search.setFixedSize(80, 32)
        self._btn_search.setStyleSheet(
            "QPushButton { background:#1565C0; color:white; border:none; border-radius:6px; font-size:12px; }"
            "QPushButton:hover { background:#1976D2; }"
        )
        self._btn_search.clicked.connect(self._do_search)
        search_row.addWidget(self._btn_search)
        root.addLayout(search_row)
        self._history_popup = QListWidget()
        self._history_popup.setFixedHeight(120)
        self._history_popup.setStyleSheet(
            "QListWidget { border:1px solid #E0E0E0; border-radius:4px; font-size:11px; background:white; color:#9E9E9E; }"
            "QListView::item { padding:6px 10px; }"
            "QListView::item:hover { background:#F5F5F5; }"
            "QListView::item:selected { background:#E3F2FD; color:#1565C0; }"
        )
        self._history_popup.setVisible(False)
        self._history_popup.itemClicked.connect(self._on_history_popup_clicked)
        self._history_popup.leaveEvent = lambda e: QTimer.singleShot(200, self._check_and_hide)
        self._history_popup.leaveEvent = lambda e: QTimer.singleShot(200, self._check_and_hide)
        root.addWidget(self._history_popup)
        self._taxon_card = TaxonCard(getattr(self._state, "data_source", "gbif"))
        self._taxon_card.setVisible(False)
        root.addWidget(self._taxon_card)
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("font-size:11px; color:#757575;")
        root.addWidget(self._status_label)
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["#", "Taxon", "Status", "Source"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self._table.setColumnWidth(0, 36)
        self._table.setColumnWidth(2, 110)
        self._table.setColumnWidth(3, 70)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setShowGrid(True)
        self._table.setItemDelegateForColumn(1, TaxonDelegate(self._table))
        self._table.setStyleSheet(
            "QTableWidget { border:1px solid #E0E0E0; border-radius:6px; font-size:12px; gridline-color:rgba(200,200,200,80); }"
            "QTableWidget::item { padding:4px 6px; }"
            "QTableWidget::item:selected { background:#E3F2FD; color:#1565C0; }"
            "QHeaderView::section { background:#F5F5F5; border:none; border-bottom:1px solid #E0E0E0; font-size:11px; font-weight:bold; color:#616161; padding:4px; }"
        )
        self._table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._table.cellClicked.connect(self._on_cell_clicked)
        root.addWidget(self._table)

    def _setup_completer_disabled(self):
        model = QStringListModel(self._history)
        self._completer = QCompleter(model, self._search_field)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self._completer.setMaxVisibleItems(10)
        self._completer.popup().setStyleSheet(
            "QListView { border:1px solid #BDBDBD; border-radius:4px; font-size:12px; background:white; }"
            "QListView::item { padding:6px 10px; min-height:28px; }"
            "QListView::item:hover { background:#F5F5F5; }"
            "QListView::item:selected { background:#E3F2FD; color:#1565C0; }"
        )
        self._search_field.setCompleter(self._completer)

    def _update_label_colors(self):
        source = getattr(self._state, "data_source", "gbif")
        color  = SOURCE_COLORS.get(source, "#43A047")
        style  = "QLabel {{ background:{c}; color:white; border-radius:6px; font-size:12px; font-weight:bold; padding:0 8px; }}".format(c=color)
        self._rank_lbl.setStyleSheet(style)
        self._taxon_lbl.setStyleSheet(style)

    def showEvent(self, event):
        source = getattr(self._state, "data_source", "gbif")
        labels = {
            "gbif":     "Source: GBIF",
            "inat":     "Source: iNaturalist",
            "combined": "Source: GBIF + iNaturalist",
        }
        self._source_label.setText(labels.get(source, ""))
        self._taxon_card.set_source(source)
        self._update_label_colors()
        # completer removed
        super().showEvent(event)

    def _do_search(self):
        query = self._search_field.text().strip()
        if not query:
            return
        source = getattr(self._state, "data_source", "gbif")
        self._status_label.setText("Searching...")
        self._table.setRowCount(0)
        self._all_results = []
        self._taxon_card.setVisible(False)
        self._btn_search.setEnabled(False)
        if self._worker:
            self._worker.quit()
        self._worker = SearchWorker(query, source)
        self._worker.results_ready.connect(self._on_results)
        self._worker.start()

    def _on_results(self, results):
        self._history_popup.setVisible(False)
        self._btn_search.setEnabled(True)
        self._all_results = results
        self._apply_rank_filter()

    def _apply_rank_filter(self):
        rank_filter = self._rank_combo.currentText().lower()
        filtered = self._all_results if rank_filter == "all" else [
            r for r in self._all_results if r.get("rank", "").lower() == rank_filter
        ]
        self._table.setRowCount(0)
        if not filtered:
            self._status_label.setText("No results found.")
            return
        self._status_label.setText("{0} results found.".format(len(filtered)))
        bold_font = QFont()
        bold_font.setBold(True)
        bold_font.setPointSize(10)
        self._table.setRowCount(len(filtered))
        for i, r in enumerate(filtered):
            num_item = QTableWidgetItem(str(i + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            num_item.setForeground(QColor("#9E9E9E"))
            self._table.setItem(i, 0, num_item)
            name_item = QTableWidgetItem(r.get("name", ""))
            name_item.setData(Qt.UserRole, r)
            self._table.setItem(i, 1, name_item)
            status = r.get("status", "")
            status_item = QTableWidgetItem(status if status else "-")
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(QColor(_status_color(status)))
            status_item.setFont(bold_font)
            self._table.setItem(i, 2, status_item)
            source_item = QTableWidgetItem(r.get("source", "").upper())
            source_item.setTextAlignment(Qt.AlignCenter)
            source_item.setForeground(QColor("#757575"))
            self._table.setItem(i, 3, source_item)
            self._table.setRowHeight(i, 32)

    def _on_cell_clicked(self, row, col):
        item = self._table.item(row, 1)
        if not item:
            return
        r = item.data(Qt.UserRole)
        if not r:
            return
        self._state.taxon_key  = r["key"]
        self._state.taxon_name = r["name"]
        self._state.taxon_rank = r["rank"]
        self._add_to_history(r["name"])
        self._status_label.setText("Loading details...")
        self._taxon_card.setVisible(False)
        if self._details_worker:
            self._details_worker.quit()
        source = getattr(self._state, "data_source", "gbif")
        self._details_worker = DetailsWorker(r["key"], source)
        self._details_worker.details_ready.connect(self._on_details)
        self._details_worker.start()

    def _on_details(self, details):
        self._status_label.setText("")
        if details:
            self._taxon_card.update_details(details)
            self._taxon_card.setVisible(True)
            self._state.taxon_data = details

    def _add_to_history(self, name):
        if name in self._history:
            self._history.remove(name)
        self._history.insert(0, name)
        self._history = self._history[:MAX_HISTORY]
        self._save_history()
        # completer removed

    def _load_history(self):
        settings = QgsSettings()
        val = settings.value(SETTINGS_KEY, "")
        self._history = [x for x in val.split("||") if x] if val else []

    def _save_history(self):
        settings = QgsSettings()
        settings.setValue(SETTINGS_KEY, "||".join(self._history))

    def eventFilter(self, obj, event):
        from qgis.PyQt.QtCore import QEvent
        if event.type() == QEvent.MouseButtonPress:
            if obj != self._search_field and obj != self._history_popup:
                self._history_popup.setVisible(False)
        return False

    def _hide_popup_if_not_hovered(self):
        QTimer.singleShot(200, self._check_and_hide)

    def _check_and_hide(self):
        if not self._history_popup.underMouse() and not self._search_field.underMouse():
            self._history_popup.setVisible(False)

    def _hide_popup_if_not_hovered(self):
        QTimer.singleShot(200, self._check_and_hide)

    def _check_and_hide(self):
        if not self._history_popup.underMouse() and not self._search_field.underMouse():
            self._history_popup.setVisible(False)

    def _on_search_focus(self, event):
        QLineEdit.focusInEvent(self._search_field, event)
        if self._history:
            self._history_popup.clear()
            for name in self._history:
                self._history_popup.addItem(name)
            self._history_popup.setVisible(True)

    def _on_history_popup_clicked(self, item):
        self._search_field.setText(item.text())
        self._history_popup.setVisible(False)
        self._do_search()

    def is_valid(self):
        return self._state.taxon_key is not None

    def retranslate_ui(self):
        self._title.setText(tr("step2_title"))
        self._btn_search.setText(tr("btn_search"))
