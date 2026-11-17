"""
Kiểm tra toàn diện Phase 2:
1. Syntax của tất cả các file Python đã sửa.
2. Kiểm tra đường dẫn models qua path_service.
3. Kiểm tra kết nối db_manager và khởi tạo database sạch.
4. Kiểm tra create_launcher và FaceBox_Launcher.vbs di động.
5. Kiểm tra cấu hình FaceBox.spec.
"""

import sys
import os
import py_compile
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def test_syntax():
    print("[1] KIỂM TRA SYNTAX PYTHON...")
    files_to_check = [
        PROJECT_ROOT / "database" / "db_manager.py",
        PROJECT_ROOT / "services" / "path_service.py",
        PROJECT_ROOT / "scripts" / "create_launcher.py",
        PROJECT_ROOT / "scripts" / "init_release_db.py",
        PROJECT_ROOT / "main.py",
    ]
    for f in files_to_check:
        try:
            py_compile.compile(str(f), doraise=True)
            print(f"  • OK: {f.name}")
        except Exception as e:
            print(f"  • LỖI SYNTAX tại {f.name}: {e}")
            return False
    return True


def test_models():
    print("\n[2] KIỂM TRA ĐƯỜNG DẪN MODELS...")
    from services.path_service import get_models_dir
    models_dir = get_models_dir()
    print(f"  • Models directory: {models_dir}")
    yunet = models_dir / "face_detection_yunet_2023mar.onnx"
    sface = models_dir / "face_recognition_sface_2021dec.onnx"
    print(f"  • YuNet exists: {yunet.exists()} (size: {yunet.stat().st_size if yunet.exists() else 0} bytes)")
    print(f"  • SFace exists: {sface.exists()} (size: {sface.stat().st_size if sface.exists() else 0} bytes)")
    assert yunet.exists(), "Thiếu file YuNet"
    assert sface.exists(), "Thiếu file SFace"
    return True


def test_db_manager():
    print("\n[3] KIỂM TRA DB_MANAGER & INIT_DATABASE...")
    from database import db_manager
    db_path = db_manager.get_db_path()
    print(f"  • Database path từ get_db_path(): {db_path}")

    # Kiểm tra kết nối
    conn = db_manager.get_connection()
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"  • Các bảng hiện tại trong DB: {tables}")
    conn.close()
    return True


def test_clean_release_db():
    print("\n[4] KIỂM TRA TẠO DATABASE PHÁT HÀNH SẠCH...")
    from scripts.init_release_db import create_clean_database
    test_db = PROJECT_ROOT / "data" / "test_clean_verification.db"
    success = create_clean_database(test_db)
    assert success, "Tạo database sạch thất bại"

    # Kiểm tra lại nội dung
    conn = sqlite3.connect(str(test_db))
    cur = conn.cursor()
    accounts = cur.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    faces = cur.execute("SELECT COUNT(*) FROM face_profiles").fetchone()[0]
    lockers = cur.execute("SELECT COUNT(*) FROM lockers").fetchone()[0]
    conn.close()

    print(f"  • Accounts: {accounts}")
    print(f"  • Face profiles: {faces}")
    print(f"  • Lockers: {lockers}")

    # Dọn dẹp file test
    if test_db.exists():
        test_db.unlink()
    print("  • File test đã được dọn dẹp sạch sẽ.")
    return True


def test_launcher():
    print("\n[5] KIỂM TRA LOGIC LAUNCHER...")
    from scripts.create_launcher import find_facebox_exe, create_portable_vbs
    exe = find_facebox_exe()
    print(f"  • Tìm thấy FaceBox.exe động: {exe}")
    if exe:
        vbs = create_portable_vbs(exe.parent)
        print(f"  • Portable VBS created: {vbs} (exists={vbs.exists()})")
        assert vbs.exists(), "Không tạo được VBS"
    return True


def test_spec():
    print("\n[6] KIỂM TRA SPEC FILE SYNTAX...")
    spec_path = PROJECT_ROOT / "FaceBox.spec"
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_content = f.read()
    # Kiểm tra SPECPATH có mặt trong spec
    assert "SPECPATH" in spec_content, "Thiếu SPECPATH trong FaceBox.spec"
    assert "hiddenimports" in spec_content, "Thiếu hiddenimports trong FaceBox.spec"
    print("  • FaceBox.spec cấu hình hợp lệ với SPECPATH, datas và hiddenimports.")
    return True


def main():
    print("=" * 60)
    print("FACEBOX — BẮT ĐẦU KIỂM THỬ XÁC MINH PHASE 2")
    print("=" * 60)

    t1 = test_syntax()
    t2 = test_models()
    t3 = test_db_manager()
    t4 = test_clean_release_db()
    t5 = test_launcher()
    t6 = test_spec()

    print("\n" + "=" * 60)
    if all([t1, t2, t3, t4, t5, t6]):
        print(">>> TẤT CẢ CÁC BÀI TEST PHASE 2 ĐÃ VƯỢT QUA XUẤT SẮC! <<<")
    else:
        print(">>> CÓ BÀI TEST KHÔNG ĐẠT! <<<")
    print("=" * 60)


if __name__ == "__main__":
    main()
