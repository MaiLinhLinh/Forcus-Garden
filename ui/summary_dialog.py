from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QWidget, QSizePolicy
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

        self.setMinimumSize(560, 500)
        self.resize(600, 740)

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
        print(f"[DEBUG] ===== SummaryDialog._build_ui =====")
        print(f"[DEBUG] Received stats: {stats}")
        print(f"[DEBUG] distraction_count: {stats.get('count', 0)}")
        print(f"[DEBUG] total_seconds: {stats.get('total_seconds', 0)}")
        print(f"[DEBUG] details length: {len(stats.get('details', []))}")

        # VALIDATION: Check data consistency upon receipt
        received_count = stats.get('count', 0)
        received_total = stats.get('total_seconds', 0)
        received_details = stats.get('details', [])
        actual_detail_count = len(received_details)
        actual_detail_sum = sum(d['seconds'] for d in received_details)

        print(f"[DEBUG] Data integrity check:")
        print(f"[DEBUG]   - Expected count: {received_count}, Actual details: {actual_detail_count}")
        print(f"[DEBUG]   - Expected total: {received_total}, Sum of details: {actual_detail_sum}")

        if received_count != actual_detail_count:
            print(f"[ERROR] CRITICAL: count={received_count} != details length={actual_detail_count}!")
            print(f"[ERROR] Missing {received_count - actual_detail_count} distraction(s) from display!")
        if received_total != actual_detail_sum:
            print(f"[ERROR] CRITICAL: total_seconds={received_total} != sum details={actual_detail_sum}!")
            print(f"[ERROR] Time discrepancy: {received_total - actual_detail_sum} seconds unaccounted for!")

        # ── Dialog background ─────────────────────────────────────────
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1f2e;
            }
        """)

        # ── Outer layout: scroll + fixed button ──────────────────────
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Wrap ALL content in a QScrollArea so dialog is always scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1a1f2e;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #1a1f2e; border: none;")
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(14)

        # ── Status Header Card ────────────────────────────────────────
        if self.is_success:
            status_icon = "🌳"
            status_text = "PHIÊN HỌC THÀNH CÔNG!"
            accent_color = "#4ade80"
            card_bg = "rgba(74, 222, 128, 0.08)"
            card_border = "rgba(74, 222, 128, 0.3)"
        else:
            status_icon = "🥀"
            status_text = "PHIÊN HỌC CHƯA HOÀN THÀNH"
            accent_color = "#f87171"
            card_bg = "rgba(248, 113, 113, 0.08)"
            card_border = "rgba(248, 113, 113, 0.3)"

        status_card = QFrame()
        status_card.setStyleSheet(f"""
            QFrame {{
                background-color: {card_bg};
                border-radius: 14px;
                border: 1px solid {card_border};
            }}
        """)
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(20, 18, 20, 18)
        status_layout.setSpacing(6)

        icon_label = QLabel(status_icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFont(QFont("Segoe UI Emoji", 52))
        icon_label.setStyleSheet("background: transparent; border: none;")
        status_layout.addWidget(icon_label)

        status_label = QLabel(status_text)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {accent_color};
            background: transparent;
            border: none;
            padding: 2px;
        """)
        status_layout.addWidget(status_label)

        layout.addWidget(status_card)

        # ── Session Info Section ──────────────────────────────────────
        info_section = self._create_info_section(subject, target_mins, actual_study_seconds)
        layout.addWidget(info_section)

        # ── Distraction Stats Section ─────────────────────────────────
        stats_section = self._create_stats_section(stats)
        layout.addWidget(stats_section)

        # ── Distraction Details Section (if any) ──────────────────────
        if stats.get("details"):
            print(f"[DEBUG] Building distraction details list...")
            print(f"[DEBUG] Number of detail items: {len(stats['details'])}")

            details_section = self._create_details_section(stats["details"])
            layout.addWidget(details_section)
        else:
            print(f"[DEBUG] No details to display in UI")

        layout.addStretch()
        scroll.setWidget(scroll_content)
        outer_layout.addWidget(scroll, 1)

        # ── Close Button (fixed at bottom, outside scroll) ────────────
        btn_container = QWidget()
        btn_container.setStyleSheet("background-color: #1a1f2e; border: none;")
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(28, 10, 28, 20)

        close_btn = QPushButton("Đóng && Học tiếp")
        close_btn.setMinimumHeight(46)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: #052e16;
                font-weight: bold;
                font-size: 15px;
                padding: 12px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4ade80;
            }
            QPushButton:pressed {
                background-color: #16a34a;
            }
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        outer_layout.addWidget(btn_container)

        print(f"[DEBUG] ===== SummaryDialog._build_ui completed =====")

    # ------------------------------------------------------------------
    # SECTION BUILDERS
    # ------------------------------------------------------------------
    def _create_info_section(self, subject: str, target_mins: int, actual_study_seconds: int) -> QWidget:
        """Create the session information section."""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #232a3e;
                border-radius: 12px;
                border: 1px solid rgba(74, 222, 128, 0.1);
            }
        """)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(6)

        # Title
        title = QLabel("Thông tin phiên học")
        title.setStyleSheet("""
            font-size: 14px; font-weight: bold; color: #4ade80;
            background: transparent; border: none;
        """)
        layout.addWidget(title)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: rgba(148, 163, 184, 0.1); border: none;")
        layout.addWidget(div)

        # Info rows — no emoji in small labels to avoid Qt render issues
        layout.addWidget(self._make_info_row("Môn học", subject, "#e2e8f0"))
        layout.addWidget(self._make_info_row("Mục tiêu", f"{target_mins} phút", "#e2e8f0"))
        layout.addWidget(self._make_info_row("Thực học", self._fmt_seconds(actual_study_seconds), "#38bdf8"))

        return section

    def _create_stats_section(self, stats: dict) -> QWidget:
        """Create the distraction statistics section."""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #232a3e;
                border-radius: 12px;
                border: 1px solid rgba(74, 222, 128, 0.1);
            }
        """)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(6)

        # Title
        title = QLabel("Thống kê xao nhãng")
        title.setStyleSheet("""
            font-size: 14px; font-weight: bold; color: #f59e0b;
            background: transparent; border: none;
        """)
        layout.addWidget(title)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: rgba(148, 163, 184, 0.1); border: none;")
        layout.addWidget(div)

        distraction_count = stats.get("count", 0)
        total_violation = stats.get("total_seconds", 0)

        print(f"[DEBUG] Displaying in UI: count={distraction_count}, total_violation={total_violation}s")

        # Stats rows
        count_color = "#4ade80" if distraction_count == 0 else "#f59e0b"
        time_color = "#4ade80" if total_violation == 0 else "#ef4444"

        layout.addWidget(self._make_info_row(
            "Số lần xao nhãng",
            f"{distraction_count} lần",
            count_color
        ))
        layout.addWidget(self._make_info_row(
            "Thời gian vi phạm",
            self._fmt_seconds(total_violation),
            time_color
        ))

        return section

    def _create_details_section(self, details: list) -> QWidget:
        """Create the distraction details section as a flat list (no nested scroll)."""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #232a3e;
                border-radius: 12px;
                border: 1px solid rgba(74, 222, 128, 0.1);
            }
        """)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(6)

        # Title with count
        title = QLabel(f"Chi tiết xao nhãng ({len(details)})")
        title.setStyleSheet("""
            font-size: 14px; font-weight: bold; color: #94a3b8;
            background: transparent; border: none;
        """)
        layout.addWidget(title)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: rgba(148, 163, 184, 0.1); border: none;")
        layout.addWidget(div)

        # Add each distraction as a card — no nested scroll, rely on outer scroll
        for idx, item in enumerate(details):
            print(f"[DEBUG]   Adding item {idx+1}: app='{item['app']}', seconds={item['seconds']}")

            card = self._create_distraction_card(item['app'], item['seconds'], idx + 1)
            layout.addWidget(card)

        return section

    def _create_distraction_card(self, app_name: str, duration: int, index: int) -> QWidget:
        """Create a card for a single distraction entry."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2a3149;
                border-radius: 8px;
                border: 1px solid rgba(148, 163, 184, 0.08);
            }
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # Index badge
        index_label = QLabel(f"#{index}")
        index_label.setFixedWidth(34)
        index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        index_label.setStyleSheet("""
            font-size: 11px;
            font-weight: bold;
            color: #94a3b8;
            background-color: rgba(148, 163, 184, 0.1);
            padding: 3px 5px;
            border-radius: 5px;
            border: none;
        """)
        layout.addWidget(index_label)

        # App name
        app_label = QLabel(app_name)
        app_label.setWordWrap(True)
        app_label.setStyleSheet("""
            font-size: 12px;
            color: #cbd5e1;
            background: transparent;
            border: none;
        """)
        layout.addWidget(app_label, 1)  # stretch factor

        # Duration badge
        duration_text = self._fmt_seconds(duration)
        duration_label = QLabel(duration_text)
        duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        duration_label.setStyleSheet("""
            font-size: 11px;
            font-weight: bold;
            color: #ef4444;
            background-color: rgba(239, 68, 68, 0.12);
            padding: 3px 8px;
            border-radius: 5px;
            border: none;
        """)
        layout.addWidget(duration_label)

        return card

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def _make_info_row(self, label: str, value: str, value_color: str = "#e2e8f0") -> QWidget:
        """Create a row with label and value."""
        row = QWidget()
        row.setStyleSheet("background-color: transparent; border: none;")

        h = QHBoxLayout(row)
        h.setContentsMargins(0, 3, 0, 3)
        h.setSpacing(12)

        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 13px; color: #94a3b8; background: transparent; border: none;")
        h.addWidget(lbl)

        h.addStretch()

        val = QLabel(value)
        val.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {value_color}; background: transparent; border: none;")
        h.addWidget(val)

        return row

    @staticmethod
    def _fmt_seconds(seconds: int) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h} giờ {m} phút {s} giây"
        if m > 0:
            return f"{m} phút {s} giây"
        return f"{s} giây"
