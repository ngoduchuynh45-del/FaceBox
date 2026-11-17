# VERSIONS.md — Nhật ký phiên bản FaceBox

Tuân thủ quy tắc Semantic Versioning (MAJOR.MINOR.PATCH).

---

## [1.3.1] — 2026-11-17
### Hoàn Thiện Cấu Hình Đóng Gói Độc Lập & Bảo Vệ Dữ Liệu Phát Hành
- **Cấu hình PyInstaller chuẩn hóa (`FaceBox.spec`)**:
  - Chuyển `PROJ_DIR` sang sử dụng biến `SPECPATH` chuẩn của PyInstaller, loại bỏ lỗi tìm tài nguyên khi gọi lệnh từ thư mục ngoài.
  - Bổ sung khai báo đầy đủ toàn bộ hidden imports cho `PySide6`, `cv2`, `numpy`, `sqlite3`, `PIL` và tất cả các submodule trong `ui/`, `services/`, `database/`.
  - Bổ sung danh sách excludes tối ưu: `scipy`, `pandas`, `unittest`, `IPython`... giúp tinh gọn kích thước bản phát hành.
- **Chuẩn hóa kết nối Database (`database/db_manager.py`)**:
  - Loại bỏ hoàn toàn dòng gán đè kết nối tĩnh `conn = sqlite3.connect(DB_PATH)` trong `get_connection()`.
  - Tích hợp tự động khởi tạo 30 ngăn tủ mặc định sạch (10 size S, 15 size M, 5 size L) khi database được tạo mới lần đầu.
  - Chuyển toàn bộ câu lệnh log về sử dụng `get_db_path()` động từ `path_service.py`.
- **Cơ chế phát hành Database sạch (`scripts/init_release_db.py`, `scripts/copy_db_to_dist.ps1`)**:
  - Không sao chép database thử nghiệm của lập trình viên vào bản phân phối; loại bỏ 100% nguy cơ rò rỉ dữ liệu tài khoản và vector khuôn mặt cá nhân.
  - Cung cấp script tự động tạo database phát hành sạch với 30 ngăn tủ mặc định sẵn sàng sử dụng.
- **Portable Launcher & Khởi chạy linh hoạt (`scripts/create_launcher.py`)**:
  - Loại bỏ các đường dẫn ổ đĩa và thư mục tuyệt đối bị hardcode.
  - Bổ sung file launcher di động `FaceBox_Launcher.vbs` tự động xác định vị trí thư mục hiện tại qua `WScript.ScriptFullName`, hoạt động ổn định khi người dùng di chuyển thư mục sang ổ đĩa khác.
  - Ứng dụng hỗ trợ khởi chạy trực tiếp bằng cách nhấn đúp vào `FaceBox.exe` mà không cần launcher.
- **Bộ cài đặt chuyên nghiệp Inno Setup 6 (`FaceBox_v1.3.1_Setup_x64.exe` ~107.01 MB)**:
  - Tự động đóng gói và giải nén toàn bộ ứng dụng bằng thuật toán nén `lzma2/ultra64`.
  - Tích hợp biểu tượng chính thức `assets/FaceBox.ico` cho bộ cài, ứng dụng và shortcut.
  - Hỗ trợ tạo Desktop Shortcut và Start Menu Shortcut.
  - Tích hợp trình gỡ cài đặt (Uninstaller), cam kết bảo toàn nguyên vẹn 100% dữ liệu người dùng tại `%LOCALAPPDATA%\FaceBox`.
- **Gói phân phối Portable ZIP (`FaceBox_v1.3.1_Portable_x64.zip` ~144.29 MB)**:
  - Đóng gói toàn bộ runtime, mô hình AI ONNX, Qt platform plugins.
  - Người dùng tải về giải nén và nhấn đúp chạy ngay, không cần cài đặt Python.
- **Cập nhật tài liệu hướng dẫn (`README.md`)**:
  - Hướng dẫn toàn diện 12 mục dành cho người dùng và lập trình viên.
  - Hướng dẫn cài đặt Setup EXE, Portable ZIP, xử lý lỗi quyền camera, SmartScreen và VC++ Redistributable.

---

## [1.3.0] — 2026-11-14
### Đóng Gói Thành Ứng Dụng Windows Độc Lập (PyInstaller onedir)
- **Tạo `services/path_service.py`**: Xử lý `get_resource_path()`, `get_data_dir()`, `get_db_path()`, `get_log_dir()`, `get_models_dir()`, hỗ trợ cả chế độ dev và chế độ PyInstaller frozen (`sys._MEIPASS`).
- **Cập nhật `services/face_recognition_service.py`**: Dùng `path_service.get_models_dir()` để nạp model YuNet/SFace — hoạt động khi app đóng gói.
- **Cập nhật `database/db_manager.py`**: Dùng `path_service.get_db_path()` và `get_resource_path('database/schema.sql')` — đảm bảo SQLite không mất dữ liệu khi chạy từ dist/.
- **Tạo `assets/FaceBox.ico` và `assets/FaceBox.png`**: Icon đa độ phân giải (16/32/48/64/128/256px), thiết kế camera phẳng vàng-đen phong cách Industrial.
- **Cập nhật `main.py`**: Bổ sung Single-Instance Mutex (`QSharedMemory`), Splash Screen công nghiệp, `sys.excepthook` với dialog lỗi và file log qua `path_service`.
- **Tạo `FaceBox.spec`**: Cấu hình PyInstaller `onedir`, `console=False`, đóng gói `models/`, `database/schema.sql`, `assets/`.
- **Build thành công**: `dist\FaceBox\FaceBox.exe` (~6.15 MB) + `_internal\` với toàn bộ thư viện.
- **Copy DB**: `data/facebox.db` → `dist/FaceBox/data/facebox.db` (giữ nguyên dữ liệu người dùng).
- **Tạo launcher Desktop**: `FaceBox.vbs` trên Desktop — nhấn đúp để mở app, không hiện cửa sổ CMD.
- **Chưa kiểm thử**: Chạy thủ công `FaceBox.exe` và xác minh camera/AI/SQLite (cần chạy thực tế).

---

## [1.2.1] — 2026-11-14
### Tối Ưu Typography & Bố Cục Văn Bản (UI Text Layout)
- **Khắc phục lỗi ép chữ nút 'Quay về Kiosk' & Sidebar Admin**:
  - Mở rộng chiều rộng sidebar Admin từ `210px` lên `235px` chuẩn tỷ lệ vàng.
  - Tách nút `btn_return_kiosk` khỏi QSS `#nav_btn`, cấu hình padding `8px 12px` và margin `6px 10px`, căn giữa sắc nét text `◀  QUAY VỀ KIOSK` (font 13px weight 900), hoàn toàn không bị co hẹp hoặc cắt thành `...`.
  - Điều chỉnh font-size 7 nút điều hướng sidebar về `13.5px` và padding `10px 12px`, đảm bảo các nhãn dài như "Nhận Diện Trực Tiếp", "Đăng Ký Khuôn Mặt" hiển thị trọn vẹn 100% trên 1 dòng.
- **Nâng cấp Hộp thoại Nhập mã PIN Quản trị (AdminLoginDialog)**:
  - Tăng kích thước hộp thoại từ `420x540px` lên `450x590px`, loại bỏ tình trạng tràn layout/đè chữ.
  - Đồng bộ màu sắc tự động theo bảng màu Dark/Light Mode, tránh lỗi chữ tàng hình trên nền tối.
  - Tinh chỉnh TouchNumericKeypad (chiều cao phím số 52px trong dialog) và căn giữa nút bánh răng `⚙️`.
- **Tối ưu các nút thao tác & Bảng dữ liệu**:
  - Rút gọn nhãn 2 nút xóa trong trang Quản lý tài khoản: `"🗑️  Xóa mẫu chọn"` và `"🗑️  Xóa tất cả"`, hiển thị vừa vặn trong panel 350px mà không bị tràn viền.
  - Mở rộng cột ID trong Bảng lịch sử lên 70px và `minimumSectionSize` lên 70px để header và icon sort không bị đè nhau.
  - Cải tiến nút Camera trên Dashboard: cập nhật nhãn qua đối tượng label nội bộ, loại bỏ lỗi vẽ chữ đè lên nhau.
  - Mở rộng AddLockerDialog lên `380x240px` và cố định chiều rộng nhãn 90px để các ô nhập liệu thẳng hàng tắp.
  - Chuẩn hóa hệ thống font: `FONT_FAMILY = '"Segoe UI", Tahoma, Arial, sans-serif'` hỗ trợ tiếng Việt toàn diện, không lỗi dấu.

---

## [1.2.0] — 2026-11-13
### Redesign Toàn Bộ Giao Diện — Industrial / Modern Smart Locker (InPost & Locker & Lock)
- **Hệ thống Thiết kế (Design System & Theme)**:
  - Bảng màu công nghiệp chuẩn InPost & Smart Locker: Primary Yellow (`#FFD500`), Primary Black (`#171717`), Light Background (`#F2F2F2`), Dark Surface (`#252525`), Dark Border (`#3A3A3A`), Success (`#16A36A`), Error (`#D94848`).
  - Hình khối vuông vức công nghiệp: `border-radius: 0–2px` trên toàn bộ hệ thống (cards, buttons, inputs, dialogs, tables).
  - Hỗ trợ chuyển đổi **Light Mode** và **Dark Mode** tức thì qua `ThemeManager`, đồng bộ cho cả Kiosk và Admin mode.
- **Logo Thương Hiệu Công Nghiệp Mới**:
  - Logo máy ảnh trực diện phẳng: Thân máy vàng `#FFD500`, viền đen `#171717`, bên trong ống kính là một hộp kiện hàng hình vuông (Square Package Box) có băng keo nắp hộp viền đen.
  - Đi kèm dòng chữ FaceBox phong cách công nghiệp và nhãn badge "SMART LOCKER".
- **Giao diện Kiosk Mode**:
  - `WelcomePage`: Tiêu đề chào mừng, logo thương hiệu lớn, 2 nút công nghiệp cực đại nổi bật: **LẤY HÀNG** (nền Vàng chữ Đen) và **GỬI HÀNG** (nền Đen chữ Vàng).
  - `AuthChoicePage`: Nút quét khuôn mặt và nhập số điện thoại độ tương phản cao, badge trạng thái hành động rõ ràng.
  - `PhoneInputPage`: Hiển thị số điện thoại lớn, bàn phím số cảm ứng viền vuông 2px màu vàng/đen công nghiệp.
  - `FaceScanPage`: Khung nhận diện elip giữ nguyên tỷ lệ $W/H = 0.72$ bất biến, thẻ trạng thái hướng dẫn dạng dark pill sắc nét.
  - `SendItemPage`: Các ô chọn kích cỡ tủ S/M/L viền khối công nghiệp, hiển thị trực tiếp số ngăn trống từ database.
  - `PickupItemPage`: Danh sách kiện hàng trực quan, tự động chọn kiện hàng, hiển thị mã ngăn tủ nổi bật.
  - `CompletePage`: Hộp thông tin mở tủ viền vàng công nghiệp, nút bấm quay lại màn hình chính sắc sảo.
- **Giao diện Admin Mode**:
  - Tích hợp `FaceBoxLogo` vào Sidebar quản trị với badge định danh.
  - Áp dụng styling vuông vức công nghiệp cho Dashboard, Đăng Ký, Nhận Diện, Quản Lý Tài Khoản, Quản Lý Tủ, Lịch Sử và Cài Đặt.
  - Bổ sung công tắc chọn Theme Light/Dark trong trang Cài Đặt và nút Đăng Xuất quay về Kiosk.
- **Bảo toàn lõi kỹ thuật**:
  - Giữ nguyên 100% thuật toán YuNet (phát hiện) và SFace (nhận diện).
  - Giữ nguyên ngưỡng Cosine Similarity 0.363 chuẩn OpenCV Model Zoo.
  - Giữ nguyên cơ sở dữ liệu SQLite và cấu trúc bảng `lockers`, `packages`, `open_history`.

---

## [1.1.0] — 2026-11-13
### Thay đổi chính & Tính năng mới
- **Kiosk & Admin Mode song song**: Tách biệt hoàn toàn giao diện phục vụ khách hàng (Kiosk) và giao diện quản trị (Admin) thông qua bộ điều phối `AppController`.
- **Admin Sidebar 7 mục**: Mở rộng từ 4 lên 7 mục chức năng:
  1. 🏠 Tổng Quan (Dashboard) với StatCard thời gian thực về tài khoản, khuôn mặt, camera và ngăn tủ.
  2. 👤 Đăng Ký Khuôn Mặt (Registration).
  3. 🔍 Nhận Diện Trực Tiếp (Recognition).
  4. 👥 Quản Lý Tài Khoản (Accounts).
  5. 📋 Lịch Sử Gửi/Nhận (History) — Tra cứu, lọc theo số điện thoại và khoảng thời gian.
  6. 🗄️ Quản Lý Tủ (Locker Management) — Hiển thị sơ đồ lưới ngăn tủ trực quan, phân loại kích cỡ (S/M/L), trạng thái (Trống/Đang dùng/Lỗi), thêm ngăn tủ mới.
  7. ⚙️ Cài Đặt (Settings) — Tinh chỉnh ngưỡng Cosine Distance, tốc độ FPS, số frame xác nhận, camera, đổi mật khẩu và thông tin hệ thống.
- **Mở rộng Cơ sở dữ liệu SQLite**:
  - Bổ sung bảng `lockers`, `packages`, `open_history` với khóa ngoại và index tối ưu.
  - Tích hợp CRUD operations đầy đủ cho cả 3 bảng mới vào `db_manager.py`.
- **Liên kết nghiệp vụ Kiosk ↔ Database**:
  - Gửi hàng (`SendItemPage`): Tự động tìm ngăn tủ trống theo size, cập nhật trạng thái ngăn tủ sang `occupied`, lưu bản ghi kiện hàng và nhật ký mở tủ.
  - Lấy hàng (`PickupItemPage`): Tự động hiển thị danh sách các kiện hàng đang lưu trữ của người dùng, giải phóng ngăn tủ về `empty` sau khi lấy, lưu nhật ký mở tủ.
- **Chuẩn hóa Khung elip nhận diện**:
  - Giữ nguyên tỷ lệ elip 0.72 trên mọi độ phân giải.
  - Phản hồi 6 trạng thái trực quan và đồng bộ thuật toán đánh giá góc mặt trên toàn bộ các màn hình.

### Sửa lỗi & Tối ưu
- Sửa lỗi nạp mô hình YuNet/SFace qua đường dẫn tiếng Việt có dấu trên Windows (dùng binary buffer).
- Chuẩn hóa Singleton `CameraService` tránh xung đột luồng và giải quyết triệt để lỗi màn hình đăng ký báo chưa bật camera.

---

## [1.0.0] — 2026-10-23
### Khởi tạo Prototype FaceBox
- Khởi tạo kiến trúc ứng dụng desktop PySide6 / Qt6.
- Tích hợp mô hình AI OpenCV YuNet (phát hiện khuôn mặt) và SFace (sinh embedding 128 chiều).
- Khởi tạo cơ sở dữ liệu SQLite ban đầu với 2 bảng `accounts` và `face_profiles`.
- Xây dựng 4 màn hình Admin cơ bản: Dashboard, Đăng Ký, Nhận Diện, Quản Lý Tài Khoản.

