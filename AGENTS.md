# AGENTS.md — Quy tắc làm việc cho AI Coding Agent

## Đọc bắt buộc trước khi bắt đầu

Mỗi khi được yêu cầu tiếp tục FaceBox, thực hiện theo thứ tự:

1. Đọc **AGENTS.md** (file này) để hiểu quy tắc làm việc
2. Đọc **CURRENT_STATE.md** để xác định công việc đang dở
3. Đọc **TASKS.md** và **PLAN.md** để xác định ưu tiên
4. Đọc **README.md** khi cần hiểu cách chạy hoặc cấu trúc hệ thống
5. Kiểm tra code thực tế trước khi kết luận về trạng thái dự án

## Quy tắc bắt buộc

### Không được làm
- Không viết lại các chức năng đã hoạt động nếu không có lý do rõ ràng
- Không tự ý thay đổi kiến trúc hoặc thư viện chính khi chưa cần thiết
- Không xóa dữ liệu người dùng hoặc cơ sở dữ liệu khi sửa code
- Không ghi đè file cấu hình hoặc dữ liệu quan trọng chưa kiểm tra
- Không đánh dấu hoàn thành nếu chưa xác minh bằng cách chạy thực tế
- Không tuyên bố đã kiểm thử nếu chưa thực sự chạy thử
- Không ghi embedding khuôn mặt vào log
- Không commit file data/facebox.db vào Git

### Phải làm
- Ưu tiên sửa lỗi nhỏ, có phạm vi rõ ràng
- Kiểm tra code thực tế trước khi kết luận
- Cập nhật tài liệu sau mỗi công việc hoàn thành
- Nếu thiếu thông tin, kiểm tra code, log và tài liệu trước khi suy đoán
- Giải thích thay đổi quan trọng trước khi thực hiện

## Cấu trúc module quan trọng

```
FaceBox/
├── main.py                          # Điểm khởi đầu
├── ui/
│   ├── main_window.py               # Cửa sổ chính, routing
│   ├── dashboard_page.py            # Trang tổng quan
│   ├── registration_page.py         # Đăng ký khuôn mặt
│   ├── recognition_page.py          # Nhận diện real-time
│   ├── accounts_page.py             # Quản lý tài khoản
│   ├── styles.py                    # QSS stylesheet
│   └── widgets.py                   # Widget tái sử dụng
├── services/
│   ├── camera_service.py            # Quản lý webcam (QThread)
│   ├── face_recognition_service.py  # Nhận diện khuôn mặt (InsightFace)
│   └── account_service.py           # Validate số điện thoại
├── database/
│   ├── db_manager.py                # SQLite CRUD operations
│   └── schema.sql                   # Định nghĩa bảng
└── data/
    └── facebox.db                   # Database (KHÔNG commit vào Git)
```

## Vị trí lưu dữ liệu quan trọng

- **Database**: `data/facebox.db` (SQLite)
- **Log**: `logs/facebox_YYYYMMDD.log`
- **Mô hình AI**: `%USERPROFILE%/.insightface/models/buffalo_sc/`

## Thư viện chính đã chọn

| Thư viện | Mục đích | Lý do chọn |
|----------|----------|------------|
| PySide6 | Giao diện desktop | Qt6 ổn định, hỗ trợ Python 3.15 |
| OpenCV | Webcam, xử lý ảnh | Chuẩn công nghiệp |
| InsightFace | Nhận diện khuôn mặt | CPU, không cần GPU, embedding chất lượng cao |
| ONNX Runtime | Chạy mô hình AI | Hỗ trợ CPU tốt |
| SQLite | Lưu trữ | Nhẹ, không cần server |

## Ngưỡng nhận diện

- Mô hình: buffalo_sc (InsightFace)
- Metric: Cosine similarity (0-1)
- Ngưỡng mặc định: 0.45
- Điều chỉnh: 0.35 (dễ nhận hơn) đến 0.65 (nghiêm ngặt hơn)

## Lưu ý bảo mật

- `face_embedding` là dữ liệu sinh trắc học nhạy cảm
- Không hiển thị raw embedding trong UI hoặc log
- File database cần được mã hóa trước khi deploy thực tế
- Prototype này CHƯA có liveness detection

## Quy trình kết thúc phiên làm việc

1. Kiểm tra các thay đổi đã thực hiện
2. Chạy những bài kiểm thử phù hợp
3. Ghi lại kết quả kiểm thử thực tế
4. Cập nhật TASKS.md
5. Cập nhật CURRENT_STATE.md với bước tiếp theo chính xác
6. Cập nhật PLAN.md nếu trạng thái giai đoạn thay đổi
7. Cập nhật CHANGELOG.md khi có thay đổi đáng kể
8. Cập nhật README.md nếu cách cài đặt/sử dụng thay đổi
