"""
FaceBox — Kiosk Welcome Page (Industrial Smart Locker)
Màn hình chào mừng chính:
- Logo FaceBox máy ảnh vàng với hộp kiện hàng vuông vức.
- Tiêu đề: 'Xin chào! Chào mừng bạn đến với FaceBox'
- Hai nút thao tác chính to rõ: LẤY HÀNG (vàng nổi bật) và GỬI HÀNG (đen công nghiệp).
- Nút bánh răng quản trị ở góc trên.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from ui.components import FaceBoxLogo
from ui import theme


class WelcomePage(QWidget):
    """Màn hình chào mừng Kiosk phong cách Industrial Smart Locker."""

    start_clicked = Signal()      # Tương thích ngược
    send_clicked = Signal()       # Chọn Gửi hàng
    pickup_clicked = Signal()     # Chọn Lấy hàng
    admin_requested = Signal()    # Bấm nút bánh răng

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("kiosk_page")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 24, 36, 32)
        layout.setSpacing(0)

        # ── Top Bar (Chỉ có Logo thương hiệu & nút Gear) ──
        top_bar = QHBoxLayout()
        self.logo = FaceBoxLogo(size=44, show_text=True)
        top_bar.addWidget(self.logo)

        top_bar.addStretch()

        self.btn_gear = QPushButton("⚙️")
        self.btn_gear.setObjectName("gear_btn")
        self.btn_gear.setFixedSize(46, 46)
        self.btn_gear.setCursor(Qt.PointingHandCursor)
        self.btn_gear.setToolTip("Quản trị hệ thống (yêu cầu mật khẩu)")
        self.btn_gear.clicked.connect(self.admin_requested.emit)
        top_bar.addWidget(self.btn_gear)

        layout.addLayout(top_bar)
        layout.addStretch(1)

        # ── Khu vực trung tâm: Lời chào & 2 nút thao tác lớn ──
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(16)
        center_layout.setContentsMargins(0, 0, 0, 0)

        # Tiêu đề chính
        welcome_lbl = QLabel("Xin chào! Chào mừng bạn đến với FaceBox")
        welcome_lbl.setObjectName("kiosk_title")
        welcome_lbl.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(welcome_lbl)

        # Hướng dẫn ngắn
        sub_lbl = QLabel("Vui lòng chọn thao tác bên dưới để bắt đầu giao dịch")
        sub_lbl.setObjectName("kiosk_subtitle")
        sub_lbl.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(sub_lbl)

        center_layout.addSpacing(32)

        # Hai nút thao tác chính phong cách Industrial Smart Locker
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(28)
        actions_layout.setAlignment(Qt.AlignCenter)

        # 1. NÚT LẤY HÀNG (Màu vàng thương hiệu #FFD500, chữ đen #171717, viền đen sắc nét)
        self.btn_pickup = QPushButton()
        self.btn_pickup.setCursor(Qt.PointingHandCursor)
        self.btn_pickup.setFixedSize(360, 220)
        self.btn_pickup.setStyleSheet("""
            QPushButton {
                background-color: #FFD500;
                border: 3px solid #171717;
                border-radius: 2px;
                text-align: center;
                padding: 24px;
            }
            QPushButton:hover {
                background-color: #FFE033;
                border-color: #000000;
            }
            QPushButton:pressed {
                background-color: #ECC500;
            }
        """)
        pickup_lay = QVBoxLayout(self.btn_pickup)
        pickup_lay.setSpacing(8)
        pickup_lay.setAlignment(Qt.AlignCenter)

        icon_pickup = QLabel("📦")
        icon_pickup.setStyleSheet("font-size: 56px; background: transparent; border: none;")
        icon_pickup.setAlignment(Qt.AlignCenter)

        title_pickup = QLabel("LẤY HÀNG")
        title_pickup.setStyleSheet("font-size: 26px; font-weight: 900; color: #171717; background: transparent; border: none; letter-spacing: 1px;")
        title_pickup.setAlignment(Qt.AlignCenter)

        desc_pickup = QLabel("Nhận kiện hàng gửi cho bạn")
        desc_pickup.setStyleSheet("font-size: 14px; color: #333333; font-weight: 600; background: transparent; border: none;")
        desc_pickup.setAlignment(Qt.AlignCenter)

        pickup_lay.addWidget(icon_pickup)
        pickup_lay.addWidget(title_pickup)
        pickup_lay.addWidget(desc_pickup)

        self.btn_pickup.clicked.connect(self._on_pickup_clicked)
        actions_layout.addWidget(self.btn_pickup)

        # 2. NÚT GỬI HÀNG (Màu đen công nghiệp #171717, chữ vàng #FFD500, viền đen sắc nét)
        self.btn_send = QPushButton()
        self.btn_send.setCursor(Qt.PointingHandCursor)
        self.btn_send.setFixedSize(360, 220)
        self.btn_send.setStyleSheet("""
            QPushButton {
                background-color: #171717;
                border: 3px solid #171717;
                border-radius: 2px;
                text-align: center;
                padding: 24px;
            }
            QPushButton:hover {
                background-color: #262626;
                border-color: #FFD500;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """)
        send_lay = QVBoxLayout(self.btn_send)
        send_lay.setSpacing(8)
        send_lay.setAlignment(Qt.AlignCenter)

        icon_send = QLabel("✉️")
        icon_send.setStyleSheet("font-size: 56px; background: transparent; border: none;")
        icon_send.setAlignment(Qt.AlignCenter)

        title_send = QLabel("GỬI HÀNG")
        title_send.setStyleSheet("font-size: 26px; font-weight: 900; color: #FFD500; background: transparent; border: none; letter-spacing: 1px;")
        title_send.setAlignment(Qt.AlignCenter)

        desc_send = QLabel("Gửi đồ vào ngăn tủ trống")
        desc_send.setStyleSheet("font-size: 14px; color: #D1D1D1; font-weight: 600; background: transparent; border: none;")
        desc_send.setAlignment(Qt.AlignCenter)

        send_lay.addWidget(icon_send)
        send_lay.addWidget(title_send)
        send_lay.addWidget(desc_send)

        self.btn_send.clicked.connect(self._on_send_clicked)
        actions_layout.addWidget(self.btn_send)

        center_layout.addLayout(actions_layout)
        layout.addWidget(center_widget)
        layout.addStretch(2)

        # ── Footer công nghiệp ──
        footer = QHBoxLayout()
        footer.addStretch()
        footer_lbl = QLabel("FACEBOX INDUSTRIAL SMART LOCKER  •  HỆ THỐNG GIAO NHẬN TỰ ĐỘNG 24/7")
        footer_lbl.setStyleSheet(f"font-size: {theme.FONT_XS}px; color: {theme.colors().text_muted}; font-weight: bold; letter-spacing: 0.5px;")
        footer.addWidget(footer_lbl)
        footer.addStretch()
        layout.addLayout(footer)

    def _on_pickup_clicked(self):
        self.pickup_clicked.emit()
        self.start_clicked.emit()

    def _on_send_clicked(self):
        self.send_clicked.emit()
        self.start_clicked.emit()
