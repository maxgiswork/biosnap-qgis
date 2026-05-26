# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication


class BioSnap:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.main_window = None

    def tr(self, msg):
        return QCoreApplication.translate('BioSnap', msg)

    def initGui(self):
        icon = QIcon(os.path.join(self.plugin_dir, 'icons', 'biosnap_b.png'))
        self.action = QAction(icon, self.tr('BioSnap'), self.iface.mainWindow())
        self.action.setToolTip(self.tr('BioSnap — Quick occurrence loader'))
        self.action.triggered.connect(self.run)
        self.toolbar = self.iface.addToolBar('BioSnap')
        self.toolbar.setObjectName('BioSnapToolbar')
        self.toolbar.addAction(self.action)
        self.iface.addPluginToMenu('BioSnap', self.action)

    def unload(self):
        self.toolbar.removeAction(self.action)
        del self.toolbar
        self.iface.removePluginMenu('BioSnap', self.action)
        if self.main_window:
            self.main_window.close()

    def run(self):
        from .ui.main_window import BioSnapDialog
        if self.main_window is None:
            self.main_window = BioSnapDialog(self.iface, self.iface.mainWindow())
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
