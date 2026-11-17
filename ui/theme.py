"""
FaceBox — Design System
Bảng màu Light/Dark, font, spacing, bo góc và bộ sinh QSS stylesheet.
Dùng chung cho cả Kiosk và Admin mode.
"""

from dataclasses import dataclass


# ─── Bảng màu Industrial Smart Locker ────────────────────────────────────────

@dataclass(frozen=True)
class ColorPalette:
    """Tập hợp đầy đủ các biến màu cho theme Industrial Smart Locker."""

    # Nền chính và bề mặt
    bg: str
    surface: str
    surface_hover: str
    surface_alt: str        # Sidebar, vùng phân chia thiết bị

    # Màu chủ đạo (Industrial Yellow / Black)
    primary: str            # Vàng thương hiệu #FFD500
    primary_hover: str
    primary_pressed: str
    on_primary: str         # Chữ trên nền vàng (#171717)

    # Secondary / Black Accent
    secondary: str          # Đen công nghiệp #171717
    secondary_hover: str
    on_secondary: str       # Chữ trên nền đen (#FFFFFF)

    # Chữ
    text: str
    text_secondary: str
    text_muted: str

    # Viền (Industrial borders)
    border: str
    border_dark: str

    # Trạng thái
    success: str
    success_bg: str
    error: str
    error_bg: str
    warning: str
    warning_bg: str


# Light Mode (InPost / Industrial Locker: nền sáng xám #F2F2F2, nút vàng #FFD500, viền đen)
LIGHT = ColorPalette(
    bg="#F2F2F2",
    surface="#FFFFFF",
    surface_hover="#EAEAEA",
    surface_alt="#E2E2E2",

    primary="#FFD500",
    primary_hover="#ECC500",
    primary_pressed="#D9B500",
    on_primary="#171717",

    secondary="#171717",
    secondary_hover="#2D2D2D",
    on_secondary="#FFFFFF",

    text="#171717",
    text_secondary="#4A4A4A",
    text_muted="#787878",

    border="#D1D1D1",
    border_dark="#171717",

    success="#16A36A",
    success_bg="#E8F8F0",
    error="#D94848",
    error_bg="#FDEAEA",
    warning="#C97D12",
    warning_bg="#FEF6E9",
)


# Dark Mode (Industrial Locker: nền đen #171717, surface #252525, viền #3A3A3A, nút vàng #FFD500)
DARK = ColorPalette(
    bg="#171717",
    surface="#252525",
    surface_hover="#323232",
    surface_alt="#1E1E1E",

    primary="#FFD500",
    primary_hover="#FFDC33",
    primary_pressed="#E6C000",
    on_primary="#171717",

    secondary="#FFFFFF",
    secondary_hover="#E2E2E2",
    on_secondary="#171717",

    text="#FFFFFF",
    text_secondary="#B0B0B0",
    text_muted="#787878",

    border="#3A3A3A",
    border_dark="#000000",

    success="#16A36A",
    success_bg="#0E3322",
    error="#D94848",
    error_bg="#3D1818",
    warning="#FFD500",
    warning_bg="#3A3005",
)


# ─── Typography ──────────────────────────────────────────────────────────────

FONT_FAMILY = '"Segoe UI", Tahoma, Arial, sans-serif'

FONT_XS   = 11    # Chú thích nhỏ
FONT_SM   = 13    # Label phụ
FONT_BODY = 15    # Nội dung chính
FONT_LG   = 17    # Nhấn mạnh
FONT_H3   = 18    # Tiêu đề nhỏ
FONT_H2   = 22    # Tiêu đề section
FONT_H1   = 28    # Tiêu đề trang

# Kiosk (cỡ lớn công nghiệp cho màn hình cảm ứng)
KIOSK_TITLE  = 34
KIOSK_SUB    = 18
KIOSK_BTN    = 20
KIOSK_HINT   = 14
KIOSK_ICON   = 40


# ─── Spacing ─────────────────────────────────────────────────────────────────

SP_XS  = 4
SP_SM  = 8
SP_MD  = 16
SP_LG  = 24
SP_XL  = 32
SP_XXL = 48


# ─── Hình khối công nghiệp (Industrial Shape: Vuông vức, border-radius 0-2px) ─

R_NONE = 0
R_SM   = 2
R_MD   = 2
R_LG   = 2
R_XL   = 2
R_PILL = 2


from PySide6.QtCore import QObject, Signal


# ─── Trạng thái theme & ThemeManager ─────────────────────────────────────────

_current: str = "light"


class ThemeManager(QObject):
    """Quản lý trạng thái theme toàn cục và phát tín hiệu khi theme thay đổi."""
    theme_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._current = "light"

    @property
    def current(self) -> str:
        return self._current

    def set_theme(self, name: str) -> None:
        global _current
        if name not in ("light", "dark"):
            raise ValueError(f"Theme '{name}' không hợp lệ. Chỉ hỗ trợ 'light' và 'dark'.")
        if self._current != name:
            self._current = name
            _current = name
            self.theme_changed.emit(name)


theme_manager = ThemeManager()


def current_theme() -> str:
    """Trả về tên theme đang dùng ('light' hoặc 'dark')."""
    return theme_manager.current


def set_theme(name: str) -> None:
    """Chuyển sang theme chỉ định."""
    theme_manager.set_theme(name)


def colors() -> ColorPalette:
    """Lấy bảng màu của theme hiện tại."""
    return LIGHT if current_theme() == "light" else DARK


def toggle_theme() -> str:
    """Đổi sang theme ngược lại, trả về tên theme mới."""
    new_theme = "dark" if current_theme() == "light" else "light"
    set_theme(new_theme)
    return new_theme


# ─── Sinh QSS Stylesheet ────────────────────────────────────────────────────

def stylesheet() -> str:
    """Sinh bộ QSS hoàn chỉnh cho theme hiện tại."""
    return _build_qss(colors())


def _build_qss(c: ColorPalette) -> str:
    return f"""
/* ═══════════════════════════════════════════════════════════
   FaceBox Industrial Smart Locker Design System — QSS
   ═══════════════════════════════════════════════════════════ */

/* ── Global ──────────────────────────────────────────────── */
QWidget {{
    background-color: {c.bg};
    color: {c.text};
    font-family: {FONT_FAMILY};
    font-size: {FONT_BODY}px;
}}

QMainWindow {{
    background-color: {c.bg};
}}

/* ── Admin Sidebar (Industrial Black & Yellow Accent) ────── */
#admin_sidebar, #sidebar {{
    background-color: #171717;
    border-right: 2px solid #282828;
}}

#sidebar_logo {{
    font-size: {FONT_H2}px;
    font-weight: 900;
    color: {c.primary};
    padding: 24px {SP_MD}px 4px {SP_MD}px;
    letter-spacing: 1.5px;
}}

#sidebar_subtitle {{
    font-size: {FONT_XS}px;
    color: #888888;
    padding: 0 {SP_MD}px {SP_LG}px {SP_MD}px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QPushButton#nav_btn {{
    background: transparent;
    border: none;
    border-radius: 0px;
    padding: 10px 12px;
    text-align: left;
    color: #D1D1D1;
    font-size: 13.5px;
    font-weight: 600;
    margin: 1px 0px;
}}

QPushButton#nav_btn:hover {{
    background-color: #262626;
    color: #FFFFFF;
}}

QPushButton#nav_btn[active="true"] {{
    background-color: #262626;
    color: #FFD500;
    font-weight: bold;
    border-left: 4px solid #FFD500;
}}

/* ── Industrial Cards (Crisp 0-2px corners) ──────────────── */
QFrame#card {{
    background-color: {c.surface};
    border: 1px solid {c.border};
    border-radius: 2px;
    padding: {SP_MD}px;
}}

QFrame#card_highlight {{
    background-color: {c.surface};
    border: 2px solid {c.primary};
    border-radius: 2px;
    padding: {SP_MD}px;
}}

/* ── Buttons (Industrial Sharp & Bold) ───────────────────── */
QPushButton#btn_primary {{
    background-color: #FFD500;
    color: #171717;
    border: 1px solid #D9B500;
    border-radius: 2px;
    padding: 10px 24px;
    font-size: {FONT_BODY}px;
    font-weight: bold;
    min-height: 40px;
    letter-spacing: 0.5px;
}}
QPushButton#btn_primary:hover {{
    background-color: #FFE033;
    border-color: #171717;
}}
QPushButton#btn_primary:pressed {{
    background-color: #ECC500;
}}
QPushButton#btn_primary:disabled {{
    background-color: {c.border};
    color: {c.text_muted};
    border-color: {c.border};
}}

QPushButton#btn_secondary {{
    background-color: {c.surface};
    color: {c.text};
    border: 2px solid {c.border};
    border-radius: 2px;
    padding: 10px 20px;
    font-size: {FONT_BODY}px;
    font-weight: 600;
    min-height: 40px;
}}
QPushButton#btn_secondary:hover {{
    background-color: {c.surface_hover};
    border-color: #171717;
    color: {c.text};
}}
QPushButton#btn_secondary:pressed {{
    background-color: {c.border};
}}

QPushButton#btn_danger {{
    background-color: {c.error_bg};
    color: {c.error};
    border: 2px solid {c.error};
    border-radius: 2px;
    padding: 8px 18px;
    font-size: {FONT_SM}px;
    font-weight: bold;
}}
QPushButton#btn_danger:hover {{
    background-color: {c.error};
    color: #FFFFFF;
}}

QPushButton#btn_success {{
    background-color: {c.success};
    color: #FFFFFF;
    border: 1px solid #148A5A;
    border-radius: 2px;
    padding: 10px 20px;
    font-size: {FONT_BODY}px;
    font-weight: bold;
    min-height: 40px;
}}
QPushButton#btn_success:hover {{
    background-color: #18B877;
}}

/* ── Inputs (Square borders with high contrast) ─────────── */
QLineEdit {{
    background-color: {c.surface};
    border: 2px solid {c.border};
    border-radius: 2px;
    padding: 10px 14px;
    color: {c.text};
    font-size: {FONT_BODY}px;
    min-height: 24px;
}}
QLineEdit:focus {{
    border-color: #FFD500;
}}
QLineEdit::placeholder {{
    color: {c.text_muted};
}}

/* ── Labels & Statuses ───────────────────────────────────── */
QLabel#label_success {{
    color: {c.success};
    background-color: {c.success_bg};
    border: 1px solid {c.success};
    border-radius: 2px;
    padding: 8px 12px;
    font-weight: 600;
}}
QLabel#label_error {{
    color: {c.error};
    background-color: {c.error_bg};
    border: 1px solid {c.error};
    border-radius: 2px;
    padding: 8px 12px;
    font-weight: 600;
}}
QLabel#label_warning {{
    color: {c.warning};
    background-color: {c.warning_bg};
    border: 1px solid {c.warning};
    border-radius: 2px;
    padding: 8px 12px;
    font-weight: 600;
}}

QLabel#stat_number {{
    font-size: 38px;
    font-weight: 900;
    color: {c.text};
}}
QLabel#stat_label {{
    font-size: {FONT_SM}px;
    color: {c.text_muted};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── Industrial Data Tables ──────────────────────────────── */
QTableWidget {{
    background-color: {c.surface};
    alternate-background-color: {c.surface_hover};
    border: 1px solid {c.border};
    border-radius: 0px;
    gridline-color: {c.border};
    color: {c.text};
    selection-background-color: #FFD500;
    selection-color: #171717;
}}
QTableWidget::item {{
    padding: 10px 12px;
    border: none;
}}
QHeaderView::section {{
    background-color: {c.surface_alt};
    color: {c.text};
    padding: 10px 12px;
    border: none;
    border-right: 1px solid {c.border};
    border-bottom: 2px solid #171717;
    font-size: {FONT_XS}px;
    font-weight: bold;
    text-transform: uppercase;
}}

/* ── Camera Area (Square housing) ────────────────────────── */
QLabel#camera_view {{
    background-color: #171717;
    border: 3px solid #3A3A3A;
    border-radius: 2px;
}}
QLabel#camera_placeholder {{
    background-color: #171717;
    border: 3px dashed #3A3A3A;
    border-radius: 2px;
    color: #888888;
    font-size: {FONT_BODY}px;
}}

/* ── Badges ──────────────────────────────────────────────── */
QLabel#badge_active {{
    background-color: {c.success_bg};
    color: {c.success};
    border: 1px solid {c.success};
    border-radius: 2px;
    padding: 4px 10px;
    font-size: {FONT_XS}px;
    font-weight: bold;
}}
QLabel#badge_inactive {{
    background-color: {c.error_bg};
    color: {c.error};
    border: 1px solid {c.error};
    border-radius: 2px;
    padding: 4px 10px;
    font-size: {FONT_XS}px;
}}

/* ── Scrollbar ───────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {c.bg};
    width: 10px;
    border-radius: 0px;
}}
QScrollBar::handle:vertical {{
    background: {c.border};
    border-radius: 0px;
    min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{
    background: #FFD500;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ── Progress bar ────────────────────────────────────────── */
QProgressBar {{
    background-color: {c.border};
    border-radius: 0px;
    border: 1px solid {c.border};
    height: 8px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: #FFD500;
    border-radius: 0px;
}}

/* ── Spinbox & Combobox ──────────────────────────────────── */
QDoubleSpinBox, QSpinBox, QComboBox {{
    background-color: {c.surface};
    border: 2px solid {c.border};
    border-radius: 2px;
    padding: 8px 10px;
    color: {c.text};
    font-weight: 600;
}}
QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: #FFD500;
}}

/* ── MessageBox & Dialog ─────────────────────────────────── */
QMessageBox, QDialog {{
    background-color: {c.surface};
    border: 2px solid #171717;
}}
QMessageBox QLabel, QDialog QLabel {{
    color: {c.text};
}}
QMessageBox QPushButton {{
    background-color: #FFD500;
    color: #171717;
    border: 1px solid #171717;
    border-radius: 2px;
    padding: 8px 20px;
    font-weight: bold;
    min-width: 80px;
}}
QMessageBox QPushButton:hover {{
    background-color: #FFE033;
}}

/* ═══════════════ KIOSK INDUSTRIAL STYLING ═════════════════ */

#kiosk_page {{
    background-color: {c.bg};
}}

#kiosk_title {{
    color: {c.text};
    font-size: {KIOSK_TITLE}px;
    font-weight: 900;
    letter-spacing: -0.5px;
}}

#kiosk_subtitle {{
    color: {c.text_secondary};
    font-size: {KIOSK_SUB}px;
}}

#kiosk_hint {{
    color: {c.text_muted};
    font-size: {KIOSK_HINT}px;
}}

#kiosk_logo_text {{
    color: #171717;
    font-size: {KIOSK_TITLE}px;
    font-weight: 900;
    letter-spacing: 1px;
}}

QPushButton#kiosk_action {{
    background-color: {c.surface};
    border: 2px solid {c.border};
    border-radius: 2px;
    padding: {SP_XL}px;
    color: {c.text};
    font-weight: bold;
}}
QPushButton#kiosk_action:hover {{
    border-color: #FFD500;
    background-color: {c.surface_hover};
}}
QPushButton#kiosk_action:checked {{
    border: 3px solid #FFD500;
    background-color: {c.surface_hover};
}}
QPushButton#kiosk_action:pressed {{
    background-color: #FFD500;
    color: #171717;
    border-color: #FFD500;
}}

/* Nút Bánh răng Admin Kiosk */
QPushButton#gear_btn {{
    background-color: {c.surface};
    border: 2px solid {c.border};
    border-radius: 2px;
    padding: 0px;
    color: {c.text};
    font-size: 20px;
    text-align: center;
}}
QPushButton#gear_btn:hover {{
    background-color: #FFD500;
    border-color: #171717;
    color: #171717;
}}

/* Nút Quay lại Kiosk */
QPushButton#back_btn {{
    background-color: {c.surface};
    border: 2px solid {c.border};
    border-radius: 2px;
    padding: 8px 16px;
    color: {c.text};
    font-size: 14px;
    font-weight: bold;
    min-width: 110px;
    text-align: center;
}}
QPushButton#back_btn:hover {{
    background-color: #FFD500;
    border-color: #171717;
    color: #171717;
}}
"""


def apply_theme(target=None) -> None:
    """Áp dụng stylesheet hiện tại cho QApplication hoặc widget chỉ định."""
    if target is not None:
        target.setStyleSheet(stylesheet())


