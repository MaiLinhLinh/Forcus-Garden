from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFrame)
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
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # ── Header ────────────────────────────────────────────────────
        header_container = QWidget()
        header_container.setStyleSheet("background: transparent; border: none;")
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)

        title_label = QLabel("📜  Lịch Sử Phiên Học")
        title_label.setStyleSheet("""
            font-size: 22px; font-weight: bold; color: #4ade80;
            background: transparent; border: none;
        """)
        header_layout.addWidget(title_label)

        subtitle = QLabel("Theo dõi hành trình học tập của bạn")
        subtitle.setStyleSheet("""
            font-size: 13px; color: #64748b;
            background: transparent; border: none;
        """)
        header_layout.addWidget(subtitle)

        layout.addWidget(header_container)

        # ── Table Card ────────────────────────────────────────────────
        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background-color: #232a3e;
                border-radius: 12px;
                border: 1px solid rgba(74, 222, 128, 0.1);
            }
        """)
        card_layout = QVBoxLayout(table_card)
        card_layout.setContentsMargins(2, 2, 2, 2)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #232a3e;
                color: #e2e8f0;
                font-size: 13px;
                border: none;
                border-radius: 12px;
                gridline-color: rgba(148, 163, 184, 0.08);
                alternate-background-color: #2a3149;
            }
            QTableWidget::item {
                padding: 10px 14px;
                border-bottom: 1px solid rgba(148, 163, 184, 0.06);
            }
            QTableWidget::item:selected {
                background-color: rgba(74, 222, 128, 0.15);
                color: #4ade80;
            }
            QHeaderView::section {
                background-color: #1e2538;
                color: #4ade80;
                padding: 12px 14px;
                font-weight: 700;
                font-size: 13px;
                border: none;
                border-bottom: 2px solid rgba(74, 222, 128, 0.25);
            }
            QTableCornerButton::section {
                background-color: #1e2538;
                border: none;
            }
        """)

        # Enable alternating row colors
        self.table.setAlternatingRowColors(True)

        # Column widths — stretch to fill
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Ngày
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Môn học
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Mục tiêu
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Thực tế
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Trạng thái

        # Row height
        self.table.verticalHeader().setDefaultSectionSize(44)

        # Table properties
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        card_layout.addWidget(self.table)
        layout.addWidget(table_card)
        self.setLayout(layout)

    def load_sessions(self):
        """Load sessions từ database và hiển thị trong bảng."""
        sessions = get_all_sessions()

        if not sessions:
            # Empty state
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("Chưa có phiên học nào. Hãy bắt đầu học nhé! 🌱")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, len(self.COLUMNS))
            return

        # Populate table
        self.table.setRowCount(len(sessions))

        for row, session in enumerate(sessions):
            # Ngày: DD/MM HH:MM
            date_str = session.started_at.strftime("%d/%m %H:%M")
            date_item = QTableWidgetItem(f"  {date_str}")
            date_item.setForeground(Qt.GlobalColor.lightGray)
            self.table.setItem(row, 0, date_item)

            # Môn học
            subject_item = QTableWidgetItem(f"  {session.subject}")
            self.table.setItem(row, 1, subject_item)

            # Mục tiêu
            target = f"{session.target_duration_mins} phút"
            target_item = QTableWidgetItem(target)
            target_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, target_item)

            # Thực tế (format chi tiết: X phút Y giây)
            actual_secs = session.actual_duration_secs or 0
            actual_mins = actual_secs // 60
            actual_remainder_secs = actual_secs % 60

            if actual_mins > 0:
                actual = f"{actual_mins}p {actual_remainder_secs}s"
            else:
                actual = f"{actual_secs}s"

            actual_item = QTableWidgetItem(actual)
            actual_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, actual_item)

            # Trạng thái — badge style
            if session.status == "success":
                status_text = "  ✅ Thành công"
            else:
                status_text = "  ❌ Thất bại"

            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, status_item)

    def showEvent(self, event):
        """Override để reload data mỗi khi tab được mở."""
        super().showEvent(event)
        self.load_sessions()
