"""
FaceBox — Portable Launcher Generator
Tạo file launcher di động (FaceBox_Launcher.vbs) hoặc Shortcut Desktop
hoàn toàn dựa trên đường dẫn tương đối, không hardcode ổ đĩa hay tên người dùng.
"""

import sys
import os
from pathlib import Path

def find_facebox_exe() -> Path:
    """Tìm file FaceBox.exe dựa trên vị trí tương đối của script."""
    current_dir = Path(__file__).resolve().parent
    candidates = [
        current_dir / "FaceBox.exe",                       # Nằm cùng thư mục với script
        current_dir.parent / "FaceBox.exe",                # Nằm ở thư mục cha
        current_dir.parent / "dist" / "FaceBox" / "FaceBox.exe",  # Cấu trúc build chuẩn của project
        Path.cwd() / "dist" / "FaceBox" / "FaceBox.exe",   # Cwd dist
        Path.cwd() / "FaceBox.exe",                        # Cwd
    ]
    for cand in candidates:
        if cand.exists() and cand.is_file():
            return cand.resolve()
    return None


def create_portable_vbs(target_dir: Path) -> Path:
    """
    Tạo launcher VBS di động ngay trong thư mục chứa FaceBox.exe.
    Launcher này sử dụng WScript.ScriptFullName để xác định thư mục hiện tại khi chạy,
    cho phép người dùng di chuyển toàn bộ thư mục sang bất kỳ ổ đĩa nào mà không bị lỗi.
    """
    vbs_path = target_dir / "FaceBox_Launcher.vbs"
    vbs_content = (
        "' FaceBox Portable Launcher\r\n"
        "Option Explicit\r\n"
        "Dim fso, shell, appDir, exePath\r\n"
        'Set fso = CreateObject("Scripting.FileSystemObject")\r\n'
        'Set shell = CreateObject("Shell.Application")\r\n'
        "\r\n"
        "appDir = fso.GetParentFolderName(WScript.ScriptFullName)\r\n"
        'exePath = fso.BuildPath(appDir, "FaceBox.exe")\r\n'
        "\r\n"
        "If Not fso.FileExists(exePath) Then\r\n"
        '    MsgBox "Khong tim thay file FaceBox.exe tai:" & vbCrLf & exePath & vbCrLf & vbCrLf & _\r\n'
        '           "Vui long kiem tra file launcher nam cung thu muc voi FaceBox.exe.", 16, "FaceBox - Loi Khoi Dong"\r\n'
        "Else\r\n"
        '    shell.ShellExecute exePath, "", appDir, "open", 1\r\n'
        "End If\r\n"
        "\r\n"
        "Set fso = Nothing\r\n"
        "Set shell = Nothing\r\n"
    )
    with open(vbs_path, "wb") as f:
        f.write(vbs_content.encode("ascii"))
    return vbs_path


def create_desktop_shortcut(exe_path: Path):
    """Tạo shortcut hoặc launcher trên Desktop trỏ đến exe_path đã xác định."""
    desktop_candidates = [
        Path(os.environ.get("USERPROFILE", "")) / "Desktop",
        Path(os.environ.get("USERPROFILE", "")) / "OneDrive" / "Desktop",
    ]
    
    vbs_content = (
        "' FaceBox Desktop Shortcut Launcher\r\n"
        "Option Explicit\r\n"
        "Dim shell, exePath, workDir\r\n"
        'Set shell = CreateObject("Shell.Application")\r\n'
        f'exePath = "{str(exe_path)}"\r\n'
        f'workDir = "{str(exe_path.parent)}"\r\n'
        "\r\n"
        'shell.ShellExecute exePath, "", workDir, "open", 1\r\n'
        "Set shell = Nothing\r\n"
    )

    created = 0
    for desk in desktop_candidates:
        if desk.exists() and desk.is_dir():
            target_file = desk / "FaceBox.vbs"
            try:
                with open(target_file, "wb") as f:
                    f.write(vbs_content.encode("utf-8"))
                created += 1
                print(f"[OK] Đã cập nhật Desktop Launcher tại: {target_file}")
            except Exception as e:
                print(f"[WARN] Không thể ghi tại {desk}: {e}")
    return created


def main():
    print("=" * 60)
    print("FaceBox — Cấu hình Portable Launcher & Desktop Shortcut")
    print("=" * 60)

    exe_path = find_facebox_exe()
    if not exe_path:
        print("[LỖI] Không tìm thấy FaceBox.exe tại các vị trí mặc định.")
        print("Vui lòng đảm bảo ứng dụng đã được đóng gói qua PyInstaller:")
        print("  pyinstaller FaceBox.spec")
        sys.exit(1)

    print(f"[1] Tìm thấy FaceBox.exe tại: {exe_path}")

    # Tạo portable launcher trong cùng thư mục với exe
    app_dir = exe_path.parent
    portable_vbs = create_portable_vbs(app_dir)
    print(f"[2] Đã tạo Portable Launcher tại: {portable_vbs}")

    # Tạo launcher trên Desktop người dùng
    create_desktop_shortcut(exe_path)
    print("[3] Hoàn tất cấu hình launcher di động.")
    print("Người dùng có thể khởi chạy ứng dụng bằng cách:")
    print("  - Nhấn đúp trực tiếp vào FaceBox.exe")
    print("  - Hoặc nhấn đúp vào FaceBox_Launcher.vbs trong thư mục cài đặt")


if __name__ == "__main__":
    main()
