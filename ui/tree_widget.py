from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor


class TreeWidget(QWidget):
    """
    Cửa sổ nổi trong suốt - luôn hiển thị trên đỉnh tất cả ứng dụng khác.
    Hiển thị: Hình cây đồng hành + Đồng hồ đếm ngược + Nút thu gọn / kết thúc.
    """

    def __init__(self, duration_minutes: int, subject: str, on_finish_callback=None):
        # Không có parent để widget hoạt động độc lập như cửa sổ riêng
        super().__init__(parent=None)

        self.total_seconds = duration_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.subject = subject
        self.on_finish_callback = on_finish_callback
        self.is_collapsed = False

        # --- Thuộc tính cửa sổ trong suốt, không viền, luôn trên đỉnh ---
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint       # Ẩn thanh tiêu đề / viền
            | Qt.WindowType.WindowStaysOnTopHint    # Luôn nổi trên tất cả app
            | Qt.WindowType.Tool                    # Không hiện trên taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Nền trong suốt
        self.setFixedSize(180, 250)

        # Vị trí góc phải dưới màn hình (sẽ được set từ ngoài nếu cần)
        self._drag_pos = QPoint()

        self._build_ui()
        self._start_timer()

    # ------------------------------------------------------------------
    # XÂY DỰNG GIAO DIỆN
    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        self.setLayout(layout)

        # --- Thanh điều khiển nhỏ (thu gọn + đóng) ---
        ctrl_bar = QHBoxLayout()
        ctrl_bar.setContentsMargins(0, 0, 0, 0)

        self.collapse_btn = QPushButton("—")
        self.collapse_btn.setFixedSize(26, 26)
        self.collapse_btn.setToolTip("Thu gọn")
        self.collapse_btn.clicked.connect(self._toggle_collapse)
        self.collapse_btn.setStyleSheet(self._ctrl_btn_style("#94a3b8"))

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setToolTip("Kết thúc phiên học")
        self.close_btn.clicked.connect(self._finish_session)
        self.close_btn.setStyleSheet(self._ctrl_btn_style("#ef4444"))

        ctrl_bar.addStretch()
        ctrl_bar.addWidget(self.collapse_btn)
        ctrl_bar.addWidget(self.close_btn)
        layout.addLayout(ctrl_bar)

        # --- Hình cây (emoji lớn, hoạt như ảnh đại diện cây) ---
        self.tree_label = QLabel("🌱")
        self.tree_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tree_label.setFont(QFont("Segoe UI Emoji", 56))
        self.tree_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.tree_label)

        # --- Đồng hồ đếm ngược ---
        self.timer_label = QLabel(self._format_time(self.remaining_seconds))
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("""
            color: #4ade80;
            font-size: 28px;
            font-weight: bold;
            font-family: 'Consolas', 'Courier New', monospace;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.timer_label)

        # --- Tên môn học ---
        subject_label = QLabel(self.subject)
        subject_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subject_label.setWordWrap(True)
        subject_label.setStyleSheet("""
            color: #94a3b8;
            font-size: 11px;
            font-style: italic;
            background: transparent;
            border: none;
        """)
        layout.addWidget(subject_label)

        # --- Background bo tròn dark glassmorphism ---
        self.setStyleSheet("""
            TreeWidget {
                background-color: rgba(26, 31, 46, 235);
                border-radius: 18px;
                border: 1px solid rgba(74, 222, 128, 0.3);
            }
        """)

    # ------------------------------------------------------------------
    # TIMER
    # ------------------------------------------------------------------
    def _start_timer(self):
        self.qt_timer = QTimer(self)
        self.qt_timer.setInterval(1000)  # Đếm ngược 1 giây / lần
        self.qt_timer.timeout.connect(self._tick)
        self.qt_timer.start()

    def _tick(self):
        """Được gọi mỗi giây bởi QTimer."""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.timer_label.setText(self._format_time(self.remaining_seconds))
            self._update_tree_emoji()  # Cập nhật biểu tượng cây theo tiến độ
        else:
            self.qt_timer.stop()
            self._finish_session()

    def _update_tree_emoji(self):
        """Thay đổi emoji cây theo % thời gian đã học."""
        progress = 1.0 - (self.remaining_seconds / self.total_seconds)
        if progress < 0.25:
            self.tree_label.setText("🌱")   # 0-25%: Mầm
        elif progress < 0.50:
            self.tree_label.setText("🌿")   # 25-50%: Nảy lá
        elif progress < 0.75:
            self.tree_label.setText("🌲")   # 50-75%: Cây nhỏ
        else:
            self.tree_label.setText("🌳")   # 75-100%: Cây trưởng thành

    def _finish_session(self):
        """Kết thúc phiên: dừng timer, gọi callback, đóng widget."""
        self.qt_timer.stop()
        elapsed = self.total_seconds - self.remaining_seconds
        if self.on_finish_callback:
            self.on_finish_callback(elapsed)
        self.close()

    # ------------------------------------------------------------------
    # THU GỌN / MỞ RỘNG
    # ------------------------------------------------------------------
    def _toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.setFixedSize(180, 55)   # Chỉ giữ lại thanh điều khiển + đồng hồ
            self.tree_label.hide()
            self.collapse_btn.setText("□")
        else:
            self.setFixedSize(180, 250)
            self.tree_label.show()
            self.collapse_btn.setText("—")

    # ------------------------------------------------------------------
    # KÉO THẢ WIDGET
    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = QPoint()

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    @staticmethod
    def _format_time(seconds: int) -> str:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    @staticmethod
    def _ctrl_btn_style(color: str) -> str:
        return f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.06);
                color: {color};
                border: none;
                font-size: 13px;
                font-weight: bold;
                border-radius: 13px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.15);
            }}
        """
