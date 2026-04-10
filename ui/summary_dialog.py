from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SummaryDialog(QDialog):
    """
    Màn hình Tổng kết bắt buộc hiển thị sau mỗi phiên học.
    Hiển thị: trạng thái hợp lệ, số lần xao nhãng, tổng thời gian vi phạm.
    """

    def __init__(
        self,
        subject: str,
        target_mins: int,
        elapsed_seconds: int,
        distraction_stats: dict,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Tổng kết phiên học")
        self.setFixedSize(420, 480)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        target_seconds = target_mins * 60
        total_distraction = distraction_stats.get("total_seconds", 0)

        # Logic thành công:
        # 1. Học đủ thời gian khai báo
        # 2. VÀ thời gian xao nhãng < 50% thời gian khai báo
        distraction_threshold = target_seconds // 2  # 50% thời gian khai báo
        self.is_success = (
            elapsed_seconds >= target_seconds and
            total_distraction < distraction_threshold
        )

        # Tính thời gian thực học = Tổng thời gian - Thời gian xao nhãng
        actual_study_seconds = max(0, elapsed_seconds - total_distraction)

        self._build_ui(subject, target_mins, actual_study_seconds, elapsed_seconds, distraction_stats)

    # ------------------------------------------------------------------
    # XÂY DỰNG GIAO DIỆN
    # ------------------------------------------------------------------
    def _build_ui(self, subject, target_mins, actual_study_seconds, elapsed_seconds, stats):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        self.setLayout(layout)

        # --- Tiêu đề trạng thái ---
        if self.is_success:
            status_icon = "🌳"
            status_text = "PHIÊN HỌC THÀNH CÔNG!"
            status_color = "#2e7d32"
            bg_color = "#f1f8e9"
        else:
            status_icon = "🥀"
            status_text = "PHIÊN HỌC CHƯA HOÀN THÀNH"
            status_color = "#b71c1c"
            bg_color = "#fff3e0"

        self.setStyleSheet(f"background-color: {bg_color};")

        icon_label = QLabel(status_icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFont(QFont("Segoe UI Emoji", 52))
        layout.addWidget(icon_label)

        status_label = QLabel(status_text)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet(
            f"font-size: 17px; font-weight: bold; color: {status_color};"
        )
        layout.addWidget(status_label)

        # --- Đường kẻ ---
        layout.addWidget(self._make_divider())

        # --- Thông tin phiên học ---
        layout.addWidget(self._make_info_row("📚  Môn học", subject))
        layout.addWidget(self._make_info_row("🎯  Mục tiêu", f"{target_mins} phút"))
        layout.addWidget(self._make_info_row(
            "⏱️  Thực học",
            self._fmt_seconds(actual_study_seconds)
        ))

        layout.addWidget(self._make_divider())

        # --- Thống kê xao nhãng ---
        distraction_count = stats.get("count", 0)
        total_violation = stats.get("total_seconds", 0)

        layout.addWidget(self._make_info_row(
            "⚠️  Số lần xao nhãng",
            f"{distraction_count} lần",
            value_color="#e65100" if distraction_count > 0 else "#2e7d32"
        ))
        layout.addWidget(self._make_info_row(
            "🚨  Thời gian vi phạm",
            self._fmt_seconds(total_violation),
            value_color="#e65100" if total_violation > 0 else "#2e7d32"
        ))

        # --- Chi tiết xao nhãng (nếu có) ---
        if stats.get("details"):
            layout.addWidget(self._make_divider())
            detail_label = QLabel("Chi tiết xao nhãng:")
            detail_label.setStyleSheet("font-size: 12px; color: #555;")
            layout.addWidget(detail_label)

            scroll = QScrollArea()
            scroll.setFixedHeight(80)
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("border: 1px solid #ddd; border-radius: 6px;")

            inner = QWidget()
            inner_layout = QVBoxLayout(inner)
            inner_layout.setContentsMargins(8, 4, 8, 4)
            inner_layout.setSpacing(2)

            for item in stats["details"]:
                row_text = f"• {item['app']}  —  {self._fmt_seconds(item['seconds'])}"
                lbl = QLabel(row_text)
                lbl.setStyleSheet("font-size: 11px; color: #444;")
                inner_layout.addWidget(lbl)

            scroll.setWidget(inner)
            layout.addWidget(scroll)

        layout.addStretch()

        # --- Nút đóng ---
        close_btn = QPushButton("Đóng & Học tiếp 🌱")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white;
                font-weight: bold; font-size: 15px;
                padding: 10px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #388e3c; }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def _make_info_row(self, label: str, value: str, value_color: str = "#1a237e") -> QWidget:
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 13px; color: #333;")
        h.addWidget(lbl)

        h.addStretch()

        val = QLabel(value)
        val.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {value_color};")
        h.addWidget(val)

        return row

    def _make_divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #c8e6c9;")
        return line

    @staticmethod
    def _fmt_seconds(seconds: int) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h} giờ {m} phút {s} giây"
        if m > 0:
            return f"{m} phút {s} giây"
        return f"{s} giây"
