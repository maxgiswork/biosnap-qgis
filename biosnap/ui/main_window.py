import os, sys
plugin_dir = os.path.dirname(os.path.dirname(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QSizePolicy, QWidget, QPushButton,
    QLineEdit, QScrollArea, QCheckBox, QMenu,
    QStackedWidget
)
from qgis.PyQt.QtCore import Qt, QSize, QPoint, QTimer
from qgis.core import QgsApplication, QgsSettings
from ui.styles import MAIN_STYLE

CHIP_SM_ON  = ("background-color:#1A1A22; color:#FFFFFF; border:none;"
               "border-radius:10px; padding:3px 12px; font-size:11px;")
CHIP_SM_OFF = ("background-color:#ECECF0; color:#1A1A22; border:none;"
               "border-radius:10px; padding:3px 12px; font-size:11px;")
SECTION_LBL = ("font-size:10px; color:#6B7280; font-weight:bold;"
               "background:transparent; margin-bottom:2px;")
FIELD = ("border:1px solid #E5E7EB; border-radius:6px;"
         "padding:4px 8px; background:#FFFFFF; font-size:12px;")
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


class ToggleSwitch(QWidget):
    COLOR_ON  = (46, 125, 50)
    COLOR_OFF = (200, 200, 200)

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self._checked = checked
        self._anim = 1.0 if checked else 0.0
        self.setFixedSize(29, 17)
        from qgis.PyQt.QtCore import Qt as _Qt
        self.setCursor(_Qt.PointingHandCursor)
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._animate)

    def isChecked(self):
        return self._checked

    def setChecked(self, val):
        self._checked = bool(val)
        self._anim = 1.0 if self._checked else 0.0
        self.update()

    def _animate(self):
        target = 1.0 if self._checked else 0.0
        if abs(self._anim - target) < 0.08:
            self._anim = target
            self._timer.stop()
        else:
            self._anim += 0.08 if target > self._anim else -0.08
        self.update()

    def mousePressEvent(self, e):
        self._checked = not self._checked
        self._timer.start()

    def paintEvent(self, e):
        from qgis.PyQt.QtGui import QPainter, QColor, QPainterPath
        from qgis.PyQt.QtCore import Qt, QRectF, QPointF
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        r = H / 2
        t = self._anim
        ro, go, bo = self.COLOR_OFF
        rn, gn, bn = self.COLOR_ON
        rc = int(ro + t * (rn - ro))
        gc = int(go + t * (gn - go))
        bc = int(bo + t * (bn - bo))
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, W, H), r, r)
        p.fillPath(path, QColor(rc, gc, bc))
        p.setPen(Qt.NoPen)
        knob_r = r - 2
        knob_x = (2 + knob_r) + t * (W - 2 * (2 + knob_r))
        p.setBrush(QColor(255, 255, 255))
        p.drawEllipse(QPointF(knob_x, H / 2), knob_r, knob_r)
        p.end()


class ColoredToggle(ToggleSwitch):
    def __init__(self, color_hex, checked=False, parent=None):
        super().__init__(checked, parent)
        self.COLOR_ON = (
            int(color_hex[1:3], 16),
            int(color_hex[3:5], 16),
            int(color_hex[5:7], 16)
        )


class AccuracySlider(QWidget):

    MARKS = [1, 10, 25, 50, 100, 500, 1000, 2000, 5000, 10000]

    def __init__(self, min_val=1, max_val=100000, value=10000, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self._value = value
        self._drag = False
        self._settings_key = 'biosnap/accuracy_slider'
        self.setFixedHeight(36)

    def value(self):
        return self._value

    def minimumSizeHint(self):
        from qgis.PyQt.QtCore import QSize
        return QSize(0, 36)

    def sizeHint(self):
        from qgis.PyQt.QtCore import QSize
        return QSize(100, 36)

    def _tx(self):
        tw = self.width() - 20
        tx = 10
        ty = 26
        return tx, tw, ty

    def _mark_x(self, i):
        tx, tw, ty = self._tx()
        n = len(self.MARKS) - 1
        start = tx + 15
        end = tx + tw - 15
        return int(start + i * (end - start) / n)

    def _nearest_mark(self, x):
        dists = [(abs(x - self._mark_x(i)), i) for i in range(len(self.MARKS))]
        return self.MARKS[min(dists)[1]]

    def _val_to_x(self, val):
        if val in self.MARKS:
            i = self.MARKS.index(val)
            return self._mark_x(i)
        tx, tw, ty = self._tx()
        n = len(self.MARKS) - 1
        for i in range(n):
            if self.MARKS[i] <= val <= self.MARKS[i+1]:
                r = (val - self.MARKS[i]) / (self.MARKS[i+1] - self.MARKS[i])
                x1 = self._mark_x(i)
                x2 = self._mark_x(i+1)
                return int(x1 + r * (x2 - x1))
        tx, tw, ty = self._tx()
        return tx + tw if val > self.MARKS[-1] else tx

    def paintEvent(self, e):
        from qgis.PyQt.QtGui import QPainter, QColor, QPen, QFont, QPainterPath
        from qgis.PyQt.QtCore import Qt, QRectF, QPointF, QRect
        GBIF_solid = QColor('#2E7D32')
        GBIF_alpha = QColor('#4CAF50')
        GBIF_alpha.setAlpha(180)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        tx, tw, ty = self._tx()
        x = self._val_to_x(self._value)
        p.setBrush(QColor('#FFFFFF'))
        p.setPen(Qt.NoPen)
        for i in range(len(self.MARKS)):
            mx = self._mark_x(i)
            if i == 0:
                mx = tx + 15
            elif i == len(self.MARKS) - 1:
                mx = tx + tw - 15
            p.drawEllipse(QPointF(float(mx), float(ty)), 3.0, 3.0)
        pen = QPen(QColor('#9CA3AF'))
        pen.setWidth(1)
        p.setPen(pen)
        p.setBrush(QColor('#E5E7EB'))
        p.drawRoundedRect(QRectF(tx, ty - 3, tw, 6), 3, 3)
        if x > tx:
            p.save()
            p.setClipRect(QRect(tx, ty - 4, max(1, x - tx), 8))
            p.setPen(Qt.NoPen)
            p.setBrush(GBIF_alpha)
            p.drawRoundedRect(QRectF(tx, ty - 3, tw, 6), 3, 3)
            p.restore()
        p.setBrush(QColor('#FFFFFF'))
        p.setPen(Qt.NoPen)
        for i in range(1, len(self.MARKS) - 1):
            mx = self._mark_x(i)
            p.drawEllipse(QPointF(float(mx), float(ty)), 3.0, 3.0)
        p.setBrush(GBIF_solid)
        p.setPen(Qt.NoPen)
        p.drawEllipse(x - 7, ty - 7, 14, 14)
        p.setBrush(QColor('#FFFFFF'))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(float(x), float(ty)), 4.0, 4.0)
        p.setPen(QColor('#1C2B1C'))
        fnt = QFont('Segoe UI', 8)
        fnt.setBold(True)
        p.setFont(fnt)
        fm = p.fontMetrics()
        if self._value >= 1000:
            txt = f"{self._value // 1000} {(self._value % 1000):03d} m"
        else:
            txt = f"{self._value} m"
        tw2 = fm.horizontalAdvance(txt)
        lx = max(0, min(self.width() - tw2, x - tw2 // 2))
        p.drawText(lx, ty - 12, txt)
        p.end()

    def _hit(self, x):
        return abs(x - self._val_to_x(self._value)) <= 12

    def mousePressEvent(self, e):
        from qgis.PyQt.QtGui import QFont, QFontMetrics
        fnt = QFont('Segoe UI', 8)
        fnt.setBold(True)
        fm = QFontMetrics(fnt)
        tx, tw, ty = self._tx()
        x = self._val_to_x(self._value)
        if self._value >= 1000:
            txt = f"{self._value // 1000} {(self._value % 1000):03d} m"
        else:
            txt = f"{self._value} m"
        tw2 = fm.horizontalAdvance(txt)
        lx = max(0, min(self.width() - tw2, x - tw2 // 2))
        h = fm.height()
        top = ty - 12 - h
        if lx <= e.x() <= lx + tw2 and top <= e.y() <= top + h + 4:
            self._show_editor(lx, top, tw2, h)
            return
        self._drag = self._hit(e.x())

    def _show_editor(self, lx, top, w, h):
        from qgis.PyQt.QtWidgets import QLineEdit
        from qgis.PyQt.QtCore import Qt
        editor = QLineEdit(self)
        editor.setFont(__import__('qgis.PyQt.QtGui', fromlist=['QFont']).QFont('Segoe UI', 8))
        editor.setText(str(self._value))
        editor.setFixedSize(max(50, w + 8), h + 6)
        editor.move(max(0, lx - 4), max(0, top - 2))
        editor.setAlignment(Qt.AlignCenter)
        editor.setStyleSheet(
            'QLineEdit { background:#FFFFFF; border:1px solid #2D7D1F;'
            'border-radius:3px; padding:0px; font-size:8pt; font-weight:bold; }')
        editor.selectAll()
        editor.show()
        editor.setFocus()
        def commit():
            try:
                val = int(editor.text())
                self._value = max(1, min(100000, val))
                if self._settings_key:
                    from qgis.core import QgsSettings
                    QgsSettings().setValue(self._settings_key + '/value', self._value)
            except ValueError:
                pass
            editor.deleteLater()
            self.update()
        _committed = [False]
        def safe_commit():
            if not _committed[0]:
                _committed[0] = True
                commit()
        editor.editingFinished.connect(safe_commit)
        def _foe(e):
            safe_commit()
            type(editor).focusOutEvent(editor, e)
        editor.focusOutEvent = _foe

    def mouseMoveEvent(self, e):
        if self._drag:
            self._value = self._nearest_mark(e.x())
            self.update()

    def mouseReleaseEvent(self, e):
        self._drag = False
        if self._settings_key:
            from qgis.core import QgsSettings
            QgsSettings().setValue(self._settings_key + '/value', self._value)


class YearRangeSlider(QWidget):

    def __init__(self, min_year=1500, max_year=2026, start=2000, end=2026, parent=None):
        super().__init__(parent)
        self.min_year = min_year
        self.max_year = max_year
        self._start = start
        self._end = end
        self._drag = None
        self._settings_key = 'biosnap/year_slider'
        self.setFixedHeight(36)
        try:
            from qgis.core import QgsSettings
            s = QgsSettings()
            self._start = int(s.value(self._settings_key + '/start', start))
            self._end   = int(s.value(self._settings_key + '/end',   end))
        except Exception:
            pass

    def years(self):
        return self._start, self._end

    def minimumSizeHint(self):
        from qgis.PyQt.QtCore import QSize
        return QSize(0, 36)

    def sizeHint(self):
        from qgis.PyQt.QtCore import QSize
        return QSize(100, 36)

    def _tx(self):
        return 10, self.width() - 20, 26

    def _year_to_x(self, year):
        tx, tw, ty = self._tx()
        r = (year - self.min_year) / max(1, self.max_year - self.min_year)
        return int(tx + r * tw)

    def _x_to_year(self, x):
        tx, tw, ty = self._tx()
        r = max(0.0, min(1.0, (x - tx) / max(1, tw)))
        return int(round(self.min_year + r * (self.max_year - self.min_year)))

    def paintEvent(self, e):
        from qgis.PyQt.QtGui import QPainter, QColor, QPen, QFont
        from qgis.PyQt.QtCore import Qt
        GBIF_solid = QColor('#2E7D32')
        GBIF_alpha = QColor('#4CAF50')
        GBIF_alpha.setAlpha(180)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        tx, tw, ty = self._tx()
        pen = QPen(QColor('#9CA3AF'))
        pen.setWidth(1)
        p.setPen(pen)
        p.setBrush(QColor('#E5E7EB'))
        p.drawRoundedRect(tx, ty - 3, tw, 6, 3, 3)
        x1 = self._year_to_x(self._start)
        x2 = self._year_to_x(self._end)
        p.setPen(Qt.NoPen)
        p.setBrush(GBIF_alpha)
        p.drawRect(x1, ty - 3, max(0, x2 - x1), 6)
        for x in [x1, x2]:
            p.setBrush(GBIF_solid)
            p.setPen(Qt.NoPen)
            p.drawEllipse(x - 7, ty - 7, 14, 14)
            p.setBrush(QColor('#FFFFFF'))
            p.setPen(Qt.NoPen)
            p.drawEllipse(x - 3, ty - 3, 6, 6)
        p.setPen(QColor('#1C2B1C'))
        fnt = QFont('Segoe UI', 8)
        fnt.setBold(True)
        p.setFont(fnt)
        fm = p.fontMetrics()
        txt1 = str(self._start)
        txt2 = str(self._end)
        w1 = fm.horizontalAdvance(txt1)
        w2 = fm.horizontalAdvance(txt2)
        lx1 = max(0, x1 - w1 // 2)
        lx2 = x2 - w2 // 2
        if lx2 < lx1 + w1 + 6:
            mid = (x1 + x2) // 2
            lx1 = max(0, mid - w1 - 3)
            lx2 = min(self.width() - w2, mid + 3)
        p.drawText(lx1, ty - 12, txt1)
        p.drawText(lx2, ty - 12, txt2)
        p.end()

    def _hit(self, x):
        x1 = self._year_to_x(self._start)
        x2 = self._year_to_x(self._end)
        d1 = abs(x - x1)
        d2 = abs(x - x2)
        if d1 <= 10 and d2 <= 10:
            self._overlap_x = x
            return 'overlap'
        if d1 <= 10: return 'left'
        if d2 <= 10: return 'right'
        return None

    def _label_hit(self, x, y):
        from qgis.PyQt.QtGui import QFont, QFontMetrics
        fnt = QFont('Segoe UI', 8)
        fnt.setBold(True)
        fm = QFontMetrics(fnt)
        tx, tw, ty = self._tx()
        x1 = self._year_to_x(self._start)
        x2 = self._year_to_x(self._end)
        txt1 = str(self._start)
        txt2 = str(self._end)
        w1 = fm.horizontalAdvance(txt1)
        w2 = fm.horizontalAdvance(txt2)
        lx1 = max(0, x1 - w1 // 2)
        lx2 = x2 - w2 // 2
        if lx2 < lx1 + w1 + 6:
            mid = (x1 + x2) // 2
            lx1 = max(0, mid - w1 - 3)
            lx2 = min(self.width() - w2, mid + 3)
        h = fm.height()
        top = ty - 12 - h
        if lx1 <= x <= lx1 + w1 and top <= y <= top + h + 4:
            return 'left', lx1, top, w1, h
        if lx2 <= x <= lx2 + w2 and top <= y <= top + h + 4:
            return 'right', lx2, top, w2, h
        return None, 0, 0, 0, 0

    def _show_year_editor(self, side, lx, top, w, h):
        from qgis.PyQt.QtWidgets import QLineEdit
        from qgis.PyQt.QtCore import Qt
        editor = QLineEdit(self)
        editor.setFont(__import__('qgis.PyQt.QtGui', fromlist=['QFont']).QFont('Segoe UI', 8))
        editor.setText(str(self._start if side == 'left' else self._end))
        editor.setFixedSize(max(40, w + 8), h + 6)
        editor.move(max(0, lx - 4), max(0, top - 2))
        editor.setAlignment(Qt.AlignCenter)
        editor.setStyleSheet(
            'QLineEdit { background:#FFFFFF; border:1px solid #2D7D1F;'
            'border-radius:3px; padding:0px; font-size:8pt; font-weight:bold; }')
        editor.selectAll()
        editor.show()
        editor.setFocus()
        def commit():
            try:
                val = int(editor.text())
                if side == 'left':
                    self._start = max(self.min_year, min(val, self._end - 1))
                else:
                    self._end = min(self.max_year, max(val, self._start + 1))
                if self._settings_key:
                    from qgis.core import QgsSettings
                    s = QgsSettings()
                    s.setValue(self._settings_key + '/start', self._start)
                    s.setValue(self._settings_key + '/end', self._end)
            except ValueError:
                pass
            editor.deleteLater()
            self.update()
        _committed = [False]
        def safe_commit():
            if not _committed[0]:
                _committed[0] = True
                commit()
        editor.editingFinished.connect(safe_commit)
        def _foe(e):
            safe_commit()
            type(editor).focusOutEvent(editor, e)
        editor.focusOutEvent = _foe

    def mousePressEvent(self, e):
        side, lx, top, w, h = self._label_hit(e.x(), e.y())
        if side:
            self._show_year_editor(side, lx, top, w, h)
            return
        self._drag = self._hit(e.x())
        self._overlap_x = e.x()

    def mouseMoveEvent(self, e):
        if self._drag == 'overlap':
            if e.x() > self._overlap_x + 2:
                self._drag = 'right'
            elif e.x() < self._overlap_x - 2:
                self._drag = 'left'
            else:
                return
        if self._drag == 'left':
            self._start = max(self.min_year, min(self._x_to_year(e.x()), self._end - 1))
            self.update()
        elif self._drag == 'right':
            self._end = min(self.max_year, max(self._x_to_year(e.x()), self._start + 1))
            self.update()

    def mouseReleaseEvent(self, e):
        self._drag = None
        self._overlap_x = None
        if self._settings_key:
            from qgis.core import QgsSettings
            s = QgsSettings()
            s.setValue(self._settings_key + '/start', self._start)
            s.setValue(self._settings_key + '/end', self._end)


class BioSnapDialog(QDialog):

    def __init__(self, iface=None, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("BioSnap")
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setMinimumWidth(320)
        self.setMinimumHeight(560)
        self.resize(460, 720)
        self.setStyleSheet(MAIN_STYLE)
        self._mode   = "single"
        self._source = "both"
        self._format = "gpkg"
        self._rank   = "Species"

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())
        root.addWidget(self._build_mode_bar())

        self._main_stack = QStackedWidget()
        self._main_stack.setStyleSheet("background:#F6F5F3;")

        # index 0 — normal scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:#F6F5F3;")
        body = QWidget()
        body.setStyleSheet("background:#F6F5F3;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(16, 14, 16, 16)
        bl.setSpacing(8)
        bl.addWidget(self._build_search_block())
        self._divider_after_search = self._divider()
        bl.addWidget(self._divider_after_search)
        bl.addWidget(self._build_territory_block())
        bl.addWidget(self._divider())
        bl.addWidget(self._build_source_block())
        bl.addWidget(self._divider())
        bl.addWidget(self._build_year_accuracy_block())
        bl.addWidget(self._build_toggles_block())
        bl.addWidget(self._divider())
        bl.addWidget(self._build_preview_block())
        bl.addWidget(self._build_output_block())
        bl.addWidget(self._build_format_block())
        bl.addSpacing(4)
        bl.addWidget(self._build_run_btn())
        scroll.setWidget(body)
        self._main_stack.addWidget(scroll)

        # index 1 — advanced panel
        self._main_stack.addWidget(self._build_advanced_panel())

        root.addWidget(self._main_stack)
        self._set_mode("single")

    # ── MODE BAR ──────────────────────────────────────────────

    _MODE_DEFAULT = (
        "QPushButton {background:#FFFFFF; color:#1C2B1C;"
        "border:2px solid #D6D9D6; border-radius:8px;"
        "min-width:70px; max-width:70px; min-height:28px; max-height:28px;"
        "font-size:12px;}"
        "QPushButton:hover {background:rgba(46,125,50,0.06); border-color:#A5D6A7;}")
    _MODE_ACTIVE = (
        "QPushButton {background:#C8E6C9; color:#2E7D32;"
        "border:2px solid #2E7D32; border-radius:8px;"
        "min-width:70px; max-width:70px; min-height:28px; max-height:28px;"
        "font-size:12px; font-weight:600;}")
    _MODE_ADV_DEFAULT = (
        "QPushButton {background:#FFFFFF; color:#6A1B9A;"
        "border:2px solid #D6D9D6; border-radius:8px;"
        "min-width:80px; max-width:80px; min-height:28px; max-height:28px;"
        "font-size:12px;}"
        "QPushButton:hover {background:#F3E5F5; border-color:#AB47BC;}")
    _MODE_ADV_ACTIVE = (
        "QPushButton {background:#E1BEE7; color:#6A1B9A;"
        "border:2px solid #6A1B9A; border-radius:8px;"
        "min-width:80px; max-width:80px; min-height:28px; max-height:28px;"
        "font-size:12px; font-weight:600;}")

    def _build_mode_bar(self):
        bar = QFrame()
        bar.setFixedHeight(44)
        bar.setStyleSheet(
            "QFrame {background:#FFFFFF; border:none;"
            "border-bottom:1px solid #E5E7EB;}")
        h = QHBoxLayout(bar)
        h.setContentsMargins(16, 7, 16, 7)
        h.setSpacing(6)
        lbl = QLabel("Mode")
        lbl.setStyleSheet(SECTION_LBL)
        h.addWidget(lbl)
        h.addSpacing(4)
        self._btn_single = QPushButton("Single")
        self._btn_single.setStyleSheet(self._MODE_ACTIVE)
        self._btn_single.clicked.connect(lambda: self._set_mode("single"))
        self._btn_batch = QPushButton("Batch")
        self._btn_batch.setStyleSheet(self._MODE_DEFAULT)
        self._btn_batch.clicked.connect(lambda: self._set_mode("batch"))
        self._btn_advanced = QPushButton("Advanced")
        self._btn_advanced.setStyleSheet(self._MODE_ADV_DEFAULT)
        self._btn_advanced.clicked.connect(lambda: self._set_mode("advanced"))
        h.addWidget(self._btn_single)
        h.addWidget(self._btn_batch)
        h.addWidget(self._btn_advanced)
        h.addStretch()
        return bar

    def _set_mode(self, mode):
        self._btn_single.setStyleSheet(
            self._MODE_ACTIVE if mode == "single" else self._MODE_DEFAULT)
        self._btn_batch.setStyleSheet(
            self._MODE_ACTIVE if mode == "batch" else self._MODE_DEFAULT)
        self._btn_advanced.setStyleSheet(
            self._MODE_ADV_ACTIVE if mode == "advanced" else self._MODE_ADV_DEFAULT)

        if mode == "advanced":
            self._mode = "advanced"
            self._main_stack.setCurrentIndex(1)
            return

        self._main_stack.setCurrentIndex(0)
        self._mode = mode
        self._search_block.setVisible(True)
        self._search_block.setMaximumHeight(16777215)
        self._btn_add_row.setVisible(mode == "batch")
        if hasattr(self, "_divider_after_search"):
            self._divider_after_search.setVisible(True)
            self._divider_after_search.setMaximumHeight(16777215)
        if hasattr(self, "_toggles_stack"):
            idx = {"single": 0, "batch": 1}.get(mode, 0)
            self._toggles_stack.setCurrentIndex(idx)
        if hasattr(self, "_sliders_stack"):
            idx = {"single": 0, "batch": 1}.get(mode, 0)
            self._sliders_stack.setCurrentIndex(idx)
            self._year_slider     = self._year_sliders.get(mode, self._year_sliders["single"])
            self._accuracy_slider = self._accuracy_sliders.get(mode, self._accuracy_sliders["single"])
        if mode == "batch":
            self._restore_batch_state()
        else:
            self._save_batch_state()
            for row in list(self._extra_rows):
                self._remove_search_row(row)

    # ── ADVANCED PANEL ────────────────────────────────────────

    _ADV_SOURCES = [
        {"key": "cites", "title": "CITES",
         "subtitle": "International Trade in Endangered Species",
         "color": "#7C3AED",
         "chips": [
             {"label": "App. I",   "ckey": "app1", "default": True},
             {"label": "App. II",  "ckey": "app2", "default": True},
             {"label": "App. III", "ckey": "app3", "default": False},
         ], "count": 318},
        {"key": "bern", "title": "Bern Convention",
         "subtitle": "European Wildlife and Natural Habitats",
         "color": "#1565C0",
         "chips": [
             {"label": "App. I",   "ckey": "app1", "default": False},
             {"label": "App. II",  "ckey": "app2", "default": True},
             {"label": "App. III", "ckey": "app3", "default": True},
         ], "count": 204},
        {"key": "bonn", "title": "Bonn Convention",
         "subtitle": "Migratory Species of Wild Animals",
         "color": "#2E7D32",
         "chips": [
             {"label": "App. I",  "ckey": "app1", "default": True},
             {"label": "App. II", "ckey": "app2", "default": False},
         ], "count": 87},
        {"key": "redbook_ua", "title": "Red Book of Ukraine",
         "subtitle": "National Red List",
         "color": "#C62828",
         "chips": [
             {"label": "CR", "ckey": "cr", "default": True,  "chip_color": "#C62828"},
             {"label": "EN", "ckey": "en", "default": True,  "chip_color": "#E65100"},
             {"label": "VU", "ckey": "vu", "default": True,  "chip_color": "#F9A825"},
             {"label": "NT", "ckey": "nt", "default": False, "chip_color": "#558B2F"},
             {"label": "LC", "ckey": "lc", "default": False, "chip_color": "#1565C0"},
         ], "count": 542},
    ]

    _CSV_SLOT_COLORS = ["#7C3AED", "#1565C0", "#2E7D32", "#C62828"]

    def _build_advanced_panel(self):
        self._adv_tab_btns    = {}
        self._adv_tab_idx     = {}
        self._adv_src_toggles = {}
        self._adv_src_chips   = {}
        self._csv_slots       = []
        panel = QWidget()
        panel.setStyleSheet("background:#F6F5F3;")
        v = QVBoxLayout(panel)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(self._build_adv_tab_bar())
        self._adv_stack = QStackedWidget()
        self._adv_stack.setStyleSheet("background:#F6F5F3;")
        tabs = [
            ("APIs",  self._build_adv_placeholder("APIs")),
            ("Lists", self._build_adv_lists_tab()),
            ("Tools", self._build_adv_placeholder("Tools")),
            ("About", self._build_adv_placeholder("About")),
        ]
        for i, (name, widget) in enumerate(tabs):
            self._adv_stack.addWidget(widget)
            self._adv_tab_idx[name] = i
        v.addWidget(self._adv_stack)
        self._adv_switch_tab("Lists")
        self._adv_load_settings()
        return panel

    def _build_adv_tab_bar(self):
        bar = QFrame()
        bar.setFixedHeight(38)
        bar.setStyleSheet(
            "QFrame {background:#FFFFFF; border:none;"
            "border-bottom:1px solid #E5E7EB;}")
        bh = QHBoxLayout(bar)
        bh.setContentsMargins(16, 0, 0, 0)
        bh.setSpacing(0)
        for tab in ["APIs", "Lists", "Tools", "About"]:
            btn = QPushButton(tab)
            btn.setFixedHeight(38)
            btn.setStyleSheet(self._adv_tab_css(False))
            btn.clicked.connect(lambda c, t=tab: self._adv_switch_tab(t))
            self._adv_tab_btns[tab] = btn
            bh.addWidget(btn)
        bh.addStretch()
        return bar

    def _adv_tab_css(self, active):
        if active:
            return ("QPushButton {background:transparent; color:#1C2B1C;"
                    "border:none; border-bottom:2px solid #2E7D32;"
                    "font-size:12px; font-weight:600; padding:0 14px; min-height:38px;}")
        return ("QPushButton {background:transparent; color:#5C6B5C;"
                "border:none; border-bottom:2px solid transparent;"
                "font-size:12px; padding:0 14px; min-height:38px;}"
                "QPushButton:hover {color:#1C2B1C;}")

    def _adv_switch_tab(self, tab):
        for t, b in self._adv_tab_btns.items():
            b.setStyleSheet(self._adv_tab_css(t == tab))
        self._adv_stack.setCurrentIndex(self._adv_tab_idx.get(tab, 0))

    def _build_adv_placeholder(self, name):
        w = QWidget()
        w.setStyleSheet("background:#F6F5F3;")
        v = QVBoxLayout(w)
        v.setAlignment(Qt.AlignCenter)
        lb = QLabel(name + "\n(coming soon)")
        lb.setAlignment(Qt.AlignCenter)
        lb.setStyleSheet("color:#9CA3AF; font-size:13px; background:transparent;")
        v.addWidget(lb)
        return w

    # ── LISTS TAB (grid layout) ───────────────────────────────

    _CARD_H = 110

    def _build_adv_lists_tab(self):
        outer = QWidget()
        outer.setStyleSheet("background:#F6F5F3;")
        ov = QVBoxLayout(outer)
        ov.setContentsMargins(0, 0, 0, 0)
        ov.setSpacing(0)
        hint = QLabel("Your custom lists \u2014 loaded from CSV, used as filters")
        hint.setStyleSheet(
            "font-size:11px; color:#5C6B5C; background:#FFFFFF;"
            "padding:6px 16px; border-bottom:1px solid #E5E7EB;")
        ov.addWidget(hint)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:#F6F5F3;")
        content = QWidget()
        content.setStyleSheet("background:#F6F5F3;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(12, 12, 12, 12)
        cl.setSpacing(8)
        # column headers
        hdr = QWidget()
        hdr.setStyleSheet("background:transparent;")
        hh = QHBoxLayout(hdr)
        hh.setContentsMargins(0, 0, 0, 2)
        hh.setSpacing(8)
        lbl_l = QLabel("Official sources")
        lbl_l.setStyleSheet(SECTION_LBL)
        lbl_r = QLabel("Custom CSV lists")
        lbl_r.setStyleSheet(SECTION_LBL)
        hh.addWidget(lbl_l, 1)
        hh.addWidget(lbl_r, 1)
        cl.addWidget(hdr)
        # 4 rows
        self._csv_slot_widgets = []
        for i, src in enumerate(self._ADV_SOURCES):
            row_w = QWidget()
            row_w.setStyleSheet("background:transparent;")
            row_h = QHBoxLayout(row_w)
            row_h.setContentsMargins(0, 0, 0, 0)
            row_h.setSpacing(8)
            row_h.addWidget(self._build_adv_src_card_compact(src), 1)
            sw = self._build_csv_slot(i)
            self._csv_slot_widgets.append(sw)
            row_h.addWidget(sw, 1)
            cl.addWidget(row_w)
        # bottom bar
        cl.addSpacing(4)
        bar_w = QWidget()
        bar_w.setStyleSheet("background:transparent;")
        bar_h = QHBoxLayout(bar_w)
        bar_h.setContentsMargins(0, 0, 0, 0)
        bar_h.setSpacing(8)
        btn_reset = QPushButton("Reset defaults")
        btn_reset.setFixedHeight(30)
        btn_reset.setStyleSheet(
            "QPushButton {background:#FFFFFF; color:#5C6B5C;"
            "border:1px solid #D6D9D6; border-radius:6px;"
            "font-size:11px; padding:0 12px;}"
            "QPushButton:hover {background:#F1F8E9; border-color:#A5D6A7;}")
        btn_reset.clicked.connect(self._adv_reset_defaults)
        btn_save = QPushButton("Save")
        btn_save.setFixedHeight(30)
        btn_save.setStyleSheet(
            "QPushButton {background:#2E7D32; color:#FFFFFF;"
            "border:none; border-radius:6px;"
            "font-size:11px; font-weight:600; padding:0 20px;}"
            "QPushButton:hover {background:#388E3C;}"
            "QPushButton:pressed {background:#1B5E20;}")
        btn_save.clicked.connect(self._adv_save_settings)
        bar_h.addWidget(btn_reset)
        bar_h.addStretch()
        bar_h.addWidget(btn_save)
        cl.addWidget(bar_w)
        cl.addStretch()
        scroll.setWidget(content)
        ov.addWidget(scroll)
        return outer

    def _build_adv_src_card_compact(self, src):
        key   = src["key"]
        color = src["color"]
        card  = QFrame()
        card.setStyleSheet(
            "QFrame {background:#FFFFFF; border:1px solid #D6D9D6; border-radius:6px;}")
        card.setFixedHeight(self._CARD_H)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        v = QVBoxLayout(card)
        v.setContentsMargins(10, 8, 8, 8)
        v.setSpacing(4)
        # row 1: title + toggle
        tr = QWidget(); tr.setStyleSheet("background:transparent;")
        th = QHBoxLayout(tr); th.setContentsMargins(0,0,0,0); th.setSpacing(4)
        lt = QLabel(src["title"])
        lt.setStyleSheet(
            "font-size:11px; font-weight:600; color:#1C2B1C; background:transparent;")
        tog = ColoredToggle(color, checked=True)
        th.addWidget(lt); th.addStretch(); th.addWidget(tog)
        v.addWidget(tr)
        self._adv_src_toggles[key] = tog
        # row 2: subtitle
        ls = QLabel(src["subtitle"])
        ls.setStyleSheet("font-size:10px; color:#9CA3AF; background:transparent;")
        ls.setWordWrap(False)
        v.addWidget(ls)
        # row 3: chips
        cr = QWidget(); cr.setStyleSheet("background:transparent;")
        ch = QHBoxLayout(cr); ch.setContentsMargins(0,0,0,0); ch.setSpacing(4)
        self._adv_src_chips[key] = {}
        for cd in src["chips"]:
            ckey = cd["ckey"]
            clr  = cd.get("chip_color", color)
            btn  = QPushButton(cd["label"])
            btn.setFixedHeight(20)
            btn.setProperty("active", cd["default"])
            btn.setStyleSheet(self._adv_chip_css(clr, cd["default"]))
            btn.clicked.connect(lambda c, b=btn, cl=clr: self._adv_toggle_chip(b, cl))
            self._adv_src_chips[key][ckey] = btn
            ch.addWidget(btn)
        ch.addStretch()
        v.addWidget(cr)
        # row 4: Update + count
        act = QWidget(); act.setStyleSheet("background:transparent;")
        ah = QHBoxLayout(act); ah.setContentsMargins(0,2,0,0); ah.setSpacing(6)
        btn_upd = QPushButton("\u21bb Update")
        btn_upd.setFixedHeight(22)
        btn_upd.setStyleSheet(
            "QPushButton {background:#F6F5F3; color:#5C6B5C;"
            "border:1px solid #D6D9D6; border-radius:4px;"
            "font-size:10px; padding:0 8px;}"
            "QPushButton:hover {background:#F1F8E9; border-color:#A5D6A7; color:#2E7D32;}")
        btn_upd.clicked.connect(lambda c, k=key: self._adv_update_source(k))
        cnt_lbl = QLabel(str(src["count"]) + " species")
        cnt_lbl.setStyleSheet("font-size:10px; color:#9CA3AF; background:transparent;")
        cnt_lbl.setObjectName("src_count_" + key)
        ah.addWidget(btn_upd); ah.addWidget(cnt_lbl); ah.addStretch()
        v.addWidget(act)
        return card

    def _adv_update_source(self, key):
        pass

    def _build_csv_slot(self, idx):
        color = self._CSV_SLOT_COLORS[idx]
        slot_data = {"path": None, "name": "", "count": 0, "enabled": True}
        self._csv_slots.append(slot_data)
        container = QWidget()
        container.setStyleSheet("background:transparent;")
        container.setFixedHeight(self._CARD_H)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cv = QVBoxLayout(container)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(0)
        # empty state
        empty = QFrame()
        empty.setObjectName("csv_empty_" + str(idx))
        empty.setStyleSheet(
            "QFrame {background:#FFFFFF; border:1px dashed #D6D9D6; border-radius:6px;}")
        empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        el = QVBoxLayout(empty)
        el.setAlignment(Qt.AlignCenter)
        el.setSpacing(3)
        plus = QLabel("+")
        plus.setAlignment(Qt.AlignCenter)
        plus.setStyleSheet("font-size:20px; color:#D6D9D6; background:transparent;")
        lcsv = QLabel("Load CSV")
        lcsv.setAlignment(Qt.AlignCenter)
        lcsv.setStyleSheet("font-size:11px; color:#9CA3AF; background:transparent;")
        el.addWidget(plus); el.addWidget(lcsv)
        empty.mousePressEvent = lambda e, i=idx: self._csv_load(i)
        empty.setCursor(Qt.PointingHandCursor)
        # loaded state
        loaded = QFrame()
        loaded.setObjectName("csv_loaded_" + str(idx))
        loaded.setStyleSheet(
            "QFrame {background:#FFFFFF; border:1px solid #D6D9D6;"
            "border-top:3px solid " + color + "; border-radius:6px;}")
        loaded.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        loaded.setVisible(False)
        lv = QVBoxLayout(loaded)
        lv.setContentsMargins(10, 8, 8, 8)
        lv.setSpacing(4)
        tr2 = QWidget(); tr2.setStyleSheet("background:transparent;")
        th2 = QHBoxLayout(tr2); th2.setContentsMargins(0,0,0,0); th2.setSpacing(4)
        name_lbl = QLabel("")
        name_lbl.setObjectName("csv_name_" + str(idx))
        name_lbl.setStyleSheet(
            "font-size:11px; font-weight:600; color:#1C2B1C; background:transparent;")
        tog2 = ColoredToggle(color, checked=True)
        th2.addWidget(name_lbl); th2.addStretch(); th2.addWidget(tog2)
        lv.addWidget(tr2)
        slot_data["toggle"] = tog2
        slot_data["name_lbl"] = name_lbl
        meta_w = QWidget(); meta_w.setStyleSheet("background:transparent;")
        meta_h = QHBoxLayout(meta_w)
        meta_h.setContentsMargins(0,0,0,0); meta_h.setSpacing(6)
        taxa_badge = QLabel("0 taxa")
        taxa_badge.setObjectName("csv_badge_" + str(idx))
        taxa_badge.setFixedHeight(18)
        taxa_badge.setStyleSheet(
            "background:" + color + "; color:#FFFFFF;"
            "border-radius:9px; font-size:10px; font-weight:600; padding:0 7px;")
        from_lbl = QLabel("from CSV")
        from_lbl.setStyleSheet("font-size:10px; color:#9CA3AF; background:transparent;")
        meta_h.addWidget(taxa_badge); meta_h.addWidget(from_lbl); meta_h.addStretch()
        lv.addWidget(meta_w)
        slot_data["taxa_badge"] = taxa_badge
        lv.addStretch()
        act_w = QWidget(); act_w.setStyleSheet("background:transparent;")
        act_h = QHBoxLayout(act_w)
        act_h.setContentsMargins(0,0,0,0); act_h.setSpacing(5)
        for label, slot_fn in [("\u21c4 Rename", self._csv_rename),
                                ("\u21bb Reload", self._csv_reload)]:
            b = QPushButton(label)
            b.setFixedHeight(22)
            b.setStyleSheet(
                "QPushButton {background:#F6F5F3; color:#5C6B5C;"
                "border:1px solid #D6D9D6; border-radius:4px;"
                "font-size:10px; padding:0 8px;}"
                "QPushButton:hover {background:#F1F8E9; border-color:#A5D6A7; color:#2E7D32;}")
            b.clicked.connect(lambda c, fn=slot_fn, i=idx: fn(i))
            act_h.addWidget(b)
        btn_del = QPushButton("\u00d7 Delete")
        btn_del.setFixedHeight(22)
        btn_del.setStyleSheet(
            "QPushButton {background:#FEF2F2; color:#C62828;"
            "border:1px solid #FECACA; border-radius:4px;"
            "font-size:10px; padding:0 8px;}"
            "QPushButton:hover {background:#FEE2E2;}")
        btn_del.clicked.connect(lambda c, i=idx: self._csv_delete(i))
        act_h.addStretch(); act_h.addWidget(btn_del)
        lv.addWidget(act_w)
        cv.addWidget(empty)
        cv.addWidget(loaded)
        slot_data["empty_w"]  = empty
        slot_data["loaded_w"] = loaded
        return container

    def _csv_load(self, idx):
        from qgis.PyQt.QtWidgets import QFileDialog, QInputDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Load CSV list", "", "CSV files (*.csv);;All files (*)")
        if not path:
            return
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = [l.strip() for l in f if l.strip()]
            count = len(lines)
        except Exception:
            count = 0
        import os
        default_name = os.path.splitext(os.path.basename(path))[0]
        name, ok = QInputDialog.getText(
            self, "List name", "Name for this list:", text=default_name)
        if not ok or not name:
            name = default_name
        slot = self._csv_slots[idx]
        slot["path"]  = path
        slot["name"]  = name
        slot["count"] = count
        self._csv_refresh_slot(idx)

    def _csv_reload(self, idx):
        slot = self._csv_slots[idx]
        if not slot.get("path"):
            return
        try:
            with open(slot["path"], encoding="utf-8", errors="replace") as f:
                lines = [l.strip() for l in f if l.strip()]
            slot["count"] = len(lines)
        except Exception:
            slot["count"] = 0
        self._csv_refresh_slot(idx)

    def _csv_delete(self, idx):
        slot = self._csv_slots[idx]
        slot["path"]  = None
        slot["name"]  = ""
        slot["count"] = 0
        self._csv_refresh_slot(idx)

    def _csv_rename(self, idx):
        from qgis.PyQt.QtWidgets import QInputDialog
        slot = self._csv_slots[idx]
        name, ok = QInputDialog.getText(
            self, "Rename list", "New name:", text=slot.get("name", ""))
        if ok and name:
            slot["name"] = name
            self._csv_refresh_slot(idx)

    def _csv_refresh_slot(self, idx):
        slot = self._csv_slots[idx]
        has = bool(slot.get("path"))
        slot["empty_w"].setVisible(not has)
        slot["loaded_w"].setVisible(has)
        if has:
            slot["name_lbl"].setText(slot["name"])
            slot["taxa_badge"].setText(str(slot["count"]) + " taxa")

    def _adv_chip_css(self, color, active):
        if active:
            return ("QPushButton {background:" + color + "; color:#FFFFFF;"
                    "border:none; border-radius:8px;"
                    "padding:0 6px; font-size:10px; font-weight:600; min-height:20px;}")
        return ("QPushButton {background:#FFFFFF; color:#5C6B5C;"
                "border:1px solid #D6D9D6; border-radius:8px;"
                "padding:0 6px; font-size:10px; min-height:20px;}"
                "QPushButton:hover {border-color:" + color + "; color:" + color + ";}")

    def _adv_toggle_chip(self, btn, color):
        active = not btn.property("active")
        btn.setProperty("active", active)
        btn.setStyleSheet(self._adv_chip_css(color, active))

    def _adv_save_settings(self):
        import json
        s = QgsSettings()
        for src in self._ADV_SOURCES:
            k = src["key"]
            tog = self._adv_src_toggles.get(k)
            if tog:
                s.setValue("biosnap/sources/" + k + "/enabled", tog.isChecked())
            for cd in src["chips"]:
                btn = self._adv_src_chips.get(k, {}).get(cd["ckey"])
                if btn:
                    s.setValue("biosnap/sources/" + k + "/" + cd["ckey"],
                               btn.property("active"))
        csv_data = []
        for slot in self._csv_slots:
            csv_data.append({
                "path":  slot.get("path", ""),
                "name":  slot.get("name", ""),
                "count": slot.get("count", 0),
            })
        s.setValue("biosnap/csv_lists", json.dumps(csv_data, ensure_ascii=False))

    def _adv_load_settings(self):
        import json
        s = QgsSettings()
        for src in self._ADV_SOURCES:
            k = src["key"]
            tog = self._adv_src_toggles.get(k)
            if tog:
                v = s.value("biosnap/sources/" + k + "/enabled", True)
                tog.setChecked(v in (True, "true", "True", 1, "1"))
            for cd in src["chips"]:
                btn = self._adv_src_chips.get(k, {}).get(cd["ckey"])
                if btn:
                    v = s.value("biosnap/sources/" + k + "/" + cd["ckey"],
                                cd["default"])
                    active = v in (True, "true", "True", 1, "1")
                    clr = cd.get("chip_color", src["color"])
                    btn.setProperty("active", active)
                    btn.setStyleSheet(self._adv_chip_css(clr, active))
        raw = s.value("biosnap/csv_lists", "")
        if raw:
            try:
                csv_data = json.loads(raw)
                for i, d in enumerate(csv_data[:4]):
                    if d.get("path"):
                        self._csv_slots[i]["path"]  = d["path"]
                        self._csv_slots[i]["name"]  = d.get("name", "")
                        self._csv_slots[i]["count"] = d.get("count", 0)
                        self._csv_refresh_slot(i)
            except Exception:
                pass

    def _adv_reset_defaults(self):
        for src in self._ADV_SOURCES:
            k = src["key"]
            tog = self._adv_src_toggles.get(k)
            if tog:
                tog.setChecked(True)
            for cd in src["chips"]:
                btn = self._adv_src_chips.get(k, {}).get(cd["ckey"])
                if btn:
                    clr = cd.get("chip_color", src["color"])
                    btn.setProperty("active", cd["default"])
                    btn.setStyleSheet(self._adv_chip_css(clr, cd["default"]))

    # ── UTILITIES ─────────────────────────────────────────────

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(
            "color:#E5E7EB; background:#E5E7EB; border:none; max-height:1px;")
        return line

    def showEvent(self, e):
        super().showEvent(e)
        self._update_slider_width()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._update_slider_width()

    def _update_slider_width(self):
        pass

    def _slbl(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(SECTION_LBL)
        return lbl

    # ── HEADER ────────────────────────────────────────────────

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
            '<span style="color:#FFFFFF;">ioSnap</span></span>')
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

    # ── SEARCH BLOCK ──────────────────────────────────────────

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
        self._rank_btn = QPushButton("Species  \u25be")
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
        self._search_field = QLineEdit()
        self._search_field.setStyleSheet(
            "QLineEdit { border:none; background:transparent;"
            "font-size:12px; color:#1A1A22; }"
            "QLineEdit:focus { border:none; }")
        self._search_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._ph_label = QLabel("Type name e.g. Chrysis ignita")
        self._ph_label.setStyleSheet(
            "color:#AAAAAA; font-size:12px; font-style:italic;"
            "background:transparent; border:none; padding-left:2px;")
        self._ph_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._ph_label.setParent(self._search_field)
        self._ph_label.move(2, 0)
        self._ph_label.resize(300, 34)
        self._ph_label.show()
        self._search_field.textChanged.connect(
            lambda: self._ph_label.setVisible(not self._search_field.text()))
        self._hist_menu_open = False
        btn_history = QPushButton("\u231b")
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
                action = hist_menu.addAction(rank + "  \u2014  " + name)
                action.triggered.connect(
                    lambda chk, n=name, r=rank: (
                        self._search_field.setText(n),
                        self._set_rank(r)))
            pos = btn_history.mapToGlobal(QPoint(0, btn_history.height()))
            hist_menu.exec_(pos)
            QTimer.singleShot(200, lambda: setattr(self, "_hist_menu_open", False))
        btn_history.clicked.connect(show_history)
        btn_search = QPushButton("\U0001f50d")
        btn_search.setFixedSize(28, 28)
        btn_search.setStyleSheet(
            "background-color:#2E7D32; color:#FFFFFF; border:none;"
            "border-radius:6px; font-size:15px;")
        btn_add = QPushButton("+")
        btn_add.setFixedSize(28, 28)
        btn_add.setStyleSheet(
            "QPushButton {background:#E3F2FD; color:#1565C0; border:none;"
            "border-radius:6px; font-size:16px; font-weight:bold;}"
            "QPushButton:hover {background:#BBDEFB;}")
        btn_add.setVisible(False)
        btn_add.clicked.connect(lambda: self._add_search_row())
        self._btn_add_row = btn_add
        h.addWidget(self._rank_btn)
        h.addWidget(self._search_field)
        h.addWidget(btn_history)
        h.addWidget(btn_search)
        h.addWidget(btn_add)
        v.addWidget(self._search_frame)
        self._extra_rows = []
        return self._search_block

    def _add_search_row(self, rank="Species", text=""):
        row_frame = QFrame()
        row_frame.setFixedHeight(38)
        row_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row_frame.setStyleSheet(
            "QFrame { background:#FFFFFF; border:1.5px solid #D6D9D6;"
            "border-radius:8px; }")
        h = QHBoxLayout(row_frame)
        h.setContentsMargins(6, 0, 4, 0)
        h.setSpacing(4)
        rank_val = [rank]
        rank_btn = QPushButton(rank + "  \u25be")
        rank_btn.setFixedHeight(28)
        rank_btn.setFixedWidth(92)
        rank_btn.setStyleSheet(RANK_BTN)
        menu = QMenu(self)
        menu.setStyleSheet(RANK_MENU)
        for r in RANKS:
            a = menu.addAction(r)
            a.triggered.connect(lambda chk, rb=rank_btn, rv=r: (
                rb.setText(rv + "  \u25be"), rank_val.__setitem__(0, rv)))
        rank_btn.clicked.connect(
            lambda: menu.exec_(rank_btn.mapToGlobal(QPoint(0, rank_btn.height()))))
        field = QLineEdit()
        field.setStyleSheet(
            "QLineEdit { border:none; background:transparent;"
            "font-size:12px; color:#1C2B1C; }"
            "QLineEdit:focus { border:none; }")
        field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ph = QLabel("Type name e.g. Chrysura trimaculata")
        ph.setStyleSheet(
            "color:#AAAAAA; font-size:12px; font-style:italic;"
            "background:transparent; border:none; padding-left:2px;")
        ph.setAttribute(Qt.WA_TransparentForMouseEvents)
        ph.setParent(field)
        ph.move(2, 0)
        ph.resize(300, 34)
        ph.show()
        field.textChanged.connect(lambda: ph.setVisible(not field.text()))
        if text:
            field.setText(text)
            ph.setVisible(False)
        btn_search = QPushButton("\U0001f50d")
        btn_search.setFixedSize(28, 28)
        btn_search.setStyleSheet(
            "background-color:#2E7D32; color:#FFFFFF; border:none;"
            "border-radius:6px; font-size:15px;")
        btn_remove = QPushButton("\u2212")
        btn_remove.setFixedSize(28, 28)
        btn_remove.setStyleSheet(
            "background-color:#D6D9D6; color:#5C6B5C; border:none;"
            "border-radius:6px; font-size:16px; font-weight:bold;")
        btn_remove.clicked.connect(lambda: self._remove_search_row(row_frame))
        h.addWidget(rank_btn)
        h.addWidget(field)
        h.addWidget(btn_search)
        h.addWidget(btn_remove)
        self._search_block.setUpdatesEnabled(False)
        self._search_block.layout().addWidget(row_frame)
        self._extra_rows.append(row_frame)
        self._search_block.setUpdatesEnabled(True)
        row_frame.setVisible(True)

    def _remove_search_row(self, row_frame):
        if row_frame in self._extra_rows:
            self._extra_rows.remove(row_frame)
        row_frame.setParent(None)
        row_frame.deleteLater()

    def _set_rank(self, rank):
        self._rank = rank
        self._rank_btn.setText(rank + "  \u25be")

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

    def _save_batch_state(self):
        import json
        rows = [{"rank": self._rank, "text": self._search_field.text()}]
        for row_frame in self._extra_rows:
            hh = row_frame.layout()
            rank_btn = hh.itemAt(0).widget()
            field    = hh.itemAt(1).widget()
            rank_text = rank_btn.text().replace("  \u25be", "").strip()
            rows.append({"rank": rank_text, "text": field.text()})
        QgsSettings().setValue("biosnap/batch_rows",
                               json.dumps(rows, ensure_ascii=False))

    def _restore_batch_state(self):
        import json
        raw = QgsSettings().value("biosnap/batch_rows", "")
        if not raw:
            return
        try:
            rows = json.loads(raw)
        except Exception:
            return
        if not rows:
            return
        first = rows[0]
        self._search_field.setText(first.get("text", ""))
        self._set_rank(first.get("rank", "Species"))
        for row in rows[1:]:
            self._add_search_row(
                rank=row.get("rank", "Species"),
                text=row.get("text", ""))

    # ── TERRITORY ─────────────────────────────────────────────

    _TERR_DEFAULT = (
        "QPushButton {background:#FFFFFF; color:#1C2B1C;"
        "border:1px solid #D6D9D6; border-radius:6px;"
        "padding:4px 6px; font-size:12px;}"
        "QPushButton:hover {background:#BBDEFB; border-color:#1565C0; color:#1565C0;}")
    _TERR_ACTIVE = (
        "QPushButton {background:#E3F2FD; color:#1565C0;"
        "border:2px solid #1565C0; border-radius:6px;"
        "padding:4px 6px; font-size:12px; font-weight:600;}")

    def _build_territory_block(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.addWidget(self._slbl("Territory"))
        frame = QFrame()
        frame.setFixedHeight(38)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setStyleSheet("QFrame { background:transparent; border:none; }")
        h = QHBoxLayout(frame)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        self._btn_layer = QPushButton(
            QgsApplication.getThemeIcon("mActionAddMap.svg"), "  Choose layer")
        self._btn_layer.setIconSize(QSize(16, 16))
        self._btn_layer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._btn_layer.setStyleSheet(self._TERR_ACTIVE)
        self._btn_layer.clicked.connect(lambda: self._set_territory("layer"))
        self._btn_draw = QPushButton(
            QgsApplication.getThemeIcon("mActionDigitizeWithCurve.svg"), "  Draw manually")
        self._btn_draw.setIconSize(QSize(16, 16))
        self._btn_draw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._btn_draw.setStyleSheet(self._TERR_DEFAULT)
        self._btn_draw.clicked.connect(lambda: self._set_territory("draw"))
        self._btn_extent = QPushButton(
            QgsApplication.getThemeIcon("mActionMapIdentification.svg"), "  Map extent")
        self._btn_extent.setIconSize(QSize(16, 16))
        self._btn_extent.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._btn_extent.setStyleSheet(self._TERR_DEFAULT)
        self._btn_extent.clicked.connect(lambda: self._set_territory("extent"))
        h.addWidget(self._btn_layer)
        h.addWidget(self._btn_draw)
        h.addWidget(self._btn_extent)
        v.addWidget(frame)
        return w

    def _set_territory(self, mode):
        self._territory_mode = mode
        mapping = {
            "layer":  (self._TERR_ACTIVE,   self._TERR_DEFAULT, self._TERR_DEFAULT),
            "draw":   (self._TERR_DEFAULT,   self._TERR_ACTIVE,  self._TERR_DEFAULT),
            "extent": (self._TERR_DEFAULT,   self._TERR_DEFAULT, self._TERR_ACTIVE),
        }
        a, b, c = mapping[mode]
        self._btn_layer.setStyleSheet(a)
        self._btn_draw.setStyleSheet(b)
        self._btn_extent.setStyleSheet(c)

    # ── SOURCE ────────────────────────────────────────────────

    _SRC_DEFAULT = (
        "QPushButton {background:#FFFFFF; color:#1C2B1C;"
        "border:1px solid #D6D9D6; border-radius:6px;"
        "padding:4px 10px; font-size:12px;}"
        "QPushButton:hover {background:rgba(46,125,50,0.06); border-color:#A5D6A7;}")
    _SRC_GBIF = (
        "QPushButton {background:#C8E6C9; color:#2E7D32;"
        "border:2px solid #2E7D32; border-radius:6px;"
        "padding:4px 10px; font-size:12px; font-weight:600;}")
    _SRC_INAT = (
        "QPushButton {background:#E3F2FD; color:#1565C0;"
        "border:2px solid #1565C0; border-radius:6px;"
        "padding:4px 10px; font-size:12px; font-weight:600;}")
    _SRC_BOTH = (
        "QPushButton {background:#F0F0F0; color:#1C2B1C;"
        "border:2px solid #1C2B1C; border-radius:6px;"
        "padding:4px 10px; font-size:12px; font-weight:600;}")

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
        self._btn_gbif = QPushButton("GBIF")
        self._btn_gbif.setFixedHeight(30)
        self._btn_gbif.setStyleSheet(self._SRC_GBIF)
        self._btn_gbif.clicked.connect(lambda: self._set_source("gbif"))
        self._btn_inat = QPushButton("iNaturalist")
        self._btn_inat.setFixedHeight(30)
        self._btn_inat.setStyleSheet(self._SRC_DEFAULT)
        self._btn_inat.clicked.connect(lambda: self._set_source("inat"))
        self._btn_both = QPushButton("Both")
        self._btn_both.setFixedHeight(30)
        self._btn_both.setStyleSheet(self._SRC_DEFAULT)
        self._btn_both.clicked.connect(lambda: self._set_source("both"))
        h.addWidget(self._btn_gbif)
        h.addWidget(self._btn_inat)
        h.addWidget(self._btn_both)
        v.addWidget(row)
        return w

    def _set_source(self, source):
        self._source = source
        styles = {
            "gbif": (self._SRC_GBIF,    self._SRC_DEFAULT, self._SRC_DEFAULT),
            "inat": (self._SRC_DEFAULT,  self._SRC_INAT,   self._SRC_DEFAULT),
            "both": (self._SRC_DEFAULT,  self._SRC_DEFAULT, self._SRC_BOTH),
        }
        g, n, b = styles.get(source, styles["gbif"])
        self._btn_gbif.setStyleSheet(g)
        self._btn_inat.setStyleSheet(n)
        self._btn_both.setStyleSheet(b)

    # ── YEAR / ACCURACY ───────────────────────────────────────

    def _build_year_accuracy_block(self):
        self._sliders_stack    = QStackedWidget()
        self._sliders_stack.setStyleSheet("background:transparent;")
        self._sliders_stack.setContentsMargins(0, 0, 0, 0)
        self._year_sliders     = {}
        self._accuracy_sliders = {}
        for mode in ["single", "batch"]:
            w = QWidget()
            w.setStyleSheet("background:transparent;")
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            h = QHBoxLayout(w)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(20)
            yw = QWidget()
            yw.setStyleSheet("background:transparent;")
            yw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            yv = QVBoxLayout(yw)
            yv.setContentsMargins(0, 0, 0, 0)
            yv.setSpacing(2)
            yv.addWidget(self._slbl("Year range"))
            yr = QWidget()
            yr.setStyleSheet("background:transparent;")
            yh = QHBoxLayout(yr)
            yh.setContentsMargins(0, 0, 0, 0)
            yh.setSpacing(6)
            ys = YearRangeSlider(1500, 2026, 2000, 2026)
            ys._settings_key = "biosnap/year_slider/" + mode
            try:
                s = QgsSettings()
                ys._start = int(s.value(ys._settings_key + '/start', 2000))
                ys._end   = int(s.value(ys._settings_key + '/end',   2026))
            except Exception:
                pass
            yh.addWidget(ys)
            yv.addWidget(yr)
            self._year_sliders[mode] = ys
            aw = QWidget()
            aw.setStyleSheet("background:transparent;")
            aw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            av = QVBoxLayout(aw)
            av.setContentsMargins(0, 0, 0, 0)
            av.setSpacing(2)
            av.addWidget(self._slbl("Accuracy \u2264"))
            ac = AccuracySlider(100, 100000, 10000)
            ac._settings_key = "biosnap/accuracy_slider/" + mode
            try:
                s = QgsSettings()
                ac._value = int(s.value(ac._settings_key + '/value', 10000))
            except Exception:
                pass
            ac.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            av.addWidget(ac)
            self._accuracy_sliders[mode] = ac
            h.addWidget(yw)
            h.addWidget(aw)
            self._sliders_stack.addWidget(w)
        self._sliders_stack.setCurrentIndex(0)
        self._year_slider     = self._year_sliders["single"]
        self._accuracy_slider = self._accuracy_sliders["single"]
        return self._sliders_stack

    # ── TOGGLES ───────────────────────────────────────────────

    _TOGGLE_KEYS     = ["has_coordinates", "has_taxonomy", "has_media",
                        "fossils_only", "no_duplicates"]
    _TOGGLE_DEFAULTS = {
        "single": {"has_coordinates": True,  "has_taxonomy": True,
                   "has_media": False, "fossils_only": False, "no_duplicates": True},
        "batch":  {"has_coordinates": True,  "has_taxonomy": True,
                   "has_media": False, "fossils_only": False, "no_duplicates": True},
    }

    def _build_toggles_block(self):
        self._toggles_stack  = QStackedWidget()
        self._toggles_stack.setStyleSheet("background:transparent;")
        self._toggle_widgets = {}
        for mode in ["single", "batch"]:
            w = QWidget()
            w.setStyleSheet("background:transparent;")
            v = QVBoxLayout(w)
            v.setContentsMargins(0, 4, 0, 0)
            v.setSpacing(6)
            toggles = {}
            def make_tog(key, mode_=mode, label="", checked=False):
                saved = QgsSettings().value(
                    "biosnap/toggles/" + mode_ + "/" + key, None)
                if saved is not None:
                    checked = saved in (True, "true", "True", 1, "1")
                t = ToggleSwitch(checked)
                t.mousePressEvent_orig = t.mousePressEvent
                def on_press(e, t_=t, k_=key, m_=mode_):
                    t_.mousePressEvent_orig(e)
                    QgsSettings().setValue(
                        "biosnap/toggles/" + m_ + "/" + k_, t_.isChecked())
                t.mousePressEvent = on_press
                lw = QWidget()
                lw.setStyleSheet("background:transparent;")
                lh = QHBoxLayout(lw)
                lh.setContentsMargins(0, 0, 0, 0)
                lh.setSpacing(8)
                lh.addWidget(t)
                lb = QLabel(label)
                lb.setStyleSheet(
                    "color:#1C2B1C; font-size:12px; background:transparent;")
                lh.addWidget(lb)
                lh.addStretch()
                toggles[key] = t
                return lw
            defs = self._TOGGLE_DEFAULTS[mode]
            pairs_list = [
                [("has_coordinates", "Has coordinates"), ("has_taxonomy",  "Has taxonomy")],
                [("has_media",       "Has media"),       ("fossils_only",  "Fossils only")],
                [("no_duplicates",   "No duplicates")],
            ]
            for pairs in pairs_list:
                row = QWidget()
                row.setStyleSheet("background:transparent;")
                rh = QHBoxLayout(row)
                rh.setContentsMargins(0, 0, 0, 0)
                rh.setSpacing(20)
                for key, label in pairs:
                    rh.addWidget(make_tog(key, mode, label, defs[key]))
                rh.addStretch()
                v.addWidget(row)
            self._toggle_widgets[mode] = toggles
            self._toggles_stack.addWidget(w)
        self._toggles_stack.setCurrentIndex(0)
        return self._toggles_stack

    def _get_toggles(self, mode=None):
        m = mode or self._mode
        if m not in self._toggle_widgets:
            m = "single"
        return {k: t.isChecked() for k, t in self._toggle_widgets[m].items()}

    # ── PREVIEW ───────────────────────────────────────────────

    def _build_preview_block(self):
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background:#F1F8E9; border:1px solid #C8E6C9;"
            "border-radius:8px; }")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 10, 12, 10)
        h.setSpacing(0)
        map_box = QFrame()
        map_box.setFixedSize(58, 46)
        map_box.setStyleSheet(
            "background:#E3F2FD; border:1px solid #BBDEFB; border-radius:4px;")
        ml = QVBoxLayout(map_box)
        ml.setContentsMargins(0, 0, 0, 0)
        lm = QLabel("map")
        lm.setAlignment(Qt.AlignCenter)
        lm.setStyleSheet("color:#1565C0; font-size:10px; background:transparent;")
        ml.addWidget(lm)
        h.addWidget(map_box)
        h.addSpacing(14)
        self._stat_labels = {}
        for key, label in [("records","Records"),("species","Species"),("families","Families")]:
            col = QWidget()
            col.setStyleSheet("background:transparent;")
            cv = QVBoxLayout(col)
            cv.setContentsMargins(0, 0, 0, 0)
            cv.setSpacing(1)
            n = QLabel("\u2014")
            n.setStyleSheet(
                "font-size:18px; font-weight:600;"
                "color:#9E9E9E; background:transparent;")
            lb = QLabel(label)
            lb.setStyleSheet(
                "font-size:10px; color:#5C6B5C; background:transparent;")
            cv.addWidget(n)
            cv.addWidget(lb)
            h.addWidget(col)
            h.addSpacing(20)
            self._stat_labels[key] = n
        return frame

    def _update_stats(self, records=None, species=None, families=None):
        data = {"records": records, "species": species, "families": families}
        for key, val in data.items():
            lbl = self._stat_labels.get(key)
            if lbl is None:
                continue
            if val is None:
                lbl.setText("\u2014")
                lbl.setStyleSheet("font-size:18px; font-weight:600;"
                    "color:#9E9E9E; background:transparent;")
            else:
                lbl.setText(str(val))
                lbl.setStyleSheet("font-size:18px; font-weight:600;"
                    "color:#1C2B1C; background:transparent;")

    # ── OUTPUT / FORMAT / RUN ─────────────────────────────────

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
        v.addWidget(row)
        return w

    def _set_format(self, fmt):
        self._format = fmt
        for f, btn in self._fmt_btns.items():
            btn.setStyleSheet(CHIP_SM_ON if f == fmt else CHIP_SM_OFF)

    def _build_run_btn(self):
        btn = QPushButton("\u26a1  Run BioSnap")
        btn.setFixedHeight(44)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setStyleSheet(
            "QPushButton {background-color:#2E7D32; color:#FFFFFF; border:none;"
            "border-radius:6px; font-size:14px; font-weight:600;}"
            "QPushButton:hover {background-color:#388E3C;}"
            "QPushButton:pressed {background-color:#1B5E20;}"
            "QPushButton:disabled {background-color:#D6D9D6; color:#9E9E9E;}")
        return btn
