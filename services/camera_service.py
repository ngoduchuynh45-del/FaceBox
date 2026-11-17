"""
FaceBox - Camera Service
Quản lý webcam tập trung: mở/đóng, đọc frame, phát tín hiệu frame mới.
Chạy trong QThread riêng để không block giao diện.
Hỗ trợ cơ chế đa người lắng nghe (multi-listener) và kiểm tra nguồn cấp frame thực tế.
"""
import time
import cv2
import logging
from PySide6.QtCore import QObject, QThread, Signal, QMutex, QMutexLocker
import numpy as np

logger = logging.getLogger(__name__)


class CameraThread(QThread):
    """
    Thread chạy webcam liên tục.
    Phát tín hiệu frame_ready mỗi khi có frame mới.
    """
    frame_ready = Signal(object)       # numpy array BGR
    error_occurred = Signal(str)       # thông báo lỗi
    status_changed = Signal(bool)      # True = đang chạy

    def __init__(self, camera_index: int = 0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self._running = False
        self._cap = None
        self._mutex = QMutex()
        self._last_frame_ts = 0.0

    def run(self):
        """Vòng lặp chính của thread camera."""
        self._cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        
        if not self._cap.isOpened():
            # Thử lại không dùng DSHOW
            self._cap = cv2.VideoCapture(self.camera_index)
        
        if not self._cap.isOpened():
            logger.error(f"Không thể mở camera {self.camera_index}")
            self.error_occurred.emit(
                f"Không thể mở webcam (index {self.camera_index}).\n"
                "Hãy kiểm tra:\n"
                "• Webcam đã kết nối chưa?\n"
                "• Webcam có đang được ứng dụng khác sử dụng không?\n"
                "• Hãy thử tắt các ứng dụng gọi video khác."
            )
            self.status_changed.emit(False)
            return

        # Cài đặt độ phân giải
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self._cap.set(cv2.CAP_PROP_FPS, 30)
        
        self._running = True
        self.status_changed.emit(True)
        logger.info(f"Camera {self.camera_index} đang chạy")

        while self._running:
            ret, frame = self._cap.read()
            if not ret or frame is None:
                logger.warning("Không đọc được frame từ camera")
                self.msleep(100)
                continue

            self._last_frame_ts = time.time()
            self.frame_ready.emit(frame)
            self.msleep(33)  # ~30 FPS

        if self._cap is not None:
            self._cap.release()
            self._cap = None

        self.status_changed.emit(False)
        logger.info("Camera đã dừng và giải phóng an toàn")

    def stop(self):
        """Dừng thread camera."""
        self._running = False
        self.wait(3000)

    def is_running(self) -> bool:
        return self._running

    def has_active_feed(self, timeout_sec: float = 2.0) -> bool:
        """Kiểm tra xem camera có đang thực sự nhận được frame trong khoảng timeout_sec không."""
        return self._running and (time.time() - self._last_frame_ts <= timeout_sec)


class CameraService(QObject):
    """
    Service quản lý camera thread tập trung.
    Cung cấp interface để start/stop camera, phát frame và kiểm tra trạng thái thực tế.
    """
    frame_ready = Signal(object)
    status_changed = Signal(bool)
    error_occurred = Signal(str)

    _instance = None  # Singleton instance

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread: CameraThread = None
        self._current_frame: np.ndarray = None

    @classmethod
    def get_instance(cls):
        """Lấy singleton instance của CameraService để tránh khởi tạo nhiều lần."""
        if cls._instance is None:
            cls._instance = CameraService()
        return cls._instance

    def start(self, camera_index: int = 0,
              on_frame=None, on_error=None, on_status=None):
        """
        Khởi động camera.
        Nếu camera đã chạy, chỉ đăng ký thêm callback (nếu có).
        """
        if on_frame:
            self.frame_ready.connect(on_frame)
        if on_error:
            self.error_occurred.connect(on_error)
        if on_status:
            self.status_changed.connect(on_status)

        if self._thread and self._thread.is_running():
            logger.info("CameraService: Camera đã chạy sẵn, kết nối listener mới")
            if on_status:
                on_status(True)
            return

        self._thread = CameraThread(camera_index)
        self._thread.frame_ready.connect(self._on_thread_frame)
        self._thread.error_occurred.connect(self.error_occurred.emit)
        self._thread.status_changed.connect(self.status_changed.emit)
        self._thread.start()

    def stop(self):
        """Dừng camera an toàn."""
        if self._thread:
            self._thread.stop()
            self._thread = None
        self._current_frame = None

    def get_current_frame(self) -> np.ndarray:
        """Lấy frame hiện tại (có thể None nếu camera chưa chạy)."""
        return self._current_frame

    def is_running(self) -> bool:
        """Kiểm tra camera thread đang chạy."""
        return self._thread is not None and self._thread.is_running()

    def has_active_feed(self) -> bool:
        """Kiểm tra camera đang thực sự đọc được frame trong 2 giây gần nhất."""
        return self._thread is not None and self._thread.has_active_feed()

    def _on_thread_frame(self, frame: np.ndarray):
        self._current_frame = frame
        self.frame_ready.emit(frame)

