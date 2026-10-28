# PLAN.md — Kế hoạch phát triển FaceBox

Cập nhật: 2026-10-23

## Tổng quan

FaceBox là ứng dụng nhận diện khuôn mặt chạy trên desktop Windows.
Phát triển theo 9 giai đoạn từ prototype đến triển khai thực tế.

---

## Giai đoạn 1: Webcam, đăng ký và nhận diện cơ bản

**Trạng thái:** `IN_PROGRESS`

**Mục tiêu:** Ứng dụng desktop chạy được, mở webcam, đăng ký và nhận diện khuôn mặt.

**Công việc:**
- [x] Tạo cấu trúc dự án
- [x] Viết code database (db_manager.py, schema.sql)
- [x] Viết camera_service.py (QThread)
- [x] Viết face_recognition_service.py (InsightFace)
- [x] Viết account_service.py (validate số điện thoại)
- [x] Viết giao diện (main_window, dashboard, registration, recognition, accounts)
- [ ] Cài đặt InsightFace + ONNX Runtime thành công
- [ ] Chạy ứng dụng lần đầu không lỗi
- [ ] Đăng ký tài khoản + khuôn mặt
- [ ] Nhận diện thành công qua webcam
- [ ] Kiểm thử xóa khuôn mặt

**Điều kiện hoàn thành:**
- Ứng dụng khởi động không lỗi
- Webcam hoạt động và hiển thị video
- Đăng ký tài khoản + khuôn mặt lưu vào database
- Nhận diện chính xác khuôn mặt đã đăng ký
- Dữ liệu tồn tại sau khi đóng/mở lại ứng dụng

**Phụ thuộc:** InsightFace phải tương thích với Python 3.15

---

## Giai đoạn 2: Hoàn thiện quản lý tài khoản

**Trạng thái:** `TODO`

**Mục tiêu:** Giao diện quản lý tài khoản hoàn chỉnh, nhiều khuôn mặt cho một số điện thoại.

**Công việc:**
- [ ] Kiểm thử thêm nhiều khuôn mặt vào cùng tài khoản
- [ ] Kiểm thử nhận diện chính xác sau khi thêm
- [ ] Cải thiện UI/UX trang Quản lý tài khoản
- [ ] Xử lý trường hợp khuôn mặt đã đăng ký cho tài khoản khác
- [ ] Thêm thumbnail ảnh nhỏ trong danh sách khuôn mặt

---

## Giai đoạn 3: Hoàn thiện UX và xử lý lỗi

**Trạng thái:** `TODO`

**Mục tiêu:** Ứng dụng ổn định, xử lý mọi tình huống lỗi.

**Công việc:**
- [ ] Kiểm thử không có webcam
- [ ] Kiểm thử webcam bị ứng dụng khác dùng
- [ ] Cải thiện thông báo lỗi (tiếng Việt, dễ hiểu)
- [ ] Thêm màn hình loading khi tải mô hình
- [ ] Tối ưu hiệu suất nhận diện
- [ ] Cân chỉnh ngưỡng nhận diện tối ưu

---

## Giai đoạn 4: Quản lý kiện hàng và lịch sử

**Trạng thái:** `TODO`

**Mục tiêu:** Thêm tính năng quản lý tủ hàng.

**Công việc:**
- [ ] Bảng Packages (kiện hàng)
- [ ] Bảng OpenHistory (lịch sử mở tủ)
- [ ] Trang quản lý kiện hàng
- [ ] Trang lịch sử mở tủ
- [ ] Báo cáo theo ngày/tuần

---

## Giai đoạn 5: Backend và đồng bộ dữ liệu

**Trạng thái:** `TODO`

**Mục tiêu:** API backend, đồng bộ nhiều thiết bị.

**Công việc:**
- [ ] FastAPI backend
- [ ] PostgreSQL database
- [ ] REST API cho tài khoản và khuôn mặt
- [ ] Đồng bộ từ desktop lên server
- [ ] Authentication

---

## Giai đoạn 6: Ứng dụng điện thoại

**Trạng thái:** `TODO`

**Mục tiêu:** App mobile cho người dùng cuối.

**Công việc:**
- [ ] Flutter hoặc React Native
- [ ] Xem trạng thái tủ
- [ ] Nhận thông báo khi có kiện hàng
- [ ] Mở tủ từ xa

---

## Giai đoạn 7: Thiết bị nhúng

**Trạng thái:** `TODO`

**Mục tiêu:** Raspberry Pi hoặc Jetson Nano với camera riêng.

**Công việc:**
- [ ] Porting sang ARM
- [ ] Tối ưu cho CPU nhúng
- [ ] Màn hình hiển thị nhỏ
- [ ] GPIO để điều khiển khóa

---

## Giai đoạn 8: Khóa điện tử

**Trạng thái:** `TODO`

**Mục tiêu:** Tích hợp điều khiển khóa tủ thật.

**Công việc:**
- [ ] Giao tiếp UART/GPIO với khóa
- [ ] Logic mở khóa an toàn
- [ ] Fallback khi nhận diện thất bại nhiều lần

---

## Giai đoạn 9: Bảo mật và triển khai thực tế

**Trạng thái:** `TODO`

**Mục tiêu:** Kiểm thử bảo mật, deploy production.

**Công việc:**
- [ ] Liveness detection (chống giả mạo bằng ảnh/video)
- [ ] Mã hóa database sinh trắc học
- [ ] Penetration testing
- [ ] GDPR/Luật bảo vệ dữ liệu cá nhân
- [ ] Tài liệu triển khai

---
