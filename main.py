"""
FaceBox - Điểm khởi đầu ứng dụng
Nhận diện khuôn mặt qua webcam laptop.

Cách chạy:
    python main.py

Yêu cầu:
    pip install PySide6 opencv-python numpy scikit-learn

Tác giả: FaceBox Team
Phiên bản: 1.0 (Prototype)
"""

import sys
import os
import logging
from datetime import datetime

# Thêm thư mục gốc vào Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QSplashScreen, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QColor


def setup_logging():
    """Cài đặt logging - ghi vào file và console."""
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"facebox_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def create_splash_screen(app: QApplication) -> QSplashScreen:
    """Tạo màn hình splash đơn giản."""
    pixmap = QPixmap(500, 300)
    pixmap.fill(QColor("#0f1117"))
    
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.showMessage(
        "FaceBox\nĐang khởi động...",
        Qt.AlignCenter | Qt.AlignBottom,
        QColor("#6366f1")
    )
    
    return splash


def main():
    """Hàm khởi động chính."""
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("FaceBox v1.0 - Đang khởi động")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Thư mục: {os.path.dirname(__file__)}")
    logger.info("=" * 50)
    
    # Đặt biến môi trường cho Qt
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    
    app = QApplication(sys.argv)
    app.setApplicationName("FaceBox")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("FaceBox")
    
    # Font mặc định
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Splash screen
    splash = create_splash_screen(app)
    splash.show()
    app.processEvents()
    
    # Import MainWindow sau splash để tránh delay
    from ui.main_window import MainWindow
    
    # Tạo cửa sổ chính
    window = MainWindow()
    
    # Đóng splash và hiện cửa sổ chính
    QTimer.singleShot(1500, lambda: (splash.close(), window.show()))
    
    logger.info("Giao diện đã sẵn sàng")
    
    # Chạy event loop
    exit_code = app.exec()
    
    logger.info(f"FaceBox đã đóng (exit code: {exit_code})")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
