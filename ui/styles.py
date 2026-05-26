# ui/styles.py
# Вся палитра и QSS стили BioSnap

COLORS = {
    "brand_red":     "#D21C1C",
    "header_bg":     "#1A1A22",
    "window_bg":     "#F6F5F3",
    "gbif_green":    "#2D7D1F",
    "inat_teal":     "#0D9488",
    "iucn_red":      "#DC2626",
    "coin_gold":     "#EAB308",
    "chip_active":   "#1A1A22",
    "chip_inactive": "#ECECF0",
    "text_light":    "#FFFFFF",
    "text_dark":     "#1A1A22",
    "text_muted":    "#6B7280",
    "border":        "#E5E7EB",
}

MAIN_STYLE = """
QDialog {
    background-color: #F6F5F3;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 13px;
    color: #1A1A22;
}

QFrame#header {
    background-color: #1A1A22;
    min-height: 56px;
    max-height: 56px;
}

QLabel#header_title {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: bold;
}

QLabel#header_subtitle {
    color: #9CA3AF;
    font-size: 10px;
}

QLabel#coin_label {
    color: #EAB308;
    font-size: 13px;
    font-weight: bold;
}

QPushButton#chip_on {
    background-color: #1A1A22;
    color: #FFFFFF;
    border: none;
    border-radius: 13px;
    padding: 4px 18px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton#chip_off {
    background-color: #ECECF0;
    color: #1A1A22;
    border: none;
    border-radius: 13px;
    padding: 4px 18px;
    font-size: 13px;
}

QPushButton#chip_off:hover {
    background-color: #DDDDE4;
}

QLineEdit#search_field {
    border: 1.5px solid #E5E7EB;
    border-radius: 8px;
    padding: 6px 10px;
    background: #FFFFFF;
    font-size: 13px;
    color: #1A1A22;
}

QLineEdit#search_field:focus {
    border: 1.5px solid #1A1A22;
}

QPushButton#btn_territory_layer {
    background-color: #2D7D1F;
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton#btn_territory_draw {
    background-color: #0D9488;
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton#source_gbif {
    background-color: #2D7D1F;
    color: #FFFFFF;
    border: none;
    border-radius: 13px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton#source_inat {
    background-color: #0D9488;
    color: #FFFFFF;
    border: none;
    border-radius: 13px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton#source_both {
    background-color: #ECECF0;
    color: #1A1A22;
    border: none;
    border-radius: 13px;
    padding: 4px 14px;
    font-size: 12px;
}

QPushButton#source_both:checked {
    background-color: #1A1A22;
    color: #FFFFFF;
}

QFrame#filter_gbif_block {
    background-color: #F0FBF0;
    border-left: 3px solid #2D7D1F;
    border-radius: 6px;
}

QFrame#filter_inat_block {
    background-color: #F0FAFA;
    border-left: 3px solid #0D9488;
    border-radius: 6px;
}

QPushButton#filter_chip_on {
    background-color: #1A1A22;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
}

QPushButton#filter_chip_off {
    background-color: #ECECF0;
    color: #1A1A22;
    border: none;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
}

QFrame#preview_panel {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
}

QLabel#preview_number {
    font-size: 20px;
    font-weight: bold;
    color: #1A1A22;
}

QLabel#preview_label {
    font-size: 10px;
    color: #6B7280;
}

QLineEdit#output_field {
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 5px 10px;
    background: #FFFFFF;
    font-size: 12px;
    color: #6B7280;
}

QPushButton#format_chip_on {
    background-color: #1A1A22;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 3px 12px;
    font-size: 11px;
    font-weight: bold;
}

QPushButton#format_chip_off {
    background-color: #ECECF0;
    color: #1A1A22;
    border: none;
    border-radius: 10px;
    padding: 3px 12px;
    font-size: 11px;
}

QPushButton#btn_run {
    background-color: #D21C1C;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 12px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#btn_run:hover {
    background-color: #B91C1C;
}

QPushButton#btn_run:pressed {
    background-color: #991B1B;
}

QPushButton#btn_advanced {
    background-color: #F3F4F6;
    color: #6B7280;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 11px;
}

QLabel#section_label {
    font-size: 10px;
    color: #6B7280;
    font-weight: bold;
}

QSpinBox, QLineEdit#year_field, QLineEdit#accuracy_field {
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 4px 8px;
    background: #FFFFFF;
    font-size: 12px;
}
"""
