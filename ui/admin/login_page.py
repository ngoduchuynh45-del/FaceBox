"""
FaceBox — Admin Login Dialog
Hộp thoại xác thực mật khẩu quản trị viên khi bấm nút bánh răng ⚙️ từ Kiosk.
- Ô nhập mật khẩu có ẩn ký tự.
- Bàn phím số cảm ứng để nhập thuận tiện trên màn hình kiosk.
- Xác thực mật khẩu quản trị (mặc định: '888888' hoặc 'admin123').
- Báo lỗi rõ ràng khi nhập sai.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from ui.components import TouchNumericKeypad
from ui import theme

# Mật khẩu quản trị mặc định của hệ thống
DEFAULT_ADMIN_PIN = "888888"


class AdminLoginDialog(QDialog):
    """Hộp thoại xác thực mật khẩu quản trị."""

    login_success = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Xác thực Quản trị viên FaceBox")
        self.setModal(True)
        self.setMinimumSize(450, 590)
        self.resize(450, 590)
        self._setup_ui()

    def _setup_ui(self):
        c = theme.colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {c.surface};
                color: {c.text};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        # Tiêu đề
        title = QLabel("QUẢN TRỊ HỆ THỐNG")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 20px; font-weight: 900; color: {c.text}; letter-spacing: 0.8px;")

        sub = QLabel("Vui lòng nhập mã PIN quản trị để tiếp tục")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"font-size: 13px; color: {c.text_muted};")

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(4)

        # Ô hiển thị PIN
        self.pin_display = QLineEdit()
        self.pin_display.setPlaceholderText("••••••")
        self.pin_display.setEchoMode(QLineEdit.Password)
        self.pin_display.setReadOnly(True)
        self.pin_display.setAlignment(Qt.AlignCenter)
        self.pin_display.setStyleSheet(f"""
            QLineEdit {{
                font-size: 26px;
                font-weight: 900;
                letter-spacing: 6px;
                height: 50px;
                border-radius: 2px;
                background-color: {c.bg};
                color: {c.text};
                border: 2px solid {c.border};
                padding: 0 12px;
            }}
            QLineEdit:focus {{
                border-color: #FFD500;
            }}
        """)
        layout.addWidget(self.pin_display)

        # Thông báo lỗi / hướng dẫn
        self.err_label = QLabel("Mã PIN mặc định: 888888")
        self.err_label.setAlignment(Qt.AlignCenter)
        self.err_label.setWordWrap(True)
        self.err_label.setMinimumHeight(22)
        self.err_label.setStyleSheet(f"font-size: 12px; color: {c.text_muted}; font-weight: 600;")
        layout.addWidget(self.err_label)

        # Bàn phím số cảm ứng (chiều cao 52px vừa vặn)
        self.keypad = TouchNumericKeypad(btn_height=52)
        self.keypad.digit_pressed.connect(self._on_digit)
        self.keypad.backspace_pressed.connect(self._on_backspace)
        self.keypad.clear_pressed.connect(self._on_clear)
        layout.addWidget(self.keypad)

        layout.addSpacing(6)

        # Hàng nút điều khiển: Hủy / Đăng nhập
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_cancel = QPushButton("Hủy bỏ")
        self.btn_cancel.setObjectName("btn_secondary")
        self.btn_cancel.setFixedHeight(46)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                border-radius: 2px;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid {c.border};
                background-color: {c.surface};
                color: {c.text};
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {c.surface_hover};
                border-color: #171717;
            }}
        """)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_login = QPushButton("ĐĂNG NHẬP →")
        self.btn_login.setObjectName("btn_primary")
        self.btn_login.setFixedHeight(46)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                border-radius: 2px;
                font-weight: 900;
                background-color: #FFD500;
                color: #171717;
                border: 2px solid #171717;
                font-size: 14px;
                letter-spacing: 0.5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #FFE033;
            }
        """)
        self.btn_login.clicked.connect(self._verify_pin)

        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_login)
        layout.addLayout(btn_row)

    def _on_digit(self, char: str):
        curr = self.pin_display.text()
        if len(curr) < 8:
            self.pin_display.setText(curr + char)
            self.err_label.setText("Mã PIN mặc định: 888888")
            self.err_label.setStyleSheet(f"font-size: 12px; color: {theme.colors().text_muted};")

    def _on_backspace(self):
        curr = self.pin_display.text()
        if curr:
            self.pin_display.setText(curr[:-1])

    def _on_clear(self):
        self.pin_display.clear()

    def _verify_pin(self):
        entered = self.pin_display.text().strip()
        if entered in (DEFAULT_ADMIN_PIN, "admin123"):
            self.login_success.emit()
            self.accept()
        else:
            self.err_label.setText("❌ Mã PIN không chính xác. Vui lòng thử lại!")
            self.err_label.setStyleSheet("font-size: 12px; color: #D94848; font-weight: bold;")
            self.pin_display.clear()

