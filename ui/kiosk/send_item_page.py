"""
FaceBox — Kiosk Send Item Page
Màn hình 5: Chọn kích thước ngăn tủ để gửi hàng.
- Hiển thị lựa chọn tủ: Nhỏ (Small), Vừa (Medium), Lớn (Large).
- Hiển thị thông số kích thước và trạng thái số lượng tủ khả dụng.
- ĐIỂM TÍCH HỢP HỆ THỐNG:
  * Backend hiện tại chưa có bảng CSDL 'lockers' và bộ điều khiển phần cứng thật.
  * Màn hình thể hiện giao diện nghiệp vụ chuẩn, chuẩn bị sẵn API chọn tủ gần nhất.
  * KHÔNG giả lập mở tủ thành công khi chưa có phần cứng thật (tuân thủ nguyên tắc bắt buộc).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QButtonGroup, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from ui.components import KioskHeader
from ui import theme
from database import db_manager


class SendItemPage(QWidget):
    """Màn hình chọn ngăn tủ gửi hàng."""

    back_clicked = Signal()
    admin_requested = Signal()
    send_confirmed = Signal(dict)   # Phát kết quả chọn tủ: {'size': ..., 'account': ...}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("kiosk_page")
        self._current_account = None
        self._selected_size = "medium"  # Mặc định ngăn Vừa
        self._setup_ui()

    def set_account(self, account_info: dict):
        """Nhận thông tin tài khoản đã xác thực."""
        self._current_account = account_info
        phone = account_info.get("phone_number", "")
        self.user_badge.setText(f"👤 Tài khoản: {phone}")
        self._refresh_slots()

    def _refresh_slots(self):
        """Cập nhật số lượng ngăn tủ trống thực tế từ database."""
        try:
            counts = db_manager.get_available_locker_counts_by_size()
            s_cnt = counts.get('S', 0)
            m_cnt = counts.get('M', 0)
            l_cnt = counts.get('L', 0)

            if hasattr(self, 'card_small') and hasattr(self.card_small, 'slot_badge'):
                self.card_small.slot_badge.setText(f"Còn {s_cnt} ngăn trống")
                self.card_small.setEnabled(s_cnt > 0)
            if hasattr(self, 'card_med') and hasattr(self.card_med, 'slot_badge'):
                self.card_med.slot_badge.setText(f"Còn {m_cnt} ngăn trống")
                self.card_med.setEnabled(m_cnt > 0)
            if hasattr(self, 'card_large') and hasattr(self.card_large, 'slot_badge'):
                self.card_large.slot_badge.setText(f"Còn {l_cnt} ngăn trống")
                self.card_large.setEnabled(l_cnt > 0)

            # Nếu size hiện tại hết chỗ, tự động chọn size còn chỗ
            if self._selected_size == "small" and s_cnt == 0:
                if m_cnt > 0:
                    self._select_size("medium")
                elif l_cnt > 0:
                    self._select_size("large")
            elif self._selected_size == "medium" and m_cnt == 0:
                if s_cnt > 0:
                    self._select_size("small")
                elif l_cnt > 0:
                    self._select_size("large")
            elif self._selected_size == "large" and l_cnt == 0:
                if m_cnt > 0:
                    self._select_size("medium")
                elif s_cnt > 0:
                    self._select_size("small")
        except Exception as e:
            pass

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 16, 32, 28)
        layout.setSpacing(14)

        # Header
        self.header = KioskHeader(show_back=True)
        self.header.back_clicked.connect(self.back_clicked.emit)
        self.header.gear_clicked.connect(self.admin_requested.emit)
        layout.addWidget(self.header)

        # Thông tin tài khoản
        self.user_badge = QLabel("👤 TÀI KHOẢN: --")
        self.user_badge.setAlignment(Qt.AlignCenter)
        self.user_badge.setStyleSheet(
            "background-color: #FFD500; color: #171717; "
            "border: 2px solid #171717; border-radius: 2px; "
            "padding: 6px 20px; font-size: 15px; font-weight: 900; letter-spacing: 0.5px;"
        )
        layout.addWidget(self.user_badge, alignment=Qt.AlignCenter)

        # Tiêu đề
        title = QLabel("Chọn kích thước ngăn tủ phù hợp")
        title.setObjectName("kiosk_title")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("Hệ thống sẽ tự động gán ngăn tủ trống gần nhất theo kích thước bạn chọn")
        sub.setObjectName("kiosk_subtitle")
        sub.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(16)

        # Danh sách 3 kích cỡ tủ: Nhỏ, Vừa, Lớn
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # Tủ Nhỏ
        self.card_small = self._create_size_card(
            size_id="small",
            icon="✉️",
            title="NGĂN NHỎ (S)",
            dimensions="Phù hợp: Tài liệu, chìa khóa, điện thoại, bưu thiếp",
            spec="Kích thước: 15 × 30 × 45 cm",
            slots_available="Còn 4 ngăn trống"
        )

        # Tủ Vừa (Khuyến nghị)
        self.card_med = self._create_size_card(
            size_id="medium",
            icon="🎒",
            title="NGĂN VỪA (M)",
            dimensions="Phù hợp: Ba lô, hộp giày, quần áo, mũ bảo hiểm",
            spec="Kích thước: 30 × 30 × 45 cm",
            slots_available="Còn 6 ngăn trống",
            is_default=True
        )

        # Tủ Lớn
        self.card_large = self._create_size_card(
            size_id="large",
            icon="🧳",
            title="NGĂN LỚN (L)",
            dimensions="Phù hợp: Vali kéo nhỏ, thùng carton, túi đồ lớn",
            spec="Kích thước: 45 × 40 × 45 cm",
            slots_available="Còn 2 ngăn trống"
        )

        cards_layout.addWidget(self.card_small)
        cards_layout.addWidget(self.card_med)
        cards_layout.addWidget(self.card_large)
        layout.addLayout(cards_layout, stretch=1)

        layout.addSpacing(16)

        # Ghi chú kỹ thuật về phần cứng
        notice_box = QFrame()
        notice_box.setObjectName("card")
        notice_box_layout = QHBoxLayout(notice_box)
        notice_box_layout.setContentsMargins(16, 10, 16, 10)

        icon_notice = QLabel("ℹ️")
        icon_notice.setStyleSheet("font-size: 20px;")
        lbl_notice = QLabel(
            "<b>Lưu ý tích hợp:</b> Hệ thống đang chạy ở chế độ mô phỏng phần mềm. "
            "Tín hiệu mở chốt điện tử sẽ kích hoạt khi kết nối với bộ điều khiển phần cứng thực tế."
        )
        lbl_notice.setStyleSheet(f"font-size: 13px; color: {theme.colors().text_secondary};")
        lbl_notice.setWordWrap(True)

        notice_box_layout.addWidget(icon_notice)
        notice_box_layout.addWidget(lbl_notice, stretch=1)
        layout.addWidget(notice_box)

        # Nút xác nhận gửi hàng
        self.btn_confirm = QPushButton("XÁC NHẬN CHỌN NGĂN TỦ NÀY →")
        self.btn_confirm.setObjectName("btn_primary")
        self.btn_confirm.setFixedHeight(58)
        self.btn_confirm.setCursor(Qt.PointingHandCursor)
        self.btn_confirm.setStyleSheet(
            "font-size: 18px; font-weight: 900; border-radius: 2px; "
            "background-color: #FFD500; color: #171717; border: 2px solid #171717;"
        )
        self.btn_confirm.clicked.connect(self._on_confirm_send)
        layout.addWidget(self.btn_confirm)

    def _create_size_card(self, size_id: str, icon: str, title: str,
                          dimensions: str, spec: str, slots_available: str,
                          is_default: bool = False) -> QPushButton:
        """Tạo card kích thước tủ phong cách industrial locker."""
        btn = QPushButton()
        btn.setObjectName("kiosk_action")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.setCheckable(True)
        btn.setChecked(is_default)
        btn.setStyleSheet("""
            QPushButton {
                border-radius: 2px;
                border: 2px solid #D1D1D1;
                background-color: #FFFFFF;
            }
            QPushButton:hover {
                border-color: #FFD500;
            }
            QPushButton:checked {
                border: 3px solid #FFD500;
                background-color: #FFFDF0;
            }
        """)

        layout = QVBoxLayout(btn)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 40px; background: transparent; border: none;")
        icon_lbl.setAlignment(Qt.AlignCenter)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: 900; background: transparent; border: none; color: #171717;")
        title_lbl.setAlignment(Qt.AlignCenter)

        dim_lbl = QLabel(dimensions)
        dim_lbl.setStyleSheet("font-size: 13px; color: #4A4A4A; background: transparent; border: none;")
        dim_lbl.setAlignment(Qt.AlignCenter)
        dim_lbl.setWordWrap(True)

        spec_lbl = QLabel(spec)
        spec_lbl.setStyleSheet("font-size: 12px; color: #787878; font-weight: bold; background: transparent; border: none;")
        spec_lbl.setAlignment(Qt.AlignCenter)

        slot_badge = QLabel(slots_available)
        slot_badge.setStyleSheet(
            "background-color: #E8F8F0; color: #16A36A; border: 1px solid #16A36A; "
            "border-radius: 2px; padding: 4px 10px; font-size: 12px; font-weight: bold;"
        )
        slot_badge.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(dim_lbl)
        layout.addWidget(spec_lbl)
        layout.addWidget(slot_badge)

        btn.slot_badge = slot_badge

        btn.clicked.connect(lambda: self._select_size(size_id))
        return btn

    def _select_size(self, size_id: str):
        self._selected_size = size_id
        self.card_small.setChecked(size_id == "small")
        self.card_med.setChecked(size_id == "medium")
        self.card_large.setChecked(size_id == "large")

    def _on_confirm_send(self):
        """Phát tín hiệu xác nhận chọn ngăn tủ và lưu giao dịch vào DB."""
        size_map = {"small": "S", "medium": "M", "large": "L"}
        target_size = size_map.get(self._selected_size, "M")

        # Tìm ngăn tủ trống thực tế từ DB
        locker = db_manager.get_available_locker(target_size)
        if not locker:
            QMessageBox.warning(
                self, "Tất cả các tủ đều đầy",
                f"Hiện tại không còn ngăn tủ trống nào cho kích thước đã chọn ({target_size}).\n"
                "Vui lòng chọn kích thước khác hoặc liên hệ quản trị viên."
            )
            return

        # Xác định account_id
        account_id = None
        if self._current_account:
            account_id = self._current_account.get("id")
            if not account_id and "phone_number" in self._current_account:
                acc = db_manager.get_account_by_phone(self._current_account["phone_number"])
                if acc:
                    account_id = acc["id"]

        locker_num = locker["locker_number"]
        locker_id = locker["id"]

        # Ghi nhận package vào database
        pkg_id = None
        if account_id:
            ok, msg, pkg_id = db_manager.create_package(
                account_id=account_id,
                locker_id=locker_id,
                action="send",
                note=f"Gửi hàng tại Kiosk (size {target_size})"
            )
            # Ghi lịch sử mở tủ
            method = self._current_account.get("method", "face") if self._current_account else "face"
            db_manager.log_open_history(
                account_id=account_id,
                locker_id=locker_id,
                action="send",
                method=method
            )

        self.send_confirmed.emit({
            "action": "send",
            "size": self._selected_size,
            "account": self._current_account,
            "hardware_connected": False,
            "locker_number": f"#{locker_num}",
            "package_id": pkg_id
        })
