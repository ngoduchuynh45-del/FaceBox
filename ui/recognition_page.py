"""
FaceBox - Trang Nhận Diện Trực Tiếp
Hiển thị camera và nhận diện khuôn mặt real-time.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QFrame,
                                QDoubleSpinBox, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import numpy as np

from ui.widgets import EllipseCameraView, SectionTitle, StatusBadge
from services.face_recognition_service import RecognitionConfirmer


class RecognitionPage(QWidget):
    """Trang nhận diện khuôn mặt real-time."""
    
    def __init__(self, face_service, camera_service, parent=None):
        super().__init__(parent)
        self.face_service = face_service
        self.camera_service = camera_service
        self._confirmer = RecognitionConfirmer(required_frames=4)
        self._recognition_active = True
        self._last_results = []
        
        # Timer để nhận diện định kỳ (không nhận diện mỗi frame - nặng CPU)
        self._recognition_timer = QTimer()
        self._recognition_timer.timeout.connect(self._run_recognition)
        self._recognition_timer.setInterval(200)  # 5 FPS nhận diện
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # ---- Camera lớn với khung elip hướng dẫn ----
        left = QVBoxLayout()
        
        cam_title = SectionTitle("Camera Trực Tiếp")
        left.addWidget(cam_title)
        
        self.camera_view = EllipseCameraView()
        left.addWidget(self.camera_view)
        
        layout.addLayout(left, 3)
        
        # ---- Panel phải: Kết quả ----
        right = QVBoxLayout()
        right.setSpacing(12)
        right.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Nhận Diện Trực Tiếp")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e2e8f0;")
        right.addWidget(title)
        
        sub = QLabel("Hệ thống tự động phân tích khuôn mặt qua webcam")
        sub.setStyleSheet("color: #64748b; font-size: 12px;")
        right.addWidget(sub)
        right.addSpacing(8)
        
        # --- Kết quả nhận diện ---
        result_frame = QFrame()
        result_frame.setObjectName("card_highlight")
        result_layout = QVBoxLayout(result_frame)
        
        r_title = QLabel("Kết quả nhận diện")
        r_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #64748b;")
        result_layout.addWidget(r_title)
        
        self.result_main = QLabel("Chờ nhận diện...")
        self.result_main.setWordWrap(True)
        self.result_main.setStyleSheet("font-size: 18px; font-weight: bold; color: #818cf8; padding: 8px 0;")
        result_layout.addWidget(self.result_main)
        
        self.result_sub = QLabel("")
        self.result_sub.setWordWrap(True)
        self.result_sub.setStyleSheet("font-size: 12px; color: #64748b;")
        result_layout.addWidget(self.result_sub)
        
        right.addWidget(result_frame)
        
        # --- Điều khiển ---
        ctrl_frame = QFrame()
        ctrl_frame.setObjectName("card")
        ctrl_layout = QVBoxLayout(ctrl_frame)
        
        c_title = QLabel("Cài đặt")
        c_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #64748b;")
        ctrl_layout.addWidget(c_title)
        
        # Ngưỡng nhận diện (Cosine Similarity)
        thresh_row = QHBoxLayout()
        thresh_row.addWidget(QLabel("Ngưỡng nhận diện:"))
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.20, 0.80)
        self.threshold_spin.setSingleStep(0.01)
        self.threshold_spin.setDecimals(3)
        self.threshold_spin.setValue(0.363)
        self.threshold_spin.setToolTip(
            "Cosine Similarity: Điểm càng cao càng giống nhau (nghiêm ngặt hơn).\n"
            "Chuẩn khuyến nghị OpenCV Model Zoo: >= 0.363\n"
            "Khoảng giá trị tối ưu: 0.363 - 0.450"
        )
        self.threshold_spin.valueChanged.connect(self._update_threshold)
        thresh_row.addWidget(self.threshold_spin)
        ctrl_layout.addLayout(thresh_row)
        
        thresh_hint = QLabel("Cosine Similarity: Càng cao càng giống (chuẩn OpenCV: >= 0.363)")
        thresh_hint.setStyleSheet("color: #4a5568; font-size: 11px;")
        ctrl_layout.addWidget(thresh_hint)
        
        # Nút bật/tắt nhận diện
        self.btn_toggle = QPushButton("⏸  Tạm dừng nhận diện")
        self.btn_toggle.setObjectName("btn_secondary")
        self.btn_toggle.clicked.connect(self._toggle_recognition)
        ctrl_layout.addWidget(self.btn_toggle)
        
        right.addWidget(ctrl_frame)
        
        # --- Trạng thái ---
        status_frame = QFrame()
        status_frame.setObjectName("card")
        status_layout = QVBoxLayout(status_frame)
        
        st_title = QLabel("Trạng thái")
        st_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #64748b;")
        status_layout.addWidget(st_title)
        
        self.camera_status = StatusBadge()
        status_layout.addWidget(self.camera_status)
        
        self.model_status = QLabel("Mô hình: Đang kiểm tra...")
        self.model_status.setStyleSheet("color: #64748b; font-size: 12px;")
        status_layout.addWidget(self.model_status)
        
        self.face_count_label = QLabel("Khuôn mặt trong DB: --")
        self.face_count_label.setStyleSheet("color: #64748b; font-size: 12px;")
        status_layout.addWidget(self.face_count_label)
        
        right.addWidget(status_frame)
        
        # Cảnh báo
        warn = QLabel(
            "⚠️ Prototype: Ảnh hoặc video có thể đánh lừa hệ thống.\n"
            "Không dùng để kiểm soát an ninh thực tế."
        )
        warn.setStyleSheet("color: #4a5568; font-size: 11px; padding: 8px;")
        warn.setWordWrap(True)
        right.addWidget(warn)
        right.addStretch()
        
        layout.addLayout(right, 2)
    
    def showEvent(self, event):
        """Bắt đầu nhận diện khi trang được hiển thị."""
        super().showEvent(event)
        self._recognition_timer.start()
        self._update_status_display()
    
    def hideEvent(self, event):
        """Dừng nhận diện khi trang bị ẩn."""
        super().hideEvent(event)
        self._recognition_timer.stop()
    
    def _run_recognition(self):
        """Chạy nhận diện trên frame hiện tại."""
        if not self._recognition_active:
            return
        
        if not self.camera_service.is_running():
            return
        
        frame = self.camera_service.get_current_frame()
        if frame is None:
            return
        
        if not self.face_service.is_ready():
            return
        
        # Nhận diện
        results = self.face_service.recognize_in_frame(frame)
        self._last_results = results
        
        # Cập nhật display (frame update chính vẫn từ camera_service)
        self._update_result_panel(results)
    
    def update_frame(self, frame):
        """Cập nhật frame với boxes nhận diện."""
        self.camera_view.display_frame_with_boxes(frame, self._last_results)
    
    def _update_result_panel(self, results: list):
        """Cập nhật panel kết quả."""
        if not results:
            self.result_main.setText("Không phát hiện khuôn mặt")
            self.result_main.setStyleSheet("font-size: 18px; color: #4a5568; padding: 8px 0;")
            self.result_sub.setText("Hãy đứng trước camera")
            return
        
        # Tìm kết quả nhận diện được
        identified = [r for r in results if r.get("identified")]
        unknown = [r for r in results if not r.get("identified")]
        
        if identified:
            phones = list(set(r["phone_number"] for r in identified))
            self.result_main.setText("✅ " + " | ".join(phones))
            self.result_main.setStyleSheet("font-size: 16px; font-weight: bold; color: #34d399; padding: 8px 0;")
            score = identified[0].get("score", 0.0)
            sim = identified[0].get("similarity", 0.0)
            thresh = self.threshold_spin.value()
            self.result_sub.setText(f"Độ tin cậy: {score:.0%} | Cosine: {sim:.3f} (ngưỡng: {thresh:.3f}) | Phát hiện {len(results)} khuôn mặt")
        else:
            self.result_main.setText("❓ Chưa xác định được tài khoản")
            self.result_main.setStyleSheet("font-size: 16px; font-weight: bold; color: #f87171; padding: 8px 0;")
            sim = results[0].get("similarity", -1.0) if results else -1.0
            thresh = self.threshold_spin.value()
            if sim > -1.0:
                self.result_sub.setText(
                    f"Phát hiện {len(results)} khuôn mặt nhưng không khớp dữ liệu đã đăng ký.\n"
                    f"Cosine cao nhất: {sim:.3f} (yêu cầu ngưỡng >= {thresh:.3f})"
                )
            else:
                self.result_sub.setText("Không có dữ liệu khuôn mặt trong cơ sở dữ liệu để so khớp.")
    
    def _toggle_recognition(self):
        """Bật/tắt nhận diện."""
        self._recognition_active = not self._recognition_active
        if self._recognition_active:
            self.btn_toggle.setText("⏸  Tạm dừng nhận diện")
            self._recognition_timer.start()
        else:
            self.btn_toggle.setText("▶  Tiếp tục nhận diện")
            self._recognition_timer.stop()
            self.result_main.setText("⏸ Đã tạm dừng")
            self.result_main.setStyleSheet("font-size: 18px; color: #4a5568; padding: 8px 0;")
    
    def _update_threshold(self, value: float):
        """Cập nhật ngưỡng nhận diện."""
        self.face_service.set_threshold(value)
    
    def _update_status_display(self):
        """Cập nhật hiển thị trạng thái."""
        if self.camera_service.is_running():
            self.camera_status.set_active()
        else:
            self.camera_status.set_inactive()
        
        if self.face_service.is_ready():
            self.model_status.setText("Mô hình: ✅ OpenCV YuNet + SFace")
            self.model_status.setStyleSheet("color: #34d399; font-size: 12px;")
        else:
            err = self.face_service.get_load_error() or "Chưa tải"
            self.model_status.setText(f"Mô hình: ❌ {err[:50]}")
            self.model_status.setStyleSheet("color: #f87171; font-size: 12px;")
    
    def update_face_count(self, count: int):
        self.face_count_label.setText(f"Khuôn mặt trong DB: {count}")
    
    def update_camera_status(self, active: bool):
        if active:
            self.camera_status.set_active()
        else:
            self.camera_status.set_inactive()
            self.camera_view.show_error("Camera chưa được bật\nVào Tổng Quan để mở camera")
