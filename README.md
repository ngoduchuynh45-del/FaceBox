# FaceBox — Industrial Smart Locker & Sinh Trắc Học Khuôn Mặt

**Hệ thống tủ thông minh nhận diện khuôn mặt 24/7 phong cách Industrial Smart Locker.**  
**Phiên bản:** v1.3.1 (Windows x64 Release)  
**Giấy phép:** Apache 2.0 (OpenCV Model Zoo YuNet & SFace) / LGPLv3 (PySide6)

> ⚠️ **Cảnh báo an ninh sinh trắc học:** Phiên bản prototype hiện tại chưa tích hợp liveness detection (phát hiện khuôn mặt sống). Không sử dụng để quản lý tài sản giá trị cao hoặc thay thế hoàn toàn các giải pháp an ninh cấp chuyên dụng.

---

## 🌟 1. GIỚI THIỆU FACEBOX

FaceBox là giải pháp phần mềm tủ thông minh (Smart Locker) thế hệ mới, kết hợp công nghệ thị giác máy tính nhận diện khuôn mặt sinh trắc học và quản lý tự động hoá quy trình giao nhận bưu kiện. Hệ thống được thiết kế theo phong cách công nghiệp **Industrial Smart Locker** (lấy cảm hứng từ các trạm tủ InPost châu Âu), mang lại trải nghiệm tối ưu, trực quan và hiện đại cho cả người sử dụng lẫn đơn vị quản lý.

---

## ⚡ 2. CÁC CHỨC NĂNG CHÍNH

### Chế độ Kiosk (Dành cho Người gửi & Người nhận hàng)
- **Giao dịch Gửi hàng:** Đăng ký / Xác thực số điện thoại, quét khuôn mặt nhanh, tự động đề xuất và gán ngăn tủ phù hợp kích thước (Size S, M, L).
- **Giao dịch Lấy hàng:** Nhận diện khuôn mặt người nhận theo thời gian thực hoặc nhập số điện thoại định danh, tự động mở đúng ngăn tủ chứa kiện hàng.
- **Giao diện Kiosk Trực quan:** Khung quét khuôn mặt elip tỷ lệ chuẩn công nghiệp, bàn phím số cảm ứng kích thước lớn, phản hồi âm thanh/hình ảnh tức thì.

### Chế độ Quản trị Admin (Dành cho Quản trị viên trạm tủ)
- **Bảo mật truy cập:** Yêu cầu mã PIN quản trị viên trước khi vào bảng điều khiển.
- **Tổng quan Dashboard:** Thống kê trực tiếp tình trạng trạm tủ (số ngăn trống, số ngăn đang giữ đồ, tỷ lệ lấp đầy).
- **Quản lý Ngăn tủ (Lockers):** Theo dõi danh sách 30 ngăn tủ mặc định (10S, 15M, 5L), hỗ trợ thao tác mở khóa khẩn cấp hoặc đổi trạng thái.
- **Lịch sử Giao dịch (History):** Tra cứu toàn bộ lượt đóng/mở tủ, thời gian và số điện thoại người thực hiện.
- **Quản lý Tài khoản (Accounts):** Quản lý danh sách người dùng, xem số lượng vector đặc trưng khuôn mặt (embedding) đã nạp.
- **Cài đặt Hệ thống (Settings):** Cấu hình camera, tinh chỉnh ngưỡng nhận diện khuôn mặt (Cosine Similarity).

---

## 🔬 3. CÔNG NGHỆ SỬ DỤNG

| Thành phần | Công nghệ / Thư viện | Ghi chú kỹ thuật |
|---|---|---|
| **Ngôn ngữ lập trình** | Python 3.10 – 3.15 | Ngôn ngữ nền tảng xử lý dữ liệu và logic hệ thống |
| **Giao diện Desktop** | PySide6 (Qt6) | High-DPI, phong cách Industrial Dark/Light, render phần cứng |
| **Thị giác máy tính** | OpenCV (opencv-python >= 4.8.0) | DirectShow camera capture, xử lý video stream đa luồng QThread |
| **Phát hiện khuôn mặt** | OpenCV YuNet (`face_detection_yunet`) | Phát hiện khuôn mặt tốc độ cao 30-60 FPS trực tiếp trên CPU |
| **Nhận diện khuôn mặt** | OpenCV SFace (`face_recognition_sface`) | Trích xuất vector đặc trưng 128 chiều, Cosine Similarity threshold 0.363 |
| **Định dạng mô hình** | ONNX | Chạy tối ưu hóa suy luận (Inference) không cần card đồ họa GPU |
| **Cơ sở dữ liệu** | SQLite 3 | Nhẹ, phi tập trung, hỗ trợ lưu trữ vector nhị phân BLOB |
| **Đóng gói ứng dụng** | PyInstaller 6.x | Đóng gói One-folder (onedir) độc lập Windows x64 |
| **Bộ cài đặt chuyên nghiệp** | Inno Setup 6 | Trình tạo file setup nén cao cấp LZMA2, quản lý shortcut và uninstaller |

---

## 💻 4. YÊU CẦU HỆ THỐNG

- **Hệ điều hành:** Windows 10 hoặc Windows 11 (phiên bản 64-bit).
- **Phần cứng:**
  - Bộ vi xử lý: Intel Core i3 / AMD Ryzen 3 trở lên (x86_64).
  - Bộ nhớ RAM: Tối thiểu 4 GB (khuyến nghị 8 GB).
  - Dung lượng ổ đĩa trống: Tối thiểu 500 MB.
  - Camera: Webcam USB hoặc Webcam tích hợp laptop hỗ trợ độ phân giải tối thiểu 720p (30fps).
- **Thư viện hệ thống:** Microsoft Visual C++ 2015-2022 Redistributable (x64).

---

## 🚀 5. HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG DÀNH CHO NGƯỜI DÙNG

Người dùng thông thường **không cần cài đặt Python**, không cần cài pip hay gõ bất kỳ dòng lệnh nào.

### Cách 1: Sử dụng Bản Cài Đặt (Khuyến nghị cho Trạm Kiosk / Máy tính để bàn)
1. Truy cập mục **Releases** trên GitHub: [FaceBox Releases](https://github.com/ngoduchuynh45-del/FaceBox/releases).
2. Tải file: `FaceBox_v1.3.1_Setup_x64.exe`.
3. Nhấn đúp vào file cài đặt và làm theo hướng dẫn trên màn hình:
   - Chọn thư mục cài đặt mong muốn.
   - Chọn tạo biểu tượng Desktop Shortcut (mặc định tích hợp icon chính thức).
   - Nhấn **Install** để hoàn tất cài đặt trong vòng vài giây.
4. Mở ứng dụng từ biểu tượng **FaceBox** trên Desktop hoặc Start Menu.

### Cách 2: Sử dụng Bản Portable (Dành cho USB / Chạy ngay không cần cài đặt)
1. Tải file: `FaceBox_v1.3.1_Portable_x64.zip` từ mục Releases.
2. Giải nén file ZIP vào một thư mục trên máy tính (ví dụ: `D:\FaceBox` hoặc `C:\Users\<Tên_Bạn>\Apps\FaceBox`).
3. Nhấn đúp vào file `FaceBox.exe` (hoặc `FaceBox_Launcher.vbs`) để bắt đầu sử dụng.

---

## 🛠️ 6. XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

### A. Cảnh báo Windows Defender SmartScreen ("Windows protected your PC")
- **Nguyên nhân:** File EXE mới phát hành từ GitHub chưa có chứng thư số doanh nghiệp trả phí (EV Certificate).
- **Khắc phục:** 
  1. Nhấp chuột vào dòng chữ gạch chân **"More info"** (Thêm thông tin).
  2. Nhấn nút **"Run anyway"** (Vẫn chạy).

### B. Lỗi không mở được Camera ("Không thể mở webcam")
- **Nguyên nhân:** Quyền truy cập camera bị tắt trên Windows, hoặc camera đang bị ứng dụng khác (Zoom, Teams, Zalo, trình duyệt) chiếm dụng.
- **Khắc phục:**
  1. Nhấn phím **Windows**, gõ `Camera privacy settings` và nhấn Enter.
  2. Đảm bảo công tắc **Camera access** (Truy cập camera) đang **BẬT (ON)**.
  3. Bật mục **Let desktop apps access your camera** (Cho phép ứng dụng màn hình nền truy cập camera).
  4. Đóng tất cả ứng dụng đang chạy có sử dụng camera và khởi động lại FaceBox.

### C. Lỗi thiếu file DLL hệ thống (`VCRUNTIME140.dll` hoặc `MSVCP140.dll was not found`)
- **Nguyên nhân:** Máy tính chưa được cài thư viện Microsoft Visual C++ Runtime.
- **Khắc phục:** Tải và cài đặt gói chính thức trực tiếp từ trang chủ Microsoft:
  - Tải về: [Microsoft Visual C++ 2015-2022 Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe)

---

## 📂 7. VỊ TRÍ DỮ LIỆU & NHẬT KÝ HOẠT ĐỘNG (RUNTIME DATA)

Để bảo đảm tính an toàn tuyệt đối và độc lập giữa mã nguồn/bộ cài với dữ liệu người dùng, khi ứng dụng đóng gói hoạt động, toàn bộ dữ liệu sinh trắc học và nhật ký được lưu trữ độc lập tại:

- **Cơ sở dữ liệu SQLite:**
  ```text
  %LOCALAPPDATA%\FaceBox\data\facebox.db
  (Đường dẫn thực tế: C:\Users\<Tên_User>\AppData\Local\FaceBox\data\facebox.db)
  ```
- **File nhật ký hoạt động (Log):**
  ```text
  %LOCALAPPDATA%\FaceBox\logs\facebox_YYYYMMDD.log
  ```

---

## 🔄 8. HƯỚNG DẪN CẬP NHẬT & GỠ CÀI ĐẶT

### Cập nhật lên phiên bản mới:
- Bạn chỉ cần chạy bộ cài đặt mới `FaceBox_vX.X.X_Setup_x64.exe` hoặc giải nén bản Portable mới đè lên thư mục ứng dụng.
- **Dữ liệu khuôn mặt, danh sách tài khoản và trạng thái ngăn tủ được bảo vệ nguyên vẹn 100%** trong `%LOCALAPPDATA%\FaceBox\data\facebox.db` và không bao giờ bị ghi đè.

### Gỡ cài đặt (Uninstall):
- Vào **Windows Settings** -> **Apps** -> **Installed Apps** (Ứng dụng đã cài đặt) -> Tìm **FaceBox** -> Chọn **Uninstall**.
- Hoặc vào Start Menu -> thư mục **FaceBox** -> chọn **Uninstall FaceBox**.
- Trình gỡ cài đặt sẽ dọn dẹp sạch sẽ các file nhị phân trong thư mục cài đặt, đồng thời **giữ lại an toàn dữ liệu người dùng trong LocalAppData** để phòng trường hợp bạn muốn cài đặt lại sau này.

---

## 👨‍💻 9. DÀNH CHO LẬP TRÌNH VIÊN (DEVELOPMENT & BUILD)

### 1. Chuẩn bị môi trường mã nguồn
```powershell
# Clone mã nguồn
git clone https://github.com/ngoduchuynh45-del/FaceBox.git
cd FaceBox

# Cài đặt thư viện
pip install -r requirements.txt

# Tải 2 mô hình ONNX từ OpenCV Zoo (nếu chưa có)
python models/download_models.py

# Khởi chạy ứng dụng ở chế độ phát triển
python main.py
```

### 2. Đóng gói bản Portable bằng PyInstaller
```powershell
pyinstaller --clean --noconfirm FaceBox.spec
```

### 3. Đóng gói bộ cài đặt bằng Inno Setup
```powershell
iscc installer\FaceBox_Setup.iss
```
File cài đặt hoàn chỉnh sẽ được tạo tại `dist\FaceBox_v1.3.1_Setup_x64.exe`.

---

## 📄 10. THÔNG TIN PHIÊN BẢN v1.3.1
- **Phát hành:** Tháng 11/2026.
- **Thay đổi chính:** Hoàn thiện cơ chế phát hành độc lập Windows x64 (Portable ZIP & Inno Setup Installer), bảo vệ dữ liệu người dùng tại LocalAppData, nạp mô hình AI an toàn chống lỗi Unicode path, chuẩn hóa giao diện Kiosk & Admin 7 tính năng.
