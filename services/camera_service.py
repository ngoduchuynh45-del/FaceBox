"""
FaceBox - Camera Service
Quản lý webcam: mở/đóng, đọc frame, phát tín hiệu frame mới.
Chạy trong QThread riêng để không block giao diện.
"""
import cv2
import logging
from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker
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
        logger.info("Camera đang chạy")

        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                logger.warning("Không đọc được frame từ camera")
                continue
            self.frame_ready.emit(frame)
            self.msleep(33)  # ~30 FPS

        self._cap.release()
        self.status_changed.emit(False)
        logger.info("Camera đã dừng")

    def stop(self):
        """Dừng thread camera."""
        self._running = False
        self.wait(3000)

    def is_running(self) -> bool:
        return self._running


class CameraService:
    """
    Service quản lý camera thread.
    Cung cấp interface để start/stop camera và nhận frame.
    """
    def __init__(self):
        self._thread: CameraThread = None
        self._current_frame: np.ndarray = None
        self._frame_callbacks = []

    def start(self, camera_index: int = 0,
              on_frame=None, on_error=None, on_status=None):
        """
        Khởi động camera.
        
        Args:
            camera_index: Index camera (mặc định 0 = webcam laptop)
            on_frame: Callback nhận numpy array frame
            on_error: Callback nhận thông báo lỗi
            on_status: Callback nhận bool trạng thái
        """
        if self._thread and self._thread.is_running():
            return  # Đã chạy rồi

        self._thread = CameraThread(camera_index)
        
        if on_frame:
            self._thread.frame_ready.connect(on_frame)
        if on_error:
            self._thread.error_occurred.connect(on_error)
        if on_status:
            self._thread.status_changed.connect(on_status)
        
        # Lưu frame mới nhất
        self._thread.frame_ready.connect(self._save_frame)
        self._thread.start()

    def stop(self):
        """Dừng camera."""
        if self._thread:
            self._thread.stop()
            self._thread = None
        self._current_frame = None

    def get_current_frame(self) -> np.ndarray:
        """Lấy frame hiện tại (có thể None nếu camera chưa chạy)."""
        return self._current_frame

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_running()

    def _save_frame(self, frame: np.ndarray):
        self._current_frame = frame
