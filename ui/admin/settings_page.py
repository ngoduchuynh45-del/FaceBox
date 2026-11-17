"""
FaceBox — Admin: Trang Cài Đặt
Điều chỉnh ngưỡng nhận diện, cài đặt camera, thay đổi mật khẩu admin,
và hiển thị thông tin hệ thống.
"""
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox,
    QGroupBox, QFormLayout, QMessageBox, QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui import theme
from database import db_manager

logger = logging.getLogger(__name__)

# Mật khẩu admin mặc định (prototype)
# TODO: Chuyển sang hash + salt khi deploy thực tế
_ADMIN_PASSWORD = "admin123"


class SettingsPage(QWidget):
    """Trang cài đặt hệ thống."""

    # Signal phát khi ngưỡng nhận diện thay đổi (để các trang khác cập nhật)
    threshold_changed = Signal(float)
    theme_changed = Signal(str)
    kiosk_requested = Signal()

    def __init__(self, face_service=None, camera_service=None, parent=None):
        super().__init__(parent)
        self.face_service = face_service
        self.camera_service = camera_service
        self._setup_ui()

    def _setup_ui(self):
        c = theme.colors()

        # Scroll area bao ngoài
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # ── Header ──
        title = QLabel("⚙️  Cài Đặt Hệ Thống")
        title.setStyleSheet(f"font-size: {theme.FONT_H1}px; font-weight: bold;")
        layout.addWidget(title)

        # ═══════════════════════════════════════════════════════
        # Section 0: Chế độ giao diện (Light / Dark Mode)
        # ═══════════════════════════════════════════════════════
        grp_theme = self._section("🎨  Chế Độ Giao Diện (Theme)")
        form0 = QFormLayout()
        form0.setSpacing(12)
        form0.setContentsMargins(16, 12, 16, 16)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["☀️ Sáng (Light Mode - InPost Yellow)", "🌙 Tối (Dark Mode - Industrial Black)"])
        self.combo_theme.setCurrentIndex(0 if theme.current_theme() == "light" else 1)
        form0.addRow("Chế độ hiển thị:", self.combo_theme)

        btn_apply_theme = QPushButton("Áp dụng giao diện")
        btn_apply_theme.setObjectName("btn_primary")
        btn_apply_theme.setFixedHeight(36)
        btn_apply_theme.setCursor(Qt.PointingHandCursor)
        btn_apply_theme.clicked.connect(self._apply_theme)
        form0.addRow("", btn_apply_theme)

        grp_theme.layout().addLayout(form0)
        layout.addWidget(grp_theme)

        # ═══════════════════════════════════════════════════════
        # Section 1: Ngưỡng nhận diện
        # ═══════════════════════════════════════════════════════
        grp_recognition = self._section("🎯  Nhận Diện Khuôn Mặt")
        form1 = QFormLayout()
        form1.setSpacing(12)
        form1.setContentsMargins(16, 12, 16, 16)

        # Ngưỡng cosine distance
        self.spin_threshold = QDoubleSpinBox()
        self.spin_threshold.setRange(0.10, 0.90)
        self.spin_threshold.setSingleStep(0.01)
        self.spin_threshold.setDecimals(3)
        self.spin_threshold.setValue(0.363)  # SFace default
        self.spin_threshold.setToolTip(
            "Cosine distance ≤ giá trị này → coi là cùng người.\n"
            "Nhỏ hơn = nghiêm ngặt hơn, lớn hơn = dễ nhận hơn.\n"
            "Mặc định SFace: 0.363"
        )
        form1.addRow("Ngưỡng nhận diện (Cosine Distance):", self.spin_threshold)

        # FPS nhận diện
        self.spin_fps = QSpinBox()
        self.spin_fps.setRange(1, 30)
        self.spin_fps.setValue(5)
        self.spin_fps.setSuffix(" FPS")
        self.spin_fps.setToolTip("Tốc độ quét khuôn mặt. Cao hơn = nhanh hơn nhưng tốn CPU hơn.")
        form1.addRow("Tốc độ quét:", self.spin_fps)

        # Số frame xác nhận
        self.spin_confirm = QSpinBox()
        self.spin_confirm.setRange(2, 10)
        self.spin_confirm.setValue(4)
        self.spin_confirm.setSuffix(" frame liên tiếp")
        self.spin_confirm.setToolTip("Số frame liên tiếp nhận đúng cùng 1 người để xác nhận.")
        form1.addRow("Xác nhận sau:", self.spin_confirm)

        # Nút áp dụng
        btn_apply_recog = QPushButton("Áp dụng thay đổi")
        btn_apply_recog.setObjectName("btn_primary")
        btn_apply_recog.setFixedHeight(36)
        btn_apply_recog.setCursor(Qt.PointingHandCursor)
        btn_apply_recog.clicked.connect(self._apply_recognition_settings)
        form1.addRow("", btn_apply_recog)

        grp_recognition.layout().addLayout(form1)
        layout.addWidget(grp_recognition)

        # ═══════════════════════════════════════════════════════
        # Section 2: Camera
        # ═══════════════════════════════════════════════════════
        grp_camera = self._section("📷  Camera")
        form2 = QFormLayout()
        form2.setSpacing(12)
        form2.setContentsMargins(16, 12, 16, 16)

        self.spin_cam_index = QSpinBox()
        self.spin_cam_index.setRange(0, 9)
        self.spin_cam_index.setValue(0)
        self.spin_cam_index.setToolTip("Chỉ số thiết bị camera (0 = camera mặc định)")
        form2.addRow("Thiết bị camera:", self.spin_cam_index)

        self.combo_resolution = QComboBox()
        self.combo_resolution.addItems([
            "640 × 480 (VGA)",
            "800 × 600 (SVGA)",
            "1280 × 720 (HD)",
            "1920 × 1080 (Full HD)",
        ])
        self.combo_resolution.setCurrentIndex(0)
        self.combo_resolution.setToolTip("Độ phân giải camera. Cao hơn = chi tiết hơn nhưng chậm hơn.")
        form2.addRow("Độ phân giải:", self.combo_resolution)

        # Nút áp dụng camera — TODO: tích hợp khi CameraService hỗ trợ thay đổi runtime
        btn_apply_cam = QPushButton("Áp dụng (cần khởi động lại camera)")
        btn_apply_cam.setObjectName("btn_secondary")
        btn_apply_cam.setFixedHeight(36)
        btn_apply_cam.setCursor(Qt.PointingHandCursor)
        btn_apply_cam.clicked.connect(self._apply_camera_settings)
        form2.addRow("", btn_apply_cam)

        grp_camera.layout().addLayout(form2)
        layout.addWidget(grp_camera)

        # ═══════════════════════════════════════════════════════
        # Section 3: Bảo mật
        # ═══════════════════════════════════════════════════════
        grp_security = self._section("🔒  Bảo Mật")
        form3 = QFormLayout()
        form3.setSpacing(12)
        form3.setContentsMargins(16, 12, 16, 16)

        self.txt_old_pw = QLineEdit()
        self.txt_old_pw.setEchoMode(QLineEdit.Password)
        self.txt_old_pw.setPlaceholderText("Nhập mật khẩu hiện tại")
        form3.addRow("Mật khẩu cũ:", self.txt_old_pw)

        self.txt_new_pw = QLineEdit()
        self.txt_new_pw.setEchoMode(QLineEdit.Password)
        self.txt_new_pw.setPlaceholderText("Nhập mật khẩu mới")
        form3.addRow("Mật khẩu mới:", self.txt_new_pw)

        self.txt_confirm_pw = QLineEdit()
        self.txt_confirm_pw.setEchoMode(QLineEdit.Password)
        self.txt_confirm_pw.setPlaceholderText("Nhập lại mật khẩu mới")
        form3.addRow("Xác nhận:", self.txt_confirm_pw)

        btn_change_pw = QPushButton("Đổi mật khẩu")
        btn_change_pw.setObjectName("btn_danger")
        btn_change_pw.setFixedHeight(36)
        btn_change_pw.setCursor(Qt.PointingHandCursor)
        btn_change_pw.clicked.connect(self._change_password)
        form3.addRow("", btn_change_pw)

        grp_security.layout().addLayout(form3)
        layout.addWidget(grp_security)

        # ═══════════════════════════════════════════════════════
        # Section 4: Thông tin hệ thống
        # ═══════════════════════════════════════════════════════
        grp_info = self._section("ℹ️  Thông Tin Hệ Thống")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(16, 12, 16, 16)
        info_layout.setSpacing(8)

        self.info_labels = {}
        info_items = [
            ("version", "Phiên bản ứng dụng:", "v1.1-alpha (Prototype)"),
            ("model", "Mô hình nhận diện:", "OpenCV YuNet + SFace"),
            ("embedding", "Kích thước embedding:", "128 chiều (float32)"),
            ("db_path", "Đường dẫn database:", db_manager.get_db_path()),
            ("accounts", "Số tài khoản:", "—"),
            ("faces", "Số khuôn mặt:", "—"),
            ("lockers", "Số ngăn tủ:", "—"),
        ]

        for key, label, value in info_items:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {theme.colors().text_muted}; font-size: {theme.FONT_SM}px;")
            lbl.setFixedWidth(200)
            val = QLabel(value)
            val.setStyleSheet(f"font-size: {theme.FONT_SM}px;")
            val.setWordWrap(True)
            row.addWidget(lbl)
            row.addWidget(val, stretch=1)
            info_layout.addLayout(row)
            self.info_labels[key] = val

        grp_info.layout().addLayout(info_layout)
        layout.addWidget(grp_info)

        # ═══════════════════════════════════════════════════════
        # Section 5: Điều hướng Kiosk
        # ═══════════════════════════════════════════════════════
        grp_nav = self._section("🚪  Điều Hướng & Đăng Xuất")
        nav_lay = QVBoxLayout()
        nav_lay.setContentsMargins(16, 12, 16, 16)
        btn_kiosk = QPushButton("🖥️  ĐĂNG XUẤT & QUAY VỀ KIOSK")
        btn_kiosk.setFixedHeight(46)
        btn_kiosk.setCursor(Qt.PointingHandCursor)
        btn_kiosk.setStyleSheet(
            "background-color: #FFD500; color: #171717; font-weight: 900; "
            "border: 2px solid #171717; border-radius: 2px; font-size: 15px;"
        )
        btn_kiosk.clicked.connect(self.kiosk_requested.emit)
        nav_lay.addWidget(btn_kiosk)
        grp_nav.layout().addLayout(nav_lay)
        layout.addWidget(grp_nav)

        layout.addStretch()

        scroll.setWidget(content)

        # Layout chính chỉ chứa scroll area
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _section(self, title: str) -> QFrame:
        """Tạo khung section có tiêu đề."""
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel(title)
        header.setStyleSheet(
            f"font-size: {theme.FONT_H3}px; font-weight: bold; "
            f"padding: 16px 16px 8px 16px;"
        )
        layout.addWidget(header)
        return frame

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_system_info()

    def _refresh_system_info(self):
        """Cập nhật thông tin hệ thống."""
        try:
            acc = db_manager.get_total_accounts()
            faces = db_manager.get_total_faces()
            stats = db_manager.get_locker_stats()
            self.info_labels['accounts'].setText(str(acc))
            self.info_labels['faces'].setText(str(faces))
            self.info_labels['lockers'].setText(
                f"{stats['total']} (Trống: {stats['empty']}, Đang dùng: {stats['occupied']}, Lỗi: {stats['error']})"
            )
        except Exception as e:
            logger.error(f"Lỗi lấy thông tin hệ thống: {e}")

    def _apply_theme(self):
        """Thay đổi theme Light / Dark Mode và cập nhật toàn bộ ứng dụng."""
        new_theme = "light" if self.combo_theme.currentIndex() == 0 else "dark"
        theme.set_theme(new_theme)
        self.theme_changed.emit(new_theme)

        # Cập nhật stylesheet cho cửa sổ chính
        top = self.window()
        if top:
            top.setStyleSheet(theme.stylesheet())

        QMessageBox.information(
            self, "Giao diện",
            f"Đã chuyển sang chế độ: {'☀️ Sáng (Light Mode)' if new_theme == 'light' else '🌙 Tối (Dark Mode)'}."
        )

    def _apply_recognition_settings(self):
        """Áp dụng thay đổi cài đặt nhận diện."""
        threshold = self.spin_threshold.value()
        fps = self.spin_fps.value()
        confirm_frames = self.spin_confirm.value()

        # Cập nhật face_service nếu có
        if self.face_service and hasattr(self.face_service, 'set_threshold'):
            self.face_service.set_threshold(threshold)

        self.threshold_changed.emit(threshold)

        logger.info(f"Cài đặt nhận diện: threshold={threshold}, fps={fps}, confirm={confirm_frames}")
        QMessageBox.information(
            self, "Đã áp dụng",
            f"Ngưỡng nhận diện: {threshold}\n"
            f"Tốc độ quét: {fps} FPS\n"
            f"Xác nhận sau: {confirm_frames} frame\n\n"
            "Lưu ý: Một số thay đổi cần khởi động lại màn hình nhận diện để có hiệu lực."
        )

    def _apply_camera_settings(self):
        """Thông báo cài đặt camera — TODO: tích hợp runtime."""
        cam_idx = self.spin_cam_index.value()
        res_idx = self.combo_resolution.currentIndex()
        res_map = [(640, 480), (800, 600), (1280, 720), (1920, 1080)]
        w, h = res_map[res_idx]

        logger.info(f"Cài đặt camera: index={cam_idx}, resolution={w}x{h}")
        QMessageBox.information(
            self, "Cài đặt camera",
            f"Camera: thiết bị #{cam_idx}\n"
            f"Độ phân giải: {w} × {h}\n\n"
            "Lưu ý: Tính năng thay đổi camera runtime đang phát triển.\n"
            "Hiện tại cần khởi động lại ứng dụng để áp dụng."
        )

    def _change_password(self):
        """Đổi mật khẩu admin (prototype: lưu trong bộ nhớ)."""
        global _ADMIN_PASSWORD
        old = self.txt_old_pw.text()
        new = self.txt_new_pw.text()
        confirm = self.txt_confirm_pw.text()

        if old != _ADMIN_PASSWORD:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu cũ không đúng.")
            return
        if len(new) < 4:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu mới phải có ít nhất 4 ký tự.")
            return
        if new != confirm:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp.")
            return

        _ADMIN_PASSWORD = new
        self.txt_old_pw.clear()
        self.txt_new_pw.clear()
        self.txt_confirm_pw.clear()

        logger.info("Mật khẩu admin đã được thay đổi")
        QMessageBox.information(self, "Thành công", "Đã đổi mật khẩu admin.")

