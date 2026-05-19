# -*- coding: utf-8 -*-
"""
BioSnap — GBIF Occurrence Downloader for QGIS
Цей файл QGIS запускає першим при завантаженні плагіна.
Функція classFactory обов'язкова — без неї QGIS не побачить плагін.
"""

def classFactory(iface):
    """
    Точка входу плагіна.
    iface — це інтерфейс QGIS, через який плагін
    може взаємодіяти з головним вікном програми.
    """
    from .biosnap import BioSnap
    return BioSnap(iface)