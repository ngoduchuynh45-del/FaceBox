"""
Bộ kiểm thử toàn diện vòng đời và luồng lưu trữ Database FaceBox:
- Chạy lần đầu ở chế độ đóng gói (Frozen mode): tạo DB tại %LOCALAPPDATA%\\FaceBox\\data\\facebox.db
- Chạy lần thứ hai: bảo toàn dữ liệu tài khoản và không chèn trùng ngăn tủ
- Kiểm tra biến môi trường FACEBOX_DATA_DIR
- Kiểm tra đường dẫn log runtime
- Kiểm tra không tạo database thứ hai trong thư mục cài đặt
- Kiểm tra bảo toàn database phát triển gốc
"""

import sys
import os
import shutil
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services import path_service
from database import db_manager


def run_tests():
    print("=" * 65)
    print("FACEBOX — KIỂM THỬ TOÀN DIỆN VÒNG ĐỜI VÀ LUỒNG DATABASE")
    print("=" * 65)

    original_frozen = getattr(sys, "frozen", False)
    original_env_data = os.environ.get("FACEBOX_DATA_DIR")
    original_env_log = os.environ.get("FACEBOX_LOG_DIR")

    # Thư mục giả lập LocalAppData cho bài test
    test_sandbox = PROJECT_ROOT / "data" / "sandbox_test_localappdata"
    if test_sandbox.exists():
        shutil.rmtree(test_sandbox)
    test_sandbox.mkdir(parents=True, exist_ok=True)

    fake_localappdata = test_sandbox / "LocalAppData"
    fake_localappdata.mkdir(parents=True, exist_ok=True)
    os.environ["LOCALAPPDATA"] = str(fake_localappdata)

    try:
        # ─────────────────────────────────────────────────────────────────
        # TEST 1: CHẠY LẦN ĐẦU Ở CHẾ ĐỘ ĐÓNG GÓI (FROZEN = TRUE)
        # ─────────────────────────────────────────────────────────────────
        print("\n[TEST 1] Chạy lần đầu ở chế độ đóng gói (Frozen Mode):")
        sys.frozen = True
        os.environ.pop("FACEBOX_DATA_DIR", None)
        os.environ.pop("FACEBOX_LOG_DIR", None)

        data_dir = path_service.get_data_dir()
        log_dir = path_service.get_log_dir()
        db_path = path_service.get_db_path()

        expected_data_dir = fake_localappdata / "FaceBox" / "data"
        expected_log_dir = fake_localappdata / "FaceBox" / "logs"
        expected_db_file = expected_data_dir / "facebox.db"

        print(f"  • Data Dir: {data_dir}")
        print(f"  • Log Dir : {log_dir}")
        print(f"  • DB Path : {db_path}")

        assert data_dir == expected_data_dir.resolve(), f"Data dir sai: {data_dir}"
        assert log_dir == expected_log_dir.resolve(), f"Log dir sai: {log_dir}"
        assert db_path == str(expected_db_file.resolve()), f"DB path sai: {db_path}"

        # Chưa khởi tạo, file DB chưa tồn tại
        assert not expected_db_file.exists(), "DB không được tự tạo trước khi gọi init_database"

        # Khởi tạo DB lần đầu
        db_manager.init_database()
        assert expected_db_file.exists(), "DB phải được tạo sau khi init_database"

        # Kiểm tra bảng và 30 ngăn tủ mặc định
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        lockers_count = cur.execute("SELECT COUNT(*) FROM lockers").fetchone()[0]
        accounts_count = cur.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        profiles_count = cur.execute("SELECT COUNT(*) FROM face_profiles").fetchone()[0]
        conn.close()

        print(f"  • Số ngăn tủ sau lần đầu: {lockers_count} (kỳ vọng: 30)")
        print(f"  • Số tài khoản sau lần đầu: {accounts_count} (kỳ vọng: 0)")
        print(f"  • Số khuôn mặt sau lần đầu: {profiles_count} (kỳ vọng: 0)")

        assert lockers_count == 30, f"Số ngăn tủ không đúng: {lockers_count}"
        assert accounts_count == 0, "Bản phát hành không được có tài khoản sẵn"
        assert profiles_count == 0, "Bản phát hành không được có khuôn mặt sẵn"
        print("  -> TEST 1 ĐẠT: Luồng tạo mới sạch tại %LOCALAPPDATA% hoàn hảo!")

        # ─────────────────────────────────────────────────────────────────
        # TEST 2: CHẠY LẦN THỨ HAI (DATABASE ĐÃ TỒN TẠI) — BẢO TOÀN DỮ LIỆU
        # ─────────────────────────────────────────────────────────────────
        print("\n[TEST 2] Chạy lần thứ hai (Bảo toàn dữ liệu đã có):")
        # Giả lập người dùng đăng ký 1 tài khoản
        ok, msg, acc_id = db_manager.create_account("0901234567")
        assert ok, f"Không tạo được tài khoản test: {msg}"
        print(f"  • Đã thêm tài khoản thử nghiệm id={acc_id}")

        # Khởi động lại ứng dụng (gọi lại init_database)
        db_manager.init_database()

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        lockers_after = cur.execute("SELECT COUNT(*) FROM lockers").fetchone()[0]
        accounts_after = cur.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        conn.close()

        print(f"  • Số tài khoản sau khi chạy lại app: {accounts_after} (kỳ vọng: 1)")
        print(f"  • Số ngăn tủ sau khi chạy lại app: {lockers_after} (kỳ vọng: 30)")

        assert accounts_after == 1, "Dữ liệu người dùng bị mất khi chạy lại!"
        assert lockers_after == 30, "Ngăn tủ bị nhân bản trùng lặp!"
        print("  -> TEST 2 ĐẠT: Dữ liệu người dùng và ngăn tủ được bảo toàn 100%!")

        # ─────────────────────────────────────────────────────────────────
        # TEST 3: CẤU HÌNH BIẾN MÔI TRƯỜNG TÙY BIẾN FACEBOX_DATA_DIR
        # ─────────────────────────────────────────────────────────────────
        print("\n[TEST 3] Cấu hình biến môi trường FACEBOX_DATA_DIR:")
        custom_data_dir = test_sandbox / "CustomUserStorage"
        os.environ["FACEBOX_DATA_DIR"] = str(custom_data_dir)

        custom_resolved = path_service.get_data_dir()
        custom_db_path = path_service.get_db_path()

        print(f"  • Custom Data Dir: {custom_resolved}")
        print(f"  • Custom DB Path : {custom_db_path}")

        assert custom_resolved == custom_data_dir.resolve()
        assert custom_db_path == str((custom_data_dir / "facebox.db").resolve())
        print("  -> TEST 3 ĐẠT: Tùy biến FACEBOX_DATA_DIR hoạt động chuẩn xác!")
        os.environ.pop("FACEBOX_DATA_DIR", None)

        # ─────────────────────────────────────────────────────────────────
        # TEST 4: CHẾ ĐỘ PHÁT TRIỂN (DEV MODE - FROZEN = FALSE)
        # ─────────────────────────────────────────────────────────────────
        print("\n[TEST 4] Chế độ phát triển (Dev Mode):")
        sys.frozen = False
        dev_data_dir = path_service.get_data_dir()
        dev_log_dir = path_service.get_log_dir()
        dev_db = path_service.get_db_path()

        print(f"  • Dev Data Dir: {dev_data_dir}")
        print(f"  • Dev Log Dir : {dev_log_dir}")
        print(f"  • Dev DB Path : {dev_db}")

        assert dev_data_dir == (PROJECT_ROOT / "data").resolve()
        assert dev_log_dir == (PROJECT_ROOT / "logs").resolve()
        assert dev_db == str((PROJECT_ROOT / "data" / "facebox.db").resolve())

        # Kiểm tra DB dev gốc còn nguyên
        dev_root_db = PROJECT_ROOT / "data" / "facebox.db"
        assert dev_root_db.exists(), "DB phát triển gốc bị mất!"
        print(f"  • DB phát triển gốc còn nguyên: {dev_root_db} ({dev_root_db.stat().st_size} bytes)")
        print("  -> TEST 4 ĐẠT: Môi trường Dev hoàn toàn độc lập và an toàn!")

        # ─────────────────────────────────────────────────────────────────
        # TEST 5: KIỂM TRA KHÔNG TỒN TẠI DATABASE TRONG THƯ MỤC CÀI ĐẶT DIST
        # ─────────────────────────────────────────────────────────────────
        print("\n[TEST 5] Kiểm tra thư mục phân phối dist/FaceBox:")
        dist_data = PROJECT_ROOT / "dist" / "FaceBox" / "data"
        dist_db = dist_data / "facebox.db"

        print(f"  • dist/FaceBox/data exists: {dist_data.exists()}")
        print(f"  • dist/FaceBox/data/facebox.db exists: {dist_db.exists()}")

        assert not dist_db.exists(), "LỖI: Bản phân phối vẫn chứa file facebox.db!"
        assert not dist_data.exists(), "LỖI: Bản phân phối vẫn chứa thư mục data!"
        print("  -> TEST 5 ĐẠT: Không tồn tại database thứ hai trong thư mục cài đặt!")

        print("\n" + "=" * 65)
        print(">>> TẤT CẢ 5 BÀI TEST ĐÃ VƯỢT QUA 100% THÀNH CÔNG! <<<")
        print("=" * 65)
        return True

    finally:
        # Khôi phục trạng thái môi trường
        if original_frozen:
            sys.frozen = original_frozen
        elif hasattr(sys, "frozen"):
            delattr(sys, "frozen")

        if original_env_data:
            os.environ["FACEBOX_DATA_DIR"] = original_env_data
        else:
            os.environ.pop("FACEBOX_DATA_DIR", None)

        if original_env_log:
            os.environ["FACEBOX_LOG_DIR"] = original_env_log
        else:
            os.environ.pop("FACEBOX_LOG_DIR", None)

        # Dọn dẹp sandbox test
        if test_sandbox.exists():
            shutil.rmtree(test_sandbox)


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
