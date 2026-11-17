"""
FaceBox — Điểm khởi đầu ứng dụng Windows
Hệ thống tủ thông minh nhận diện khuôn mặt 24/7.
Hỗ trợ cả chế độ chạy mã nguồn Python và chế độ đóng gói FaceBox.exe độc lập.
"""

import sys
import os
import logging
import traceback
from datetime import datetime

# Thêm thư mục gốc vào Python path khi chạy dev
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PySide6.QtCore import Qt, QTimer, QSharedMemory
from PySide6.QtGui import QFont, QPixmap, QColor, QIcon, QPainter, QBrush, QPen

from services.path_service import get_resource_path, get_log_dir, is_frozen


def setup_logging():
    """Cài đặt logging ghi vào file và console."""
    log_dir = get_log_dir()
    log_file = log_dir / f"facebox_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(str(log_file), encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("facebox")


def create_splash_screen() -> QSplashScreen:
    """Tạo màn hình splash phong cách Industrial Smart Locker (Vàng / Đen)."""
    pixmap = QPixmap(520, 320)
    pixmap.fill(QColor("#171717"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)

    # Viền vàng công nghiệp
    painter.setPen(QPen(QColor("#FFD500"), 3))
    painter.drawRect(2, 2, 516, 316)

    # Thân logo icon mini
    icon_path = get_resource_path(os.path.join("assets", "FaceBox.png"))
    if icon_path.exists():
        logo_pix = QPixmap(str(icon_path)).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(220, 50, logo_pix)

    # Chữ FaceBox
    painter.setFont(QFont("Segoe UI", 26, QFont.Bold))
    painter.setPen(QColor("#FFFFFF"))
    painter.drawText(0, 175, 520, 40, Qt.AlignCenter, "FaceBox")

    # Nhãn Smart Locker
    painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
    painter.setPen(QColor("#FFD500"))
    painter.drawText(0, 215, 520, 30, Qt.AlignCenter, "INDUSTRIAL SMART LOCKER")

    # Dòng khởi động
    painter.setFont(QFont("Segoe UI", 10))
    painter.setPen(QColor("#A0A0A0"))
    painter.drawText(0, 265, 520, 25, Qt.AlignCenter, "Đang khởi tạo hệ thống và tải mô hình AI...")

    painter.end()

    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    return splash


def setup_exception_hook(logger):
    """Bắt các exception chưa được xử lý để ghi log và hiển thị thông báo lỗi."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.critical(f"Ngoại lệ chưa được xử lý (Fatal Unhandled Exception):\n{err_msg}")
        try:
            QMessageBox.critical(
                None,
                "FaceBox — Lỗi Hệ Thống",
                f"Đã xảy ra lỗi nghiêm trọng:\n{exc_value}\n\n"
                f"Vui lòng xem chi tiết trong file log tại:\n{get_log_dir()}"
            )
        except Exception:
            pass

    sys.excepthook = handle_exception


def main():
    """Điểm khởi động chính của ứng dụng FaceBox."""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info(f"FaceBox v1.3.1 — Khởi chạy (Frozen={is_frozen()})")
    logger.info(f"Python: {sys.version}")
    logger.info(f"App dir: {_BASE_DIR}")
    logger.info("=" * 60)

    # Đặt biến môi trường cho Qt
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    # Đăng ký AppUserModelID riêng biệt trên Windows để hiển thị đúng Icon trên Taskbar
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FaceBox.IndustrialSmartLocker.1.3.1")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("FaceBox")
    app.setApplicationDisplayName("FaceBox — Industrial Smart Locker")
    app.setApplicationVersion("1.3.1")
    app.setOrganizationName("FaceBox")

    setup_exception_hook(logger)

    # 1. Cơ chế Single-Instance Mutex (Ngăn chạy nhiều bản cùng lúc)
    shared_mem = QSharedMemory("FaceBox_SingleInstance_Mutex_Memory")
    if not shared_mem.create(1):
        # Đã có một tiến trình FaceBox đang chạy
        logger.warning("Đã phát hiện một tiến trình FaceBox đang hoạt động. Ngăn chặn mở cửa sổ trùng lặp.")
        QMessageBox.information(
            None,
            "FaceBox",
            "Ứng dụng FaceBox hiện đang chạy trên máy tính của bạn.\n"
            "Vui lòng kiểm tra cửa sổ FaceBox trên thanh tác vụ (Taskbar)."
        )
        sys.exit(0)

    # 2. Đặt Icon ứng dụng Windows
    icon_ico = get_resource_path(os.path.join("assets", "FaceBox.ico"))
    icon_png = get_resource_path(os.path.join("assets", "FaceBox.png"))
    if icon_ico.exists():
        app.setWindowIcon(QIcon(str(icon_ico)))
    elif icon_png.exists():
        app.setWindowIcon(QIcon(str(icon_png)))

    # 3. Font mặc định toàn hệ thống
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # 4. Hiển thị màn hình Splash
    splash = create_splash_screen()
    splash.show()
    app.processEvents()

    # 5. Khởi tạo AppController (Giao diện Kiosk mặc định)
    from ui.app_controller import AppController
    window = AppController()

    # Đóng splash sau 1.2s và hiện cửa sổ chính
    QTimer.singleShot(1200, lambda: (splash.close(), window.show()))

    logger.info("Giao diện Kiosk đã sẵn sàng hoạt động")

    exit_code = app.exec()
    logger.info(f"FaceBox đã đóng (Mã thoát: {exit_code})")

    # Giải phóng vùng nhớ chia sẻ
    shared_mem.detach()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
