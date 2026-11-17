# CHANGELOG.md — Lịch sử thay đổi FaceBox

---

## [v1.2.1] - 2026-11-14

### Tối Ưu Typography & Bố Cục Văn Bản (T023)
- **Khắc phục lỗi ép chữ nút 'Quay về Kiosk' & Sidebar Admin**:
  - Mở rộng chiều rộng sidebar từ `210px` lên `235px` trong `ui/main_window.py`.
  - Tách nút `btn_return_kiosk` thành selector riêng, đặt padding `8px 12px`, margin `6px 10px`, căn giữa text `◀  QUAY VỀ KIOSK` (font 13px weight 900), hiển thị rộng rãi, không bị cắt text.
  - Tinh chỉnh font-size 7 mục nav sidebar về `13.5px` và padding `10px 12px` trong `ui/theme.py`, đảm bảo các tiêu đề nav dài như "Nhận Diện Trực Tiếp", "Đăng Ký Khuôn Mặt" không chạm mép.
- **Nâng cấp Hộp thoại Nhập mã PIN Quản trị (AdminLoginDialog)**:
  - Mở rộng kích thước dialog từ `420x540px` lên `450x590px`, loại bỏ tình trạng tràn layout/đè chữ.
  - Tích hợp màu sắc động theo Theme (Light/Dark Mode), tránh lỗi chữ màu đen bị tàng hình ở Dark Mode.
  - Hỗ trợ tham số `btn_height` trong `TouchNumericKeypad` (52px cho dialog, 68px cho màn hình cảm ứng Kiosk).
  - Tinh chỉnh nút bánh răng `⚙️` (`gear_btn`) padding `0px`, icon căn giữa chuẩn xác.
- **Tối ưu Bảng dữ liệu & Các nút thao tác**:
  - Rút gọn nhãn nút xóa trong trang Quản lý tài khoản: `"🗑️  Xóa mẫu chọn"` và `"🗑️  Xóa tất cả"`, hiển thị vừa vặn trong panel 350px.
  - Tăng độ rộng cột ID bảng lịch sử lên `70px` và đặt `setMinimumSectionSize(70)` để header và icon sort không bị đè.
  - Cải tiến nút Camera trên Dashboard: cập nhật nhãn qua đối tượng label nội bộ, loại bỏ lỗi vẽ chữ đè lên layout.
  - Mở rộng AddLockerDialog lên `380x240px` và cố định chiều rộng nhãn 90px để các ô nhập liệu thẳng hàng tắp.
  - Chuẩn hóa font hệ thống: `FONT_FAMILY = '"Segoe UI", Tahoma, Arial, sans-serif'` hỗ trợ tiếng Việt toàn diện, không lỗi dấu.

---

## [v1.2.0] - 2026-11-13

### Redesign Toàn Bộ Giao Diện — Industrial Smart Locker (T022)
- **Hệ thống Thiết kế & Bảng màu (InPost Poland / Locker & Lock)**:
  - Thiết lập bảng màu chuẩn công nghiệp: Primary Yellow (`#FFD500`), Primary Black (`#171717`), Light Background (`#F2F2F2`), Dark Surface (`#252525`), Dark Border (`#3A3A3A`), Success (`#16A36A`), Error (`#D94848`).
  - Hình khối vuông vức (`border-radius: 0–2px`), loại bỏ hoàn toàn góc bo tròn kiểu SaaS.
  - Hỗ trợ đầy đủ **Light Mode** và **Dark Mode** với bộ sinh stylesheet QSS tự động và lớp `ThemeManager`.
- **Thiết kế Logo Phẳng Công Nghiệp Mới**:
  - Biểu tượng chiếc máy ảnh nhìn trực diện: Thân vàng `#FFD500`, viền đen `#171717`, ống kính tròn màu đen, bên trong là hộp kiện hàng hình vuông (Square Package Box) có băng dán nắp hộp viền đen.
  - Đi kèm dòng chữ FaceBox và nhãn badge "SMART LOCKER".
- **Chuẩn hóa Giao diện Kiosk**:
  - `WelcomePage`: Thiết kế nổi bật với 2 nút hành động cực đại: **LẤY HÀNG** (Vàng/Đen) và **GỬI HÀNG** (Đen/Vàng).
  - `AuthChoicePage`: Nút quét khuôn mặt và nhập số điện thoại tương phản cao.
  - `PhoneInputPage`: Bàn phím số cảm ứng viền vuông 2px vàng/đen, màn hình số to rõ.
  - `FaceScanPage`: Khung nhận diện elip tỷ lệ 0.72 chuẩn hóa, viền trạng thái rõ ràng.
  - `SendItemPage`: Các card chọn ngăn S/M/L viền khối công nghiệp, hiển thị số ngăn trống thực tế.
  - `PickupItemPage`: Danh sách kiện hàng trực quan, hỗ trợ chọn kiện nhận hàng.
  - `CompletePage`: Hộp thông tin mở tủ viền vàng sắc sảo, nút quay về Kiosk rõ ràng.
- **Chuẩn hóa Giao diện Admin**:
  - Đồng bộ bảng màu và hình khối 2px cho toàn bộ 7 trang: Dashboard, Đăng Ký, Nhận Diện, Quản Lý Tài Khoản, Lịch Sử, Quản Lý Tủ, Cài Đặt.
  - Logo FaceBox Industrial Camera hiển thị trên Sidebar quản trị.
  - Cung cấp tùy chọn đổi theme Light/Dark và nút Đăng Xuất quay về Kiosk trong Cài Đặt.
- **Bảo toàn lõi kỹ thuật & thuật toán**:
  - Giữ nguyên mô hình AI OpenCV YuNet và SFace, ngưỡng nhận diện 0.363.
  - Giữ nguyên cơ sở dữ liệu SQLite và cấu trúc bảng ngăn tủ/kiện hàng.

---

## [v1.1-alpha] - 2026-11-13

### Tích hợp Nghiệp vụ Kiosk ↔ Database Locker (Phase 2 - T021)
- **Luồng Gửi hàng Kiosk (`SendItemPage`)**:
  - Tự động hiển thị số lượng ngăn tủ trống thực tế theo kích thước (S/M/L) từ DB.
  - Tự động gán ngăn tủ trống thực tế và tạo bản ghi kiện hàng (`packages`).
  - Ghi nhận lịch sử mở tủ (`open_history`) với hành động `send` và phương thức tương ứng.
- **Luồng Lấy hàng Kiosk (`PickupItemPage`)**:
  - Tra cứu các kiện hàng đang lưu của tài khoản theo số điện thoại đã xác thực.
  - Hiển thị danh sách kiện hàng trực quan, hỗ trợ chọn kiện hàng để nhận.
  - Đánh dấu kiện hàng đã nhận (`picked_up`), giải phóng ngăn tủ về `empty` và ghi log `open_history`.
- **Thống kê Dashboard Admin (`DashboardPage`)**:
  - Bổ sung `StatCard` hiển thị số ngăn tủ khả dụng theo thời gian thực (Trống/Tổng).
  - Bổ sung nút truy cập nhanh đến Quản lý ngăn tủ và Lịch sử.

### Hoàn thiện Giao diện Quản trị Admin (Phase 2 - T020)
- **Mở rộng Sidebar 7 mục**: Mở rộng từ 4 lên 7 mục chức năng đầy đủ: Tổng Quan, Đăng Ký, Nhận Diện, Quản Lý Tài Khoản, Lịch Sử Gửi/Nhận, Quản Lý Tủ, Cài Đặt.
- **Trang Lịch Sử (`HistoryPage`)**: Bảng dữ liệu tra cứu lịch sử mở tủ, hỗ trợ bộ lọc số điện thoại và khoảng thời gian.
- **Trang Quản Lý Tủ (`LockerPage`)**: Hiển thị sơ đồ lưới các ngăn tủ kèm kích thước và trạng thái màu sắc; dialog thêm nhiều ngăn tủ mới.
- **Trang Cài Đặt (`SettingsPage`)**: Tinh chỉnh ngưỡng Cosine Distance, tốc độ nhận diện FPS, cấu hình camera, đổi mật khẩu và xem thông tin hệ thống.
- **Mở rộng Database Schema**: Bổ sung các bảng `lockers`, `packages`, `open_history` cùng các hàm CRUD tương ứng trong `db_manager.py`.

### Chuẩn hóa Khung Nhận Diện Khuôn Mặt (Phase 2 - T019)
- **Bảo toàn tỷ lệ hình học Elip**: Khung elip luôn giữ đúng tỷ lệ khuôn mặt người $W/H = 0.72$ bất biến khi thay đổi kích thước cửa sổ (nhỏ, vừa, phóng to toàn màn hình, siêu rộng ultrawide hoặc màn hình dọc).
- **Căn giữa tuyệt đối**: Tâm elip luôn trùng khớp với tâm hình ảnh camera hiển thị ($W_{cam}/2, H_{cam}/2$), không bị méo hình camera (giữ nguyên `Qt.KeepAspectRatio`).
- **Màu sắc và hiệu ứng trực quan**:
  - Trạng thái bình thường: Màu xám trung tính (Slate-400 `#94a3b8`).
  - Khuôn mặt quá xa / quá gần / lệch tâm: Viền đỏ (Red-500 `#ef4444`) kèm thông điệp hướng dẫn rõ ràng.
  - Vị trí khuôn mặt hợp lệ: Viền xanh lá (Green-500 `#22c55e`).
  - Nhận diện thành công: Hiệu ứng xanh lá nhẹ (Green-400 `#4ade80` kèm radial glow mềm bên trong elip).
- **Đồng bộ hóa hình học**: `EllipseCameraView.evaluate_face_geometry()` dùng chung cho cả Kiosk (`face_scan_page.py`), Admin Đăng Ký (`registration_page.py`) và Admin Nhận Diện (`recognition_page.py`).

### Phase 1 & Khắc phục Camera Lifecycle & Face Recognition Signal (T017, T018)

**Tính năng mới (Phase 1):**
- Triển khai `AppController` hỗ trợ 2 chế độ độc lập: `KIOSK_MODE` và `ADMIN_MODE`.
- Bộ màn hình Kiosk hoàn chỉnh: `WelcomePage`, `RoleSelectPage`, `AuthMethodPage`, `SendItemPage`, `FaceScanPage`, `PinInputPage`, `SuccessPage`.
- Bộ Design System chuẩn Linear (`ui/theme.py`, `ui/components.py`).

**Sửa lỗi & Tối ưu Camera / AI (T018):**
- **Centralized Camera Manager**: `CameraService` trở thành singleton quản lý tập trung 1 `cv2.VideoCapture(0)` duy nhất, kiểm tra luồng thực tế qua `has_active_feed()`, `_last_frame_ts`, tránh xung đột thiết bị phần cứng.
- **Khắc phục lỗi Signal Kiosk FaceScan**: Bổ sung `reset()` và `add_result(phone)` cho `RecognitionConfirmer` trong `services/face_recognition_service.py`, phát signal `authenticated.emit` chính xác khi đạt 4 frames liên tục.
- **Khắc phục lỗi Admin Camera Registration**: `MainWindow` nhận chung instance `CameraService` từ `AppController`, tự động đồng bộ và kích hoạt khi mở trang Đăng Ký, không báo lỗi ảo "Vui lòng mở camera".
- **Kiểm thử tự động**: Vượt qua 100% 7 kịch bản kiểm thử tích hợp vòng đời camera và nhận diện.

---

## [v1.0-alpha] - 2026-10-23

### Khởi tạo dự án và chạy thành công lần đầu

**Thư viện đã cài:**
- PySide6 6.12.0 ✅
- opencv-python 5.0.0 ✅
- numpy 2.5.4 ✅
- scikit-learn 1.9.1 ✅
- scipy 1.18.1 ✅

**Mô hình AI (không cần cài thêm):**
- YuNet face_detection_yunet_2023mar.onnx (1.2 MB) ✅
- SFace face_recognition_sface_2021dec.onnx (38.7 MB) ✅
- Nguồn: OpenCV Model Zoo (Apache 2.0)

**Quyết định quan trọng:**
- **Không dùng InsightFace**: ONNX Runtime chưa hỗ trợ Python 3.15
- **Không dùng DeepFace**: Xung đột dependency với Python 3.15
- **Chọn OpenCV built-in YuNet+SFace**: Tích hợp sẵn, không cần runtime riêng

**Lỗi đã sửa:**
- `SyntaxError` dòng 226 `main_window.py`: `ff"..."` → `f"..."`
- `IndentationError` dòng 217 `recognition_page.py`: 16 spaces → 12 spaces

**Trạng thái kiểm thử:**
- ✅ App khởi động, giao diện hiển thị
- ✅ Mô hình YuNet + SFace tải thành công
- ✅ Database khởi tạo thành công
- ⏳ Chưa kiểm thử webcam và nhận diện thực tế

---
