"""
FaceBox - Các widget tái sử dụng
"""
from PySide6.QtWidgets import (QLabel, QFrame, QVBoxLayout, QHBoxLayout,
                                QPushButton, QSizePolicy)
from PySide6.QtCore import Qt, QSize, QTimer, QRectF, QPointF
from PySide6.QtGui import QImage, QPixmap, QFont, QColor, QPainter, QPen, QBrush, QRadialGradient
import numpy as np
import cv2


class StatCard(QFrame):
    """Card hiển thị số liệu thống kê."""
    def __init__(self, number: str, label: str, color: str = "#818cf8", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(4)
        
        self.number_label = QLabel(number)
        self.number_label.setObjectName("stat_number")
        self.number_label.setStyleSheet(f"color: {color}; font-size: 36px; font-weight: bold;")
        self.number_label.setAlignment(Qt.AlignCenter)
        
        self.text_label = QLabel(label)
        self.text_label.setObjectName("stat_label")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        
        layout.addWidget(self.number_label)
        layout.addWidget(self.text_label)
    
    def update_value(self, value: str):
        self.number_label.setText(value)


class CameraView(QLabel):
    """Widget hiển thị hình ảnh từ camera."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("camera_view")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(480, 360)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Hiển thị ảnh placeholder khi camera chưa bật."""
        self.setText("📷\n\nCamera chưa được bật\n\nNhấn nút để mở camera")
        self.setObjectName("camera_placeholder")
        self.setStyleSheet("""
            QLabel {
                background-color: #0a0e17;
                border: 2px dashed #2d3748;
                border-radius: 12px;
                color: #4a5568;
                font-size: 14px;
            }
        """)
    
    def display_frame(self, frame: np.ndarray):
        """Hiển thị frame từ OpenCV (BGR numpy array)."""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            # Scale giữ tỷ lệ
            scaled = pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled)
            self.setText("")
        except Exception:
            pass
    
    def display_frame_with_boxes(self, frame: np.ndarray, results: list):
        """Hiển thị frame kèm khung và nhãn nhận diện."""
        try:
            display_frame = frame.copy()
            
            for r in results:
                bbox = r['bbox']
                x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
                
                identified = r.get('identified', False)
                phone = r.get('phone_number', '')
                score = r.get('score', 0.0)
                sim = r.get('similarity', -1.0)
                
                # Màu khung
                if identified:
                    color = (52, 211, 153)   # xanh lá (#34d399)
                    label_text = f"SDT: {phone}"
                    sub_text = f"Tin cay: {score:.0%} | Cos: {sim:.3f}"
                else:
                    color = (248, 113, 113)   # đỏ (#f87171)
                    label_text = "Chua xac dinh"
                    sub_text = f"Cos: {sim:.3f}" if sim > -1.0 else ""
                
                # Vẽ khung
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
                
                # Nền nhãn
                label_y = max(y1 - 38, 5)
                box_width = 240 if sub_text else 160
                cv2.rectangle(display_frame, (x1, label_y - 5), 
                              (x1 + box_width, label_y + 24), (15, 23, 42), -1)
                
                # Text nhãn
                cv2.putText(display_frame, label_text, (x1 + 4, label_y + 11),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.48, color, 1, cv2.LINE_AA)
                
                if sub_text:
                    cv2.putText(display_frame, sub_text, (x1 + 4, label_y + 24),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.38, (203, 213, 225), 1, cv2.LINE_AA)
            
            self.display_frame(display_frame)
        except Exception as e:
            self.display_frame(frame)
    
    def show_error(self, message: str):
        """Hiển thị thông báo lỗi trong vùng camera."""
        self.setText(f"⚠️\n\n{message}")
        self.setStyleSheet("""
            QLabel {
                background-color: #1a0505;
                border: 2px solid #7f1d1d;
                border-radius: 12px;
                color: #f87171;
                font-size: 13px;
                padding: 20px;
            }
        """)


# ─────────────────────────────────────────────────────────────────────────────
# Trạng thái khuôn mặt trong khung quét
# ─────────────────────────────────────────────────────────────────────────────
FACE_STATE_NONE      = "none"       # Chưa phát hiện khuôn mặt: màu trung tính
FACE_STATE_TOO_FAR   = "too_far"    # Khuôn mặt quá nhỏ / xa: màu đỏ kèm hướng dẫn
FACE_STATE_TOO_CLOSE = "too_close"  # Khuôn mặt quá lớn / gần: màu đỏ kèm hướng dẫn
FACE_STATE_OFFCENTER = "offcenter"  # Khuôn mặt lệch khỏi tâm elip: màu đỏ kèm hướng dẫn
FACE_STATE_READY     = "ready"      # Khuôn mặt đã căn chỉnh đúng: màu xanh lá
FACE_STATE_SUCCESS   = "success"    # Nhận diện thành công: hiệu ứng xanh lá nhẹ


class EllipseCameraView(QLabel):
    """
    Widget camera chuyên dụng với khung elip (Ellipse/Oval) chuẩn hóa:
      - Tỷ lệ elip (width / height) luôn giữ bất biến ở 0.72 trên mọi kích thước màn hình
      - Khung elip luôn nằm chính xác ở tâm vùng camera hiển thị
      - Vẽ bằng hình học Ellipse thực sự (QPainter.drawEllipse)
      - Lớp phủ tối (vignette) làm nổi bật vùng nhận diện mà không che khuất camera
      - Tự động thích ứng mượt mà khi resize cửa sổ
      - Màu viền phản hồi chuẩn xác theo trạng thái nhận diện
    """

    # Hằng số hình học elip
    ELLIPSE_ASPECT_RATIO = 0.72   # Tỷ lệ chiều rộng / chiều cao khuôn mặt người chuẩn
    MAX_HEIGHT_FRAC      = 0.74   # Chiếm tối đa 74% chiều cao vùng camera
    MAX_WIDTH_FRAC       = 0.60   # Chiếm tối đa 60% chiều rộng vùng camera

    # Màu viền elip theo trạng thái (chuyển màu mượt mà)
    _STATE_COLORS = {
        FACE_STATE_NONE:      QColor(148, 163, 184, 210),   # xám trung tính Slate-400
        FACE_STATE_TOO_FAR:   QColor(239, 68, 68, 240),     # đỏ Red-500
        FACE_STATE_TOO_CLOSE: QColor(239, 68, 68, 240),     # đỏ Red-500
        FACE_STATE_OFFCENTER: QColor(239, 68, 68, 240),     # đỏ Red-500
        FACE_STATE_READY:     QColor(34, 197, 94, 240),     # xanh lá Green-500
        FACE_STATE_SUCCESS:   QColor(74, 222, 128, 255),    # xanh lá nhẹ Green-400
    }

    # Nhãn hướng dẫn theo trạng thái
    _STATE_LABELS = {
        FACE_STATE_NONE:      "Đưa khuôn mặt vào khung hình",
        FACE_STATE_TOO_FAR:   "Khuôn mặt quá xa — Hãy lại gần hơn",
        FACE_STATE_TOO_CLOSE: "Khuôn mặt quá gần — Hãy lùi ra xa một chút",
        FACE_STATE_OFFCENTER: "Căn chỉnh khuôn mặt vào giữa khung",
        FACE_STATE_READY:     "Vị trí khuôn mặt hợp lệ ✓",
        FACE_STATE_SUCCESS:   "Nhận diện thành công ✓",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("camera_view")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(480, 360)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Trạng thái hiện tại và trạng thái màu hiển thị (smooth transition)
        self._face_state     = FACE_STATE_NONE
        self._display_state  = FACE_STATE_NONE
        self._state_hold_ms  = 0
        self._last_state_ts  = 0

        # Scan-line animation
        self._scan_y_frac   = 0.0   # 0.0 → 1.0 (vị trí tương đối trong elip)
        self._scan_dir      = 1
        self._scanning      = False  # chỉ chạy khi đang quét

        # Timer animation ~30fps
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(33)
        self._anim_timer.timeout.connect(self._tick_animation)
        self._anim_timer.start()

        # Blend màu (tránh flash giật)
        self._current_r = 148.0
        self._current_g = 163.0
        self._current_b = 184.0
        self._current_a = 210.0

        self._show_state_label = True
        self._custom_label = None
        self._vignette_alpha = 130   # độ tối vừa phải để không che khuất camera
        self._last_frame_bgr = None  # lưu giữ frame cuối để phục vụ resize tức thì

        self._show_placeholder()

    # ── Geometry & Face Evaluation API (Dùng chung cho toàn hệ thống) ──────────

    @classmethod
    def calculate_ellipse_geometry(cls, view_w: float, view_h: float,
                                   pixmap_w: float = None, pixmap_h: float = None) -> QRectF:
        """
        Tính toán tọa độ và kích thước khung elip bảo đảm:
        1. Luôn là hình elip với tỷ lệ el_w / el_h = ELLIPSE_ASPECT_RATIO (0.72).
        2. Tỷ lệ elip bất biến khi thay đổi kích thước cửa sổ (nhỏ, vừa, toàn màn hình).
        3. Luôn nằm chính giữa vùng camera hiển thị.
        4. Không bao giờ tràn khỏi vùng camera hoặc bị méo.
        """
        if pixmap_w and pixmap_h and pixmap_w > 0 and pixmap_h > 0:
            cam_w = float(pixmap_w)
            cam_h = float(pixmap_h)
            cam_x = (view_w - cam_w) / 2.0
            cam_y = (view_h - cam_h) / 2.0
        else:
            cam_w = float(view_w)
            cam_h = float(view_h)
            cam_x = 0.0
            cam_y = 0.0

        cam_cx = cam_x + cam_w / 2.0
        cam_cy = cam_y + cam_h / 2.0

        max_h = cam_h * cls.MAX_HEIGHT_FRAC
        max_w = cam_w * cls.MAX_WIDTH_FRAC

        if max_h * cls.ELLIPSE_ASPECT_RATIO <= max_w:
            el_h = max_h
            el_w = el_h * cls.ELLIPSE_ASPECT_RATIO
        else:
            el_w = max_w
            el_h = el_w / cls.ELLIPSE_ASPECT_RATIO

        el_x = cam_cx - el_w / 2.0
        el_y = cam_cy - el_h / 2.0

        return QRectF(el_x, el_y, el_w, el_h)

    @classmethod
    def get_normalized_radii(cls, frame_w: int, frame_h: int) -> tuple[float, float]:
        """Trả về bán kính chuẩn hóa (rx_norm, ry_norm) của elip trong camera frame (0..1)."""
        geom = cls.calculate_ellipse_geometry(float(frame_w), float(frame_h))
        rx_norm = (geom.width() / 2.0) / float(frame_w)
        ry_norm = (geom.height() / 2.0) / float(frame_h)
        return rx_norm, ry_norm

    @classmethod
    def evaluate_face_geometry(cls, face_data, frame_w: int, frame_h: int) -> tuple[str, str]:
        """
        Đánh giá vị trí khuôn mặt so với khung elip:
        Hỗ trợ cả định dạng [x1, y1, x2, y2] (bbox) và [x, y, w, h, ...] (YuNet face row).
        - Quá xa: diện tích nhỏ (< 4.5% frame) -> màu đỏ
        - Quá gần: diện tích lớn (> 55% frame) -> màu đỏ
        - Lệch tâm: tâm mặt nằm ngoài khung elip -> màu đỏ
        - Hợp lệ: nằm vừa vặn trong khung elip -> màu xanh lá
        """
        if len(face_data) > 4:
            # Định dạng YuNet face_row: [x, y, w, h, ...]
            fx = float(face_data[0])
            fy = float(face_data[1])
            fw = float(face_data[2])
            fh = float(face_data[3])
        else:
            # Định dạng bbox: [x1, y1, x2, y2]
            x1 = float(face_data[0])
            y1 = float(face_data[1])
            x2 = float(face_data[2])
            y2 = float(face_data[3])
            fx = x1
            fy = y1
            fw = max(0.0, x2 - x1)
            fh = max(0.0, y2 - y1)

        face_area_frac = (fw * fh) / float(frame_w * frame_h)
        face_cx = (fx + fw / 2.0) / float(frame_w)
        face_cy = (fy + fh / 2.0) / float(frame_h)

        rx_norm, ry_norm = cls.get_normalized_radii(frame_w, frame_h)
        dx = (face_cx - 0.5) / rx_norm
        dy = (face_cy - 0.5) / ry_norm
        dist_sq = dx * dx + dy * dy

        if face_area_frac < 0.045:
            return FACE_STATE_TOO_FAR, cls._STATE_LABELS[FACE_STATE_TOO_FAR]
        elif face_area_frac > 0.55:
            return FACE_STATE_TOO_CLOSE, cls._STATE_LABELS[FACE_STATE_TOO_CLOSE]
        elif dist_sq > 1.30:
            return FACE_STATE_OFFCENTER, cls._STATE_LABELS[FACE_STATE_OFFCENTER]
        else:
            return FACE_STATE_READY, cls._STATE_LABELS[FACE_STATE_READY]

    # ── Placeholder ──────────────────────────────────────────────────────────

    def _show_placeholder(self):
        self.setText("📷\n\nCamera chưa được bật\n\nNhấn nút để mở camera")
        self.setStyleSheet("""
            QLabel {
                background-color: #0a0e17;
                border: 2px dashed #2d3748;
                border-radius: 12px;
                color: #4a5568;
                font-size: 14px;
            }
        """)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_face_state(self, state: str):
        """Đặt trạng thái khuôn mặt (dùng hằng FACE_STATE_*)."""
        if state != self._face_state:
            self._face_state = state
            self.update()

    def set_custom_label(self, text: str = None):
        """Đặt nhãn chữ tùy biến bên dưới elip (None để dùng nhãn mặc định theo state)."""
        self._custom_label = text
        self.update()

    def set_show_state_label(self, show: bool):
        """Bật/tắt nhãn hướng dẫn phía dưới elip."""
        self._show_state_label = show
        self.update()

    def set_scanning(self, active: bool):
        """Bật/tắt animation đường quét."""
        self._scanning = active

    # ── Animation ────────────────────────────────────────────────────────────

    def _tick_animation(self):
        """Cập nhật animation và smooth-blend màu."""
        target = self._STATE_COLORS.get(self._face_state, self._STATE_COLORS[FACE_STATE_NONE])
        tr, tg, tb, ta = target.red(), target.green(), target.blue(), target.alpha()
        speed = 0.14   # tốc độ blend mượt mà
        self._current_r += (tr - self._current_r) * speed
        self._current_g += (tg - self._current_g) * speed
        self._current_b += (tb - self._current_b) * speed
        self._current_a += (ta - self._current_a) * speed

        # Scan-line
        if self._scanning:
            self._scan_y_frac += 0.018 * self._scan_dir
            if self._scan_y_frac >= 1.0:
                self._scan_y_frac = 1.0
                self._scan_dir = -1
            elif self._scan_y_frac <= 0.0:
                self._scan_y_frac = 0.0
                self._scan_dir = 1

        self.update()  # trigger paintEvent

    # ── Frame display & Resize ────────────────────────────────────────────────

    def resizeEvent(self, event):
        """Xử lý thích ứng tức thì khi resize cửa sổ."""
        super().resizeEvent(event)
        if self._last_frame_bgr is not None:
            self._update_pixmap_from_frame(self._last_frame_bgr)
        self.update()

    def _update_pixmap_from_frame(self, frame: np.ndarray):
        """Scale hình ảnh camera giữ đúng tỷ lệ góc (KeepAspectRatio) không méo hình."""
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            scaled = QPixmap.fromImage(qt_img).scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled)
            self.setText("")
        except Exception:
            pass

    def display_frame(self, frame: np.ndarray):
        """Cập nhật frame camera. Elip overlay được vẽ trong paintEvent."""
        self._last_frame_bgr = frame
        self._update_pixmap_from_frame(frame)

    def display_frame_with_boxes(self, frame: np.ndarray, results: list):
        """
        Hiển thị frame kèm khung và nhãn nhận diện (phục vụ màn hình nhận diện trực tiếp).
        Khung elip và vignette vẫn được vẽ chồng lên trên.
        """
        try:
            display_frame = frame.copy()
            has_identified = False
            has_face = len(results) > 0

            for r in results:
                bbox = r['bbox']
                x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]

                identified = r.get('identified', False)
                phone = r.get('phone_number', '')
                score = r.get('score', 0.0)
                sim = r.get('similarity', -1.0)

                if identified:
                    has_identified = True
                    color = (52, 211, 153)   # xanh lá (#34d399)
                    label_text = f"SDT: {phone}"
                    sub_text = f"Tin cay: {score:.0%} | Cos: {sim:.3f}"
                else:
                    color = (248, 113, 113)   # đỏ (#f87171)
                    label_text = "Chua xac dinh"
                    sub_text = f"Cos: {sim:.3f}" if sim > -1.0 else ""

                # Vẽ khung khuôn mặt
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)

                # Nền nhãn
                label_y = max(y1 - 38, 5)
                box_width = 240 if sub_text else 160
                cv2.rectangle(display_frame, (x1, label_y - 5),
                              (x1 + box_width, label_y + 24), (15, 23, 42), -1)

                # Text nhãn
                cv2.putText(display_frame, label_text, (x1 + 4, label_y + 11),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.48, color, 1, cv2.LINE_AA)

                if sub_text:
                    cv2.putText(display_frame, sub_text, (x1 + 4, label_y + 24),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (203, 213, 225), 1, cv2.LINE_AA)

            # Cập nhật màu viền elip theo kết quả nhận diện
            if has_identified:
                self.set_face_state(FACE_STATE_SUCCESS)
            elif has_face:
                state, _ = self.evaluate_face_geometry(results[0]['bbox'], display_frame.shape[1], display_frame.shape[0])
                self.set_face_state(state)
            else:
                self.set_face_state(FACE_STATE_NONE)

            self.display_frame(display_frame)
        except Exception:
            self.display_frame(frame)

    def show_error(self, message: str):
        self.setText(f"⚠️\n\n{message}")
        self.setStyleSheet("""
            QLabel {
                background-color: #1a0505;
                border: 2px solid #7f1d1d;
                border-radius: 12px;
                color: #f87171;
                font-size: 13px;
                padding: 20px;
            }
        """)

    # ── Painting ──────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        """Vẽ frame camera trước, sau đó vẽ elip overlay bằng QPainter."""
        super().paintEvent(event)   # vẽ QLabel (pixmap / text)

        # Chỉ vẽ overlay khi có pixmap (camera đang chạy)
        pm = self.pixmap()
        if pm is None or pm.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w = float(self.width())
        h = float(self.height())
        pm_w = float(pm.width())
        pm_h = float(pm.height())

        # ── Tính kích thước và vị trí elip chuẩn hóa tỷ lệ ──────────────────
        ellipse_rect = self.calculate_ellipse_geometry(w, h, pm_w, pm_h)
        el_x = ellipse_rect.x()
        el_y = ellipse_rect.y()
        el_w = ellipse_rect.width()
        el_h = ellipse_rect.height()

        # ── Lớp tối bên ngoài elip (vignette) ───────────────────────────────
        painter.save()
        from PySide6.QtGui import QPainterPath
        full_path = QPainterPath()
        full_path.addRect(0, 0, w, h)
        ellipse_path = QPainterPath()
        ellipse_path.addEllipse(ellipse_rect)
        vignette_path = full_path - ellipse_path   # phần ngoài elip

        # Lớp tối nhẹ nhàng làm nổi bật vùng nhận diện mà không che khuất camera
        painter.fillPath(vignette_path, QColor(8, 12, 24, self._vignette_alpha))

        # Hiệu ứng xanh lá nhẹ khi nhận diện thành công
        if self._face_state == FACE_STATE_SUCCESS:
            success_brush = QRadialGradient(ellipse_rect.center(), max(el_w, el_h) * 0.55)
            success_brush.setColorAt(0.0, QColor(34, 197, 94, 38))
            success_brush.setColorAt(0.65, QColor(34, 197, 94, 16))
            success_brush.setColorAt(1.0, QColor(34, 197, 94, 0))
            painter.fillPath(ellipse_path, success_brush)

        painter.restore()

        # ── Viền elip (smooth color transition) ─────────────────────────────
        ellipse_color = QColor(
            int(self._current_r), int(self._current_g),
            int(self._current_b), int(self._current_a)
        )
        is_ready = (self._face_state == FACE_STATE_READY)
        is_success = (self._face_state == FACE_STATE_SUCCESS)

        # Viền ngoài mảnh (glow)
        glow_pen = QPen(QColor(
            int(self._current_r), int(self._current_g),
            int(self._current_b), 70 if is_success else 45
        ))
        glow_pen.setWidth(8 if is_success else 5)
        painter.setPen(glow_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(ellipse_rect.adjusted(-2, -2, 2, 2))

        # Viền chính
        main_pen = QPen(ellipse_color)
        main_pen.setWidth(3 if (is_ready or is_success) else 2)
        painter.setPen(main_pen)
        painter.drawEllipse(ellipse_rect)

        # ── Scan-line animation ──────────────────────────────────────────────
        if self._scanning:
            cx = ellipse_rect.center().x()
            cy = ellipse_rect.center().y()
            rx, ry = el_w / 2.0, el_h / 2.0
            scan_alpha = int(180 * (0.5 + 0.5 * abs(self._scan_y_frac * 2 - 1)))
            scan_color = QColor(int(self._current_r), int(self._current_g),
                                int(self._current_b), scan_alpha)
            # Vị trí y của scan-line bên trong elip
            rel_y = -1.0 + 2.0 * self._scan_y_frac   # -1 → 1
            scan_y = cy + rel_y * ry
            # Tính nửa chiều rộng elip tại scan_y
            if abs(rel_y) < 1.0:
                half_x = rx * (1.0 - rel_y ** 2) ** 0.5
                x_left  = cx - half_x + 4
                x_right = cx + half_x - 4
                scan_pen = QPen(scan_color)
                scan_pen.setWidth(2)
                painter.setPen(scan_pen)
                painter.drawLine(QPointF(x_left, scan_y), QPointF(x_right, scan_y))

        # ── Nhãn trạng thái phía dưới elip ───────────────────────────────────
        if self._show_state_label:
            label_text = self._custom_label or self._STATE_LABELS.get(self._face_state, "")
            if label_text:
                font = painter.font()
                font.setPointSize(10)
                font.setBold(True)
                painter.setFont(font)

                fm = painter.fontMetrics()
                text_w = fm.horizontalAdvance(label_text)
                text_h = fm.height()
                text_x = ellipse_rect.center().x() - text_w / 2.0
                text_y = el_y + el_h + 12

                # Kẹp trong widget
                text_y = min(text_y, h - text_h - 8)

                # Nền pill
                pad_x, pad_y = 12, 5
                bg_rect = QRectF(text_x - pad_x, text_y - pad_y,
                                 text_w + pad_x * 2, text_h + pad_y * 2)
                bg_color = QColor(8, 12, 24, 190)
                painter.setBrush(QBrush(bg_color))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(bg_rect, 10, 10)

                # Chữ
                text_color = ellipse_color if self._face_state != FACE_STATE_NONE else QColor(148, 163, 184)
                painter.setPen(text_color)
                painter.drawText(QPointF(text_x, text_y + text_h - fm.descent()), label_text)

        painter.end()



class StatusBadge(QLabel):
    """Badge trạng thái nhỏ."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_inactive()

    
    def set_active(self, text="● Đang hoạt động"):
        self.setText(text)
        self.setObjectName("badge_active")
        self.setStyleSheet("""
            QLabel {
                background-color: #064e3b;
                color: #34d399;
                border: 1px solid #16A36A;
                border-radius: 2px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
    
    def set_inactive(self, text="○ Chưa hoạt động"):
        self.setText(text)
        self.setObjectName("badge_inactive")
        self.setStyleSheet("""
            QLabel {
                background-color: #1a0a0a;
                color: #f87171;
                border: 1px solid #D94848;
                border-radius: 2px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }
        """)


class SectionTitle(QLabel):
    """Tiêu đề phần."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #94a3b8;
                padding: 8px 0;
                border-bottom: 1px solid #1e2635;
                margin-bottom: 8px;
            }
        """)
