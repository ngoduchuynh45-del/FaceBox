"""
FaceBox — Kiosk Pickup Item Page
Màn hình 6: Lấy hàng từ ngăn tủ dành cho tài khoản đã xác thực.
- Tra cứu danh sách các ngăn tủ đang chứa hàng thuộc về tài khoản.
- Không cho phép chọn ngăn tủ trống.
- Tuân thủ nguyên tắc: Không tạo dữ liệu giả, phân biệt rõ điểm tích hợp database.
  Nếu chưa có bảng giao dịch/hàng hóa, hiển thị thông báo trạng thái trung thực
  và cung cấp điểm tích hợp sạch cho backend tương lai.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QListWidget, QListWidgetItem, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from ui.components import KioskHeader
from ui import theme
from database import db_manager


class PickupItemPage(QWidget):
    """Màn hình lấy hàng Kiosk."""

    back_clicked = Signal()
    admin_requested = Signal()
    pickup_confirmed = Signal(dict)   # Phát kết quả: {'action': 'pickup', 'locker_number': ..., ...}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("kiosk_page")
        self._current_account = None
        self._selected_locker = None
        self._setup_ui()

    def set_account(self, account_info: dict):
        """Nhận thông tin tài khoản và kiểm tra đơn hàng/tủ chứa đồ."""
        self._current_account = account_info
        phone = account_info.get("phone_number", "")
        self.user_badge.setText(f"👤 Tài khoản: {phone}")

        # Kiểm tra logic lưu trữ hàng hóa
        self._load_pending_lockers(account_info)

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
        title = QLabel("Kiểm tra kiện hàng của bạn")
        title.setObjectName("kiosk_title")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("Danh sách các ngăn tủ đang lưu trữ hàng thuộc số điện thoại của bạn")
        sub.setObjectName("kiosk_subtitle")
        sub.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(12)

        # Khu vực hiển thị danh sách ngăn tủ chứa hàng
        self.container_box = QFrame()
        self.container_box.setObjectName("card")
        self.container_layout = QVBoxLayout(self.container_box)
        self.container_layout.setContentsMargins(24, 24, 24, 24)
        self.container_layout.setSpacing(16)

        # Widget trạng thái khi chưa có kiện hàng
        self.empty_state_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_state_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(12)

        icon_box = QLabel("📭")
        icon_box.setStyleSheet("font-size: 54px; background: transparent;")
        icon_box.setAlignment(Qt.AlignCenter)

        self.empty_title = QLabel("Hiện không có kiện hàng nào cần lấy")
        self.empty_title.setStyleSheet("font-size: 20px; font-weight: bold; background: transparent;")
        self.empty_title.setAlignment(Qt.AlignCenter)

        self.empty_desc = QLabel(
            "Tài khoản của bạn chưa có kiện hàng nào đang lưu tại cây tủ này, "
            "hoặc toàn bộ hàng gửi trước đó đã được nhận hoàn tất."
        )
        self.empty_desc.setStyleSheet(f"font-size: 14px; color: {theme.colors().text_secondary}; background: transparent;")
        self.empty_desc.setAlignment(Qt.AlignCenter)
        self.empty_desc.setWordWrap(True)

        empty_layout.addWidget(icon_box)
        empty_layout.addWidget(self.empty_title)
        empty_layout.addWidget(self.empty_desc)
        self.container_layout.addWidget(self.empty_state_widget)

        # Scroll area chứa danh sách kiện hàng thực tế khi có
        self.package_scroll = QScrollArea()
        self.package_scroll.setWidgetResizable(True)
        self.package_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.package_list_widget = QWidget()
        self.package_list_layout = QVBoxLayout(self.package_list_widget)
        self.package_list_layout.setContentsMargins(0, 0, 0, 0)
        self.package_list_layout.setSpacing(12)
        self.package_scroll.setWidget(self.package_list_widget)
        self.package_scroll.setVisible(False)
        self.container_layout.addWidget(self.package_scroll)

        layout.addWidget(self.container_box, stretch=1)

        # Ghi chú về phần cứng
        notice_box = QFrame()
        notice_box.setObjectName("card")
        notice_box_layout = QHBoxLayout(notice_box)
        notice_box_layout.setContentsMargins(16, 10, 16, 10)

        icon_notice = QLabel("⚠️")
        icon_notice.setStyleSheet("font-size: 20px;")
        lbl_notice = QLabel(
            "<b>Nguyên tắc an toàn:</b> Hệ thống tuân thủ nghiêm ngặt bảo mật — "
            "không cho phép mở các ngăn tủ trống hoặc ngăn tủ của khách hàng khác."
        )
        lbl_notice.setStyleSheet(f"font-size: 13px; color: {theme.colors().text_secondary};")
        lbl_notice.setWordWrap(True)

        notice_box_layout.addWidget(icon_notice)
        notice_box_layout.addWidget(lbl_notice, stretch=1)
        layout.addWidget(notice_box)

        # Nút xác nhận lấy hàng (chỉ kích hoạt khi có tủ được chọn)
        self.btn_confirm_pickup = QPushButton("MỞ NGĂN TỦ LẤY HÀNG")
        self.btn_confirm_pickup.setObjectName("btn_primary")
        self.btn_confirm_pickup.setFixedHeight(58)
        self.btn_confirm_pickup.setCursor(Qt.PointingHandCursor)
        self.btn_confirm_pickup.setStyleSheet(
            "font-size: 18px; font-weight: 900; border-radius: 2px; "
            "background-color: #FFD500; color: #171717; border: 2px solid #171717;"
        )
        self.btn_confirm_pickup.setEnabled(False)
        self.btn_confirm_pickup.clicked.connect(self._on_confirm_pickup)
        layout.addWidget(self.btn_confirm_pickup)

    def _load_pending_lockers(self, account_info: dict):
        """Tra cứu các kiện hàng đang lưu của tài khoản từ database."""
        self._selected_package = None
        self.btn_confirm_pickup.setEnabled(False)
        self.btn_confirm_pickup.setText("MỞ NGĂN TỦ LẤY HÀNG")

        # Xóa các widget kiện hàng cũ
        while self.package_list_layout.count():
            item = self.package_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Lấy account_id
        account_id = account_info.get("id")
        if not account_id and "phone_number" in account_info:
            acc = db_manager.get_account_by_phone(account_info["phone_number"])
            if acc:
                account_id = acc["id"]

        packages = []
        if account_id:
            packages = db_manager.get_stored_packages_by_account(account_id)

        if not packages:
            self.empty_state_widget.setVisible(True)
            self.package_scroll.setVisible(False)
            return

        self.empty_state_widget.setVisible(False)
        self.package_scroll.setVisible(True)

        # Tạo card cho từng kiện hàng
        self._package_buttons = []
        for pkg in packages:
            btn = QPushButton()
            btn.setObjectName("kiosk_action")
            btn.setCheckable(True)
            btn.setFixedHeight(84)
            btn.setCursor(Qt.PointingHandCursor)

            hlay = QHBoxLayout(btn)
            hlay.setContentsMargins(20, 12, 20, 12)
            hlay.setSpacing(16)

            icon_lbl = QLabel("📦")
            icon_lbl.setStyleSheet("font-size: 32px; background: transparent; border: none;")

            info_lay = QVBoxLayout()
            info_lay.setSpacing(4)
            num_lbl = QLabel(f"Ngăn tủ #{pkg['locker_number']}  (Kích cỡ {pkg.get('size', 'M')})")
            num_lbl.setStyleSheet("font-size: 18px; font-weight: bold; background: transparent; border: none;")
            time_lbl = QLabel(f"Thời gian gửi: {pkg.get('created_at', '')}")
            time_lbl.setStyleSheet(f"font-size: 13px; color: {theme.colors().text_secondary}; background: transparent; border: none;")

            info_lay.addWidget(num_lbl)
            info_lay.addWidget(time_lbl)

            hlay.addWidget(icon_lbl)
            hlay.addLayout(info_lay, stretch=1)

            status_badge = QLabel("Chờ lấy")
            status_badge.setStyleSheet(
                "background-color: #DFFBE9; color: #16A36A; border: 1px solid #16A36A; "
                "border-radius: 2px; padding: 4px 10px; font-size: 13px; font-weight: bold;"
            )
            hlay.addWidget(status_badge)

            btn.clicked.connect(lambda checked, p=pkg, b=btn: self._select_package(p, b))
            self.package_list_layout.addWidget(btn)
            self._package_buttons.append(btn)

        # Tự động chọn kiện đầu tiên làm mặc định
        if packages:
            self._select_package(packages[0], self._package_buttons[0])

    def _select_package(self, pkg: dict, clicked_btn: QPushButton):
        self._selected_package = pkg
        for b in getattr(self, '_package_buttons', []):
            b.setChecked(b == clicked_btn)
        locker_num = pkg.get('locker_number', '?')
        self.btn_confirm_pickup.setEnabled(True)
        self.btn_confirm_pickup.setText(f"MỞ NGĂN TỦ #{locker_num} LẤY HÀNG →")

    def _on_confirm_pickup(self):
        """Xác nhận lấy hàng và cập nhật database."""
        if not self._selected_package:
            return

        pkg = self._selected_package
        pkg_id = pkg.get("id")
        locker_id = pkg.get("locker_id")
        locker_num = pkg.get("locker_number")

        account_id = None
        if self._current_account:
            account_id = self._current_account.get("id")
            if not account_id and "phone_number" in self._current_account:
                acc = db_manager.get_account_by_phone(self._current_account["phone_number"])
                if acc:
                    account_id = acc["id"]

        # Cập nhật trạng thái kiện hàng trong DB (giải phóng ngăn tủ)
        if pkg_id:
            db_manager.pickup_package(pkg_id)

        # Ghi log mở tủ
        method = self._current_account.get("method", "face") if self._current_account else "face"
        db_manager.log_open_history(
            account_id=account_id,
            locker_id=locker_id,
            action="receive",
            method=method
        )

        self.pickup_confirmed.emit({
            "action": "pickup",
            "account": self._current_account,
            "hardware_connected": False,
            "locker_number": f"#{locker_num}",
            "package_id": pkg_id
        })

