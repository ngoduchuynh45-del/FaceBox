"""
FaceBox - Trang Quản Lý Tài Khoản
Xem, tìm kiếm, xóa tài khoản và khuôn mặt.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QLineEdit,
                                QFrame, QTableWidget, QTableWidgetItem,
                                QHeaderView, QMessageBox, QSplitter,
                                QScrollArea, QSizePolicy, QListWidget,
                                QListWidgetItem, QAbstractItemView)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont
from database import db_manager
from ui.widgets import SectionTitle


class AccountsPage(QWidget):
    """Trang quản lý tài khoản."""
    
    data_changed = Signal()  # Phát khi dữ liệu thay đổi
    
    def __init__(self, face_service, parent=None):
        super().__init__(parent)
        self.face_service = face_service
        self._selected_account_id = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Quản Lý Tài Khoản")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e2e8f0;")
        header.addWidget(title)
        header.addStretch()
        
        btn_refresh = QPushButton("🔄 Làm mới")
        btn_refresh.setObjectName("btn_secondary")
        btn_refresh.clicked.connect(self.refresh_data)
        header.addWidget(btn_refresh)
        layout.addLayout(header)
        
        # Search
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm kiếm theo số điện thoại...")
        self.search_input.textChanged.connect(self._on_search)
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)
        
        # Splitter: danh sách tài khoản | chi tiết khuôn mặt
        splitter = QSplitter(Qt.Horizontal)
        
        # === Bên trái: Danh sách tài khoản ===
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_title = SectionTitle("Danh sách tài khoản")
        left_layout.addWidget(left_title)
        
        self.account_table = QTableWidget()
        self.account_table.setColumnCount(3)
        self.account_table.setHorizontalHeaderLabels(["Số điện thoại", "Khuôn mặt", "Ngày tạo"])
        self.account_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.account_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.account_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.account_table.setColumnWidth(1, 90)
        self.account_table.setColumnWidth(2, 110)
        self.account_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.account_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.account_table.setAlternatingRowColors(True)
        self.account_table.itemSelectionChanged.connect(self._on_account_selected)
        self.account_table.verticalHeader().setVisible(False)
        left_layout.addWidget(self.account_table)
        
        # Nút xóa tài khoản
        btn_delete_account = QPushButton("🗑️  Xóa tài khoản đã chọn")
        btn_delete_account.setObjectName("btn_danger")
        btn_delete_account.clicked.connect(self._delete_selected_account)
        left_layout.addWidget(btn_delete_account)
        
        splitter.addWidget(left_widget)
        
        # === Bên phải: Chi tiết khuôn mặt ===
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 0, 0, 0)
        
        right_title = SectionTitle("Khuôn mặt đã đăng ký")
        right_layout.addWidget(right_title)
        
        self.account_info_label = QLabel("← Chọn một tài khoản để xem chi tiết")
        self.account_info_label.setStyleSheet("color: #4a5568; font-size: 13px; padding: 8px;")
        right_layout.addWidget(self.account_info_label)
        
        self.face_list = QListWidget()
        self.face_list.setStyleSheet("""
            QListWidget {
                background-color: #161b27;
                border: 1px solid #1e2635;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 10px 14px;
                border-bottom: 1px solid #1e2635;
                color: #e2e8f0;
            }
            QListWidget::item:selected {
                background-color: #1e2d54;
            }
            QListWidget::item:hover {
                background-color: #1a1f2e;
            }
        """)
        right_layout.addWidget(self.face_list)
        
        face_btn_row = QHBoxLayout()
        btn_delete_face = QPushButton("🗑️  Xóa khuôn mặt đã chọn")
        btn_delete_face.setObjectName("btn_danger")
        btn_delete_face.clicked.connect(self._delete_selected_face)
        
        btn_delete_all_faces = QPushButton("🗑️  Xóa tất cả khuôn mặt")
        btn_delete_all_faces.setObjectName("btn_danger")
        btn_delete_all_faces.clicked.connect(self._delete_all_faces)
        
        face_btn_row.addWidget(btn_delete_face)
        face_btn_row.addWidget(btn_delete_all_faces)
        right_layout.addLayout(face_btn_row)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 350])
        
        layout.addWidget(splitter)
        
        # Thống kê
        self.stats_label = QLabel("Đang tải...")
        self.stats_label.setStyleSheet("color: #4a5568; font-size: 12px;")
        layout.addWidget(self.stats_label)
    
    def refresh_data(self):
        """Tải lại toàn bộ dữ liệu."""
        self._load_accounts()
        self._clear_face_list()
        self._update_stats()
    
    def _load_accounts(self, query: str = ""):
        """Tải danh sách tài khoản."""
        if query:
            accounts = db_manager.search_accounts(query)
        else:
            accounts = db_manager.get_all_accounts()
        
        self.account_table.setRowCount(0)
        for acc in accounts:
            row = self.account_table.rowCount()
            self.account_table.insertRow(row)
            
            phone_item = QTableWidgetItem(acc['phone_number'])
            phone_item.setData(Qt.UserRole, acc['id'])
            
            face_count = acc['face_count']
            face_item = QTableWidgetItem(str(face_count))
            face_item.setTextAlignment(Qt.AlignCenter)
            if face_count == 0:
                face_item.setForeground(QColor("#f87171"))
            else:
                face_item.setForeground(QColor("#34d399"))
            
            created = acc.get('created_at', '')[:10] if acc.get('created_at') else ''
            date_item = QTableWidgetItem(created)
            date_item.setTextAlignment(Qt.AlignCenter)
            
            self.account_table.setItem(row, 0, phone_item)
            self.account_table.setItem(row, 1, face_item)
            self.account_table.setItem(row, 2, date_item)
    
    def _on_search(self, text: str):
        self._load_accounts(text)
        self._clear_face_list()
    
    def _on_account_selected(self):
        """Xử lý khi chọn tài khoản."""
        rows = self.account_table.selectedItems()
        if not rows:
            return
        
        row = self.account_table.currentRow()
        phone_item = self.account_table.item(row, 0)
        if not phone_item:
            return
        
        account_id = phone_item.data(Qt.UserRole)
        phone = phone_item.text()
        self._selected_account_id = account_id
        
        self.account_info_label.setText(f"📱 {phone}")
        self._load_faces(account_id)
    
    def _load_faces(self, account_id: int):
        """Tải danh sách khuôn mặt của tài khoản."""
        self.face_list.clear()
        profiles = db_manager.get_face_profiles_by_account(account_id)
        
        if not profiles:
            item = QListWidgetItem("  (Chưa có khuôn mặt nào được đăng ký)")
            item.setForeground(QColor("#4a5568"))
            self.face_list.addItem(item)
            return
        
        for p in profiles:
            created = p.get('created_at', '')[:16] if p.get('created_at') else ''
            text = f"👤  {p['label']}  —  {created}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, p['id'])
            self.face_list.addItem(item)
    
    def _clear_face_list(self):
        self.face_list.clear()
        self._selected_account_id = None
        self.account_info_label.setText("← Chọn một tài khoản để xem chi tiết")
    
    def _delete_selected_account(self):
        """Xóa tài khoản được chọn."""
        if self._selected_account_id is None:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một tài khoản trong danh sách.")
            return
        
        row = self.account_table.currentRow()
        phone_item = self.account_table.item(row, 0)
        phone = phone_item.text() if phone_item else "?"
        
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc muốn xóa tài khoản {phone}?\n\n"
            "Toàn bộ khuôn mặt liên kết cũng sẽ bị xóa vĩnh viễn.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, msg = db_manager.delete_account(self._selected_account_id)
            if success:
                self._reload_embeddings()
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Thành công", "Đã xóa tài khoản.")
            else:
                QMessageBox.critical(self, "Lỗi", msg)
    
    def _delete_selected_face(self):
        """Xóa khuôn mặt được chọn."""
        item = self.face_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một khuôn mặt.")
            return
        
        profile_id = item.data(Qt.UserRole)
        if not profile_id:
            return
        
        label = item.text().strip()
        
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Xóa khuôn mặt:\n{label}\n\nHành động này không thể hoàn tác.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, msg = db_manager.delete_face_profile(profile_id)
            if success:
                self._reload_embeddings()
                if self._selected_account_id:
                    self._load_faces(self._selected_account_id)
                self._load_accounts(self.search_input.text())
                self._update_stats()
                self.data_changed.emit()
            else:
                QMessageBox.critical(self, "Lỗi", msg)
    
    def _delete_all_faces(self):
        """Xóa tất cả khuôn mặt của tài khoản đã chọn."""
        if self._selected_account_id is None:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một tài khoản.")
            return
        
        row = self.account_table.currentRow()
        phone_item = self.account_table.item(row, 0)
        phone = phone_item.text() if phone_item else "?"
        
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Xóa TẤT CẢ khuôn mặt của tài khoản {phone}?\n\nHành động này không thể hoàn tác.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, msg = db_manager.delete_all_faces_of_account(self._selected_account_id)
            if success:
                self._reload_embeddings()
                self._load_faces(self._selected_account_id)
                self._load_accounts(self.search_input.text())
                self._update_stats()
                self.data_changed.emit()
                QMessageBox.information(self, "Thành công", msg)
            else:
                QMessageBox.critical(self, "Lỗi", msg)
    
    def _reload_embeddings(self):
        """Reload embedding cache."""
        try:
            from database import db_manager as dm
            self.face_service.load_known_embeddings(dm.get_all_face_embeddings())
        except Exception:
            pass
    
    def _update_stats(self):
        total_acc = db_manager.get_total_accounts()
        total_faces = db_manager.get_total_faces()
        self.stats_label.setText(
            f"Tổng: {total_acc} tài khoản  |  {total_faces} khuôn mặt đã đăng ký"
        )
    
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()
