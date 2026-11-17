"""
FaceBox - Trang Tổng Quan (Dashboard)
Hiển thị thống kê, trạng thái webcam và nút điều hướng nhanh.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QFrame, QGridLayout,
                                QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ui.widgets import StatCard, StatusBadge, SectionTitle


class DashboardPage(QWidget):
    """Trang tổng quan chính."""
    
    # Tín hiệu điều hướng
    navigate_to_register = Signal()
    navigate_to_recognize = Signal()
    navigate_to_accounts = Signal()
    navigate_to_lockers = Signal()
    navigate_to_history = Signal()
    open_camera_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)
        
        # ---- Header ----
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_area = QVBoxLayout()
        title = QLabel("Tổng Quan")
        title.setObjectName("page_title")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e2e8f0;")
        
        subtitle = QLabel("Quản lý nhận diện khuôn mặt")
        subtitle.setStyleSheet("color: #64748b; font-size: 13px; margin-top: 4px;")
        
        title_area.addWidget(title)
        title_area.addWidget(subtitle)
        
        self.camera_badge = StatusBadge()
        header_layout.addLayout(title_area)
        header_layout.addStretch()
        header_layout.addWidget(self.camera_badge)
        
        layout.addWidget(header)
        layout.addSpacing(24)
        
        # ---- Stats Row ----
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.account_card = StatCard("0", "Tài khoản đã đăng ký", "#818cf8")
        self.face_card = StatCard("0", "Khuôn mặt đã lưu", "#34d399")
        self.locker_card = StatCard("0/0", "Ngăn tủ (Trống/Tổng)", "#38bdf8")
        self.status_card = StatCard("OFF", "Trạng thái Camera", "#fbbf24")
        
        stats_layout.addWidget(self.account_card)
        stats_layout.addWidget(self.face_card)
        stats_layout.addWidget(self.locker_card)
        stats_layout.addWidget(self.status_card)
        
        layout.addLayout(stats_layout)
        layout.addSpacing(24)
        
        # ---- Quick Actions ----
        actions_title = SectionTitle("Thao tác nhanh")
        layout.addWidget(actions_title)
        layout.addSpacing(12)
        
        actions_grid = QGridLayout()
        actions_grid.setSpacing(12)
        
        # Nút mở camera
        self.btn_camera = self._make_action_btn(
            "📷  Mở Camera", 
            "Bật webcam để bắt đầu",
            "#1e2d54", "#818cf8"
        )
        self.btn_camera.clicked.connect(self.open_camera_requested)
        
        # Nút đăng ký
        btn_register = self._make_action_btn(
            "👤  Đăng Ký Khuôn Mặt",
            "Thêm tài khoản và khuôn mặt mới",
            "#064e3b", "#34d399"
        )
        btn_register.clicked.connect(self.navigate_to_register)
        
        # Nút nhận diện
        btn_recognize = self._make_action_btn(
            "🔍  Nhận Diện Trực Tiếp",
            "Nhận diện khuôn mặt qua webcam",
            "#1a1f35", "#818cf8"
        )
        btn_recognize.clicked.connect(self.navigate_to_recognize)
        
        # Nút quản lý tài khoản
        btn_accounts = self._make_action_btn(
            "👥  Quản Lý Tài Khoản",
            "Xem và xóa tài khoản, khuôn mặt",
            "#1a0a1a", "#a78bfa"
        )
        btn_accounts.clicked.connect(self.navigate_to_accounts)

        # Nút quản lý tủ
        btn_lockers = self._make_action_btn(
            "🗄️  Quản Lý Ngăn Tủ",
            "Xem sơ đồ và thêm/sửa ngăn tủ",
            "#082f49", "#38bdf8"
        )
        btn_lockers.clicked.connect(self.navigate_to_lockers)

        # Nút lịch sử
        btn_history = self._make_action_btn(
            "📋  Lịch Sử Gửi/Nhận",
            "Tra cứu nhật ký mở tủ và giao dịch",
            "#2e1065", "#c084fc"
        )
        btn_history.clicked.connect(self.navigate_to_history)
        
        actions_grid.addWidget(self.btn_camera, 0, 0)
        actions_grid.addWidget(btn_register, 0, 1)
        actions_grid.addWidget(btn_recognize, 1, 0)
        actions_grid.addWidget(btn_accounts, 1, 1)
        actions_grid.addWidget(btn_lockers, 2, 0)
        actions_grid.addWidget(btn_history, 2, 1)
        
        layout.addLayout(actions_grid)
        
        # ---- Security Notice ----
        layout.addSpacing(24)
        notice = QFrame()
        notice.setObjectName("card")
        notice_layout = QHBoxLayout(notice)
        notice_layout.setContentsMargins(16, 12, 16, 12)
        
        icon = QLabel("⚠️")
        icon.setStyleSheet("font-size: 18px;")
        icon.setFixedWidth(30)
        
        notice_text = QLabel(
            "<b style='color:#fbbf24'>Lưu ý Bảo mật:</b> "
            "<span style='color:#94a3b8'>Đây là phiên bản prototype. Dữ liệu khuôn mặt là thông tin "
            "sinh trắc học nhạy cảm. Chưa có cơ chế chống giả mạo (liveness detection). "
            "Không sử dụng để kiểm soát an ninh thực tế.</span>"
        )
        notice_text.setWordWrap(True)
        notice_text.setStyleSheet("font-size: 12px;")
        
        notice_layout.addWidget(icon)
        notice_layout.addWidget(notice_text)
        layout.addWidget(notice)
        layout.addStretch()
    
    def _make_action_btn(self, title: str, subtitle: str, bg_color: str, accent_color: str) -> QPushButton:
        """Tạo nút action card phong cách industrial locker."""
        frame = QPushButton()
        frame.setFixedHeight(84)
        frame.setCursor(Qt.PointingHandCursor)
        frame.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 2px solid {accent_color};
                border-radius: 2px;
                text-align: left;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: {accent_color};
                border-color: #FFD500;
            }}
        """)
        
        inner_layout = QVBoxLayout(frame)
        inner_layout.setContentsMargins(20, 14, 20, 14)
        inner_layout.setSpacing(4)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {accent_color}; font-size: 15px; font-weight: bold; background: transparent; border: none;")
        title_lbl.setAttribute(Qt.WA_TranslucentBackground)
        title_lbl.setMouseTracking(False)
        
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("color: #64748b; font-size: 12px; background: transparent; border: none;")
        sub_lbl.setAttribute(Qt.WA_TranslucentBackground)
        
        inner_layout.addWidget(title_lbl)
        inner_layout.addWidget(sub_lbl)
        
        frame._title_lbl = title_lbl
        frame._sub_lbl = sub_lbl
        
        return frame
    
    def update_stats(self, account_count: int, face_count: int, camera_active: bool, locker_stats: dict = None):
        """Cập nhật thống kê."""
        self.account_card.update_value(str(account_count))
        self.face_card.update_value(str(face_count))
        self.status_card.update_value("ON" if camera_active else "OFF")
        
        if locker_stats:
            empty = locker_stats.get('empty', 0)
            total = locker_stats.get('total', 0)
            self.locker_card.update_value(f"{empty}/{total}")
        
        if camera_active:
            self.camera_badge.set_active("● Camera đang hoạt động")
            if hasattr(self.btn_camera, "_title_lbl"):
                self.btn_camera._title_lbl.setText("⏹  Tắt Camera")
                self.btn_camera._sub_lbl.setText("Dừng phát video từ webcam")
        else:
            self.camera_badge.set_inactive("○ Camera chưa bật")
            if hasattr(self.btn_camera, "_title_lbl"):
                self.btn_camera._title_lbl.setText("📷  Mở Camera")
                self.btn_camera._sub_lbl.setText("Bật webcam để bắt đầu")
