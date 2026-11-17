"""
FaceBox — Admin: Trang Lịch Sử Gửi/Nhận
Hiển thị lịch sử mở tủ với bộ lọc theo ngày và số điện thoại.
"""
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QDateEdit, QComboBox, QSizePolicy
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

from ui import theme
from database import db_manager

logger = logging.getLogger(__name__)

# Mapping hiển thị tiếng Việt
ACTION_LABELS = {
    'send': 'Gửi hàng',
    'receive': 'Nhận hàng',
    'admin_open': 'Admin mở',
}
METHOD_LABELS = {
    'face': 'Khuôn mặt',
    'pin': 'Mã PIN',
    'admin': 'Quản trị',
}


class HistoryPage(QWidget):
    """Trang lịch sử gửi/nhận hàng và mở tủ."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ── Header ──
        header = QHBoxLayout()
        title = QLabel("📋  Lịch Sử Gửi / Nhận")
        title.setStyleSheet(f"font-size: {theme.FONT_H1}px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        self.lbl_total = QLabel("Tổng: 0 bản ghi")
        self.lbl_total.setStyleSheet(f"font-size: {theme.FONT_SM}px; color: {theme.colors().text_muted};")
        header.addWidget(self.lbl_total)
        layout.addLayout(header)

        # ── Thanh bộ lọc ──
        filter_frame = QFrame()
        filter_frame.setObjectName("card")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(12)

        # Tìm theo SĐT
        filter_layout.addWidget(QLabel("SĐT:"))
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("Nhập số điện thoại...")
        self.txt_phone.setFixedWidth(180)
        filter_layout.addWidget(self.txt_phone)

        # Từ ngày
        filter_layout.addWidget(QLabel("Từ:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        filter_layout.addWidget(self.date_from)

        # Đến ngày
        filter_layout.addWidget(QLabel("Đến:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        filter_layout.addWidget(self.date_to)

        # Nút lọc
        btn_search = QPushButton("🔍  Tìm kiếm")
        btn_search.setObjectName("btn_primary")
        btn_search.setFixedHeight(36)
        btn_search.setCursor(Qt.PointingHandCursor)
        btn_search.clicked.connect(self._apply_filter)
        filter_layout.addWidget(btn_search)

        # Nút xóa bộ lọc
        btn_clear = QPushButton("Xóa bộ lọc")
        btn_clear.setObjectName("btn_secondary")
        btn_clear.setFixedHeight(36)
        btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.clicked.connect(self._clear_filter)
        filter_layout.addWidget(btn_clear)

        filter_layout.addStretch()
        layout.addWidget(filter_frame)

        # ── Bảng dữ liệu ──
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Thời gian", "Số điện thoại", "Ngăn tủ", "Hành động", "Phương thức", "ID"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)

        # Độ rộng cột
        h = self.table.horizontalHeader()
        h.setMinimumSectionSize(70)
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Thời gian
        h.setSectionResizeMode(1, QHeaderView.Stretch)           # SĐT
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Ngăn tủ
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Hành động
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Phương thức
        h.setSectionResizeMode(5, QHeaderView.Fixed)             # ID
        self.table.setColumnWidth(5, 70)

        layout.addWidget(self.table, stretch=1)

        # ── Thanh trạng thái ──
        status_bar = QHBoxLayout()
        self.lbl_status = QLabel("Sẵn sàng")
        self.lbl_status.setStyleSheet(f"color: {theme.colors().text_muted}; font-size: {theme.FONT_XS}px;")
        status_bar.addWidget(self.lbl_status)
        status_bar.addStretch()

        btn_refresh = QPushButton("🔄  Làm mới")
        btn_refresh.setObjectName("btn_secondary")
        btn_refresh.setFixedHeight(32)
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.clicked.connect(self.load_data)
        status_bar.addWidget(btn_refresh)
        layout.addLayout(status_bar)

    def showEvent(self, event):
        """Tải dữ liệu khi trang được hiển thị."""
        super().showEvent(event)
        self.load_data()

    def load_data(self):
        """Tải toàn bộ lịch sử mở tủ."""
        try:
            records = db_manager.get_open_history(limit=500)
            total = db_manager.get_open_history_count()
            self._populate_table(records)
            self.lbl_total.setText(f"Tổng: {total} bản ghi")
            self.lbl_status.setText(f"Đã tải {len(records)} bản ghi")
        except Exception as e:
            logger.error(f"Lỗi tải lịch sử: {e}")
            self.lbl_status.setText(f"Lỗi: {e}")

    def _apply_filter(self):
        """Áp dụng bộ lọc tìm kiếm."""
        phone = self.txt_phone.text().strip()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        try:
            records = db_manager.search_open_history(
                phone_query=phone,
                date_from=date_from,
                date_to=date_to
            )
            self._populate_table(records)
            self.lbl_status.setText(f"Tìm thấy {len(records)} kết quả")
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm: {e}")
            self.lbl_status.setText(f"Lỗi: {e}")

    def _clear_filter(self):
        """Xóa bộ lọc và tải lại toàn bộ."""
        self.txt_phone.clear()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        self.load_data()

    def _populate_table(self, records: list):
        """Đổ dữ liệu vào bảng."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(records))

        c = theme.colors()
        for row, rec in enumerate(records):
            # Thời gian
            ts = rec.get('timestamp', '')
            self.table.setItem(row, 0, QTableWidgetItem(str(ts)))

            # Số điện thoại
            phone = rec.get('phone_number', '—')
            self.table.setItem(row, 1, QTableWidgetItem(str(phone) if phone else '—'))

            # Ngăn tủ
            locker_num = rec.get('locker_number')
            self.table.setItem(row, 2, QTableWidgetItem(f"#{locker_num}" if locker_num else '—'))

            # Hành động
            action = rec.get('action', '')
            action_item = QTableWidgetItem(ACTION_LABELS.get(action, action))
            if action == 'send':
                action_item.setForeground(QColor(c.primary))
            elif action == 'receive':
                action_item.setForeground(QColor(c.success))
            else:
                action_item.setForeground(QColor(c.warning))
            self.table.setItem(row, 3, action_item)

            # Phương thức
            method = rec.get('method', '')
            self.table.setItem(row, 4, QTableWidgetItem(METHOD_LABELS.get(method, method)))

            # ID
            self.table.setItem(row, 5, QTableWidgetItem(str(rec.get('id', ''))))

        self.table.setSortingEnabled(True)

