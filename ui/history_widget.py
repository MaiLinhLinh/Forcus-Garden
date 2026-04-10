from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from database.session_repo import get_all_sessions


class HistoryWidget(QWidget):
    """Tab lịch sử hiển thị tất cả phiên học dưới dạng bảng."""

    COLUMNS = ["Ngày", "Môn học", "Mục tiêu", "Thực tế", "Trạng thái"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Title
        title_label = QLabel("📜 LỊCH SỬ CỦA BẠN")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2e7d32; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 13px;
                border: 1px solid #ddd;
                border-radius: 6px;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #ddd;
            }
        """)

        # Column widths
        self.table.setColumnWidth(0, 120)  # Ngày
        self.table.setColumnWidth(1, 200)  # Môn học
        self.table.setColumnWidth(2, 100)  # Mục tiêu
        self.table.setColumnWidth(3, 100)  # Thực tế
        self.table.setColumnWidth(4, 100)  # Trạng thái

        # Table properties
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_sessions(self):
        """Load sessions từ database và hiển thị trong bảng."""
        sessions = get_all_sessions()

        if not sessions:
            # Empty state
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("Chưa có phiên học nào. Hãy bắt đầu học nhé! 🌱")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, len(self.COLUMNS))
            return

        # Populate table
        self.table.setRowCount(len(sessions))

        for row, session in enumerate(sessions):
            # Ngày: DD/MM HH:MM
            date_str = session.started_at.strftime("%d/%m %H:%M")
            self.table.setItem(row, 0, QTableWidgetItem(date_str))

            # Môn học
            self.table.setItem(row, 1, QTableWidgetItem(session.subject))

            # Mục tiêu
            target = f"{session.target_duration_mins} phút"
            self.table.setItem(row, 2, QTableWidgetItem(target))

            # Thực tế (format chi tiết: X phút Y giây)
            actual_secs = session.actual_duration_secs or 0
            actual_mins = actual_secs // 60
            actual_remainder_secs = actual_secs % 60

            if actual_mins > 0:
                actual = f"{actual_mins} phút {actual_remainder_secs} giây"
            else:
                actual = f"{actual_secs} giây"

            self.table.setItem(row, 3, QTableWidgetItem(actual))

            # Trạng thái (emoji only)
            status = "✅" if session.status == "success" else "❌"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, status_item)

    def showEvent(self, event):
        """Override để reload data mỗi khi tab được mở."""
        super().showEvent(event)
        self.load_sessions()
