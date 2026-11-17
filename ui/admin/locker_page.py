"""
FaceBox — Admin: Trang Quản Lý Tủ
Hiển thị sơ đồ ngăn tủ dạng lưới, trạng thái từng ngăn và thao tác quản lý.
"""
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea, QDialog, QComboBox,
    QSpinBox, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from ui import theme
from database import db_manager

logger = logging.getLogger(__name__)

# Mapping hiển thị tiếng Việt
STATUS_LABELS = {
    'empty': 'Trống',
    'occupied': 'Đang dùng',
    'error': 'Lỗi',
}
SIZE_LABELS = {
    'S': 'Nhỏ (S)',
    'M': 'Vừa (M)',
    'L': 'Lớn (L)',
}


class LockerCard(QFrame):
    """Widget hiển thị một ngăn tủ trong sơ đồ."""

    clicked = Signal(dict)  # Phát thông tin ngăn tủ khi click

    def __init__(self, locker_data: dict, parent=None):
        super().__init__(parent)
        self.locker_data = locker_data
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(140, 120)
        self._setup_ui()

    def _setup_ui(self):
        c = theme.colors()
        status = self.locker_data.get('status', 'empty')
        size = self.locker_data.get('size', 'M')
        number = self.locker_data.get('locker_number', 0)

        # Chọn màu theo trạng thái
        if status == 'empty':
            border_color = c.success
            bg_color = c.success_bg
            status_text = "Trống"
            status_icon = "✅"
        elif status == 'occupied':
            border_color = c.primary
            bg_color = c.surface
            status_text = "Đang dùng"
            status_icon = "📦"
        else:  # error
            border_color = c.error
            bg_color = c.error_bg
            status_text = "Lỗi"
            status_icon = "⚠️"

        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 2px;
            }}
            QFrame#card:hover {{
                border-width: 3px;
                border-color: #FFD500;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        # Số ngăn tủ
        lbl_number = QLabel(f"#{number}")
        lbl_number.setStyleSheet(f"font-size: {theme.FONT_H3}px; font-weight: bold; border: none; background: transparent;")
        lbl_number.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_number)

        # Icon trạng thái + size
        lbl_icon = QLabel(f"{status_icon}  {size}")
        lbl_icon.setStyleSheet(f"font-size: {theme.FONT_BODY}px; border: none; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_icon)

        # Nhãn trạng thái
        lbl_status = QLabel(status_text)
        lbl_status.setStyleSheet(f"font-size: {theme.FONT_XS}px; color: {border_color}; border: none; background: transparent;")
        lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_status)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.locker_data)
        super().mousePressEvent(event)


class AddLockerDialog(QDialog):
    """Dialog thêm ngăn tủ mới."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Ngăn Tủ Mới")
        self.setMinimumSize(380, 240)
        self.resize(380, 240)
        self._setup_ui()

    def _setup_ui(self):
        c = theme.colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c.surface}; color: {c.text}; }}")
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        # Số ngăn tủ
        row1 = QHBoxLayout()
        lbl1 = QLabel("Số ngăn tủ:")
        lbl1.setFixedWidth(90)
        row1.addWidget(lbl1)
        self.spin_number = QSpinBox()
        self.spin_number.setRange(1, 999)
        self.spin_number.setValue(1)
        row1.addWidget(self.spin_number)
        layout.addLayout(row1)

        # Kích thước
        row2 = QHBoxLayout()
        lbl2 = QLabel("Kích thước:")
        lbl2.setFixedWidth(90)
        row2.addWidget(lbl2)
        self.combo_size = QComboBox()
        self.combo_size.addItems(["S - Nhỏ", "M - Vừa", "L - Lớn"])
        self.combo_size.setCurrentIndex(1)  # Mặc định M
        row2.addWidget(self.combo_size)
        layout.addLayout(row2)

        # Số lượng tạo
        row3 = QHBoxLayout()
        lbl3 = QLabel("Số lượng:")
        lbl3.setFixedWidth(90)
        row3.addWidget(lbl3)
        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 50)
        self.spin_count.setValue(1)
        self.spin_count.setToolTip("Tạo liên tiếp nhiều ngăn tủ bắt đầu từ số trên")
        row3.addWidget(self.spin_count)
        layout.addLayout(row3)

        layout.addStretch()

        # Nút hành động
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Hủy bỏ")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_ok = QPushButton("Tạo ngăn tủ")
        btn_ok.setObjectName("btn_primary")
        btn_ok.setFixedHeight(38)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_ok)

        layout.addLayout(btn_row)

    def get_values(self):
        size_map = {0: 'S', 1: 'M', 2: 'L'}
        return {
            'start_number': self.spin_number.value(),
            'size': size_map[self.combo_size.currentIndex()],
            'count': self.spin_count.value(),
        }


class LockerPage(QWidget):
    """Trang quản lý ngăn tủ — hiển thị sơ đồ lưới và thao tác."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ── Header ──
        header = QHBoxLayout()
        title = QLabel("🗄️  Quản Lý Ngăn Tủ")
        title.setStyleSheet(f"font-size: {theme.FONT_H1}px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        btn_add = QPushButton("＋  Thêm ngăn tủ")
        btn_add.setObjectName("btn_primary")
        btn_add.setFixedHeight(38)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._show_add_dialog)
        header.addWidget(btn_add)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setObjectName("btn_secondary")
        btn_refresh.setFixedSize(38, 38)
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setToolTip("Làm mới")
        btn_refresh.clicked.connect(self.load_data)
        header.addWidget(btn_refresh)

        layout.addLayout(header)

        # ── Thống kê nhanh ──
        stats_frame = QFrame()
        stats_frame.setObjectName("card")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(16, 12, 16, 12)
        stats_layout.setSpacing(24)

        self.lbl_total = self._stat_label("Tổng", "0")
        self.lbl_empty = self._stat_label("Trống", "0", theme.colors().success)
        self.lbl_occupied = self._stat_label("Đang dùng", "0", theme.colors().primary)
        self.lbl_error = self._stat_label("Lỗi", "0", theme.colors().error)

        stats_layout.addWidget(self.lbl_total)
        stats_layout.addWidget(self.lbl_empty)
        stats_layout.addWidget(self.lbl_occupied)
        stats_layout.addWidget(self.lbl_error)
        stats_layout.addStretch()

        layout.addWidget(stats_frame)

        # ── Sơ đồ lưới ngăn tủ ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)
        scroll.setWidget(self.grid_container)

        layout.addWidget(scroll, stretch=1)

        # ── Chú thích ──
        legend = QHBoxLayout()
        legend.setSpacing(16)
        legend.addWidget(self._legend_item("✅ Trống", theme.colors().success))
        legend.addWidget(self._legend_item("📦 Đang dùng", theme.colors().primary))
        legend.addWidget(self._legend_item("⚠️ Lỗi", theme.colors().error))
        legend.addStretch()
        layout.addLayout(legend)

    def _stat_label(self, label: str, value: str, color: str = None) -> QWidget:
        """Tạo widget hiển thị thống kê nhỏ."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        lbl_val = QLabel(value)
        lbl_val.setObjectName("_stat_val")
        c = color or theme.colors().text
        lbl_val.setStyleSheet(f"font-size: {theme.FONT_H2}px; font-weight: bold; color: {c};")
        lay.addWidget(lbl_val)

        lbl_name = QLabel(label)
        lbl_name.setStyleSheet(f"font-size: {theme.FONT_XS}px; color: {theme.colors().text_muted};")
        lay.addWidget(lbl_name)

        w._value_label = lbl_val  # Lưu tham chiếu để cập nhật
        return w

    def _legend_item(self, text: str, color: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: {theme.FONT_XS}px; color: {color};")
        return lbl

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()

    def load_data(self):
        """Tải danh sách ngăn tủ và cập nhật sơ đồ."""
        try:
            lockers = db_manager.get_all_lockers()
            stats = db_manager.get_locker_stats()
            self._update_stats(stats)
            self._rebuild_grid(lockers)
        except Exception as e:
            logger.error(f"Lỗi tải dữ liệu ngăn tủ: {e}")

    def _update_stats(self, stats: dict):
        self.lbl_total._value_label.setText(str(stats.get('total', 0)))
        self.lbl_empty._value_label.setText(str(stats.get('empty', 0)))
        self.lbl_occupied._value_label.setText(str(stats.get('occupied', 0)))
        self.lbl_error._value_label.setText(str(stats.get('error', 0)))

    def _rebuild_grid(self, lockers: list):
        """Xóa lưới cũ và tạo lại từ dữ liệu mới."""
        # Xóa tất cả widget cũ
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not lockers:
            placeholder = QLabel("Chưa có ngăn tủ nào.\nBấm '＋ Thêm ngăn tủ' để tạo.")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet(f"color: {theme.colors().text_muted}; font-size: {theme.FONT_LG}px; padding: 48px;")
            self.grid_layout.addWidget(placeholder, 0, 0)
            return

        # Bố trí 5 cột
        cols = 5
        for idx, locker in enumerate(lockers):
            card = LockerCard(locker)
            card.clicked.connect(self._on_locker_clicked)
            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(card, row, col)

    def _on_locker_clicked(self, locker_data: dict):
        """Hiển thị chi tiết khi bấm vào ngăn tủ."""
        c = theme.colors()
        number = locker_data.get('locker_number', '?')
        status = STATUS_LABELS.get(locker_data.get('status', ''), locker_data.get('status', ''))
        size = SIZE_LABELS.get(locker_data.get('size', ''), locker_data.get('size', ''))

        info = (
            f"Ngăn tủ #{number}\n\n"
            f"Kích thước: {size}\n"
            f"Trạng thái: {status}\n"
            f"ID: {locker_data.get('id', '?')}"
        )

        # TODO: Khi có phần cứng thực tế, thêm nút "Mở tủ" ở đây
        QMessageBox.information(self, f"Ngăn tủ #{number}", info)

    def _show_add_dialog(self):
        """Hiển thị dialog thêm ngăn tủ mới."""
        dlg = AddLockerDialog(self)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.get_values()
            start = vals['start_number']
            size = vals['size']
            count = vals['count']

            success_count = 0
            errors = []
            for i in range(count):
                num = start + i
                ok, msg = db_manager.create_locker(num, size)
                if ok:
                    success_count += 1
                else:
                    errors.append(f"#{num}: {msg}")

            if success_count > 0:
                logger.info(f"Đã tạo {success_count} ngăn tủ")

            if errors:
                QMessageBox.warning(
                    self, "Cảnh báo",
                    f"Đã tạo {success_count} ngăn tủ.\n"
                    f"Có {len(errors)} lỗi:\n" + "\n".join(errors[:5])
                )

            self.load_data()

