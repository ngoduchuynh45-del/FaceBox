# CHANGELOG.md — Lịch sử thay đổi FaceBox

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
