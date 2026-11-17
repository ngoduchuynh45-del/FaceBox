"""
FaceBox — Kiosk Authentication Choice Page
Màn hình 3: Lựa chọn phương thức xác thực (Quét khuôn mặt hoặc Nhập số điện thoại).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, Signal

from ui.components import KioskHeader, KioskActionCard
from ui import theme


class AuthChoicePage(QWidget):
    """Màn hình chọn hình thức xác thực danh tính."""

    back_clicked = Signal()
    admin_requested = Signal()
    face_auth_selected = Signal()    # Chọn nhận diện khuôn mặt
    phone_auth_selected = Signal()   # Chọn nhập số điện thoại

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("kiosk_page")
        self._action_type = "giao dịch"
        self._setup_ui()

    def set_action_type(self, action_name: str):
        """action_name: 'GỬI HÀNG' hoặc 'LẤY HÀNG'"""
        self._action_type = action_name
        self.action_badge.setText(f"Giao dịch: {action_name.upper()}")

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 16, 32, 32)
        layout.setSpacing(16)

        # Header
        self.header = KioskHeader(show_back=True)
        self.header.back_clicked.connect(self.back_clicked.emit)
        self.header.gear_clicked.connect(self.admin_requested.emit)
        layout.addWidget(self.header)

        # Badge thông tin loại giao dịch
        self.action_badge = QLabel("GIAO DỊCH: LẤY HÀNG")
        self.action_badge.setStyleSheet(
            "background-color: #FFD500; color: #171717; "
            "border: 2px solid #171717; border-radius: 2px; "
            "padding: 6px 18px; font-weight: 900; font-size: 14px; letter-spacing: 1px;"
        )
        self.action_badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.action_badge, alignment=Qt.AlignCenter)

        # Tiêu đề
        title = QLabel("Xác thực danh tính của bạn")
        title.setObjectName("kiosk_title")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("Chọn cách xác thực thuận tiện nhất đối với bạn")
        sub.setObjectName("kiosk_subtitle")
        sub.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(20)

        # 2 thẻ lựa chọn phương thức
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(28)

        # Phương thức 1: Quét khuôn mặt (Khuyến nghị)
        self.card_face = KioskActionCard(
            icon="👤",
            title="QUÉT KHUÔN MẶT",
            description="Nhanh chóng & tiện lợi. Nhìn vào camera trong 2 giây để xác thực tự động"
        )
        self.card_face.clicked.connect(self.face_auth_selected.emit)

        # Phương thức 2: Nhập số điện thoại
        self.card_phone = KioskActionCard(
            icon="📱",
            title="NHẬP SỐ ĐIỆN THOẠI",
            description="Nhập số điện thoại tài khoản đã đăng ký trên hệ thống FaceBox"
        )
        self.card_phone.clicked.connect(self.phone_auth_selected.emit)

        cards_layout.addWidget(self.card_face)
        cards_layout.addWidget(self.card_phone)
        layout.addLayout(cards_layout, stretch=1)

        layout.addSpacing(16)

        hint = QLabel("🔒 Dữ liệu sinh trắc học được bảo mật an toàn theo tiêu chuẩn mã hóa nội bộ.")
        hint.setObjectName("kiosk_hint")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

