# FaceBox — Ứng dụng Nhận Diện Khuôn Mặt

**Phiên bản:** 1.0 (Prototype)  
**Cập nhật:** 2026-10-23

> ⚠️ **Cảnh báo bảo mật:** Đây là phiên bản prototype nội bộ. Dữ liệu khuôn mặt là thông tin sinh trắc học nhạy cảm. Hệ thống chưa có cơ chế chống giả mạo (liveness detection). **Không sử dụng để kiểm soát an ninh thực tế.**

---

## Mục tiêu

FaceBox là ứng dụng desktop Windows cho phép:
- Mở webcam và hiển thị hình ảnh trực tiếp
- Đăng ký tài khoản bằng số điện thoại Việt Nam
- Đăng ký một hoặc nhiều khuôn mặt cho cùng một số điện thoại
- Nhận diện khuôn mặt real-time và hiển thị số điện thoại liên kết
- Quản lý và xóa khuôn mặt đã đăng ký
- Lưu dữ liệu bền vững qua SQLite

---

## Công nghệ

| Thành phần | Thư viện | Phiên bản |
|-----------|---------|-----------|
| Giao diện desktop | PySide6 | 6.12+ |
| Webcam + xử lý ảnh | OpenCV | 5.0+ |
| Tính toán số học | NumPy | 2.5+ |
| Phát hiện khuôn mặt | YuNet (OpenCV built-in) | - |
| Nhận diện khuôn mặt | SFace (OpenCV built-in) | - |
| Cơ sở dữ liệu | SQLite | built-in Python |

**Không cần cài GPU** — chạy hoàn toàn trên CPU.

---

## Cấu trúc thư mục

```
FaceBox/
├── main.py                          # Điểm khởi đầu — chạy file này
├── requirements.txt                 # Thư viện cần cài
├── README.md                        # File này
├── AGENTS.md                        # Quy tắc làm việc cho AI Agent
├── PLAN.md                          # Kế hoạch phát triển 9 giai đoạn
├── TASKS.md                         # Danh sách công việc
├── CURRENT_STATE.md                 # Trạng thái hiện tại (quan trọng nhất)
├── CHANGELOG.md                     # Lịch sử thay đổi
│
├── ui/
│   ├── main_window.py               # Cửa sổ chính, sidebar điều hướng
│   ├── dashboard_page.py            # Trang tổng quan và thống kê
│   ├── registration_page.py         # Trang đăng ký khuôn mặt
│   ├── recognition_page.py          # Trang nhận diện real-time
│   ├── accounts_page.py             # Trang quản lý tài khoản
│   ├── styles.py                    # QSS stylesheet (dark theme)
│   └── widgets.py                   # Widget tái sử dụng
│
├── services/
│   ├── camera_service.py            # Quản lý webcam (chạy trong QThread)
│   ├── face_recognition_service.py  # YuNet + SFace nhận diện
│   └── account_service.py           # Validate số điện thoại Việt Nam
│
├── database/
│   ├── db_manager.py                # SQLite CRUD operations
│   └── schema.sql                   # Định nghĩa bảng (accounts, face_profiles)
│
├── models/
│   ├── download_models.py           # Script tải model AI
│   ├── face_detection_yunet_2023mar.onnx   # Model phát hiện khuôn mặt
│   └── face_recognition_sface_2021dec.onnx # Model nhận diện khuôn mặt
│
├── data/
│   └── facebox.db                   # Database SQLite (tạo tự động)
│
└── logs/
    └── facebox_YYYYMMDD.log         # Log ứng dụng
```

---

## Yêu cầu môi trường

- **Windows** 10/11
- **Python** 3.10–3.15
- **RAM** tối thiểu 2GB
- **Webcam** USB hoặc tích hợp laptop

---

## Cài đặt và khởi chạy

### Bước 1: Cài đặt Python
Tải từ https://python.org — phiên bản 3.10 trở lên

### Bước 2: Cài thư viện
```powershell
pip install PySide6 opencv-python numpy
```

### Bước 3: Tải mô hình AI
```powershell
cd "d:\Project Antigravity IDE\Thu muc moi\FaceBox"
python models\download_models.py
```

Mô hình sẽ được tải vào thư mục `models/` (~40 MB).  
Nguồn: OpenCV Model Zoo — https://github.com/opencv/opencv_zoo (License: Apache 2.0)

### Bước 4: Chạy ứng dụng
```powershell
cd "d:\Project Antigravity IDE\Thu muc moi\FaceBox"
python main.py
```

---

## Cách sử dụng

### Mở webcam
1. Vào **Tổng Quan**
2. Nhấn nút **"📷 Mở Camera"**
3. Webcam sẽ bật (có thể mất 2-3 giây)

### Đăng ký tài khoản và khuôn mặt
1. Vào **Đăng Ký Khuôn Mặt** (sau khi mở camera)
2. Nhập số điện thoại (VD: 0912345678) → nhấn **Xác nhận**
3. Nhìn thẳng vào camera → nhấn **Bắt đầu quét**
4. Hệ thống tự động chụp 10 mẫu (~3 giây)
5. Nhấn **Lưu khuôn mặt**

### Thêm khuôn mặt vào tài khoản đã có
- Nhập **cùng số điện thoại** đã đăng ký
- Hệ thống sẽ nhận ra tài khoản đã tồn tại và cho phép thêm khuôn mặt mới

### Nhận diện khuôn mặt
1. Vào **Nhận Diện Trực Tiếp**
2. Đứng trước camera
3. Hệ thống tự động nhận diện và hiển thị số điện thoại

### Quản lý tài khoản
- Vào **Quản Lý Tài Khoản**
- Tìm kiếm theo số điện thoại
- Chọn tài khoản → xem danh sách khuôn mặt
- Xóa từng khuôn mặt hoặc xóa toàn bộ

---

## Vị trí lưu dữ liệu

| Loại dữ liệu | Vị trí |
|-------------|--------|
| Database (embedding khuôn mặt) | `data/facebox.db` |
| Log ứng dụng | `logs/facebox_YYYYMMDD.log` |
| Mô hình AI | `models/*.onnx` |

### Sao lưu dữ liệu
Chỉ cần sao chép file `data/facebox.db`.  
**Lưu ý:** File này chứa dữ liệu sinh trắc học — bảo quản cẩn thận.

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách khắc phục |
|-----|-------------|----------------|
| "Không thể mở webcam" | Webcam đang bị app khác dùng | Tắt Skype, Teams, Zoom... rồi thử lại |
| "Không tìm thấy model" | Chưa tải model AI | Chạy `python models/download_models.py` |
| "Không phát hiện khuôn mặt" | Ánh sáng yếu hoặc góc lệch | Đảm bảo đủ ánh sáng, nhìn thẳng camera |
| "Khuôn mặt quá nhỏ" | Đứng quá xa camera | Đứng gần hơn (~50cm) |
| App không khởi động | Thiếu PySide6 | `pip install PySide6` |
| Nhận diện sai người | Ngưỡng quá thấp | Tăng ngưỡng trong trang Nhận Diện |

---

## Ngưỡng nhận diện

Mô hình SFace dùng **cosine distance** (khoảng cách cosine):
- **0.0** = giống hệt nhau
- **1.0** = hoàn toàn khác nhau
- **Ngưỡng mặc định: 0.363** (khuyến nghị từ tài liệu OpenCV)

Điều chỉnh trong trang **Nhận Diện Trực Tiếp**:
- Giảm ngưỡng → nghiêm ngặt hơn (ít nhận nhầm, có thể bỏ sót)
- Tăng ngưỡng → dễ nhận hơn (có thể nhận nhầm người)

---

## Giới hạn hiện tại (Phiên bản 1.0)

- Chưa có chống giả mạo (liveness detection)
- Chưa mã hóa database sinh trắc học
- Chưa kết nối mạng hoặc server
- Chưa có ứng dụng điện thoại
- Chưa điều khiển khóa tủ hàng

---

## Chức năng sẽ bổ sung (xem PLAN.md)

- Giai đoạn 4: Quản lý kiện hàng và lịch sử mở tủ
- Giai đoạn 5: Backend và đồng bộ đám mây
- Giai đoạn 6: App điện thoại
- Giai đoạn 7-8: Thiết bị nhúng + khóa điện tử
- Giai đoạn 9: Bảo mật và triển khai thực tế
