"""
FaceBox - Giao diện hiện đại với dark theme
Định nghĩa toàn bộ stylesheet QSS
"""

MAIN_STYLE = """
/* ========= GLOBAL ========= */
QWidget {
    background-color: #0f1117;
    color: #e2e8f0;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0f1117;
}

/* ========= SIDEBAR ========= */
#sidebar {
    background-color: #161b27;
    border-right: 1px solid #1e2635;
    min-width: 200px;
    max-width: 200px;
}

#sidebar_logo {
    font-size: 22px;
    font-weight: bold;
    color: #6366f1;
    padding: 20px 16px 10px 16px;
    letter-spacing: 2px;
}

#sidebar_subtitle {
    font-size: 10px;
    color: #64748b;
    padding: 0 16px 20px 16px;
}

QPushButton#nav_btn {
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    color: #94a3b8;
    font-size: 13px;
    margin: 2px 8px;
}

QPushButton#nav_btn:hover {
    background-color: #1e2635;
    color: #e2e8f0;
}

QPushButton#nav_btn[active="true"] {
    background-color: #1e2d54;
    color: #818cf8;
    font-weight: bold;
    border-left: 3px solid #6366f1;
}

/* ========= MAIN CONTENT ========= */
#content_area {
    background-color: #0f1117;
}

#page_title {
    font-size: 24px;
    font-weight: bold;
    color: #e2e8f0;
    padding: 24px 24px 8px 24px;
}

#page_subtitle {
    font-size: 13px;
    color: #64748b;
    padding: 0 24px 16px 24px;
}

/* ========= CARDS ========= */
QFrame#card {
    background-color: #161b27;
    border: 1px solid #1e2635;
    border-radius: 12px;
    padding: 16px;
}

QFrame#card_highlight {
    background-color: #1a1f35;
    border: 1px solid #312e81;
    border-radius: 12px;
    padding: 16px;
}

QLabel#stat_number {
    font-size: 36px;
    font-weight: bold;
    color: #818cf8;
}

QLabel#stat_label {
    font-size: 12px;
    color: #64748b;
}

/* ========= BUTTONS ========= */
QPushButton#btn_primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #4f46e5);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
    min-height: 36px;
}

QPushButton#btn_primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #818cf8, stop:1 #6366f1);
}

QPushButton#btn_primary:pressed {
    background: #4338ca;
}

QPushButton#btn_primary:disabled {
    background: #374151;
    color: #6b7280;
}

QPushButton#btn_secondary {
    background-color: #1e2635;
    color: #94a3b8;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    min-height: 36px;
}

QPushButton#btn_secondary:hover {
    background-color: #2d3748;
    color: #e2e8f0;
    border-color: #4a5568;
}

QPushButton#btn_danger {
    background-color: #1a0a0a;
    color: #f87171;
    border: 1px solid #7f1d1d;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
}

QPushButton#btn_danger:hover {
    background-color: #7f1d1d;
    color: white;
}

QPushButton#btn_success {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #047857);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
    min-height: 36px;
}

QPushButton#btn_success:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
}

/* ========= INPUTS ========= */
QLineEdit {
    background-color: #1e2635;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 10px 14px;
    color: #e2e8f0;
    font-size: 14px;
    min-height: 20px;
}

QLineEdit:focus {
    border-color: #6366f1;
    background-color: #1a2340;
}

QLineEdit::placeholder {
    color: #4a5568;
}

/* ========= LABELS ========= */
QLabel#label_info {
    color: #94a3b8;
    font-size: 12px;
}

QLabel#label_success {
    color: #34d399;
    background-color: #064e3b;
    border-radius: 6px;
    padding: 8px 12px;
}

QLabel#label_error {
    color: #f87171;
    background-color: #7f1d1d;
    border-radius: 6px;
    padding: 8px 12px;
}

QLabel#label_warning {
    color: #fbbf24;
    background-color: #451a03;
    border-radius: 6px;
    padding: 8px 12px;
}

/* ========= TABLE ========= */
QTableWidget {
    background-color: #161b27;
    alternate-background-color: #1a1f2e;
    border: 1px solid #1e2635;
    border-radius: 8px;
    gridline-color: #1e2635;
    color: #e2e8f0;
    selection-background-color: #1e2d54;
}

QTableWidget::item {
    padding: 8px 12px;
    border: none;
}

QHeaderView::section {
    background-color: #0f1117;
    color: #64748b;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #1e2635;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ========= CAMERA VIEW ========= */
QLabel#camera_view {
    background-color: #0a0e17;
    border: 2px solid #1e2635;
    border-radius: 12px;
}

QLabel#camera_placeholder {
    background-color: #0a0e17;
    border: 2px dashed #2d3748;
    border-radius: 12px;
    color: #4a5568;
    font-size: 14px;
}

/* ========= STATUS BADGE ========= */
QLabel#badge_active {
    background-color: #064e3b;
    color: #34d399;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: bold;
}

QLabel#badge_inactive {
    background-color: #1a0a0a;
    color: #f87171;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
}

/* ========= SCROLLBAR ========= */
QScrollBar:vertical {
    background: #0f1117;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #2d3748;
    border-radius: 4px;
    min-height: 40px;
}

QScrollBar::handle:vertical:hover {
    background: #4a5568;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ========= PROGRESS ========= */
QProgressBar {
    background-color: #1e2635;
    border-radius: 4px;
    border: none;
    height: 6px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #818cf8);
    border-radius: 4px;
}

/* ========= SPINBOX ========= */
QDoubleSpinBox, QSpinBox {
    background-color: #1e2635;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 6px 10px;
    color: #e2e8f0;
}

QDoubleSpinBox:focus, QSpinBox:focus {
    border-color: #6366f1;
}

/* ========= MESSAGEBOX ========= */
QMessageBox {
    background-color: #161b27;
}

QMessageBox QLabel {
    color: #e2e8f0;
}

QMessageBox QPushButton {
    background-color: #1e2635;
    color: #94a3b8;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 6px 16px;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background-color: #2d3748;
    color: #e2e8f0;
}
"""
