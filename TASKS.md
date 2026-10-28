# TASKS.md — Danh sách công việc FaceBox

Cập nhật: 2026-10-23 16:20

## Đang thực hiện (IN_PROGRESS)

| ID | Mô tả | Ghi chú |
|----|-------|---------|
| T002 | Kiểm thử toàn bộ chức năng sau khi app chạy được | Cần test thủ công |

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

## Bị chặn (BLOCKED)

Không có
