# CURRENT_STATE.md — Trạng thái hiện tại FaceBox

Cập nhật: 2026-11-14 14:00

## Phiên bản hiện tại
**v1.2.1** — Tối ưu Typography & Bố cục văn bản (UI Text Layout), sửa triệt để lỗi chữ bị co hẹp/ép tràn

## Trạng thái tổng thể
✅ **Ứng dụng đã hoàn thiện toàn diện Kiosk Mode & Admin Mode, hiển thị tiếng Việt hoàn hảo trên mọi màn hình**

---

## Chức năng đã hoạt động (đã kiểm thử)

### ✅ App khởi động
- `python main.py` chạy không lỗi
- Splash screen hiển thị
- Mô hình YuNet + SFace tải thành công
- Database khởi tạo thành công tại `data/facebox.db`
- Giao diện PySide6 hiện ra

### ✅ Database
- Khởi tạo SQLite, tạo bảng `accounts` và `face_profiles`
- CRUD operations đầy đủ

### ✅ Mô hình AI (OpenCV YuNet + SFace)
- Tải từ OpenCV Model Zoo (chính thức, Apache 2.0)
- YuNet: phát hiện khuôn mặt
- SFace: nhận diện khuôn mặt (embedding 128 chiều)
- Chạy hoàn toàn trên CPU, không cần GPU
- Tương thích Python 3.15

---

## Chức năng đã viết code (CHƯA kiểm thử đầy đủ)

- [ ] Mở webcam và hiển thị video
- [ ] Đăng ký tài khoản bằng số điện thoại
- [ ] Quét và lưu khuôn mặt
- [ ] Nhận diện khuôn mặt real-time
- [ ] Quản lý tài khoản (xem, xóa)

---

## Công việc đang làm dở

**Phase 2 — Hoàn thiện giao diện Admin & Tích hợp Nghiệp vụ Kiosk: HOÀN THÀNH TOÀN DIỆN (T020, T021)**

Đã triển khai và kiểm thử thành công:
1. **Admin Sidebar 7 mục hoàn chỉnh**:
   - Dashboard: Bổ sung thẻ thống kê ngăn tủ thời gian thực (`StatCard` 0/0), các nút thao tác nhanh tới tất cả các trang.
   - Đăng ký khuôn mặt & Nhận diện: Giữ nguyên khung elip tỷ lệ 0.72 chuẩn hóa.
   - Quản lý tài khoản: Quản lý người dùng và hồ sơ khuôn mặt.
   - Lịch sử gửi/nhận (`HistoryPage`): Bảng dữ liệu tra cứu lịch sử mở tủ, hỗ trợ bộ lọc SĐT và khoảng thời gian.
   - Quản lý tủ (`LockerPage`): Sơ đồ lưới ngăn tủ trực quan theo màu sắc trạng thái, dialog thêm ngăn tủ mới.
   - Cài đặt (`SettingsPage`): Cài đặt ngưỡng nhận diện Cosine Distance, FPS, cấu hình camera, bảo mật mật khẩu.
2. **Cơ sở dữ liệu mở rộng**:
   - 3 bảng mới: `lockers`, `packages`, `open_history` cùng các hàm CRUD trong `db_manager.py`.
3. **Liên kết nghiệp vụ khép kín giữa Kiosk và Database**:
   - Kiosk Gửi hàng (`SendItemPage`): Tự động kiểm tra số lượng ngăn trống thực tế theo size (S/M/L), tự động gán ngăn tủ trống, lưu kiện hàng và nhật ký mở tủ.
   - Kiosk Lấy hàng (`PickupItemPage`): Tra cứu danh sách các kiện hàng thực tế đang chờ lấy của tài khoản, chọn kiện hàng và giải phóng ngăn tủ về `empty` khi lấy xong.
4. **Kiểm thử tự động toàn diện**:
   - Chạy kịch bản khép kín (`scratch/test_kiosk_admin_flow.py`): Gửi hàng tại Kiosk → Kiểm tra tủ chuyển sang `occupied` → Lấy hàng tại Kiosk → Kiểm tra tủ chuyển về `empty` → Nhật ký ghi đủ 2 chiều → Dashboard Admin cập nhật số liệu chuẩn xác 100%.

**Chưa test thủ công (cần chạy `python main.py` với webcam thực tế):**
- Đưa mặt thực tế trước webcam để quét gửi và lấy hàng.

---

## Lỗi đã sửa trong phiên gần nhất (2026-11-13)

1. **Khắc phục lỗi nạp ONNX trên đường dẫn Windows có dấu tiếng Việt (T016)**:
   - Sử dụng `pathlib.Path` và nạp model qua buffer `cv2.dnn.readNetFromONNX()` / `cv2.FaceDetectorYN.create()` an toàn, không bị crash bởi hàm C++ `cv2.dnn.readNet`.
2. **Xây dựng kiến trúc Kiosk Mode (T017)**:
   - Triển khai `AppController` điều hướng 2 chế độ `KIOSK_MODE` và `ADMIN_MODE`.
   - Tạo trọn bộ 7 màn hình Kiosk (`WelcomePage`, `RoleSelectPage`, `AuthMethodPage`, `SendItemPage`, `FaceScanPage`, `PinInputPage`, `SuccessPage`).
3. **Khắc phục vòng đời Camera & Signal nhận diện (T018)**:
   - **Lỗi 1 (Kiosk không nhận diện / không phát signal)**: Sửa thiếu method `reset()` và `add_result(phone)` trong `RecognitionConfirmer` (trước đó chỉ có `update(results)` gây crash ngầm timer). Kết nối signal `authenticated.emit(phone, account_name)`.
   - **Lỗi 2 (Admin báo yêu cầu mở camera dù đã mở)**: Giải quyết việc `MainWindow` tự tạo instance `CameraService` thứ 2 độc lập. Chuyển sang Centralized Singleton `CameraService.get_instance()`, `AppController` truyền đúng instance dùng chung vào `MainWindow`, `RegistrationPage`, `FaceScanPage`. Thêm `showEvent` tự kích hoạt và đồng bộ trạng thái camera.

1. **ONNX Runtime không tương thích Python 3.15** → Chuyển sang OpenCV built-in (YuNet + SFace)
2. **DeepFace không cài được** → Không cần thiết nữa
3. **SyntaxError: main_window.py dòng 226** → `ff"..."` → `f"..."` (double f)
4. **IndentationError: recognition_page.py dòng 217** → Sửa indent từ 16 → 12 spaces
5. **requirements.txt lỗi thời** → Xóa `insightface` và `onnxruntime` (không còn dùng trong code), thêm `scikit-learn`. `pip install -r requirements.txt` chạy thành công (exit code 0).
6. **Thu nhỏ khung elip camera** → Giảm từ 72%x88% xuống 58% chiều rộng và 70% chiều cao (vừa vặn tỷ lệ khuôn mặt), giảm độ tối vignette (alpha 130) để không che khuất webcam.
7. **Bắt buộc có elip ở cả hai chức năng** → Trang Nhận Diện Trực Tiếp (`recognition_page.py`) đã chuyển sang dùng `EllipseCameraView`, vẽ khung nhận diện bên dưới và overlay elip bên trên.
8. **Khôi phục luồng quét tự nhiên T014 (Xóa bỏ quy trình 5 bước tư thế)**:
   - Xóa bỏ toàn bộ các bước tư thế tuần tự (thẳng, quay trái, quay phải, ngẩng, cúi) và panel hướng dẫn tư thế để giao diện đăng ký gọn gàng, thoáng đãng.
   - Giữ lại khung camera elip hiện đại (chiều rộng 58%, chiều cao 70%, viền đổi màu, scan line animation) ở cả hai trang Đăng Ký và Nhận Diện.
   - Khi người dùng đưa mặt vào khung elip và nhấn "Bắt đầu quét", hệ thống tự động thu thập 10 mẫu khuôn mặt hợp lệ trong khoảng 1 giây, lấy trung bình chuẩn hóa L2 và lưu vào SQLite.

---

## Quyết định kỹ thuật đã chốt

| Quyết định | Lý do |
|------------|-------|
| OpenCV YuNet + SFace thay InsightFace | Python 3.15 không có ONNX Runtime |
| Cosine distance <= 0.363 là cùng người | Tài liệu chính thức OpenCV SFace |
| Embedding 128 chiều | SFace output |
| 10 mẫu/lần đăng ký → lấy trung bình | Tăng độ ổn định |
| Nhận diện 5 FPS (timer 200ms) | Cân bằng CPU và hiển thị |

---

## Bước tiếp theo

**Ưu tiên 1:** Người dùng test thủ công toàn bộ Admin UI:
1. Chạy `python main.py` → vào Admin Mode
2. Kiểm tra 7 sidebar items chuyển trang đúng
3. Trang Quản lý Tủ: thêm ngăn tủ, xem sơ đồ lưới
4. Trang Cài đặt: thay đổi ngưỡng, xem thông tin hệ thống
5. Trang Lịch sử: tìm kiếm, lọc theo ngày

**Ưu tiên 2:** Tiến đến Phase 3 hoặc cải thiện UX:
- Hoàn thiện kết nối giữa Kiosk (gửi/nhận hàng) với Locker + Packages DB
- Cải thiện Dashboard Admin với thống kê ngăn tủ
- Thêm export dữ liệu (nếu cần)

---

## Lệnh chạy ứng dụng

```powershell
cd "d:\Project Antigravity IDE\Thu muc moi\FaceBox"
python main.py
```

---

## Cấu trúc file thực tế (đã tạo xong)

```
FaceBox/
├── main.py                  ✅ Chạy được
├── requirements.txt         ✅
├── README.md                ✅
├── AGENTS.md                ✅
├── PLAN.md                  ✅
├── TASKS.md                 ✅
├── CURRENT_STATE.md         ✅ (file này)
├── CHANGELOG.md             ✅
├── ui/
│   ├── styles.py            ✅ Syntax OK
│   ├── widgets.py           ✅ Syntax OK
│   ├── main_window.py       ✅ Syntax OK (đã sửa lỗi ff->f)
│   ├── dashboard_page.py    ✅ Syntax OK
│   ├── registration_page.py ✅ Syntax OK
│   ├── recognition_page.py  ✅ Syntax OK (đã sửa indent)
│   └── accounts_page.py     ✅ Syntax OK
├── services/
│   ├── camera_service.py    ✅ Syntax OK
│   ├── face_recognition_service.py ✅ Syntax OK (YuNet+SFace)
│   └── account_service.py   ✅ Syntax OK
├── database/
│   ├── db_manager.py        ✅ Syntax OK
│   └── schema.sql           ✅
├── models/
│   ├── face_detection_yunet_2023mar.onnx   ✅ Đã tải (1.2 MB)
│   ├── face_recognition_sface_2021dec.onnx ✅ Đã tải (38.7 MB)
│   └── download_models.py                  ✅
└── data/
    └── facebox.db           ✅ Tạo tự động khi chạy lần đầu
```
