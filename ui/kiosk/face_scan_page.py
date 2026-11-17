"""
FaceBox — Kiosk Face Scan Page
Màn hình 4: Quét khuôn mặt trực tiếp tại Kiosk.
- Hiển thị camera qua EllipseCameraView.
- Khung elip đổi màu trực quan (xám -> vàng khi chưa rõ -> xanh khi nhận diện thành công).
- Tích hợp RecognitionConfirmer: yêu cầu 4 frame liên tiếp để xác nhận chính xác tài khoản.
- Hiển thị số điện thoại tài khoản xác thực thành công.
- Có thông báo hướng dẫn khi không tìm thấy tài khoản hoặc khuôn mặt chưa đúng vị trí.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
import numpy as np
import logging

from ui.components import KioskHeader
from ui.widgets import (
    EllipseCameraView,
    FACE_STATE_NONE, FACE_STATE_TOO_FAR, FACE_STATE_TOO_CLOSE,
    FACE_STATE_OFFCENTER, FACE_STATE_READY, FACE_STATE_SUCCESS
)
from services.face_recognition_service import RecognitionConfirmer
from ui import theme

logger = logging.getLogger("facebox.kiosk.face_scan")


class FaceScanPage(QWidget):
    """Màn hình quét khuôn mặt tại Kiosk."""

    back_clicked = Signal()
    admin_requested = Signal()
    authenticated = Signal(dict)   # Phát thông tin tài khoản: {'phone_number': ..., 'account_id': ..., 'similarity': ...}
    switch_to_phone = Signal()     # Chuyển sang nhập SĐT khi muốn đổi phương thức

    def __init__(self, face_service, camera_service, parent=None):
        super().__init__(parent)
        self.setObjectName("kiosk_page")
        self.face_service = face_service
        self.camera_service = camera_service

        self._confirmer = RecognitionConfirmer(required_frames=4)
        self._is_active = False
        self._is_success = False

        # Timer chạy nhận diện định kỳ (5 FPS để tiết kiệm CPU và mượt giao diện)
        self._recog_timer = QTimer(self)
        self._recog_timer.setInterval(200)
        self._recog_timer.timeout.connect(self._process_recognition)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 16, 32, 24)
        layout.setSpacing(12)

        # Header
        self.header = KioskHeader(show_back=True)
        self.header.back_clicked.connect(self._on_back)
        self.header.gear_clicked.connect(self.admin_requested.emit)
        layout.addWidget(self.header)

        # Thanh thông tin trạng thái & tài khoản phía trên camera
        top_info_box = QVBoxLayout()
        top_info_box.setSpacing(4)

        self.title_label = QLabel("Đang quét khuôn mặt...")
        self.title_label.setObjectName("kiosk_title")
        self.title_label.setStyleSheet("font-size: 26px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)

        # Banner hiển thị số điện thoại khi nhận diện thành công
        self.phone_banner = QLabel("Vui lòng nhìn thẳng vào camera bên dưới")
        self.phone_banner.setAlignment(Qt.AlignCenter)
        self.phone_banner.setStyleSheet(
            f"font-size: 16px; color: {theme.colors().text_secondary}; padding: 4px;"
        )

        top_info_box.addWidget(self.title_label)
        top_info_box.addWidget(self.phone_banner)
        layout.addLayout(top_info_box)

        # Vùng hiển thị camera với khung hình elip chuyên dụng
        cam_container = QHBoxLayout()
        self.camera_view = EllipseCameraView()
        self.camera_view.setMinimumSize(540, 400)
        self.camera_view.set_scanning(True)
        cam_container.addWidget(self.camera_view, alignment=Qt.AlignCenter)
        layout.addLayout(cam_container, stretch=1)

        # Hộp thông báo phản hồi (Status / Error pill - Phong cách Industrial)
        self.status_pill = QLabel("Đang tìm kiếm khuôn mặt...")
        self.status_pill.setAlignment(Qt.AlignCenter)
        self.status_pill.setStyleSheet(
            "background-color: #252525; color: #FFFFFF; "
            "border: 2px solid #3A3A3A; border-radius: 2px; "
            "padding: 8px 24px; font-size: 15px; font-weight: bold;"
        )
        layout.addWidget(self.status_pill, alignment=Qt.AlignCenter)

        # Nút chuyển sang nhập số điện thoại dự phòng
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()

        self.btn_switch_phone = QPushButton("📱 Nhập số điện thoại thay thế")
        self.btn_switch_phone.setObjectName("btn_secondary")
        self.btn_switch_phone.setFixedHeight(46)
        self.btn_switch_phone.setCursor(Qt.PointingHandCursor)
        self.btn_switch_phone.setStyleSheet(
            "border-radius: 2px; font-weight: bold; border: 2px solid #3A3A3A; padding: 0 20px;"
        )
        self.btn_switch_phone.clicked.connect(self._on_switch_phone)
        bottom_row.addWidget(self.btn_switch_phone)

        bottom_row.addStretch()
        layout.addLayout(bottom_row)

    def showEvent(self, event):
        """Kích hoạt quét khi màn hình hiển thị."""
        super().showEvent(event)
        self._is_active = True
        self._is_success = False
        self._confirmer.reset()

        self.title_label.setText("Đang quét khuôn mặt...")
        self.title_label.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {theme.colors().text};")
        self.phone_banner.setText("Vui lòng nhìn thẳng vào camera bên dưới")
        self.phone_banner.setStyleSheet(f"font-size: 16px; color: {theme.colors().text_secondary};")

        self.camera_view.set_scanning(True)
        self.camera_view.set_face_state(FACE_STATE_NONE)
        self.camera_view.set_custom_label("Đưa khuôn mặt vào giữa khung hình")

        self._recog_timer.start()

    def hideEvent(self, event):
        """Dừng nhận diện khi rời khỏi màn hình."""
        super().hideEvent(event)
        self._is_active = False
        self._recog_timer.stop()
        self.camera_view.set_scanning(False)

    def update_frame(self, frame: np.ndarray):
        """Hiển thị frame camera từ CameraService."""
        if self._is_active:
            self.camera_view.display_frame(frame)

    def _process_recognition(self):
        """Thực hiện nhận diện khuôn mặt trên frame hiện tại."""
        if not self._is_active or self._is_success:
            return

        if not self.camera_service.is_running():
            try:
                self.camera_service.start()
            except Exception:
                pass
            self.status_pill.setText("⚠️ Đang kết nối camera...")
            return

        if not self.face_service.is_ready():
            self.status_pill.setText("⚠️ Mô hình AI đang khởi động, vui lòng chờ giây lát...")
            return

        frame = self.camera_service.get_current_frame()
        if frame is None:
            self.status_pill.setText("Đang chờ tín hiệu hình ảnh...")
            return

        # 1. Phát hiện & nhận diện khuôn mặt (YuNet + SFace)
        try:
            results = self.face_service.recognize_in_frame(frame)
        except Exception as e:
            logger.error(f"Lỗi nhận diện khuôn mặt: {e}")
            return

        # 2. Phân loại kết quả theo yêu cầu nghiệp vụ
        if not results:
            # Trạng thái: Không phát hiện khuôn mặt / Đang tìm khuôn mặt
            self.camera_view.set_face_state(FACE_STATE_NONE)
            self.camera_view.set_custom_label("Đưa khuôn mặt vào giữa khung elip")
            self.status_pill.setText("Đang tìm kiếm khuôn mặt...")
            self.status_pill.setStyleSheet(
                f"background-color: {theme.colors().surface}; "
                f"color: {theme.colors().text_secondary}; "
                f"border: 1px solid {theme.colors().border}; "
                f"border-radius: {theme.R_PILL}px; "
                f"padding: 8px 24px; font-size: 15px; font-weight: 500;"
            )
            self._confirmer.reset()
            return

        if len(results) > 1:
            # Trạng thái: Phát hiện nhiều khuôn mặt
            self.camera_view.set_face_state(FACE_STATE_OFFCENTER)
            self.camera_view.set_custom_label("Phát hiện nhiều người trước camera")
            self.status_pill.setText("⚠️ Phát hiện nhiều khuôn mặt. Vui lòng chỉ 1 người đứng trước camera.")
            self.status_pill.setStyleSheet(
                "background-color: #FFF6E0; color: #C97D12; border: 1px solid #C97D12; "
                "border-radius: 999px; padding: 8px 24px; font-size: 14px; font-weight: bold;"
            )
            self._confirmer.reset()
            return

        # Xử lý 1 khuôn mặt hợp lệ
        target_face = results[0]
        identified = target_face.get("identified", False)
        phone = target_face.get("phone_number", "")
        sim = target_face.get("similarity", 0.0)

        # Đánh giá vị trí khuôn mặt so với elip
        geom_state, geom_msg = self.camera_view.evaluate_face_geometry(
            target_face['bbox'], frame.shape[1], frame.shape[0]
        )

        # Ghi nhận qua RecognitionConfirmer (yêu cầu 4 frame liên tiếp)
        confirmed_phone, is_confirmed = self._confirmer.add_result(phone if identified else None)

        if identified and is_confirmed and confirmed_phone:
            # Trạng thái: Nhận diện thành công và được xác nhận ổn định!
            self._is_success = True
            self._recog_timer.stop()

            self.camera_view.set_scanning(False)
            self.camera_view.set_face_state(FACE_STATE_SUCCESS)
            self.camera_view.set_custom_label(f"Xác thực thành công: {confirmed_phone} ✓")

            # Cập nhật thông tin giao diện
            self.title_label.setText("✅ XÁC THỰC THÀNH CÔNG")
            self.title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #16A36A;")

            self.phone_banner.setText(f"Số điện thoại: {confirmed_phone}")
            self.phone_banner.setStyleSheet("font-size: 20px; font-weight: bold; color: #16A36A; padding: 4px;")

            self.status_pill.setText(f"Chào mừng bạn! Đang chuyển tiếp...")
            self.status_pill.setStyleSheet(
                "background-color: #DFFBE9; color: #16A36A; border: 1px solid #16A36A; "
                "border-radius: 999px; padding: 8px 24px; font-size: 15px; font-weight: bold;"
            )

            # Chuyển bước tiếp theo sau khi người dùng thấy kết quả phản hồi
            QTimer.singleShot(900, lambda: self.authenticated.emit({
                "phone_number": confirmed_phone,
                "account_id": target_face.get("account_id"),
                "similarity": sim,
                "method": "face"
            }))

        elif identified:
            # Trạng thái: Đang xác thực (đang tích lũy frame xác nhận)
            self.camera_view.set_face_state(FACE_STATE_READY)
            self.camera_view.set_custom_label(f"Nhận diện {phone}... Vui lòng giữ yên")
            self.status_pill.setText(f"Đang xác thực danh tính... Giữ yên khuôn mặt")
            self.status_pill.setStyleSheet(
                f"background-color: {theme.colors().surface}; "
                f"color: {theme.colors().primary}; "
                f"border: 1px solid {theme.colors().primary}; "
                f"border-radius: {theme.R_PILL}px; "
                f"padding: 8px 24px; font-size: 15px; font-weight: bold;"
            )
        elif geom_state != FACE_STATE_READY:
            # Khuôn mặt chưa đúng vị trí (quá xa / quá gần / lệch tâm)
            self.camera_view.set_face_state(geom_state)
            self.camera_view.set_custom_label(geom_msg)
            self.status_pill.setText(geom_msg)
            self.status_pill.setStyleSheet(
                "background-color: #FDE8E8; color: #D94848; border: 1px solid #D94848; "
                "border-radius: 999px; padding: 8px 24px; font-size: 14px;"
            )
        else:
            # Trạng thái: Vị trí đúng nhưng chưa tìm thấy tài khoản
            self.camera_view.set_face_state(FACE_STATE_OFFCENTER)
            self.camera_view.set_custom_label("Khuôn mặt chưa khớp với tài khoản nào")
            self.status_pill.setText("Không tìm thấy tài khoản tương ứng. Bạn có thể chọn nhập SĐT bên dưới.")
            self.status_pill.setStyleSheet(
                "background-color: #FDE8E8; color: #D94848; border: 1px solid #D94848; "
                "border-radius: 999px; padding: 8px 24px; font-size: 14px;"
            )

    def _on_back(self):
        self._is_active = False
        self._recog_timer.stop()
        self.back_clicked.emit()

    def _on_switch_phone(self):
        self._is_active = False
        self._recog_timer.stop()
        self.switch_to_phone.emit()

