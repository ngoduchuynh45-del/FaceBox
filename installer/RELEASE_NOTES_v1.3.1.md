# FaceBox v1.3.1 – Windows Release

Bản phát hành chính thức đầu tiên của hệ thống tủ thông minh định danh khuôn mặt sinh trắc học **FaceBox** dưới dạng ứng dụng Windows 64-bit độc lập.

---

## 🌟 1. GIỚI THIỆU PHIÊN BẢN

FaceBox phiên bản **v1.3.1** mang đến giải pháp trạm tủ thông minh phong cách **Industrial Smart Locker** hoàn chỉnh, hoạt động độc lập trên Windows mà **không yêu cầu người dùng phải cài đặt môi trường lập trình Python hay bất kỳ thư viện dòng lệnh nào**.

---

## ⚡ 2. CÁC TÍNH NĂNG CHÍNH

### Chế độ Kiosk (Gửi & Nhận hàng):
- **Giao dịch Gửi hàng:** Hỗ trợ nhập số điện thoại hoặc quét khuôn mặt nhanh, tự động phân phối và mở ngăn tủ phù hợp kích thước kiện hàng (Size S, M, L).
- **Giao dịch Lấy hàng:** Nhận diện khuôn mặt thời gian thực hoặc nhập mã xác thực/SĐT để tự động giải phóng ngăn tủ.
- **Khung quét sinh trắc học:** Khung elip nhận diện khuôn mặt tỷ lệ chuẩn 0.72 với phản hồi màu sắc trực quan (Đang nhận diện, Thành công, Từ chối).
- **Bàn phím số công nghiệp:** Phím bấm cảm ứng lớn, độ nảy và tương phản cao, tối ưu cho màn hình cảm ứng hoặc chuột máy tính.

### Chế độ Quản trị Admin:
- **Bảo mật truy cập:** Đăng nhập an toàn bằng mã PIN quản trị viên.
- **Tổng quan Dashboard:** Thống kê trực quan số ngăn tủ trống, số ngăn đang chứa hàng và tỷ lệ sử dụng trạm.
- **Quản lý Ngăn tủ (Lockers):** Giám sát trạng thái 30 ngăn tủ mặc định, hỗ trợ mở khẩn cấp hoặc bảo trì ngăn tủ.
- **Lịch sử Giao dịch (History):** Tra cứu toàn diện lịch sử đóng/mở tủ theo thời gian.
- **Quản lý Tài khoản (Accounts):** Theo dõi danh sách tài khoản và số lượng profile vector khuôn mặt (embedding) đã đăng ký.
- **Cài đặt Hệ thống (Settings):** Cấu hình camera và tinh chỉnh ngưỡng nhạy nhận diện khuôn mặt.

---

## 🔬 3. CÔNG NGHỆ NỀN TẢNG

- **Giao diện người dùng:** PySide6 (Qt6 for Python) với Design System chuẩn Industrial Smart Locker (Màu vàng #FFD500 / Đen #171717).
- **Thị giác máy tính:** OpenCV (opencv-python >= 4.8.0), đa luồng DirectShow camera capture.
- **Mô hình AI:**
  - Phát hiện khuôn mặt: OpenCV YuNet (`face_detection_yunet_2023mar.onnx`) chạy cực nhanh trên CPU (~30-60 FPS).
  - Trích xuất đặc trưng sinh trắc học: OpenCV SFace (`face_recognition_sface_2021dec.onnx`) trích xuất vector 128 chiều.
- **Cơ sở dữ liệu:** SQLite 3 lưu trữ cấu trúc tủ, lịch sử và vector khuôn mặt BLOB.
- **Đóng gói ứng dụng:** PyInstaller 6.x (onedir) & Inno Setup 6 (bộ cài đặt nén lzma2).

---

## 📦 4. SẢN PHẨM PHÁT HÀNH (RELEASE ASSETS)

Người dùng có thể lựa chọn 1 trong 2 hình thức cài đặt:

1. **`FaceBox_v1.3.1_Setup_x64.exe` (107.01 MB)**:
   - Bộ cài đặt Windows Setup chính thức.
   - Tự động tạo biểu tượng trên Desktop và Start Menu với icon FaceBox chính thức.
   - Tích hợp trình gỡ cài đặt (Uninstaller) an toàn.
   - Tự động bảo vệ dữ liệu người dùng khi cập nhật phiên bản mới.

2. **`FaceBox_v1.3.1_Portable_x64.zip` (144.29 MB)**:
   - Bản di động (Portable), chỉ cần tải về, giải nén và nhấn đúp vào `FaceBox.exe` (hoặc `FaceBox_Launcher.vbs`) để chạy ngay.
   - Thích hợp lưu trữ trên USB hoặc chạy thử nghiệm không cần cài đặt.

---

## 💻 5. YÊU CẦU HỆ THỐNG

- **Hệ điều hành:** Windows 10 hoặc Windows 11 (64-bit).
- **Phần cứng:** CPU x64 (Intel Core i3 / AMD Ryzen 3 trở lên), RAM tối thiểu 4GB, ổ cứng trống 500MB.
- **Thiết bị ghi hình:** Webcam USB hoặc Webcam tích hợp laptop (720p trở lên).
- **Thư viện hệ thống:** [Microsoft Visual C++ 2015-2022 Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe).

---

## 🔒 6. BẢO MẬT VÀ DỮ LIỆU SINH TRẮC HỌC

- **Bảo mật khuôn mặt:** Ứng dụng **không bao giờ lưu trữ ảnh chụp khuôn mặt thực tế** của người dùng. Khuôn mặt sau khi quét được mã hóa thành vector 128 số thực dấu phẩy động (L2 normalized) không thể tái tạo lại thành khuôn mặt ban đầu.
- **Cách ly dữ liệu:** Toàn bộ cơ sở dữ liệu và file nhật ký hoạt động được lưu độc lập tại `%LOCALAPPDATA%\FaceBox\`. Việc nâng cấp hoặc gỡ cài đặt ứng dụng sẽ **không xóa mất dữ liệu người dùng**.

---

## ⚠️ 7. CÁC GIỚI HẠN ĐÃ BIẾT & PHÂN ĐỊNH KIỂM THỬ

### Đã kiểm thử & Xác minh đạt:
- ✅ Đóng gói PyInstaller onedir và Inno Setup x64 không thiếu file phụ thuộc.
- ✅ Khởi chạy độc lập trên Windows không cần Python.
- ✅ Tự động kết nối camera và nạp mô hình AI YuNet + SFace qua binary buffer (chống lỗi đường dẫn có dấu tiếng Việt).
- ✅ Khởi tạo cơ sở dữ liệu 30 ngăn tủ mặc định tại LocalAppData.
- ✅ Trình cài đặt và gỡ cài đặt bảo toàn 100% dữ liệu người dùng.

### Giới hạn & Chưa kiểm thử:
- ⚠️ **Liveness Detection:** Phiên bản prototype hiện tại chưa có tính năng phát hiện khuôn mặt sống (liveness detection chống giả mạo ảnh in/màn hình điện thoại). Khuyến cáo không sử dụng cho mục đích lưu trữ tài sản giá trị đặc biệt cao.
- ⚠️ **Môi trường Windows sạch:** Đã kiểm thử toàn diện trên máy phát triển Windows 11 x64; trên máy người dùng mới cần đảm bảo đã cài gói Microsoft Visual C++ Runtime.
