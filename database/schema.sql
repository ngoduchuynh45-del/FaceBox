-- FaceBox Database Schema v1.0
-- Cảnh báo bảo mật: face_embedding là dữ liệu sinh trắc học nhạy cảm.
-- Trong triển khai thực tế, cần mã hóa file database này.

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS face_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    face_embedding BLOB NOT NULL,
    label TEXT DEFAULT 'Khuon mat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_face_profiles_account_id ON face_profiles(account_id);
CREATE INDEX IF NOT EXISTS idx_accounts_phone ON accounts(phone_number);

-- ── Bảng ngăn tủ (Lockers) ──────────────────────────────────────────────────
-- Mỗi ngăn tủ có số thứ tự, kích thước (S/M/L) và trạng thái.
CREATE TABLE IF NOT EXISTS lockers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    locker_number INTEGER NOT NULL UNIQUE,
    size TEXT NOT NULL DEFAULT 'M' CHECK(size IN ('S', 'M', 'L')),
    status TEXT NOT NULL DEFAULT 'empty' CHECK(status IN ('empty', 'occupied', 'error')),
    current_package_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (current_package_id) REFERENCES packages(id) ON DELETE SET NULL
);

-- ── Bảng kiện hàng (Packages) ───────────────────────────────────────────────
-- Theo dõi mỗi lần gửi/nhận hàng qua tủ.
CREATE TABLE IF NOT EXISTS packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    locker_id INTEGER,
    action TEXT NOT NULL CHECK(action IN ('send', 'receive')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'stored', 'picked_up', 'expired')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    picked_up_at TIMESTAMP,
    note TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (locker_id) REFERENCES lockers(id) ON DELETE SET NULL
);

-- ── Bảng lịch sử mở tủ (Open History) ──────────────────────────────────────
-- Ghi lại mỗi lần mở tủ: ai mở, ngăn nào, bằng phương thức gì.
CREATE TABLE IF NOT EXISTS open_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    locker_id INTEGER,
    action TEXT NOT NULL CHECK(action IN ('send', 'receive', 'admin_open')),
    method TEXT NOT NULL DEFAULT 'face' CHECK(method IN ('face', 'pin', 'admin')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE SET NULL,
    FOREIGN KEY (locker_id) REFERENCES lockers(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_lockers_status ON lockers(status);
CREATE INDEX IF NOT EXISTS idx_packages_account ON packages(account_id);
CREATE INDEX IF NOT EXISTS idx_packages_locker ON packages(locker_id);
CREATE INDEX IF NOT EXISTS idx_open_history_account ON open_history(account_id);
CREATE INDEX IF NOT EXISTS idx_open_history_timestamp ON open_history(timestamp);
