"""
FaceBox - Database Manager
Quản lý kết nối và thao tác với SQLite database.
"""
import sqlite3
import os
import numpy as np
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

from services.path_service import get_db_path as _resolve_db_path, get_resource_path


def get_db_path() -> str:
    """Trả về đường dẫn database SQLite an toàn, có quyền ghi."""
    return _resolve_db_path()


# Tương thích ngược biến DB_PATH
DB_PATH = get_db_path()


def init_database() -> None:
    """Khởi tạo database, tạo bảng nếu chưa có."""
    db_file = get_db_path()
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    conn = get_connection()
    try:
        schema_path = str(get_resource_path(os.path.join('database', 'schema.sql')))
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
        logger.info(f"Database khởi tạo tại: {db_file}")
    except Exception as e:
        logger.error(f"Lỗi khởi tạo database: {e}")
        raise
    finally:
        conn.close()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---- ACCOUNT OPERATIONS ----

def create_account(phone_number: str) -> Tuple[bool, str, Optional[int]]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO accounts (phone_number) VALUES (?)", (phone_number,))
        conn.commit()
        return True, "Tạo tài khoản thành công", cursor.lastrowid
    except sqlite3.IntegrityError:
        return False, f"Số điện thoại {phone_number} đã được đăng ký", None
    except Exception as e:
        return False, f"Lỗi: {str(e)}", None
    finally:
        conn.close()


def get_account_by_phone(phone_number: str) -> Optional[dict]:
    conn = get_connection()
    try:
        cur = conn.execute("SELECT id, phone_number, created_at FROM accounts WHERE phone_number = ?", (phone_number,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_account_by_id(account_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        cur = conn.execute("SELECT id, phone_number, created_at FROM accounts WHERE id = ?", (account_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_accounts() -> List[dict]:
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT a.id, a.phone_number, a.created_at, COUNT(fp.id) as face_count
            FROM accounts a LEFT JOIN face_profiles fp ON a.id = fp.account_id
            GROUP BY a.id ORDER BY a.created_at DESC
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def search_accounts(query: str) -> List[dict]:
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT a.id, a.phone_number, a.created_at, COUNT(fp.id) as face_count
            FROM accounts a LEFT JOIN face_profiles fp ON a.id = fp.account_id
            WHERE a.phone_number LIKE ?
            GROUP BY a.id ORDER BY a.created_at DESC
        """, (f"%{query}%",))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def delete_account(account_id: int) -> Tuple[bool, str]:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        conn.commit()
        return (True, "Đã xóa tài khoản") if cur.rowcount > 0 else (False, "Không tìm thấy tài khoản")
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def get_total_accounts() -> int:
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    finally:
        conn.close()


# ---- FACE PROFILE OPERATIONS ----

def save_face_profile(account_id: int, embedding: np.ndarray, label: str = None) -> Tuple[bool, str, Optional[int]]:
    conn = get_connection()
    try:
        if not label:
            count = conn.execute("SELECT COUNT(*) FROM face_profiles WHERE account_id = ?", (account_id,)).fetchone()[0]
            label = f"Khuôn mặt {count + 1}"
        
        # Đảm bảo embedding float32 128 chiều và chuẩn hóa L2
        emb = embedding.flatten().astype(np.float32)
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb = emb / norm
            
        embedding_bytes = emb.tobytes()
        cur = conn.execute("INSERT INTO face_profiles (account_id, face_embedding, label) VALUES (?, ?, ?)",
                           (account_id, sqlite3.Binary(embedding_bytes), label))
        conn.commit()
        profile_id = cur.lastrowid
        logger.info(f"[DB] Đã lưu profile id={profile_id} cho account_id={account_id}, nhãn='{label}', "
                    f"shape={emb.shape}, bytes={len(embedding_bytes)}, DB={DB_PATH}")
        return True, f"Đã lưu {label}", profile_id
    except Exception as e:
        logger.error(f"[DB] Lỗi lưu khuôn mặt cho account_id={account_id}: {e}")
        return False, f"Lỗi: {str(e)}", None
    finally:
        conn.close()


def get_face_profiles_by_account(account_id: int) -> List[dict]:
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT id, account_id, label, created_at FROM face_profiles WHERE account_id = ? ORDER BY created_at",
            (account_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_all_face_embeddings() -> List[dict]:
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT fp.id as profile_id, fp.account_id, fp.face_embedding, fp.label, a.phone_number
            FROM face_profiles fp JOIN accounts a ON fp.account_id = a.id
        """)
        result = []
        rows = cur.fetchall()
        for row in rows:
            d = dict(row)
            try:
                raw_bytes = d.pop('face_embedding')
                emb = np.frombuffer(raw_bytes, dtype=np.float32).copy()
                if emb.shape[0] != 128:
                    logger.warning(f"[DB] Profile id={d.get('profile_id')} số chiều={emb.shape[0]} (kỳ vọng 128)")
                norm = np.linalg.norm(emb)
                if norm > 0:
                    emb = emb / norm
                d['embedding'] = emb
                result.append(d)
            except Exception as decode_err:
                logger.error(f"[DB] Lỗi giải mã embedding profile_id={d.get('profile_id')}: {decode_err}")

        logger.info(f"[DB] Tải thành công {len(result)}/{len(rows)} embedding từ DB: {DB_PATH}")
        return result
    except Exception as e:
        logger.error(f"[DB] Lỗi truy vấn bảng face_profiles: {e}")
        return []
    finally:
        conn.close()


def delete_face_profile(profile_id: int) -> Tuple[bool, str]:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM face_profiles WHERE id = ?", (profile_id,))
        conn.commit()
        return (True, "Da xoa khuon mat") if cur.rowcount > 0 else (False, "Khong tim thay")
    except Exception as e:
        return False, f"Loi: {str(e)}"
    finally:
        conn.close()


def delete_all_faces_of_account(account_id: int) -> Tuple[bool, str]:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM face_profiles WHERE account_id = ?", (account_id,))
        conn.commit()
        return True, f"Da xoa {cur.rowcount} khuon mat"
    except Exception as e:
        return False, f"Loi: {str(e)}"
    finally:
        conn.close()


def get_total_faces() -> int:
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM face_profiles").fetchone()[0]
    finally:
        conn.close()


# ---- LOCKER OPERATIONS ----

def get_all_lockers() -> List[dict]:
    """Lấy danh sách tất cả ngăn tủ."""
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT l.id, l.locker_number, l.size, l.status, l.current_package_id, l.created_at
            FROM lockers l ORDER BY l.locker_number
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_locker_by_number(locker_number: int) -> Optional[dict]:
    conn = get_connection()
    try:
        cur = conn.execute("SELECT * FROM lockers WHERE locker_number = ?", (locker_number,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_locker(locker_number: int, size: str = 'M') -> Tuple[bool, str]:
    conn = get_connection()
    try:
        conn.execute("INSERT INTO lockers (locker_number, size) VALUES (?, ?)", (locker_number, size))
        conn.commit()
        return True, f"Đã tạo ngăn tủ #{locker_number} ({size})"
    except sqlite3.IntegrityError:
        return False, f"Ngăn tủ #{locker_number} đã tồn tại"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def update_locker_status(locker_id: int, status: str, package_id: Optional[int] = None) -> Tuple[bool, str]:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE lockers SET status = ?, current_package_id = ? WHERE id = ?",
            (status, package_id, locker_id)
        )
        conn.commit()
        return True, f"Đã cập nhật trạng thái ngăn tủ"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def get_locker_stats() -> dict:
    """Thống kê ngăn tủ: tổng, trống, đang dùng, lỗi."""
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) FROM lockers").fetchone()[0]
        empty = conn.execute("SELECT COUNT(*) FROM lockers WHERE status='empty'").fetchone()[0]
        occupied = conn.execute("SELECT COUNT(*) FROM lockers WHERE status='occupied'").fetchone()[0]
        error = conn.execute("SELECT COUNT(*) FROM lockers WHERE status='error'").fetchone()[0]
        return {"total": total, "empty": empty, "occupied": occupied, "error": error}
    finally:
        conn.close()


def get_available_locker(size: str = 'M') -> Optional[dict]:
    """Tìm một ngăn tủ trống theo kích thước (hoặc bất kỳ ngăn trống nào)."""
    conn = get_connection()
    try:
        # Ưu tiên đúng kích thước
        cur = conn.execute(
            "SELECT * FROM lockers WHERE status = 'empty' AND size = ? ORDER BY locker_number ASC LIMIT 1",
            (size,)
        )
        row = cur.fetchone()
        if not row:
            # Nếu hết size đó, tìm ngăn trống bất kỳ
            cur = conn.execute(
                "SELECT * FROM lockers WHERE status = 'empty' ORDER BY locker_number ASC LIMIT 1"
            )
            row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_available_locker_counts_by_size() -> dict:
    """Đếm số ngăn tủ trống theo từng kích thước: S, M, L."""
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT size, COUNT(*) as cnt
            FROM lockers
            WHERE status = 'empty'
            GROUP BY size
        """)
        counts = {'S': 0, 'M': 0, 'L': 0}
        for row in cur.fetchall():
            sz = row['size']
            if sz in counts:
                counts[sz] = row['cnt']
        return counts
    finally:
        conn.close()


def delete_locker(locker_id: int) -> Tuple[bool, str]:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM lockers WHERE id = ?", (locker_id,))
        conn.commit()
        return (True, "Đã xóa ngăn tủ") if cur.rowcount > 0 else (False, "Không tìm thấy")
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


# ---- PACKAGE OPERATIONS ----

def create_package(account_id: int, locker_id: Optional[int], action: str, note: str = '') -> Tuple[bool, str, Optional[int]]:
    conn = get_connection()
    try:
        status = 'stored' if action == 'send' else 'pending'
        cur = conn.execute(
            "INSERT INTO packages (account_id, locker_id, action, status, note) VALUES (?, ?, ?, ?, ?)",
            (account_id, locker_id, action, status, note)
        )
        conn.commit()
        pkg_id = cur.lastrowid
        # Nếu gửi hàng → cập nhật trạng thái ngăn tủ
        if action == 'send' and locker_id:
            update_locker_status(locker_id, 'occupied', pkg_id)
        return True, "Đã tạo kiện hàng", pkg_id
    except Exception as e:
        return False, f"Lỗi: {str(e)}", None
    finally:
        conn.close()


def get_packages(limit: int = 100, offset: int = 0) -> List[dict]:
    """Lấy danh sách kiện hàng với thông tin tài khoản và ngăn tủ."""
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT p.id, p.account_id, p.locker_id, p.action, p.status,
                   p.created_at, p.picked_up_at, p.note,
                   a.phone_number, l.locker_number
            FROM packages p
            LEFT JOIN accounts a ON p.account_id = a.id
            LEFT JOIN lockers l ON p.locker_id = l.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_packages_count() -> int:
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0]
    finally:
        conn.close()


def get_stored_packages_by_account(account_id: int) -> List[dict]:
    """Lấy danh sách các kiện hàng đang lưu trong tủ của tài khoản (chờ nhận)."""
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT p.id, p.account_id, p.locker_id, p.action, p.status,
                   p.created_at, p.note, l.locker_number, l.size
            FROM packages p
            JOIN lockers l ON p.locker_id = l.id
            WHERE p.account_id = ? AND p.status = 'stored'
            ORDER BY p.created_at DESC
        """, (account_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def pickup_package(package_id: int) -> Tuple[bool, str]:
    """Đánh dấu kiện hàng đã lấy ra."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE packages SET status='picked_up', picked_up_at=CURRENT_TIMESTAMP WHERE id=? AND status='stored'",
            (package_id,)
        )
        if cur.rowcount > 0:
            # Giải phóng ngăn tủ
            row = conn.execute("SELECT locker_id FROM packages WHERE id=?", (package_id,)).fetchone()
            if row and row['locker_id']:
                conn.execute("UPDATE lockers SET status='empty', current_package_id=NULL WHERE id=?",
                             (row['locker_id'],))
            conn.commit()
            return True, "Kiện hàng đã được lấy"
        else:
            return False, "Không tìm thấy kiện hàng hoặc đã được lấy"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


# ---- OPEN HISTORY OPERATIONS ----

def log_open_history(account_id: Optional[int], locker_id: Optional[int],
                     action: str, method: str = 'face') -> Tuple[bool, str]:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO open_history (account_id, locker_id, action, method) VALUES (?, ?, ?, ?)",
            (account_id, locker_id, action, method)
        )
        conn.commit()
        return True, "Đã ghi lịch sử"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


def get_open_history(limit: int = 100, offset: int = 0) -> List[dict]:
    """Lấy lịch sử mở tủ với thông tin tài khoản và ngăn tủ."""
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT h.id, h.account_id, h.locker_id, h.action, h.method, h.timestamp,
                   a.phone_number, l.locker_number
            FROM open_history h
            LEFT JOIN accounts a ON h.account_id = a.id
            LEFT JOIN lockers l ON h.locker_id = l.id
            ORDER BY h.timestamp DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_open_history_count() -> int:
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM open_history").fetchone()[0]
    finally:
        conn.close()


def search_open_history(phone_query: str = '', date_from: str = '', date_to: str = '',
                        limit: int = 100) -> List[dict]:
    """Tìm kiếm lịch sử mở tủ theo số điện thoại và khoảng thời gian."""
    conn = get_connection()
    try:
        sql = """
            SELECT h.id, h.account_id, h.locker_id, h.action, h.method, h.timestamp,
                   a.phone_number, l.locker_number
            FROM open_history h
            LEFT JOIN accounts a ON h.account_id = a.id
            LEFT JOIN lockers l ON h.locker_id = l.id
            WHERE 1=1
        """
        params = []
        if phone_query:
            sql += " AND a.phone_number LIKE ?"
            params.append(f"%{phone_query}%")
        if date_from:
            sql += " AND h.timestamp >= ?"
            params.append(date_from)
        if date_to:
            sql += " AND h.timestamp <= ?"
            params.append(date_to + " 23:59:59")
        sql += " ORDER BY h.timestamp DESC LIMIT ?"
        params.append(limit)
        cur = conn.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
