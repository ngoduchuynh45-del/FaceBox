"""
FaceBox - Trang Đăng Ký Khuôn Mặt (Phiên bản T014)
Quét khuôn mặt trực tiếp với khung camera hình elip và tự động thu thập mẫu.
Đã loại bỏ quy trình 5 bước tư thế để người dùng đăng ký nhanh chóng, tự nhiên.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QLineEdit,
                                QFrame, QProgressBar)
from PySide6.QtCore import Qt, Signal
import numpy as np
import cv2
import logging
import time

logger = logging.getLogger("facebox.ui.registration")

from ui.widgets import (EllipseCameraView, SectionTitle,
                         FACE_STATE_NONE, FACE_STATE_TOO_FAR, FACE_STATE_TOO_CLOSE,
                         FACE_STATE_OFFCENTER, FACE_STATE_READY)
from services.account_service import validate_phone, get_or_create_account
from database import db_manager

# Số lượng mẫu khuôn mặt cần thu thập để lấy vector đặc trưng trung bình
_TARGET_SAMPLES = 10


class RegistrationPage(QWidget):
    """Trang đăng ký khuôn mặt với khung elip trực quan (T014)."""

    request_embedding = Signal()
    camera_toggle = Signal()

    def __init__(self, face_service, camera_service, parent=None):
        super().__init__(parent)
        self.face_service = face_service
        self.camera_service = camera_service

        self._current_account_id = None
        self._captured_embeddings = []       # Danh sách các embedding mẫu
        self._is_capturing = False           # Trạng thái đang quét
        self._frame_counter = 0              # Đếm frame để giãn cách lấy mẫu
        self._capture_interval_frames = 3    # Cách 3 frame lấy 1 mẫu (~100ms)
        self._last_diag_time = 0.0           # Tiết lưu log chẩn đoán

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ---- Cột trái: Camera hiển thị trực tiếp với khung elip ----
        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)

        cam_title = SectionTitle("Hình ảnh trực tiếp")
        left_panel.addWidget(cam_title)

        # Widget camera hình elip (kích thước 58% x 70% tối ưu)
        self.camera_view = EllipseCameraView()
        left_panel.addWidget(self.camera_view)

        layout.addLayout(left_panel, 3)

        # ---- Cột phải: Form thao tác ----
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)

        # Tiêu đề
        title = QLabel("Đăng Ký Khuôn Mặt")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e2e8f0;")
        right_panel.addWidget(title)

        sub = QLabel("Nhập số điện thoại để tạo hoặc chọn tài khoản")
        sub.setStyleSheet("color: #64748b; font-size: 12px; margin-bottom: 8px;")
        right_panel.addWidget(sub)

        # --- Bước 1: Tài khoản ---
        step1_frame = QFrame()
        step1_frame.setObjectName("card")
        step1_layout = QVBoxLayout(step1_frame)
        step1_layout.setSpacing(8)

        s1_title = QLabel("Bước 1: Tài khoản")
        s1_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #94a3b8;")
        step1_layout.addWidget(s1_title)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("VD: 0912345678 hoặc +84912345678")
        self.phone_input.setMaxLength(15)
        self.phone_input.returnPressed.connect(self._on_confirm_phone)
        step1_layout.addWidget(self.phone_input)

        btn_row = QHBoxLayout()
        self.btn_confirm_phone = QPushButton("Xác nhận số điện thoại")
        self.btn_confirm_phone.setObjectName("btn_primary")
        self.btn_confirm_phone.clicked.connect(self._on_confirm_phone)

        self.btn_reset = QPushButton("Đặt lại")
        self.btn_reset.setObjectName("btn_secondary")
        self.btn_reset.clicked.connect(self._reset_form)
        self.btn_reset.setEnabled(False)

        btn_row.addWidget(self.btn_confirm_phone)
        btn_row.addWidget(self.btn_reset)
        step1_layout.addLayout(btn_row)

        self.account_status_label = QLabel("")
        self.account_status_label.setWordWrap(True)
        self.account_status_label.setVisible(False)
        step1_layout.addWidget(self.account_status_label)

        right_panel.addWidget(step1_frame)

        # --- Bước 2: Quét khuôn mặt ---
        self.step2_frame = QFrame()
        self.step2_frame.setObjectName("card")
        self.step2_frame.setEnabled(False)
        step2_layout = QVBoxLayout(self.step2_frame)
        step2_layout.setSpacing(8)

        s2_title = QLabel("Bước 2: Quét khuôn mặt")
        s2_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #94a3b8;")
        step2_layout.addWidget(s2_title)

        # Nhãn tùy chọn
        label_row = QHBoxLayout()
        label_row.addWidget(QLabel("Nhãn (tùy chọn):"))
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("VD: Chủ tài khoản, Mẫu chính...")
        label_row.addWidget(self.label_input)
        step2_layout.addLayout(label_row)

        # Thanh tiến trình quét
        self.progress_label = QLabel("Chưa bắt đầu quét")
        self.progress_label.setStyleSheet("color: #64748b; font-size: 12px;")
        step2_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, _TARGET_SAMPLES)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        step2_layout.addWidget(self.progress_bar)

        # Nút hành động
        btn_row2 = QHBoxLayout()
        self.btn_start_scan = QPushButton("▶  Bắt đầu quét")
        self.btn_start_scan.setObjectName("btn_primary")
        self.btn_start_scan.clicked.connect(self._start_capture)

        self.btn_save = QPushButton("💾  Lưu khuôn mặt")
        self.btn_save.setObjectName("btn_success")
        self.btn_save.clicked.connect(self._save_face)
        self.btn_save.setEnabled(False)

        btn_row2.addWidget(self.btn_start_scan)
        btn_row2.addWidget(self.btn_save)
        step2_layout.addLayout(btn_row2)

        # Thông báo trạng thái quét
        self.scan_status_label = QLabel("")
        self.scan_status_label.setWordWrap(True)
        self.scan_status_label.setVisible(False)
        step2_layout.addWidget(self.scan_status_label)

        right_panel.addWidget(self.step2_frame)
        right_panel.addStretch()

        layout.addLayout(right_panel, 2)

    def _show_status(self, label: QLabel, message: str, status_type: str = "info"):
        """Hiển thị thông báo trạng thái với màu sắc tương ứng."""
        colors = {
            "success": ("color: #34d399; background: #064e3b;", "✅ "),
            "error":   ("color: #f87171; background: #7f1d1d;", "❌ "),
            "warning": ("color: #fbbf24; background: #451a03;", "⚠️ "),
            "info":    ("color: #94a3b8; background: #1e2635;", "ℹ️ "),
        }
        style, icon = colors.get(status_type, colors["info"])
        label.setStyleSheet(f"QLabel {{ {style} border-radius: 6px; padding: 8px 12px; }}")
        label.setText(icon + message)
        label.setVisible(True)

    def _on_confirm_phone(self):
        """Xác nhận số điện thoại hợp lệ."""
        phone = self.phone_input.text().strip()

        if not self.camera_service.is_running():
            self._show_status(self.account_status_label,
                "Vui lòng mở camera trước (Trang Tổng Quan → Mở Camera)", "warning")
            return

        if not self.face_service.is_ready():
            self._show_status(self.account_status_label,
                f"Mô hình nhận diện chưa sẵn sàng:\n{self.face_service.get_load_error()}", "error")
            return

        success, msg, account_id, is_new = get_or_create_account(phone)

        if success:
            self._current_account_id = account_id
            profiles = db_manager.get_face_profiles_by_account(account_id)
            existing_count = len(profiles)
            if not is_new and existing_count > 0:
                msg = f"Tài khoản {phone} đã có {existing_count} mẫu. Bạn có thể quét để bổ sung thêm mẫu."
                if not self.label_input.text():
                    self.label_input.setText(f"Mẫu {existing_count + 1}")
            status_type = "success" if is_new else "info"
            self._show_status(self.account_status_label, msg, status_type)
            self.step2_frame.setEnabled(True)
            self.btn_confirm_phone.setEnabled(False)
            self.phone_input.setEnabled(False)
            self.btn_reset.setEnabled(True)
        else:
            self._show_status(self.account_status_label, msg, "error")

    def _start_capture(self):
        """Bắt đầu thu thập các mẫu khuôn mặt."""
        if not self.camera_service.is_running():
            self._show_status(self.scan_status_label, "Camera chưa được bật", "error")
            return

        self._captured_embeddings = []
        self._frame_counter = 0
        self._is_capturing = True

        self.progress_bar.setRange(0, _TARGET_SAMPLES)
        self.progress_bar.setValue(0)
        self.btn_start_scan.setEnabled(False)
        self.btn_save.setEnabled(False)

        # Kích hoạt hiệu ứng quét scan-line trên camera
        self.camera_view.set_scanning(True)
        self.progress_label.setText(f"Đang chuẩn bị quét (0/{_TARGET_SAMPLES})...")
        self._show_status(
            self.scan_status_label,
            "Đang quét khuôn mặt... Vui lòng nhìn vào khung elip và giữ yên.",
            "info"
        )

    def _process_capture_frame(self, frame: np.ndarray):
        """Xử lý từng frame khi đang bật chế độ quét."""
        faces = self.face_service.detect_faces(frame)
        if not faces:
            self.camera_view.set_face_state(FACE_STATE_NONE)
            self.camera_view.set_custom_label("Đưa khuôn mặt vào khung elip")
            return

        # Chọn khuôn mặt lớn nhất
        face_row = max(faces, key=lambda f: f[2] * f[3])
        fx, fy, fw, fh = int(face_row[0]), int(face_row[1]), int(face_row[2]), int(face_row[3])
        fh_frame, fw_frame = frame.shape[:2]

        # Tính toán vị trí và diện tích so với elip
        face_cx = (fx + fw / 2) / fw_frame
        face_cy = (fy + fh / 2) / fh_frame
        face_area_frac = (fw * fh) / (fw_frame * fh_frame)

        rx_norm = 0.29   # 0.58 / 2
        ry_norm = 0.35   # 0.70 / 2
        dx = (face_cx - 0.5) / rx_norm
        dy = (face_cy - 0.5) / ry_norm
        in_ellipse = (dx * dx + dy * dy) <= 1.35

        # Tiết lưu log chẩn đoán (~1s/lần)
        now = time.time()
        should_diag_log = (now - self._last_diag_time >= 1.0)

        # Kiểm tra cự ly và căn chỉnh
        if face_area_frac < 0.05:
            self.camera_view.set_face_state(FACE_STATE_TOO_FAR)
            self.camera_view.set_custom_label("Đưa khuôn mặt lại gần hơn")
            if should_diag_log:
                self._last_diag_time = now
                logger.info(f"[Scan] Khuôn mặt quá xa ({face_area_frac:.1%} < 5%)")
            return
        elif face_area_frac > 0.55:
            self.camera_view.set_face_state(FACE_STATE_TOO_CLOSE)
            self.camera_view.set_custom_label("Lùi ra xa một chút")
            if should_diag_log:
                self._last_diag_time = now
                logger.info(f"[Scan] Khuôn mặt quá gần ({face_area_frac:.1%} > 55%)")
            return
        elif not in_ellipse:
            self.camera_view.set_face_state(FACE_STATE_OFFCENTER)
            self.camera_view.set_custom_label("Căn chỉnh khuôn mặt vào giữa khung")
            if should_diag_log:
                self._last_diag_time = now
                logger.info(f"[Scan] Khuôn mặt lệch tâm (dist_sq={dx*dx+dy*dy:.2f} > 1.35)")
            return

        # Kiểm tra chất lượng ánh sáng và độ sắc nét
        ok_qual, qual_msg = self.face_service.check_face_quality(frame, face_row)
        if not ok_qual:
            self.camera_view.set_face_state(FACE_STATE_OFFCENTER)
            self.camera_view.set_custom_label(qual_msg)
            if should_diag_log:
                self._last_diag_time = now
                logger.info(f"[Scan] Chất lượng chưa đạt: {qual_msg}")
            return

        # Mặt đạt chuẩn -> Trích xuất mẫu theo chu kỳ frame
        self.camera_view.set_face_state(FACE_STATE_READY)
        self._frame_counter += 1

        if self._frame_counter % self._capture_interval_frames == 0:
            embedding = self.face_service.get_embedding(frame, face_row)
            if embedding is None:
                embedding, _ = self.face_service.get_embedding_from_frame(frame, face_row)

            if embedding is not None:
                self._captured_embeddings.append(embedding)
                current_count = len(self._captured_embeddings)
                self.progress_bar.setValue(current_count)
                self.progress_label.setText(f"Đang quét: {current_count}/{_TARGET_SAMPLES} mẫu...")
                self.camera_view.set_custom_label(f"Đang ghi nhận ({current_count}/{_TARGET_SAMPLES})... Giữ yên")

                if current_count >= _TARGET_SAMPLES:
                    # Hoàn tất quét đủ 10 mẫu
                    self._is_capturing = False
                    self.camera_view.set_scanning(False)
                    self.camera_view.set_face_state(FACE_STATE_READY)
                    self.camera_view.set_custom_label("Đã quét đủ mẫu ✓ (Sẵn sàng lưu)")

                    self.progress_label.setText(f"Hoàn thành: {_TARGET_SAMPLES}/{_TARGET_SAMPLES} mẫu")
                    self._show_status(
                        self.scan_status_label,
                        f"Đã thu thập đủ {_TARGET_SAMPLES} mẫu khuôn mặt hợp lệ! Nhấn 'Lưu khuôn mặt' để hoàn tất.",
                        "success"
                    )
                    self.btn_save.setEnabled(True)
                    self.btn_start_scan.setEnabled(True)

    def _evaluate_face_position(self, frame: np.ndarray):
        """Căn chỉnh vị trí khuôn mặt khi camera chạy nhưng chưa bấm 'Bắt đầu quét'."""
        if not self.face_service.is_ready():
            return

        faces = self.face_service.detect_faces(frame)
        if not faces:
            self.camera_view.set_face_state(FACE_STATE_NONE)
            self.camera_view.set_custom_label(None)
            return

        face_row = max(faces, key=lambda f: f[2] * f[3])
        fx, fy, fw, fh = int(face_row[0]), int(face_row[1]), int(face_row[2]), int(face_row[3])
        fh_frame, fw_frame = frame.shape[:2]

        face_cx = (fx + fw / 2) / fw_frame
        face_cy = (fy + fh / 2) / fh_frame
        face_area_frac = (fw * fh) / (fw_frame * fh_frame)

        rx_norm = 0.29   # 0.58 / 2
        ry_norm = 0.35   # 0.70 / 2
        dx = (face_cx - 0.5) / rx_norm
        dy = (face_cy - 0.5) / ry_norm
        in_ellipse = (dx * dx + dy * dy) <= 1.35

        if face_area_frac < 0.05:
            self.camera_view.set_face_state(FACE_STATE_TOO_FAR)
            self.camera_view.set_custom_label("Đưa khuôn mặt lại gần hơn")
        elif face_area_frac > 0.55:
            self.camera_view.set_face_state(FACE_STATE_TOO_CLOSE)
            self.camera_view.set_custom_label("Lùi ra xa một chút")
        elif not in_ellipse:
            self.camera_view.set_face_state(FACE_STATE_OFFCENTER)
            self.camera_view.set_custom_label("Căn chỉnh khuôn mặt vào giữa khung")
        else:
            self.camera_view.set_face_state(FACE_STATE_READY)
            self.camera_view.set_custom_label("Đã căn chỉnh khuôn mặt ✓ (Sẵn sàng quét)")

    def update_frame(self, frame: np.ndarray):
        """Cập nhật frame camera liên tục từ CameraService."""
        self.camera_view.display_frame(frame)
        try:
            if self._is_capturing:
                self._process_capture_frame(frame)
            else:
                self._evaluate_face_position(frame)
        except Exception as e:
            logger.error(f"Lỗi xử lý frame đăng ký: {e}", exc_info=True)

    def _save_face(self):
        """Lưu vector embedding trung bình vào cơ sở dữ liệu."""
        if len(self._captured_embeddings) < _TARGET_SAMPLES:
            self._show_status(self.scan_status_label, f"Chưa thu thập đủ {_TARGET_SAMPLES} mẫu", "error")
            return

        if self._current_account_id is None:
            self._show_status(self.scan_status_label, "Chưa chọn tài khoản", "error")
            return

        # Tính embedding trung bình và chuẩn hóa L2
        avg_embedding = np.mean(self._captured_embeddings, axis=0).astype(np.float32)
        norm = np.linalg.norm(avg_embedding)
        if norm > 0:
            avg_embedding = avg_embedding / norm

        label = self.label_input.text().strip() or None

        success, msg, profile_id = db_manager.save_face_profile(
            self._current_account_id, avg_embedding, label
        )

        if success:
            self._show_status(self.scan_status_label, msg, "success")
            self.btn_save.setEnabled(False)
            self._captured_embeddings = []
            self.progress_bar.setValue(0)
            self._reload_embeddings()
        else:
            self._show_status(self.scan_status_label, msg, "error")

    def _reload_embeddings(self):
        """Nạp lại cache embedding trong face service."""
        try:
            all_embeddings = db_manager.get_all_face_embeddings()
            self.face_service.load_known_embeddings(all_embeddings)
        except Exception:
            pass

    def _reset_form(self):
        """Đặt lại toàn bộ form về trạng thái ban đầu."""
        self._current_account_id = None
        self._captured_embeddings = []
        self._is_capturing = False
        self._frame_counter = 0

        self.camera_view.set_scanning(False)
        self.camera_view.set_face_state(FACE_STATE_NONE)
        self.camera_view.set_custom_label(None)

        self.phone_input.setEnabled(True)
        self.phone_input.clear()
        self.label_input.clear()
        self.btn_confirm_phone.setEnabled(True)
        self.btn_reset.setEnabled(False)
        self.step2_frame.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_start_scan.setEnabled(True)
        self.progress_bar.setValue(0)

        self.account_status_label.setVisible(False)
        self.scan_status_label.setVisible(False)
        self.progress_label.setText("Chưa bắt đầu quét")
