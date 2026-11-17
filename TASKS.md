# TASKS.md — Danh sách công việc FaceBox

Cập nhật: 2026-11-13 15:43

## Đang thực hiện (IN_PROGRESS)

| ID | Mô tả | Ghi chú |
|----|-------|---------|
| — | Không có task nào đang thực hiện | — |

## Chưa bắt đầu (TODO)

| ID | Mô tả | Phụ thuộc |
|----|-------|-----------|
| T003 | Kiểm thử mở webcam và hiển thị video | T002 |
| T004 | Kiểm thử đăng ký tài khoản bằng số điện thoại | T002 |
| T005 | Kiểm thử đăng ký khuôn mặt + lưu DB | T004 |
| T006 | Kiểm thử nhận diện khuôn mặt đã đăng ký | T005 |
| T007 | Kiểm thử đóng/mở lại app - dữ liệu tồn tại | T005 |
| T008 | Kiểm thử xóa khuôn mặt | T005 |
| T009 | Kiểm thử thêm khuôn mặt 2 vào cùng tài khoản | T005 |
| T010 | Tinh chỉnh ngưỡng nhận diện (nếu cần) | T006 |
| T011 | Khởi tạo Git repository | - |
| T012 | Kiểm thử khi không có webcam | T002 |
| T013 | Kiểm thử với khuôn mặt chưa đăng ký - không nhận nhầm | T006 |

## Đã hoàn thành (DONE)

| ID | Mô tả | Ngày |
|----|-------|------|
| T000 | Khởi tạo cấu trúc dự án | 2026-10-23 |
| T000b | Viết database/schema.sql | 2026-10-23 |
| T000c | Viết database/db_manager.py | 2026-10-23 |
| T000d | Viết services/camera_service.py | 2026-10-23 |
| T000e | Viết services/face_recognition_service.py (YuNet+SFace) | 2026-10-23 |
| T000f | Viết services/account_service.py | 2026-10-23 |
| T000g | Viết ui/styles.py + ui/widgets.py | 2026-10-23 |
| T000h | Viết ui/dashboard_page.py | 2026-10-23 |
| T000i | Viết ui/registration_page.py | 2026-10-23 |
| T000j | Viết ui/recognition_page.py | 2026-10-23 |
| T000k | Viết ui/accounts_page.py | 2026-10-23 |
| T000l | Viết ui/main_window.py | 2026-10-23 |
| T000m | Viết main.py | 2026-10-23 |
| T000n | Cài đặt PySide6, OpenCV, NumPy, scikit-learn | 2026-10-23 |
| T000o | Tạo file tài liệu đầy đủ | 2026-10-23 |
| T001a | Giải quyết Python 3.15 - ONNX không tương thích | 2026-10-23 |
| T001b | Chuyển sang OpenCV YuNet+SFace (không cần ONNX Runtime) | 2026-10-23 |
| T001c | Tải model YuNet + SFace từ OpenCV Model Zoo | 2026-10-23 |
| T001d | Sửa 2 lỗi syntax (ff->f, indent error) | 2026-10-23 |
| T002a | Chạy app lần đầu thành công - model tải OK | 2026-10-23 |
| T014 | Thu nhỏ elip camera (58%x70%) và phủ ở cả Đăng Ký & Nhận Diện | 2026-10-27 |
| T014b | Khôi phục luồng quét tự nhiên T014: xóa bỏ hoàn toàn quy trình 5 bước tư thế | 2026-10-28 |
| T015 | Tạo file Word Báo cáo Kỹ thuật & Hướng dẫn FaceBox (FaceBox_Bao_Cao_Du_An.docx) | 2026-11-07 |
| T016 | Debug và chuẩn hóa nạp model YuNet/SFace qua pathlib + buffer (chống lỗi OpenCV Unicode path) | 2026-11-13 |
| T017 | Phase 1: Xây dựng Design System, Kiosk Mode 7 màn hình, AppController chuyển Kiosk ↔ Admin | 2026-11-13 |
| T018 | Khắc phục vòng đời Camera & Tín hiệu nhận diện Kiosk/Admin (Centralized Camera Manager & Confirmer API) | 2026-11-13 |
| T019 | Bổ sung Phase 2: Chuẩn hóa khung elip nhận diện khuôn mặt (bảo toàn tỷ lệ 0.72 bất biến, căn giữa camera, 6 trạng thái màu, đồng bộ hình học) | 2026-11-13 |
| T020 | Phase 2: Mở rộng Admin UI — Sidebar 7 mục, DB schema mới (lockers/packages/open_history), 3 trang mới (Lịch sử, Quản lý Tủ, Cài đặt) | 2026-11-13 |
| T021 | Phase 2: Tích hợp nghiệp vụ Kiosk ↔ Locker/Packages DB (Gửi hàng gán tủ, Lấy hàng giải phóng tủ, Dashboard thống kê ngăn tủ) | 2026-11-13 |
| T022 | Redesign toàn diện UI theo phong cách Industrial Smart Locker (InPost Poland / Locker & Lock): Bảng màu Vàng #FFD500 / Đen #171717, hình khối vuông vức 0-2px, Logo Camera phẳng + Hộp kiện hàng, hỗ trợ Light/Dark Theme đồng bộ cho cả Kiosk và Admin | 2026-11-13 |
| T023 | Tối ưu Typography & Bố cục văn bản (UI Text Layout): Sửa lỗi chữ bị ép/cắt ở nút 'Quay về Kiosk', mở rộng sidebar 235px, nâng cấp hộp thoại AdminLoginDialog (450x590px), chuẩn hóa font Segoe UI hỗ trợ tiếng Việt hoàn hảo, tối ưu các nhãn, nút xóa và bảng dữ liệu | 2026-11-14 |
| T024 | Phase 1 Đóng gói: Tạo path_service, cập nhật face_recognition_service + db_manager, tạo FaceBox.ico, cập nhật main.py (mutex, splash, error handler), tạo FaceBox.spec, build PyInstaller onedir thành công (FaceBox.exe ~6.15MB) | 2026-11-14 |
| T024b | Phase 1 Đóng gói - Hoàn thiện: Copy facebox.db sang dist/FaceBox/data/, tạo FaceBox.vbs launcher trên Desktop (không hiện CMD), cập nhật VERSIONS.md → v1.3.0 | 2026-11-14 |
| T024c | Fix launcher VBS: Junction C:\FaceBoxApp → dist\FaceBox (tránh Unicode), viết VBS ASCII-only, xác minh FaceBox.exe chạy OK (217 MB RAM, AI + Camera + DB đều hoạt động) | 2026-11-14 |
| T025 | Kiểm thử FaceBox.exe tự động: khởi động OK, YuNet+SFace nạp qua binary buffer, DB kết nối 2 tài khoản/1 embedding, Camera 0 hoạt động, Responding=True | 2026-11-14 |

## Bị chặn (BLOCKED)

Không có
