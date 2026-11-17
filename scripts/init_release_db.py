"""
FaceBox — Clean Release Database Generator
Tạo cơ sở dữ liệu SQLite sạch cho bản phát hành:
- Đọc trực tiếp từ database/schema.sql
- KHÔNG chứa dữ liệu tài khoản, không chứa embedding sinh trắc học cá nhân
- KHÔNG chứa lịch sử hoặc kiện hàng thử nghiệm
- Khởi tạo 30 ngăn tủ mặc định sẵn sàng sử dụng (10 size S, 15 size M, 5 size L)
"""

import sys
import os
import sqlite3
from pathlib import Path

def create_clean_database(db_path: Path) -> bool:
    """Tạo database sạch hoàn toàn tại db_path."""
    project_root = Path(__file__).resolve().parent.parent
    schema_file = project_root / "database" / "schema.sql"

    if not schema_file.exists():
        print(f"[LỖI] Không tìm thấy schema file tại: {schema_file}")
        return False

    # Đảm bảo thư mục cha tồn tại
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Nếu file đã tồn tại, xóa file cũ để đảm bảo sạch 100%
    if db_path.exists():
        try:
            db_path.unlink()
            print(f"[INFO] Đã xóa database cũ tại: {db_path}")
        except Exception as e:
            print(f"[LỖI] Không thể xóa database cũ: {e}")
            return False

    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(schema_sql)

        # Khởi tạo 30 ngăn tủ mặc định chuẩn Industrial Smart Locker
        default_lockers = []
        # Ngăn nhỏ (S): #1 - #10 (thư từ, bưu phẩm nhỏ, điện thoại)
        for i in range(1, 11):
            default_lockers.append((i, 'S', 'empty'))
        # Ngăn trung (M): #11 - #25 (hộp giày, balo, kiện hàng tiêu chuẩn)
        for i in range(11, 26):
            default_lockers.append((i, 'M', 'empty'))
        # Ngăn lớn (L): #26 - #30 (thùng carton lớn, vali)
        for i in range(26, 31):
            default_lockers.append((i, 'L', 'empty'))

        conn.executemany(
            "INSERT INTO lockers (locker_number, size, status) VALUES (?, ?, ?)",
            default_lockers
        )
        conn.commit()

        # Kiểm tra tính toàn vẹn và bảo mật dữ liệu
        cur = conn.cursor()
        acc_count = cur.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        face_count = cur.execute("SELECT COUNT(*) FROM face_profiles").fetchone()[0]
        pkg_count = cur.execute("SELECT COUNT(*) FROM packages").fetchone()[0]
        hist_count = cur.execute("SELECT COUNT(*) FROM open_history").fetchone()[0]
        locker_count = cur.execute("SELECT COUNT(*) FROM lockers").fetchone()[0]

        print("-" * 50)
        print("XÁC MINH CƠ SỞ DỮ LIỆU SẠCH (RELEASE DB):")
        print(f"  • Đường dẫn: {db_path.resolve()}")
        print(f"  • Tài khoản (accounts): {acc_count} (Yêu cầu: 0)")
        print(f"  • Khuôn mặt (face_profiles): {face_count} (Yêu cầu: 0)")
        print(f"  • Kiện hàng (packages): {pkg_count} (Yêu cầu: 0)")
        print(f"  • Lịch sử mở tủ (open_history): {hist_count} (Yêu cầu: 0)")
        print(f"  • Ngăn tủ mặc định (lockers): {locker_count} (10S, 15M, 5L)")
        print("-" * 50)

        assert acc_count == 0, "Bảo mật vi phạm: Có tài khoản trong release DB!"
        assert face_count == 0, "Bảo mật vi phạm: Có khuôn mặt trong release DB!"
        assert locker_count == 30, "Lỗi: Số lượng ngăn tủ không đúng 30!"

        print("[THÀNH CÔNG] Cơ sở dữ liệu phát hành đã được tạo an toàn và bảo mật.")
        return True

    except Exception as e:
        print(f"[LỖI] Thất bại khi tạo database phát hành: {e}")
        return False
    finally:
        conn.close()


def main():
    project_root = Path(__file__).resolve().parent.parent
    # Mặc định tạo trong thư mục dist/FaceBox/data nếu thư mục dist tồn tại,
    # hoặc tạo file mẫu data/facebox_clean_template.db
    target_dist_db = project_root / "dist" / "FaceBox" / "data" / "facebox.db"
    
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1]).resolve()
    else:
        target_path = target_dist_db

    create_clean_database(target_path)


if __name__ == "__main__":
    main()
