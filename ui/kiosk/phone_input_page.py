"""
FaceBox — Kiosk Phone Input Page
Màn hình nhập số điện thoại bằng bàn phím cảm ứng số lớn:
- Hiển thị ô nhập số điện thoại to rõ.
- Bàn phím số TouchNumericKeypad (0-9, Xóa, Backspace).
- Kiểm tra tính hợp lệ bằng services.account_service.validate_phone.
- Tra cứu tài khoản từ cơ sở dữ liệu database.db_manager.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal

from ui.components import KioskHeader, TouchNumericKeypad
from services.account_service import validate_phone
from database import db_manager
from ui import theme


class PhoneInputPage(QWidget):
    """Màn hình nhập số điện thoại trên Kiosk."""

    back_clicked = Signal()
    admin_requested = Signal()
    authenticated = Signal(dict)   # Phát tài khoản: {'phone_number': ..., 'account_id': ..., 'method': 'phone'}
    switch_to_face = Signal()      # Chuyển sang quét khuôn mặt

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("kiosk_page")
        self._action_type = "giao dịch"
        self._setup_ui()

    def set_action_type(self, action_name: str):
        self._action_type = action_name

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 16, 32, 24)
        layout.setSpacing(14)

        # Header
        self.header = KioskHeader(show_back=True)
        self.header.back_clicked.connect(self.back_clicked.emit)
        self.header.gear_clicked.connect(self.admin_requested.emit)
        layout.addWidget(self.header)

        # Tiêu đề
        title = QLabel("Nhập số điện thoại tài khoản")
        title.setObjectName("kiosk_title")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("Sử dụng bàn phím số bên dưới để nhập số điện thoại của bạn")
        sub.setObjectName("kiosk_subtitle")
        sub.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(10)

        # Khung chứa ô hiển thị SĐT & Bàn phím số
        content_box = QHBoxLayout()
        content_box.setSpacing(32)

        # Cột trái: Ô nhập số điện thoại + thông báo + nút xác nhận
        left_col = QVBoxLayout()
        left_col.setSpacing(16)
        left_col.setAlignment(Qt.AlignCenter)

        self.phone_display = QLineEdit()
        self.phone_display.setPlaceholderText("09xxxxxxxx")
        self.phone_display.setReadOnly(True)  # Chỉ nhập qua bàn phím cảm ứng trên màn hình
        self.phone_display.setAlignment(Qt.AlignCenter)
        self.phone_display.setStyleSheet(
            "font-size: 34px; font-weight: 900; letter-spacing: 3px; "
            "height: 68px; border-radius: 2px; "
            "background-color: #FFFFFF; color: #171717; "
            "border: 3px solid #171717;"
        )
        left_col.addWidget(self.phone_display)

        # Nhãn thông báo lỗi / trạng thái
        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setWordWrap(True)
        self.msg_label.setFixedHeight(44)
        self.msg_label.setStyleSheet(
            "font-size: 14px; border-radius: 2px; padding: 6px 12px; font-weight: bold;"
        )
        self.msg_label.setVisible(False)
        left_col.addWidget(self.msg_label)

        # Nút xác nhận
        self.btn_submit = QPushButton("XÁC NHẬN TIẾP TỤC →")
        self.btn_submit.setObjectName("btn_primary")
        self.btn_submit.setFixedHeight(58)
        self.btn_submit.setCursor(Qt.PointingHandCursor)
        self.btn_submit.setStyleSheet(
            "font-size: 18px; font-weight: 900; border-radius: 2px; "
            "background-color: #FFD500; color: #171717; border: 2px solid #171717;"
        )
        self.btn_submit.clicked.connect(self._on_submit)
        left_col.addWidget(self.btn_submit)

        # Nút đổi sang quét khuôn mặt
        self.btn_switch_face = QPushButton("👤 Chuyển sang quét khuôn mặt")
        self.btn_switch_face.setObjectName("btn_secondary")
        self.btn_switch_face.setFixedHeight(44)
        self.btn_switch_face.setCursor(Qt.PointingHandCursor)
        self.btn_switch_face.clicked.connect(self.switch_to_face.emit)
        left_col.addWidget(self.btn_switch_face)

        content_box.addLayout(left_col, stretch=1)

        # Cột phải: Bàn phím số cảm ứng
        keypad_frame = QFrame()
        keypad_frame.setObjectName("card")
        keypad_frame.setFixedWidth(340)
        keypad_layout = QVBoxLayout(keypad_frame)
        keypad_layout.setContentsMargins(16, 16, 16, 16)

        self.keypad = TouchNumericKeypad()
        self.keypad.digit_pressed.connect(self._on_digit)
        self.keypad.backspace_pressed.connect(self._on_backspace)
        self.keypad.clear_pressed.connect(self._on_clear)
        keypad_layout.addWidget(self.keypad)

        content_box.addWidget(keypad_frame)
        layout.addLayout(content_box, stretch=1)

    def showEvent(self, event):
        super().showEvent(event)
        self.phone_display.clear()
        self.msg_label.setVisible(False)

    def _on_digit(self, char: str):
        current = self.phone_display.text()
        if len(current) < 12:
            self.phone_display.setText(current + char)
            self.msg_label.setVisible(False)

    def _on_backspace(self):
        current = self.phone_display.text()
        if current:
            self.phone_display.setText(current[:-1])
            self.msg_label.setVisible(False)

    def _on_clear(self):
        self.phone_display.clear()
        self.msg_label.setVisible(False)

    def _on_submit(self):
        raw_phone = self.phone_display.text().strip()
        is_valid, validated_or_msg = validate_phone(raw_phone)

        if not is_valid:
            self._show_error(validated_or_msg)
            return

        phone_number = validated_or_msg

        # Tra cứu tài khoản trong cơ sở dữ liệu
        account = db_manager.get_account_by_phone(phone_number)
        if not account:
            self._show_error(f"Không tìm thấy tài khoản {phone_number}. Vui lòng đăng ký tài khoản trước.")
            return

        # Xác thực thành công
        self.msg_label.setStyleSheet("background-color: #DFFBE9; color: #16A36A; font-weight: bold; padding: 8px;")
        self.msg_label.setText("✅ Xác thực thành công! Đang chuyển tiếp...")
        self.msg_label.setVisible(True)

        self.authenticated.emit({
            "phone_number": phone_number,
            "account_id": account["id"],
            "method": "phone"
        })

    def _show_error(self, message: str):
        self.msg_label.setStyleSheet("background-color: #FDE8E8; color: #D94848; font-weight: 500; padding: 8px;")
        self.msg_label.setText(f"❌ {message}")
        self.msg_label.setVisible(True)

