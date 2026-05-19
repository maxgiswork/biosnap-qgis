# -*- coding: utf-8 -*-
"""
BioSnap — GBIF Occurrence Downloader for QGIS
Головний клас плагіна.
"""

from qgis.PyQt.QtWidgets import QAction, QDialog, QVBoxLayout, QLabel
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt
import os


class BioSnap:
    """
    Головний клас плагіна BioSnap.
    QGIS створює один екземпляр цього класу
    при завантаженні плагіна.
    """

    def __init__(self, iface):
        """
        iface — інтерфейс QGIS.
        Зберігаємо його щоб використовувати пізніше.
        """
        self.iface = iface
        self.action = None
        self.window = None

    def initGui(self):
        """
        QGIS викликає цей метод після завантаження плагіна.
        Тут додаємо іконку на панель інструментів.
        """
        # Створюємо кнопку (Action) для панелі QGIS
        self.action = QAction(
            "BioSnap",           # текст кнопки
            self.iface.mainWindow()
        )

        # Підказка при наведенні миші
        self.action.setToolTip("BioSnap — GBIF Occurrence Downloader")

        # При кліку на кнопку — викликати метод run()
        self.action.triggered.connect(self.run)

        # Додати кнопку на панель інструментів QGIS
        self.iface.addToolBarIcon(self.action)

        # Додати пункт у меню Plugins
        self.iface.addPluginToMenu("BioSnap", self.action)

    def unload(self):
        """
        QGIS викликає цей метод при вимкненні плагіна.
        Тут прибираємо все що додали у initGui().
        """
        self.iface.removePluginMenu("BioSnap", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """
        Викликається при кліку на іконку BioSnap.
        Відкриває головне вікно плагіна.
        """
        # Якщо вікно ще не створене — створюємо
        if self.window is None:
            self.window = BioSnapWindow(self.iface.mainWindow())

        # Показуємо вікно
        self.window.show()
        self.window.raise_()


class BioSnapWindow(QDialog):
    """
    Головне вікно плагіна BioSnap.
    Поки що порожнє — заповнимо на наступних етапах.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Налаштування вікна
        self.setWindowTitle("BioSnap — GBIF Occurrence Downloader")
        self.setMinimumSize(640, 600)

        # Вікно немодальне — можна працювати з QGIS паралельно
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint
        )

        # Поки що просто текст по центру
        layout = QVBoxLayout()
        label = QLabel("🌍 BioSnap завантажується...\n\nЕтап 1 — Скелет плагіна")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)