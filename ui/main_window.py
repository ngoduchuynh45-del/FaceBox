"""
FaceBox - Main Window
Cửa sổ chính tích hợp sidebar navigation và các trang con.
"""
import sys
import logging
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout,
                                QVBoxLayout, QPushButton, QLabel,
                                QStackedWidget, QMessageBox, QFrame,
                                QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

from ui.styles import MAIN_STYLE
from ui.components import FaceBoxLogo
from ui import theme
from ui.dashboard_page import DashboardPage
from ui.registration_page import RegistrationPage
from ui.recognition_page import RecognitionPage
from ui.accounts_page import AccountsPage
from ui.admin.history_page import HistoryPage
from ui.admin.locker_page import LockerPage
from ui.admin.settings_page import SettingsPage

from services.camera_service import CameraService
from services.face_recognition_service import FaceRecognitionService
from database import db_manager
import numpy as np

logger = logging.getLogger(__name__)

# Index của từng trang
PAGE_DASHBOARD = 0
PAGE_REGISTER  = 1
PAGE_RECOGNIZE = 2
PAGE_ACCOUNTS  = 3
PAGE_HISTORY   = 4
PAGE_LOCKERS   = 5
PAGE_SETTINGS  = 6


class ModelLoaderThread(QThread):
    """Thread tải mô hình AI để không block giao diện."""
    finished = Signal(bool, str)
    
    def __init__(self, face_service: FaceRecognitionService):
        super().__init__()
        self.face_service = face_service
    
    def run(self):
        success, msg = self.face_service.initialize()
        self.finished.emit(success, msg)


class MainWindow(QMainWindow):
    """Cửa sổ chính của FaceBox (Admin Mode)."""

    kiosk_requested = Signal()  # Phát khi người dùng bấm quay về Kiosk
    
    def __init__(self, face_service=None, camera_service=None):
        super().__init__()
        self.setWindowTitle("FaceBox - Nhận Diện Khuôn Mặt")
        self.setMinimumSize(1100, 700)
        self.resize(1200, 750)
        
        # Nhận hoặc khởi tạo services tập trung
        self.camera_service = camera_service if camera_service is not None else CameraService.get_instance()
        self.face_service = face_service if face_service is not None else FaceRecognitionService()
        
        # Áp dụng stylesheet chuẩn từ theme
        self.setStyleSheet(theme.stylesheet())
        theme.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Tạo giao diện
        self._setup_ui()
        
        # Khởi tạo database
        self._init_database()
        
        # Tải mô hình AI trong background nếu chưa sẵn sàng
        if not self.face_service.is_ready():
            self._load_model()
        else:
            self._update_model_status_ui()
        
        # Cập nhật trạng thái hiển thị camera ban đầu
        if self.camera_service.is_running():
            self.sidebar_cam_btn.setText("⏹  Tắt Camera")
            self.recognize_page.update_camera_status(True)
        
        # Timer cập nhật stats định kỳ
        self._stats_timer = QTimer()
        self._stats_timer.timeout.connect(self._update_dashboard_stats)
        self._stats_timer.start(2000)
        
        logger.info("MainWindow đã khởi tạo với services tập trung")
    
    def _setup_ui(self):
        """Xây dựng layout chính."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ========== SIDEBAR ==========
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(235)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo FaceBox Industrial Camera
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(14, 20, 14, 12)
        
        self.sidebar_logo = FaceBoxLogo(size=36, show_text=True)
        logo_layout.addWidget(self.sidebar_logo)
        sidebar_layout.addWidget(logo_widget)
        
        # Divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #2D2D2D;")
        sidebar_layout.addWidget(divider)
        sidebar_layout.addSpacing(8)
        
        # Nav buttons
        self.nav_buttons = []
        nav_items = [
            ("🏠  Tổng Quan",           PAGE_DASHBOARD),
            ("👤  Đăng Ký Khuôn Mặt",  PAGE_REGISTER),
            ("🔍  Nhận Diện Trực Tiếp", PAGE_RECOGNIZE),
            ("👥  Quản Lý Tài Khoản",  PAGE_ACCOUNTS),
            ("📋  Lịch Sử Gửi/Nhận",   PAGE_HISTORY),
            ("🗄️  Quản Lý Tủ",         PAGE_LOCKERS),
            ("⚙️  Cài Đặt",            PAGE_SETTINGS),
        ]
        
        for text, page_idx in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("nav_btn")
            btn.setFixedHeight(42)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=page_idx: self._navigate_to(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append((btn, page_idx))
        
        sidebar_layout.addStretch()
        
        # Camera toggle ở cuối sidebar
        sidebar_layout.addWidget(QFrame())  # Spacer
        self.sidebar_cam_btn = QPushButton("📷  Mở Camera")
        self.sidebar_cam_btn.setObjectName("nav_btn")
        self.sidebar_cam_btn.setFixedHeight(42)
        self.sidebar_cam_btn.setCursor(Qt.PointingHandCursor)
        self.sidebar_cam_btn.clicked.connect(self._toggle_camera)
        sidebar_layout.addWidget(self.sidebar_cam_btn)
        
        # Version
        version_lbl = QLabel("v1.1  |  Prototype")
        version_lbl.setStyleSheet("color: #2d3748; font-size: 10px; padding: 12px 16px;")
        sidebar_layout.addWidget(version_lbl)
        
        main_layout.addWidget(self.sidebar)
        
        # ========== CONTENT AREA ==========
        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")
        
        # Tạo các trang
        self.dashboard_page = DashboardPage()
        self.register_page = RegistrationPage(self.face_service, self.camera_service)
        self.recognize_page = RecognitionPage(self.face_service, self.camera_service)
        self.accounts_page = AccountsPage(self.face_service)
        self.history_page = HistoryPage()
        self.locker_page = LockerPage()
        self.settings_page = SettingsPage(self.face_service, self.camera_service)
        
        self.stack.addWidget(self.dashboard_page)  # 0
        self.stack.addWidget(self.register_page)   # 1
        self.stack.addWidget(self.recognize_page)  # 2
        self.stack.addWidget(self.accounts_page)   # 3
        self.stack.addWidget(self.history_page)    # 4
        self.stack.addWidget(self.locker_page)     # 5
        self.stack.addWidget(self.settings_page)   # 6
        
        main_layout.addWidget(self.stack)
        
        # Kết nối tín hiệu
        self.dashboard_page.navigate_to_register.connect(lambda: self._navigate_to(PAGE_REGISTER))
        self.dashboard_page.navigate_to_recognize.connect(lambda: self._navigate_to(PAGE_RECOGNIZE))
        self.dashboard_page.navigate_to_accounts.connect(lambda: self._navigate_to(PAGE_ACCOUNTS))
        self.dashboard_page.navigate_to_lockers.connect(lambda: self._navigate_to(PAGE_LOCKERS))
        self.dashboard_page.navigate_to_history.connect(lambda: self._navigate_to(PAGE_HISTORY))
        self.dashboard_page.open_camera_requested.connect(self._toggle_camera)
        self.accounts_page.data_changed.connect(self._update_dashboard_stats)
        self.settings_page.kiosk_requested.connect(self.kiosk_requested.emit)
        
        # Trang mặc định
        self._navigate_to(PAGE_DASHBOARD)
    
    def _navigate_to(self, page_idx: int):
        """Chuyển trang và cập nhật sidebar."""
        self.stack.setCurrentIndex(page_idx)
        
        for btn, idx in self.nav_buttons:
            is_active = (idx == page_idx)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _on_theme_changed(self):
        """Cập nhật giao diện khi người dùng đổi Light / Dark theme."""
        self.setStyleSheet(theme.stylesheet())
        if hasattr(self, "sidebar_logo"):
            self.sidebar_logo.update_theme()
    
    def _init_database(self):
        """Khởi tạo database."""
        try:
            db_manager.init_database()
            logger.info("Database đã khởi tạo")
        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi Database",
                f"Không thể khởi tạo cơ sở dữ liệu:\n{str(e)}\n\n"
                "Kiểm tra quyền ghi vào thư mục dự án."
            )
    
    def _update_model_status_ui(self):
        """Cập nhật trạng thái mô hình lên giao diện khi đã ready."""
        try:
            embeddings = db_manager.get_all_face_embeddings()
            if hasattr(self, "recognize_page"):
                self.recognize_page._update_status_display()
                self.recognize_page.update_face_count(len(embeddings))
        except Exception as e:
            logger.debug(f"Update model status UI error: {e}")

    def _load_model(self):
        """Tải mô hình AI trong background thread."""
        self._model_thread = ModelLoaderThread(self.face_service)
        self._model_thread.finished.connect(self._on_model_loaded)
        self._model_thread.start()
    
    def _on_model_loaded(self, success: bool, message: str):
        """Xử lý khi mô hình đã tải xong."""
        if success:
            logger.info("Mô hình AI đã tải thành công")
            # Nạp embedding từ DB
            try:
                db_path = db_manager.get_db_path()
                embeddings = db_manager.get_all_face_embeddings()
                acc_count = db_manager.get_total_accounts()
                self.face_service.load_known_embeddings(embeddings)
                logger.info(f"[Startup Log] Đường dẫn database thực tế: {db_path}")
                logger.info(f"[Startup Log] Tổng số tài khoản: {acc_count} | Tổng số profile embedding: {len(embeddings)}")
                if embeddings:
                    emb = embeddings[0]['embedding']
                    logger.info(f"[Startup Log] Thông tin embedding: shape={emb.shape}, dtype={emb.dtype}, norm={np.linalg.norm(emb):.4f}")
            except Exception as e:
                logger.error(f"[Startup Log] Lỗi nạp embedding: {e}")
        else:
            logger.error(f"Lỗi tải mô hình: {message}")
            # Hiển thị cảnh báo nhưng không block app
            QMessageBox.warning(
                self, "Cảnh báo - Mô hình nhận diện",
                f"Không thể tải mô hình nhận diện:\n\n{message}\n\n"
                "Hãy chạy: python models\\download_models.py\n\n"
                "Ứng dụng vẫn chạy nhưng chức năng nhận diện không khả dụng."
            )
    
    def _toggle_camera(self):
        """Bật/tắt camera."""
        if self.camera_service.is_running():
            self.camera_service.stop()
            self.sidebar_cam_btn.setText("📷  Mở Camera")
            self._update_dashboard_stats()
        else:
            self.camera_service.start(
                camera_index=0,
                on_frame=self._on_camera_frame,
                on_error=self._on_camera_error,
                on_status=self._on_camera_status
            )
    
    def _on_camera_frame(self, frame):
        """Phân phối frame đến các trang."""
        current_page = self.stack.currentIndex()
        if current_page == PAGE_REGISTER:
            self.register_page.update_frame(frame)
        elif current_page == PAGE_RECOGNIZE:
            self.recognize_page.update_frame(frame)
    
    def _on_camera_error(self, error_msg: str):
        """Xử lý lỗi camera."""
        QMessageBox.warning(self, "Lỗi Camera", error_msg)
        self._update_dashboard_stats()
    
    def _on_camera_status(self, is_active: bool):
        """Cập nhật khi trạng thái camera thay đổi."""
        if is_active:
            self.sidebar_cam_btn.setText("⏹  Tắt Camera")
        else:
            self.sidebar_cam_btn.setText("📷  Mở Camera")
        
        self.recognize_page.update_camera_status(is_active)
        self._update_dashboard_stats()
    
    def _update_dashboard_stats(self):
        """Cập nhật số liệu thống kê trên Dashboard."""
        try:
            acc_count = db_manager.get_total_accounts()
            face_count = db_manager.get_total_faces()
            locker_stats = db_manager.get_locker_stats()
            cam_active = self.camera_service.is_running()
            self.dashboard_page.update_stats(acc_count, face_count, cam_active, locker_stats)
            self.recognize_page.update_face_count(face_count)
        except Exception as e:
            logger.error(f"Lỗi cập nhật stats: {e}")
    
    def closeEvent(self, event):
        """Dọn dẹp khi đóng ứng dụng."""
        logger.info("Đang đóng ứng dụng...")
        self._stats_timer.stop()
        self.camera_service.stop()
        
        if hasattr(self, '_model_thread') and self._model_thread.isRunning():
            self._model_thread.quit()
            self._model_thread.wait(3000)
        
        super().closeEvent(event)
        logger.info("Ứng dụng đã đóng")
