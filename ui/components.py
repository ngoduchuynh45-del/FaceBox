"""
FaceBox — Reusable UI Components
Các widget dùng chung cho Kiosk và Admin mode.
Được xây dựng theo Design System hiện đại, phong cách Linear, thân thiện với màn hình cảm ứng.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QSize, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath

from ui import theme


class FaceBoxLogo(QWidget):
    """
    Logo FaceBox Industrial Smart Locker:
    - Biểu tượng chiếc máy ảnh nhìn trực diện phẳng, thân màu vàng (#FFD500), viền đen (#171717).
    - Bên trong ống kính là một hộp kiện hàng hình vuông (Square Package Box).
    - Nhãn thương hiệu 'FaceBox' đậm nét công nghiệp, rõ ràng.
    """

    def __init__(self, size: int = 48, show_text: bool = True, parent=None):
        super().__init__(parent)
        self.logo_size = size
        self.show_text = show_text
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Icon widget tự vẽ bằng QPainter
        self.icon_widget = _CameraLogoIcon(self.logo_size)
        layout.addWidget(self.icon_widget)

        if self.show_text:
            text_layout = QVBoxLayout()
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(1)

            self.brand_label = QLabel("FaceBox")
            self.brand_label.setObjectName("brand_name")
            self.brand_label.setStyleSheet(
                f"font-size: {int(self.logo_size * 0.46)}px; font-weight: 900; "
                f"color: {theme.colors().text}; letter-spacing: 1px;"
            )

            self.tag_label = QLabel("SMART LOCKER")
            self.tag_label.setObjectName("brand_tag")
            self.tag_label.setStyleSheet(
                f"font-size: {theme.FONT_XS}px; font-weight: bold; "
                f"color: #FFD500; background-color: #171717; "
                f"padding: 1px 4px; border-radius: 2px; letter-spacing: 1px;"
            )

            text_layout.addWidget(self.brand_label)
            text_layout.addWidget(self.tag_label)
            layout.addLayout(text_layout)

    def update_theme(self):
        """Cập nhật màu sắc theo theme."""
        if hasattr(self, "brand_label"):
            self.brand_label.setStyleSheet(
                f"font-size: {int(self.logo_size * 0.46)}px; font-weight: 900; "
                f"color: {theme.colors().text}; letter-spacing: 1px;"
            )
        self.icon_widget.update()


class _CameraLogoIcon(QWidget):
    """
    Widget vẽ icon camera phẳng công nghiệp:
    - Thân máy ảnh màu vàng #FFD500, viền đen #171717.
    - Ống kính màu đen.
    - Bên trong ống kính là hộp hàng hình vuông màu vàng, băng keo nắp hộp viền đen.
    """

    def __init__(self, size: int = 48, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, int(size * 0.82))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w = float(self.width())
        h = float(self.height())

        yellow_color = QColor("#FFD500")
        dark_color = QColor("#171717")
        box_color = QColor("#FFD500")

        # 1. Thân máy ảnh (vàng, viền đen, góc vuông bo cực nhẹ 2px)
        body_y = h * 0.22
        body_h = h * 0.78
        body_w = w * 0.94
        body_x = (w - body_w) / 2.0

        painter.setPen(QPen(dark_color, 2.5))
        painter.setBrush(QBrush(yellow_color))
        painter.drawRoundedRect(QRectF(body_x, body_y, body_w, body_h), 2.0, 2.0)

        # 2. Gờ ống ngắm / nút bấm phía trên (phẳng)
        bump_w = w * 0.30
        bump_h = h * 0.20
        bump_x = (w - bump_w) / 2.0
        painter.drawRoundedRect(QRectF(bump_x, 1.0, bump_w, bump_h + 3), 1.5, 1.5)

        # Đèn flash nhỏ góc phải
        flash_w = w * 0.12
        flash_h = h * 0.08
        flash_x = body_x + body_w - flash_w - (w * 0.08)
        flash_y = body_y + (h * 0.10)
        painter.setPen(QPen(dark_color, 1.5))
        painter.setBrush(QBrush(dark_color))
        painter.drawRect(QRectF(flash_x, flash_y, flash_w, flash_h))

        # 3. Ống kính (vòng tròn màu đen)
        lens_r = min(body_w, body_h) * 0.38
        cx = w / 2.0
        cy = body_y + body_h / 2.0

        painter.setPen(QPen(dark_color, 2.5))
        painter.setBrush(QBrush(dark_color))
        painter.drawEllipse(QRectF(cx - lens_r, cy - lens_r, lens_r * 2.0, lens_r * 2.0))

        # 4. Hộp kiện hàng hình vuông (Square Package Box) bên trong ống kính
        box_size = lens_r * 1.05
        box_half = box_size / 2.0
        bx = cx - box_half
        by = cy - box_half

        painter.setPen(QPen(dark_color, 1.5))
        painter.setBrush(QBrush(box_color))
        painter.drawRect(QRectF(bx, by, box_size, box_size))

        # Chi tiết băng dán kiện hàng (đường chữ thập công nghiệp)
        painter.setPen(QPen(dark_color, 1.5))
        # Đường dọc giữa hộp
        painter.drawLine(int(cx), int(by), int(cx), int(by + box_size))
        # Đường ngang phân nắp hộp
        painter.drawLine(int(bx), int(cy - box_size * 0.15), int(bx + box_size), int(cy - box_size * 0.15))

        painter.end()


class KioskHeader(QWidget):
    """
    Thanh header chuẩn cho các màn hình Kiosk:
    - Nút Quay lại (có thể ẩn ở Welcome).
    - Logo FaceBox ở giữa hoặc bên trái.
    - Nút Bánh răng (truy cập chế độ Admin) ở góc trên bên phải.
    """

    back_clicked = Signal()
    gear_clicked = Signal()

    def __init__(self, show_back: bool = True, parent=None):
        super().__init__(parent)
        self.show_back = show_back
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(72)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(16)

        # Nút Back
        self.btn_back = QPushButton("← Quay lại")
        self.btn_back.setObjectName("back_btn")
        self.btn_back.setFixedHeight(44)
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.clicked.connect(self.back_clicked.emit)
        if not self.show_back:
            self.btn_back.setVisible(False)
        layout.addWidget(self.btn_back)

        layout.addStretch()

        # Logo trung tâm
        self.logo = FaceBoxLogo(size=38, show_text=True)
        layout.addWidget(self.logo)

        layout.addStretch()

        # Nút Gear (Admin)
        self.btn_gear = QPushButton("⚙️")
        self.btn_gear.setObjectName("gear_btn")
        self.btn_gear.setFixedSize(46, 46)
        self.btn_gear.setCursor(Qt.PointingHandCursor)
        self.btn_gear.setToolTip("Quản trị hệ thống (yêu cầu mật khẩu)")
        self.btn_gear.clicked.connect(self.gear_clicked.emit)
        layout.addWidget(self.btn_gear)

    def set_back_visible(self, visible: bool):
        self.btn_back.setVisible(visible)


class KioskActionCard(QPushButton):
    """
    Card lựa chọn kích thước lớn, dễ thao tác trên màn hình cảm ứng:
    - Biểu tượng lớn
    - Tiêu đề to rõ
    - Mô tả hướng dẫn
    - Hiệu ứng hover / click phản hồi xúc giác thị giác
    """

    def __init__(self, icon: str, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("kiosk_action")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("font-size: 52px; background: transparent; border: none;")
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; background: transparent; border: none;")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("font-size: 14px; color: #64748B; background: transparent; border: none;")
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setWordWrap(True)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.desc_label)


class TouchNumericKeypad(QWidget):
    """
    Bàn phím số cảm ứng kích thước lớn cho Kiosk:
    Gồm các phím 0-9, phím Xóa (Clear), phím Backspace, và phím Xác nhận (OK).
    """

    digit_pressed = Signal(str)     # Phát ký tự số ('0'-'9')
    backspace_pressed = Signal()    # Xóa 1 ký tự
    clear_pressed = Signal()        # Xóa tất cả
    submit_pressed = Signal()       # Bấm xác nhận

    def __init__(self, btn_height: int = 68, parent=None):
        super().__init__(parent)
        self.btn_height = btn_height
        self._setup_ui()

    def _setup_ui(self):
        grid = QGridLayout(self)
        grid.setSpacing(10)
        grid.setContentsMargins(0, 0, 0, 0)

        # Các phím số từ 1 đến 9
        buttons = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("Xóa", 3, 0), ("0", 3, 1), ("⌫", 3, 2),
        ]

        for text, r, c in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(self.btn_height)
            btn.setCursor(Qt.PointingHandCursor)

            if text.isdigit():
                btn.setObjectName("btn_secondary")
                btn.setStyleSheet(f"font-size: {int(self.btn_height * 0.36)}px; font-weight: bold; border-radius: 2px;")
                btn.clicked.connect(lambda checked, d=text: self.digit_pressed.emit(d))
            elif text == "Xóa":
                btn.setObjectName("btn_secondary")
                btn.setStyleSheet(f"font-size: 14px; font-weight: bold; color: #D94848; border-radius: 2px;")
                btn.clicked.connect(self.clear_pressed.emit)
            elif text == "⌫":
                btn.setObjectName("btn_secondary")
                btn.setStyleSheet(f"font-size: {int(self.btn_height * 0.34)}px; font-weight: bold; border-radius: 2px;")
                btn.clicked.connect(self.backspace_pressed.emit)

            grid.addWidget(btn, r, c)

