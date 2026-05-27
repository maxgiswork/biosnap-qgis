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
TOGGLE_ON  = ("QCheckBox { font-size:12px; color:#1C2B1C;"
              "background:transparent; spacing:8px; }"
              "QCheckBox::indicator { width:34px; height:20px;"
              "border-radius:10px; background-color:#2E7D32; border:none; }"
              "QCheckBox::indicator:unchecked { background-color:#C8C8C8; }")
TOGGLE_OFF = ("QCheckBox { font-size:12px; color:#5C6B5C;"
              "background:transparent; spacing:8px; }"
              "QCheckBox::indicator { width:34px; height:20px;"
              "border-radius:10px; background-color:#C8C8C8; border:none; }"
              "QCheckBox::indicator:checked { background-color:#2E7D32; }")
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



class AccuracySlider(QWidget):

    MARKS = [1, 10, 25, 50, 100, 500, 1000, 2000, 5000, 10000]

    def __init__(self, min_val=1, max_val=100000, value=10000, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self._value = value
        self._drag = False
        self._settings_key = 'biosnap/accuracy_slider'
        self.setFixedHeight(44)
        try:
            from qgis.core import QgsSettings
            s = QgsSettings()
            self._value = int(s.value(self._settings_key + '/value', value))
        except Exception:
            pass

    def value(self):
        return self._value

    def minimumSizeHint(self):
        from qgis.PyQt.QtCore import QSize
        return QSize(0, 44)

    def sizeHint(self):
        from qgis.PyQt.QtCore import QSize
        return QSize(100, 44)

    def _tx(self):
        tw = self.width() - 20
        tx = 10
        ty = 32
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
        # ищем ближайшую метку
        if val in self.MARKS:
            i = self.MARKS.index(val)
            return self._mark_x(i)
        # для произвольных значений — линейно между метками
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
        from qgis.PyQt.QtGui import QPainter, QColor, QPen, QFont
        from qgis.PyQt.QtCore import Qt
        GBIF_solid = QColor('#2E7D32')
        GBIF_alpha = QColor('#4CAF50')
        GBIF_alpha.setAlpha(180)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        tx, tw, ty = self._tx()
        x = self._val_to_x(self._value)
        from qgis.PyQt.QtGui import QPainterPath
        from qgis.PyQt.QtCore import QRectF
        from qgis.PyQt.QtCore import QPointF
        # метки — рисуем ДО трека (под обводкой)
        # крайние с отступом 15px внутрь
        p.setBrush(QColor('#FFFFFF'))
        p.setPen(Qt.NoPen)
        for i in range(len(self.MARKS)):
            mx = self._mark_x(i)
            if i == 0:
                mx = tx + 15
            elif i == len(self.MARKS) - 1:
                mx = tx + tw - 15
            p.drawEllipse(QPointF(float(mx), float(ty)), 3.0, 3.0)
        # трек поверх крайних меток
        from qgis.PyQt.QtCore import QRectF, QRect
        from qgis.PyQt.QtGui import QPainterPath, QRegion
        pen = QPen(QColor('#9CA3AF'))
        pen.setWidth(1)
        p.setPen(pen)
        p.setBrush(QColor('#E5E7EB'))
        p.drawRoundedRect(QRectF(tx, ty - 3, tw, 6), 3, 3)
        # заполненная часть — рисуем полный rounded rect, клипаем справа по x
        if x > tx:
            p.save()
            p.setClipRect(QRect(tx, ty - 4, max(1, x - tx), 8))
            p.setPen(Qt.NoPen)
            p.setBrush(GBIF_alpha)
            p.drawRoundedRect(QRectF(tx, ty - 3, tw, 6), 3, 3)
            p.restore()
        # внутренние метки поверх трека
        p.setBrush(QColor('#FFFFFF'))
        p.setPen(Qt.NoPen)
        for i in range(1, len(self.MARKS) - 1):
            mx = self._mark_x(i)
            p.drawEllipse(QPointF(float(mx), float(ty)), 3.0, 3.0)

        # ползунок
        p.setBrush(GBIF_solid)
        p.setPen(Qt.NoPen)
        p.drawEllipse(x - 7, ty - 7, 14, 14)
        p.setBrush(QColor('#FFFFFF'))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(float(x), float(ty)), 4.0, 4.0)
        # подпись только над ползунком
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
                    s = QgsSettings()
                    s.setValue(self._settings_key + '/value', self._value)
            except ValueError:
                pass
            editor.deleteLater()
            self.update()

        editor.editingFinished.connect(commit)
        editor.focusOutEvent = lambda e: (commit(), type(editor).focusOutEvent(editor, e))

    def mouseMoveEvent(self, e):
        if self._drag:
            self._value = self._nearest_mark(e.x())
            self.update()

    def mouseReleaseEvent(self, e):
        self._drag = False
        if self._settings_key:
            from qgis.core import QgsSettings
            s = QgsSettings()
            s.setValue(self._settings_key + '/value', self._value)

class YearRangeSlider(QWidget):

    def __init__(self, min_year=1500, max_year=2026, start=2000, end=2026, parent=None):
        super().__init__(parent)
        self.min_year = min_year
        self.max_year = max_year
        self._start = start
        self._end = end
        self._drag = None
        self._settings_key = 'biosnap/year_slider'
        self.setFixedHeight(44)
        # загружаем сохранённые значения
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
        return QSize(0, 44)

    def sizeHint(self):
        from qgis.PyQt.QtCore import QSize
        return QSize(100, 44)

    def _tx(self):
        tw = self.width() - 20
        tx = 10
        ty = 32
        return tx, tw, ty

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
        # трек — серая обводка 1px
        pen = QPen(QColor('#9CA3AF'))
        pen.setWidth(1)
        p.setPen(pen)
        p.setBrush(QColor('#E5E7EB'))
        p.drawRoundedRect(tx, ty - 3, tw, 6, 3, 3)
        # активный диапазон — GBIF 65% opacity
        x1 = self._year_to_x(self._start)
        x2 = self._year_to_x(self._end)
        p.setPen(Qt.NoPen)
        p.setBrush(GBIF_alpha)
        p.drawRect(x1, ty - 3, max(0, x2 - x1), 6)
        # ползунки с белым кружком внутри 6px
        for x in [x1, x2]:
            p.setBrush(GBIF_solid)
            p.setPen(Qt.NoPen)
            p.drawEllipse(x - 7, ty - 7, 14, 14)
            p.setBrush(QColor('#FFFFFF'))
            p.setPen(Qt.NoPen)
            p.drawEllipse(x - 3, ty - 3, 6, 6)
        # подписи без слипания
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
            # кружки совпадают — запоминаем позицию, решим при движении
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

        editor.editingFinished.connect(commit)
        editor.focusOutEvent = lambda e: (commit(), type(editor).focusOutEvent(editor, e))

    def mousePressEvent(self, e):
        side, lx, top, w, h = self._label_hit(e.x(), e.y())
        if side:
            self._show_year_editor(side, lx, top, w, h)
            return
        self._drag = self._hit(e.x())
        self._overlap_x = e.x()

    def mouseMoveEvent(self, e):
        if self._drag == 'overlap':
            # определяем направление по первому движению
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

    _MODE_DEFAULT = (
        "QPushButton {background:#FFFFFF; color:#1C2B1C;"
        "border:1px solid #D6D9D6; border-radius:8px;"
        "min-width:70px; max-width:70px; min-height:28px; max-height:28px;"
        "font-size:12px;}"
        "QPushButton:hover {background:rgba(46,125,50,0.06);"
        "border-color:#A5D6A7;}")
    _MODE_ACTIVE = (
        "QPushButton {background:#C8E6C9; color:#2E7D32;"
        "border:2px solid #2E7D32; border-radius:8px;"
        "min-width:70px; max-width:70px; min-height:28px; max-height:28px;"
        "font-size:12px; font-weight:600;}")
    _MODE_ADV_DEFAULT = (
        "QPushButton {background:#FFFFFF; color:#6A1B9A;"
        "border:1px solid #D6D9D6; border-radius:8px;"
        "min-width:80px; max-width:80px; min-height:28px; max-height:28px;"
        "font-size:12px;}"
        "QPushButton:hover {background:#F3E5F5;"
        "border-color:#AB47BC;}")
    _MODE_ADV_ACTIVE = (
        "QPushButton {background:#E1BEE7; color:#6A1B9A;"
        "border:2px solid #6A1B9A; border-radius:8px;"
        "min-width:80px; max-width:80px; min-height:28px; max-height:28px;"
        "font-size:12px; font-weight:600;}")

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
        return w

    def _set_mode(self, mode):
        self._mode = mode
        self._btn_single.setStyleSheet(
            self._MODE_ACTIVE if mode == "single" else self._MODE_DEFAULT)
        self._btn_batch.setStyleSheet(
            self._MODE_ACTIVE if mode == "batch" else self._MODE_DEFAULT)
        self._btn_advanced.setStyleSheet(
            self._MODE_ADV_ACTIVE if mode == "advanced" else self._MODE_ADV_DEFAULT)
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
            "color:#AAAAAA; font-size:12px; font-style:italic;"
            "background:transparent; border:none; padding-left:2px;")
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
            "background-color:#2E7D32; color:#FFFFFF; border:none;"
            "border-radius:6px; font-size:15px;")

        h.addWidget(self._rank_btn)
        h.addWidget(self._search_field)
        h.addWidget(btn_history)
        h.addWidget(btn_search)

        v.addWidget(self._search_frame)
        return self._search_block

    _TERR_DEFAULT = (
        "QPushButton {background:#FFFFFF; color:#1C2B1C;"
        "border:1px solid #D6D9D6; border-radius:6px;"
        "padding:4px 6px; font-size:12px;}"
        "QPushButton:hover {background:#BBDEFB; border-color:#1565C0;"
        "color:#1565C0;}")
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
        self._territory_frame = frame
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
            "layer":  (self._TERR_ACTIVE,  self._TERR_DEFAULT, self._TERR_DEFAULT),
            "draw":   (self._TERR_DEFAULT,  self._TERR_ACTIVE,  self._TERR_DEFAULT),
            "extent": (self._TERR_DEFAULT,  self._TERR_DEFAULT, self._TERR_ACTIVE),
        }
        a, b, c = mapping[mode]
        self._btn_layer.setStyleSheet(a)
        self._btn_draw.setStyleSheet(b)
        self._btn_extent.setStyleSheet(c)

    _SRC_DEFAULT = (
        "QPushButton {background:#FFFFFF; color:#1C2B1C;"
        "border:1px solid #D6D9D6; border-radius:6px;"
        "padding:4px 10px; font-size:12px;}"
        "QPushButton:hover {background:rgba(46,125,50,0.06);"
        "border-color:#A5D6A7;}")
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
            "gbif":  (self._SRC_GBIF,    self._SRC_DEFAULT, self._SRC_DEFAULT),
            "inat":  (self._SRC_DEFAULT,  self._SRC_INAT,   self._SRC_DEFAULT),
            "both":  (self._SRC_DEFAULT,  self._SRC_DEFAULT, self._SRC_BOTH),
        }
        g, n, b = styles.get(source, styles["gbif"])
        self._btn_gbif.setStyleSheet(g)
        self._btn_inat.setStyleSheet(n)
        self._btn_both.setStyleSheet(b)

    def _build_year_accuracy_block(self):
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
        yv.setSpacing(4)
        yv.addWidget(self._slbl("Year range"))
        yr = QWidget()
        yr.setStyleSheet("background:transparent;")
        yh = QHBoxLayout(yr)
        yh.setContentsMargins(0, 0, 0, 0)
        yh.setSpacing(6)
        self._year_slider = YearRangeSlider(1500, 2026, 2000, 2026)

        yh.addWidget(self._year_slider)
        yv.addWidget(yr)
        aw = QWidget()
        aw.setStyleSheet("background:transparent;")
        aw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        av = QVBoxLayout(aw)
        av.setContentsMargins(0, 0, 0, 0)
        av.setSpacing(4)
        av.addWidget(self._slbl("Accuracy ≤"))
        self._accuracy_slider = AccuracySlider(100, 100000, 10000)
        self._accuracy_slider.setSizePolicy(
            __import__("qgis.PyQt.QtWidgets", fromlist=["QSizePolicy"]).QSizePolicy.Expanding,
            __import__("qgis.PyQt.QtWidgets", fromlist=["QSizePolicy"]).QSizePolicy.Fixed)
        av.addWidget(self._accuracy_slider)
        h.addWidget(yw)
        h.addWidget(aw)

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
            n = QLabel("—")
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
                lbl.setText("—")
                lbl.setStyleSheet("font-size:18px; font-weight:600;"
                    "color:#9E9E9E; background:transparent;")
            else:
                lbl.setText(str(val))
                lbl.setStyleSheet("font-size:18px; font-weight:600;"
                    "color:#1C2B1C; background:transparent;")


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
        btn = QPushButton("⚡  Run BioSnap")
        btn.setFixedHeight(44)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setStyleSheet(
            "QPushButton {background-color:#2E7D32; color:#FFFFFF; border:none;"
            "border-radius:6px; font-size:14px; font-weight:600;}"
            "QPushButton:hover {background-color:#388E3C;}"
            "QPushButton:pressed {background-color:#1B5E20;}"
            "QPushButton:disabled {background-color:#D6D9D6; color:#9E9E9E;}")
        return btn
