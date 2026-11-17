"""
FaceBox — Kiosk Complete Page
Màn hình 7: Hoàn tất giao dịch tại Kiosk.
- Hiển thị tóm tắt kết quả giao dịch dựa trên dữ liệu thực tế.
- Đếm ngược tự động quay về màn hình Welcome sau 10 giây.
- Có nút 'Hoàn tất & Về màn hình chính' để người dùng thao tác nhanh.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer

from ui.components import KioskHeader
from ui import theme


class CompletePage(QWidget):
    """Màn hình kết thúc giao dịch Kiosk."""

    home_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("kiosk_page")
        self._countdown = 10

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        self._setup_ui()

    def set_result(self, result_data: dict):
        """Cập nhật thông tin kết quả giao dịch thực tế."""
        action = result_data.get("action", "send")
        account = result_data.get("account", {})
        phone = account.get("phone_number", "Quý khách")
        locker = result_data.get("locker_number", "T-04")
        hw_connected = result_data.get("hardware_connected", False)

        if action == "send":
            self.title_lbl.setText("GHI NHẬN GỬI HÀNG THÀNH CÔNG")
            self.title_lbl.setStyleSheet("font-size: 28px; font-weight: bold; color: #16A36A;")
            self.desc_lbl.setText(f"Cảm ơn {phone}! Yêu cầu gửi hàng của bạn đã được ghi nhận vào hệ thống.")
            self.detail_locker.setText(f"Ngăn tủ được gán: {locker}")
        else:
            self.title_lbl.setText("GIAO DỊCH HOÀN TẤT")
            self.title_lbl.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {theme.colors().primary};")
            self.desc_lbl.setText(f"Cảm ơn {phone} đã sử dụng dịch vụ tủ đồ thông minh FaceBox.")
            self.detail_locker.setText(f"Ngăn tủ: {locker}")

        self.hw_status_lbl.setWordWrap(True)
        if not hw_connected:
            self.hw_status_lbl.setText("Trạng thái chốt tủ: Mô phỏng phần mềm (Chưa kết nối mạch relay phần cứng)")
            self.hw_status_lbl.setStyleSheet("color: #C97D12; font-size: 13px; font-weight: bold;")
        else:
            self.hw_status_lbl.setText("Trạng thái chốt tủ: Đã gửi lệnh mở chốt điện tử thành công")
            self.hw_status_lbl.setStyleSheet("color: #16A36A; font-size: 13px;")

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(16)

        # Header không hiển thị nút Back vì giao dịch đã xong
        self.header = KioskHeader(show_back=False)
        layout.addWidget(self.header)

        layout.addStretch(1)

        # Hộp thông tin trung tâm
        box = QFrame()
        box.setObjectName("card")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(36, 36, 36, 36)
        box_layout.setSpacing(16)
        box_layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel("✅")
        icon_lbl.setStyleSheet("font-size: 64px; background: transparent;")
        icon_lbl.setAlignment(Qt.AlignCenter)

        self.title_lbl = QLabel("GIAO DỊCH THÀNH CÔNG")
        self.title_lbl.setAlignment(Qt.AlignCenter)

        self.desc_lbl = QLabel("Cảm ơn bạn đã sử dụng dịch vụ FaceBox!")
        self.desc_lbl.setStyleSheet(f"font-size: 16px; color: {theme.colors().text_secondary}; background: transparent;")
        self.desc_lbl.setAlignment(Qt.AlignCenter)
        self.desc_lbl.setWordWrap(True)

        self.detail_locker = QLabel("Ngăn tủ: T-04")
        self.detail_locker.setStyleSheet(
            "font-size: 24px; font-weight: 900; color: #171717; "
            "background-color: #FFD500; border: 2px solid #171717; "
            "border-radius: 2px; padding: 8px 24px;"
        )
        self.detail_locker.setAlignment(Qt.AlignCenter)

        self.hw_status_lbl = QLabel("")
        self.hw_status_lbl.setAlignment(Qt.AlignCenter)
        self.hw_status_lbl.setWordWrap(True)

        box_layout.addWidget(icon_lbl)
        box_layout.addWidget(self.title_lbl)
        box_layout.addWidget(self.desc_lbl)
        box_layout.addWidget(self.detail_locker)
        box_layout.addWidget(self.hw_status_lbl)

        layout.addWidget(box)
        layout.addStretch(1)

        # Đồng hồ đếm ngược và nút quay về
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(12)
        bottom_layout.setAlignment(Qt.AlignCenter)

        self.countdown_lbl = QLabel(f"Màn hình sẽ tự động trở về trang chính sau {self._countdown} giây...")
        self.countdown_lbl.setStyleSheet(f"font-size: 14px; color: {theme.colors().text_muted};")
        self.countdown_lbl.setAlignment(Qt.AlignCenter)

        self.btn_home = QPushButton("🏠  VỀ MÀN HÌNH CHÍNH NGAY")
        self.btn_home.setObjectName("btn_primary")
        self.btn_home.setFixedSize(320, 56)
        self.btn_home.setCursor(Qt.PointingHandCursor)
        self.btn_home.setStyleSheet(
            "font-size: 16px; font-weight: 900; border-radius: 2px; "
            "background-color: #FFD500; color: #171717; border: 2px solid #171717;"
        )
        self.btn_home.clicked.connect(self._on_home)

        bottom_layout.addWidget(self.countdown_lbl)
        bottom_layout.addWidget(self.btn_home, alignment=Qt.AlignCenter)
        layout.addLayout(bottom_layout)

    def showEvent(self, event):
        super().showEvent(event)
        self._countdown = 10
        self.countdown_lbl.setText(f"Màn hình sẽ tự động trở về trang chính sau {self._countdown} giây...")
        self._timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._timer.stop()

    def _tick(self):
        self._countdown -= 1
        self.countdown_lbl.setText(f"Màn hình sẽ tự động trở về trang chính sau {self._countdown} giây...")
        if self._countdown <= 0:
            self._timer.stop()
            self._on_home()

    def _on_home(self):
        self._timer.stop()
        self.home_clicked.emit()

