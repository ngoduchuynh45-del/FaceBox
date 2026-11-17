"""
FaceBox - QSS Stylesheet
Xuất stylesheet thống nhất từ Design System theme.py (Industrial Smart Locker)
"""
from ui.theme import stylesheet, theme_manager

# MAIN_STYLE động lấy từ theme hiện tại
MAIN_STYLE = stylesheet()


def get_current_style() -> str:
    """Lấy stylesheet hiện tại theo theme đang kích hoạt."""
    return stylesheet()
