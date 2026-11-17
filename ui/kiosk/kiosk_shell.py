"""
FaceBox — Kiosk Shell
Widget chính điều phối toàn bộ các màn hình trong chế độ Kiosk:
  - Trang 0: WelcomePage
  - Trang 1: TransactionChoicePage
  - Trang 2: AuthChoicePage
  - Trang 3: FaceScanPage
  - Trang 4: PhoneInputPage
  - Trang 5: SendItemPage
  - Trang 6: PickupItemPage
  - Trang 7: CompletePage

Đảm bảo luồng giao dịch khép kín, phân phối frame camera và hỗ trợ chuyển sang Admin.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt, Signal
import numpy as np
import logging

from ui.kiosk.welcome_page import WelcomePage
from ui.kiosk.transaction_choice_page import TransactionChoicePage
from ui.kiosk.auth_choice_page import AuthChoicePage
from ui.kiosk.face_scan_page import FaceScanPage
from ui.kiosk.phone_input_page import PhoneInputPage
from ui.kiosk.send_item_page import SendItemPage
from ui.kiosk.pickup_item_page import PickupItemPage
from ui.kiosk.complete_page import CompletePage
from ui.admin.login_page import AdminLoginDialog

logger = logging.getLogger("facebox.kiosk.shell")

PAGE_WELCOME     = 0
PAGE_TX_CHOICE   = 1
PAGE_AUTH_CHOICE = 2
PAGE_FACE_SCAN   = 3
PAGE_PHONE_INPUT = 4
PAGE_SEND_ITEM   = 5
PAGE_PICKUP_ITEM = 6
PAGE_COMPLETE    = 7


class KioskShell(QWidget):
    """Giao diện Kiosk dành cho người dùng tại cây tủ FaceBox."""

    admin_login_requested = Signal()  # Phát khi đăng nhập admin thành công

    def __init__(self, face_service, camera_service, parent=None):
        super().__init__(parent)
        self.setObjectName("kiosk_page")
        self.face_service = face_service
        self.camera_service = camera_service

        self._current_action = "send"  # 'send' hoặc 'pickup'
        self._current_account = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()

        # Khởi tạo 8 trang giao diện của Kiosk
        self.welcome_page = WelcomePage()
        self.tx_choice_page = TransactionChoicePage()
        self.auth_choice_page = AuthChoicePage()
        self.face_scan_page = FaceScanPage(self.face_service, self.camera_service)
        self.phone_input_page = PhoneInputPage()
        self.send_item_page = SendItemPage()
        self.pickup_item_page = PickupItemPage()
        self.complete_page = CompletePage()

        self.stack.addWidget(self.welcome_page)      # 0
        self.stack.addWidget(self.tx_choice_page)    # 1
        self.stack.addWidget(self.auth_choice_page)  # 2
        self.stack.addWidget(self.face_scan_page)    # 3
        self.stack.addWidget(self.phone_input_page)  # 4
        self.stack.addWidget(self.send_item_page)    # 5
        self.stack.addWidget(self.pickup_item_page)  # 6
        self.stack.addWidget(self.complete_page)     # 7

        layout.addWidget(self.stack)
        self.go_to_welcome()

    def _connect_signals(self):
        # 1. Welcome -> Tx Choice hoặc trực tiếp vào Gửi/Lấy hàng
        self.welcome_page.start_clicked.connect(lambda: self.stack.setCurrentIndex(PAGE_TX_CHOICE))
        self.welcome_page.pickup_clicked.connect(lambda: self._start_tx("pickup"))
        self.welcome_page.send_clicked.connect(lambda: self._start_tx("send"))
        self.welcome_page.admin_requested.connect(self._prompt_admin)

        # 2. Tx Choice
        self.tx_choice_page.back_clicked.connect(self.go_to_welcome)
        self.tx_choice_page.admin_requested.connect(self._prompt_admin)
        self.tx_choice_page.send_selected.connect(lambda: self._start_tx("send"))
        self.tx_choice_page.pickup_selected.connect(lambda: self._start_tx("pickup"))

        # 3. Auth Choice
        self.auth_choice_page.back_clicked.connect(self.go_to_welcome)
        self.auth_choice_page.admin_requested.connect(self._prompt_admin)
        self.auth_choice_page.face_auth_selected.connect(self._start_face_auth)
        self.auth_choice_page.phone_auth_selected.connect(self._start_phone_auth)

        # 4. Face Scan
        self.face_scan_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(PAGE_AUTH_CHOICE))
        self.face_scan_page.admin_requested.connect(self._prompt_admin)
        self.face_scan_page.switch_to_phone.connect(self._start_phone_auth)
        self.face_scan_page.authenticated.connect(self._on_authenticated)

        # 5. Phone Input
        self.phone_input_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(PAGE_AUTH_CHOICE))
        self.phone_input_page.admin_requested.connect(self._prompt_admin)
        self.phone_input_page.switch_to_face.connect(self._start_face_auth)
        self.phone_input_page.authenticated.connect(self._on_authenticated)

        # 6. Send Item
        self.send_item_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(PAGE_AUTH_CHOICE))
        self.send_item_page.admin_requested.connect(self._prompt_admin)
        self.send_item_page.send_confirmed.connect(self._on_transaction_completed)

        # 7. Pickup Item
        self.pickup_item_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(PAGE_AUTH_CHOICE))
        self.pickup_item_page.admin_requested.connect(self._prompt_admin)
        self.pickup_item_page.pickup_confirmed.connect(self._on_transaction_completed)

        # 8. Complete
        self.complete_page.home_clicked.connect(self.go_to_welcome)

    def _start_tx(self, action: str):
        self._current_action = action
        action_name = "GỬI HÀNG" if action == "send" else "LẤY HÀNG"
        self.auth_choice_page.set_action_type(action_name)
        self.phone_input_page.set_action_type(action_name)
        self.stack.setCurrentIndex(PAGE_AUTH_CHOICE)

    def _start_face_auth(self):
        # Mở camera nếu camera chưa chạy
        if not self.camera_service.is_running():
            self.camera_service.start()
        self.stack.setCurrentIndex(PAGE_FACE_SCAN)

    def _start_phone_auth(self):
        self.stack.setCurrentIndex(PAGE_PHONE_INPUT)

    def _on_authenticated(self, account_data: dict):
        """Xử lý khi người dùng xác thực thành công qua khuôn mặt hoặc số điện thoại."""
        self._current_account = account_data
        logger.info(f"[Kiosk] Người dùng xác thực thành công: {account_data.get('phone_number')} (phương thức: {account_data.get('method')})")

        if self._current_action == "send":
            self.send_item_page.set_account(account_data)
            self.stack.setCurrentIndex(PAGE_SEND_ITEM)
        else:
            self.pickup_item_page.set_account(account_data)
            self.stack.setCurrentIndex(PAGE_PICKUP_ITEM)

    def _on_transaction_completed(self, result_data: dict):
        """Chuyển đến màn hình hoàn tất giao dịch."""
        self.complete_page.set_result(result_data)
        self.stack.setCurrentIndex(PAGE_COMPLETE)

    def go_to_welcome(self):
        """Đặt lại trạng thái và về trang Welcome."""
        self._current_account = None
        self.stack.setCurrentIndex(PAGE_WELCOME)

    def update_frame(self, frame: np.ndarray):
        """Phân phối frame từ camera đến trang quét khuôn mặt nếu trang đó đang mở."""
        if self.stack.currentIndex() == PAGE_FACE_SCAN:
            self.face_scan_page.update_frame(frame)

    def _prompt_admin(self):
        """Mở hộp thoại nhập mật khẩu quản trị."""
        dlg = AdminLoginDialog(self)
        dlg.login_success.connect(self.admin_login_requested.emit)
        dlg.exec()

