# -*- coding: utf-8 -*-
import os
import sys
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtCore import Qt
# Додаємо папку плагіна до sys.path
plugin_dir = os.path.dirname(__file__)
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)
from core.i18n import load_language, get_saved_language
class BioSnap:
    def __init__(self, iface):
        self.iface  = iface
        self.action = None
        self.window = None
        load_language(get_saved_language())
    def initGui(self):
        self.action = QAction("BioSnap", self.iface.mainWindow())
        self.action.setToolTip("BioSnap — GBIF Occurrence Downloader")
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("BioSnap", self.action)
    def unload(self):
        self.iface.removePluginMenu("BioSnap", self.action)
        self.iface.removeToolBarIcon(self.action)
        self.window = None
    def run(self):
        if self.window is None:
            from ui.main_window import MainWindow
            self.window = MainWindow(self.iface.mainWindow())
        self.window.show()
        self.window.raise_()
