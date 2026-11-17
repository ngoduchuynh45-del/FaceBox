"""
FaceBox — Kiosk Transaction Choice Page
Màn hình 2: Lựa chọn loại giao dịch (Gửi hàng hoặc Lấy hàng).
Thiết kế hai thẻ lựa chọn siêu lớn, tối ưu hóa cho thao tác chạm cảm ứng.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from ui.components import KioskHeader, KioskActionCard
from ui import theme


class TransactionChoicePage(QWidget):
    """Màn hình chọn Gửi hàng hoặc Lấy hàng."""

    back_clicked = Signal()
    admin_requested = Signal()
    send_selected = Signal()     # Người dùng chọn Gửi hàng
    pickup_selected = Signal()   # Người dùng chọn Lấy hàng

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("kiosk_page")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 16, 32, 32)
        layout.setSpacing(16)

        # Header
        self.header = KioskHeader(show_back=True)
        self.header.back_clicked.connect(self.back_clicked.emit)
        self.header.gear_clicked.connect(self.admin_requested.emit)
        layout.addWidget(self.header)

        # Tiêu đề hướng dẫn
        title_box = QVBoxLayout()
        title_box.setSpacing(6)

        title = QLabel("Bạn muốn thực hiện giao dịch gì?")
        title.setObjectName("kiosk_title")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("Vui lòng chạm vào một trong hai lựa chọn bên dưới")
        sub.setObjectName("kiosk_subtitle")
        sub.setAlignment(Qt.AlignCenter)

        title_box.addWidget(title)
        title_box.addWidget(sub)
        layout.addLayout(title_box)

        layout.addSpacing(24)

        # Khu vực 2 nút lớn: Lấy hàng & Gửi hàng
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(28)

        # Nút 1: Lấy hàng
        self.card_pickup = KioskActionCard(
            icon="📦",
            title="LẤY HÀNG",
            description="Mở tủ để lấy bưu phẩm hoặc đồ gửi của bạn"
        )
        self.card_pickup.clicked.connect(self.pickup_selected.emit)

        # Nút 2: Gửi hàng
        self.card_send = KioskActionCard(
            icon="📮",
            title="GỬI HÀNG",
            description="Gửi bưu kiện hoặc cất đồ vào tủ trống"
        )
        self.card_send.clicked.connect(self.send_selected.emit)

        cards_layout.addWidget(self.card_pickup)
        cards_layout.addWidget(self.card_send)
        layout.addLayout(cards_layout, stretch=1)

        layout.addSpacing(16)

        # Hướng dẫn hỗ trợ
        hint = QLabel("💡 Cần hỗ trợ? Vui lòng liên hệ ban quản trị hoặc nhấn biểu tượng ⚙️ ở góc trên.")
        hint.setObjectName("kiosk_hint")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

