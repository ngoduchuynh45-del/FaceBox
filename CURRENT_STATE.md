# CURRENT_STATE.md — Trạng thái hiện tại FaceBox

Cập nhật: 2026-10-23 16:20

## Phiên bản hiện tại
**v1.0-alpha** — Giao diện chạy được, mô hình tải thành công

## Trạng thái tổng thể
✅ **Ứng dụng đã khởi động thành công lần đầu tiên**

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

**T002: Kiểm thử toàn bộ chức năng** — ứng dụng đã chạy, cần người dùng test thực tế:
1. Mở camera (Tổng Quan → Mở Camera)
2. Đăng ký tài khoản + khuôn mặt
3. Nhận diện

---

## Lỗi đã sửa trong phiên này

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

**Ưu tiên 1:** Người dùng test thủ công:
1. Mở camera → kiểm tra video hiển thị
2. Đăng ký khuôn mặt → kiểm tra lưu vào DB
3. Nhận diện → kiểm tra kết quả

**Ưu tiên 2 (nếu có lỗi phát hiện khi test):**
- Xem log: `logs/facebox_YYYYMMDD.log`
- Báo cáo lỗi cụ thể để sửa

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
