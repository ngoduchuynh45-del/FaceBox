"""
FaceBox — Path Service
Quản lý tập trung toàn bộ đường dẫn tài nguyên (models, schema, assets)
và dữ liệu runtime (database, logs), hỗ trợ cả chế độ Development (Source Code)
và chế độ Production (PyInstaller Executable).
"""

import sys
import os
import shutil
from pathlib import Path

# Thư mục gốc dự án khi chạy mã nguồn
_DEV_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def is_frozen() -> bool:
    """Kiểm tra xem ứng dụng có đang chạy dưới dạng bản đóng gói (PyInstaller) hay không."""
    return getattr(sys, "frozen", False)


def get_app_dir() -> Path:
    """
    Trả về thư mục cài đặt / chứa ứng dụng.
    - Khi đóng gói (frozen): Thư mục chứa file FaceBox.exe.
    - Khi dev: Thư mục gốc của project FaceBox.
    """
    if is_frozen():
        return Path(sys.executable).parent
    return _DEV_PROJECT_ROOT


def get_resource_path(relative_path: str) -> Path:
    """
    Tìm đường dẫn tuyệt đối đến tài nguyên đọc (chỉ đọc như models, schema, assets).
    Tìm theo thứ tự ưu tiên:
    1. Thư mục tạm _MEIPASS của PyInstaller (nếu có).
    2. Thư mục cài đặt chứa file FaceBox.exe.
    3. Thư mục gốc dự án mã nguồn.
    """
    rel = Path(relative_path)

    # 1. Thư mục _MEIPASS (PyInstaller bundle)
    if is_frozen():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            cand = Path(meipass) / rel
            if cand.exists():
                return cand.resolve()

        # 2. Cạnh file exe
        exe_cand = get_app_dir() / rel
        if exe_cand.exists():
            return exe_cand.resolve()

    # 3. Thư mục dự án mã nguồn
    dev_cand = _DEV_PROJECT_ROOT / rel
    if dev_cand.exists():
        return dev_cand.resolve()

    # Mặc định trả về đường dẫn tương đối từ app dir
    return (get_app_dir() / rel).resolve()


def get_data_dir() -> Path:
    """
    Trả về thư mục lưu trữ dữ liệu người dùng (có quyền GHI).
    Quy tắc an toàn và bảo toàn dữ liệu:
    1. Nếu có biến môi trường FACEBOX_DATA_DIR: dùng biến đó.
    2. Khi chạy Dev (mã nguồn): dùng thư mục 'data/' ở gốc dự án.
    3. Khi chạy Frozen (bản đóng gói): MẶC ĐỊNH LUÔN DÙNG %LOCALAPPDATA%/FaceBox/data.
       Tuyệt đối không lưu vào thư mục cạnh EXE để tránh tạo database thứ hai và
       bảo vệ dữ liệu không bị xóa/ghi đè khi người dùng nâng cấp hoặc gỡ cài đặt.
    """
    env_dir = os.environ.get("FACEBOX_DATA_DIR")
    if env_dir:
        p = Path(env_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    if not is_frozen():
        p = _DEV_PROJECT_ROOT / "data"
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    # Khi chạy frozen exe: Luôn dùng %LOCALAPPDATA%/FaceBox/data
    local_app_base = os.environ.get("LOCALAPPDATA")
    if local_app_base:
        p = Path(local_app_base) / "FaceBox" / "data"
    else:
        p = Path.home() / "AppData" / "Local" / "FaceBox" / "data"

    p.mkdir(parents=True, exist_ok=True)
    return p.resolve()


def get_db_path() -> str:
    """
    Trả về đường dẫn file SQLite database 'facebox.db'.
    Chỉ trả về đường dẫn đích trong thư mục dữ liệu người dùng (get_data_dir()).
    Không sao chép database mẫu từ thư mục cài đặt; nếu chưa có, init_database()
    sẽ tự động khởi tạo database sạch từ schema.sql tại đúng vị trí này.
    """
    data_dir = get_data_dir()
    target_db = data_dir / "facebox.db"
    return str(target_db.resolve())


def get_log_dir() -> Path:
    """
    Trả về thư mục lưu log file (có quyền GHI).
    Quy tắc:
    1. Nếu có biến môi trường FACEBOX_LOG_DIR: dùng biến đó.
    2. Khi chạy Dev: dùng thư mục 'logs/' ở gốc dự án.
    3. Khi chạy Frozen: MẶC ĐỊNH LUÔN DÙNG %LOCALAPPDATA%/FaceBox/logs.
    """
    env_dir = os.environ.get("FACEBOX_LOG_DIR")
    if env_dir:
        p = Path(env_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    if not is_frozen():
        p = _DEV_PROJECT_ROOT / "logs"
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    # Khi chạy frozen exe: Luôn dùng %LOCALAPPDATA%/FaceBox/logs
    local_app_base = os.environ.get("LOCALAPPDATA")
    if local_app_base:
        p = Path(local_app_base) / "FaceBox" / "logs"
    else:
        p = Path.home() / "AppData" / "Local" / "FaceBox" / "logs"

    p.mkdir(parents=True, exist_ok=True)
    return p.resolve()


def get_models_dir() -> Path:
    """Trả về thư mục chứa model ONNX (YuNet, SFace)."""
    return get_resource_path("models")

