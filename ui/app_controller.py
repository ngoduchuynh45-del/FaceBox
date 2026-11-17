"""
FaceBox — App Controller
Bộ điều phối chế độ hoạt động chính của FaceBox:
- Quản lý hai chế độ riêng biệt: KIOSK_MODE và ADMIN_MODE.
- Mặc định khởi động vào KIOSK_MODE (dành cho người gửi/nhận hàng).
- Chuyển sang ADMIN_MODE khi người quản trị bấm ⚙️ và xác thực mật khẩu.
- Chuyển lại KIOSK_MODE khi bấm nút 'Về Kiosk' trong Admin.
- Quản lý tập trung CameraService và FaceRecognitionService, phân phối frame camera.
"""

import sys
import logging
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer

from ui import theme
from ui.kiosk.kiosk_shell import KioskShell
from ui.main_window import MainWindow, ModelLoaderThread
from services.camera_service import CameraService
from services.face_recognition_service import FaceRecognitionService
from database import db_manager

logger = logging.getLogger("facebox.controller")

MODE_KIOSK = 0
MODE_ADMIN = 1


class AppController(QMainWindow):
    """Cửa sổ chính điều phối toàn bộ ứng dụng FaceBox."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaceBox — Hệ Thống Tủ Thông Minh & Định Danh Sinh Trắc Học")
        self.setMinimumSize(1100, 720)
        self.resize(1240, 780)

        # 1. Khởi tạo các services cốt lõi
        self.camera_service = CameraService()
        self.face_service = FaceRecognitionService()

        # 2. Khởi tạo cơ sở dữ liệu SQLite
        self._init_database()

        # 3. Áp dụng stylesheet hệ thống
        self.setStyleSheet(theme.stylesheet())

        # 4. Tạo Stack chứa 2 chế độ (Kiosk vs Admin)
        self.root_stack = QStackedWidget()
        self.setCentralWidget(self.root_stack)

        # Tạo Kiosk Shell
        self.kiosk_shell = KioskShell(self.face_service, self.camera_service)
        self.kiosk_shell.admin_login_requested.connect(self.switch_to_admin)
        self.root_stack.addWidget(self.kiosk_shell)  # Index 0: Kiosk

        # Tạo Admin Shell (dùng chung instance services tập trung)
        self.admin_shell = MainWindow(face_service=self.face_service, camera_service=self.camera_service)
        self.admin_shell.kiosk_requested.connect(self.switch_to_kiosk)
        self._setup_admin_kiosk_return_btn()
        self.root_stack.addWidget(self.admin_shell)  # Index 1: Admin

        # 5. Mặc định mở Kiosk Mode khi khởi động
        self.root_stack.setCurrentIndex(MODE_KIOSK)

        # 6. Tải mô hình AI nền
        self._load_models_background()

        # 7. Khởi động Camera Service và kết nối phân phối frame
        self._start_camera_service()

        logger.info("AppController đã khởi tạo thành công. Mặc định: KIOSK_MODE")

    def _init_database(self):
        """Khởi tạo database an toàn."""
        try:
            db_manager.init_database()
            logger.info("Database SQLite đã sẵn sàng")
        except Exception as e:
            logger.error(f"Lỗi khởi tạo database: {e}")

    def _setup_admin_kiosk_return_btn(self):
        """Bổ sung nút 'Quay về Kiosk' vào sidebar của Admin với typography tối ưu."""
        try:
            from PySide6.QtWidgets import QPushButton
            btn_kiosk = QPushButton("◀  QUAY VỀ KIOSK")
            btn_kiosk.setObjectName("btn_return_kiosk")
            btn_kiosk.setFixedHeight(44)
            btn_kiosk.setCursor(Qt.PointingHandCursor)
            btn_kiosk.setStyleSheet("""
                QPushButton#btn_return_kiosk {
                    background-color: #FFD500;
                    color: #171717;
                    border: 2px solid #171717;
                    border-radius: 2px;
                    margin: 6px 10px;
                    padding: 8px 12px;
                    font-size: 13px;
                    font-weight: 900;
                    letter-spacing: 0.5px;
                    text-align: center;
                }
                QPushButton#btn_return_kiosk:hover {
                    background-color: #FFE033;
                    border-color: #000000;
                }
                QPushButton#btn_return_kiosk:pressed {
                    background-color: #ECC500;
                }
            """)
            btn_kiosk.clicked.connect(self.switch_to_kiosk)

            # Chèn vào sidebar của Admin MainWindow phía trên camera toggle
            sidebar_layout = self.admin_shell.sidebar.layout()
            sidebar_layout.insertWidget(sidebar_layout.count() - 2, btn_kiosk)
        except Exception as e:
            logger.warning(f"Không thể thêm nút Quay về Kiosk vào Admin: {e}")

    def _load_models_background(self):
        """Nạp mô hình YuNet + SFace trong background thread."""
        self._model_thread = ModelLoaderThread(self.face_service)
        self._model_thread.finished.connect(self._on_model_loaded)
        self._model_thread.start()

    def _on_model_loaded(self, success: bool, message: str):
        if success:
            logger.info("Mô hình AI YuNet + SFace đã nạp thành công")
            try:
                embeddings = db_manager.get_all_face_embeddings()
                self.face_service.load_known_embeddings(embeddings)
                logger.info(f"Đã nạp {len(embeddings)} profile embedding từ database vào bộ nhớ nhận diện")
            except Exception as e:
                logger.error(f"Lỗi nạp embedding từ DB: {e}")
        else:
            logger.error(f"Lỗi nạp mô hình AI: {message}")

    def _start_camera_service(self):
        """Khởi động camera và phân phối frame liên tục tới chế độ đang kích hoạt."""
        self.camera_service.start(
            camera_index=0,
            on_frame=self._on_camera_frame,
            on_error=self._on_camera_error
        )

    def _on_camera_frame(self, frame: np.ndarray):
        """Phân phối frame tới Shell đang hiển thị."""
        current_mode = self.root_stack.currentIndex()
        if current_mode == MODE_KIOSK:
            self.kiosk_shell.update_frame(frame)
        elif current_mode == MODE_ADMIN:
            self.admin_shell._on_camera_frame(frame)

    def _on_camera_error(self, err_msg: str):
        logger.warning(f"Camera warning: {err_msg}")

    def switch_to_admin(self):
        """Chuyển sang chế độ Quản trị (Admin Mode)."""
        logger.info("Chuyển sang ADMIN_MODE")
        self.root_stack.setCurrentIndex(MODE_ADMIN)
        if hasattr(self.admin_shell, "sidebar_cam_btn"):
            if self.camera_service.is_running():
                self.admin_shell.sidebar_cam_btn.setText("⏹  Tắt Camera")
            else:
                self.admin_shell.sidebar_cam_btn.setText("📷  Mở Camera")
        if hasattr(self.admin_shell, "recognize_page"):
            self.admin_shell.recognize_page.update_camera_status(self.camera_service.is_running())
        self.admin_shell._update_dashboard_stats()

    def switch_to_kiosk(self):
        """Chuyển về chế độ Kiosk phục vụ khách hàng."""
        logger.info("Chuyển về KIOSK_MODE")
        self.kiosk_shell.go_to_welcome()
        self.root_stack.setCurrentIndex(MODE_KIOSK)

    def closeEvent(self, event):
        """Dọn dẹp tài nguyên khi đóng ứng dụng."""
        logger.info("Đang đóng FaceBox...")
        if hasattr(self, "camera_service"):
            self.camera_service.stop()
        if hasattr(self, "_model_thread") and self._model_thread.isRunning():
            self._model_thread.quit()
            self._model_thread.wait(3000)
        super().closeEvent(event)

