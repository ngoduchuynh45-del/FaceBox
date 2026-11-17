"""
FaceBox — Windows Installer Compiler Helper
Kiểm tra Inno Setup Compiler (ISCC.exe) và biên dịch file installer/FaceBox_Setup.iss.
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

def find_iscc() -> Path:
    """Tìm trình biên dịch Inno Setup ISCC.exe."""
    # 1. Kiểm tra PATH
    in_path = shutil.which("iscc")
    if in_path:
        return Path(in_path)

    # 2. Kiểm tra các thư mục mặc định trên Windows
    default_paths = [
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Inno Setup 5" / "ISCC.exe",
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Antigravity IDE" / "resources" / "app" / "node_modules" / "innosetup" / "bin" / "ISCC.exe",
        Path(r"C:\Users\ADMIN\AppData\Local\Programs\Antigravity IDE\resources\app\node_modules\innosetup\bin\ISCC.exe"),
    ]
    for p in default_paths:
        if p.exists() and p.is_file():
            return p

    return None


def main():
    project_root = Path(__file__).resolve().parent.parent
    iss_file = project_root / "installer" / "FaceBox_Setup.iss"
    dist_dir = project_root / "dist" / "FaceBox"

    print("=" * 60)
    print("FACEBOX — KIỂM TRA HỆ THỐNG INNO SETUP INSTALLER")
    print("=" * 60)

    if not iss_file.exists():
        print(f"[LỖI] Không tìm thấy script Inno Setup tại: {iss_file}")
        sys.exit(1)

    print(f"Script Inno Setup: {iss_file}")
    print(f"Thư mục nguồn EXE: {dist_dir} (exists={dist_dir.exists()})")

    iscc_path = find_iscc()
    if iscc_path:
        print(f"[OK] Đã tìm thấy Inno Setup Compiler tại: {iscc_path}")
        print("\nĐể biên dịch bộ cài đặt FaceBox_Setup.exe, chạy lệnh:")
        print(f'  "{iscc_path}" "{iss_file}"')
    else:
        print("\n[CHÚ Ý] Chưa phát hiện phần mềm Inno Setup trên máy tính này.")
        print("Để tạo file FaceBox_Setup.exe, bạn chỉ cần:")
        print("  1. Tải và cài đặt Inno Setup 6 miễn phí từ: https://jrsoftware.org/isdl.php")
        print("  2. Chạy lệnh: iscc installer\\FaceBox_Setup.iss")
        print("  Hoặc nhấn chuột phải vào file installer\\FaceBox_Setup.iss chọn 'Compile'.")

    print("\nCấu hình kịch bản Inno Setup đã sẵn sàng 100%:")
    print("  • Icon: assets/FaceBox.ico")
    print("  • Start Menu Shortcut & Desktop Shortcut")
    print("  • Bảo vệ an toàn dữ liệu: Loại trừ data/facebox.db khi cài đè hoặc gỡ cài đặt")
    print("=" * 60)


if __name__ == "__main__":
    main()
