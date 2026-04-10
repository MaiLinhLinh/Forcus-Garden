from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QPushButton, QTextEdit,
                             QMessageBox, QApplication)
from PyQt6.QtGui import QScreen

from ui.tree_widget import TreeWidget
from ui.summary_dialog import SummaryDialog
from core.tracker import FocusTrackerThread
from database.session_repo import (
    create_session, save_distraction, close_session, get_distraction_stats
)


class CreateSessionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_widget = None
        self.tracker_thread = None
        self._session_id = None          # ID phiên đang chạy trong DB
        self._current_subject = ""
        self._target_mins = 25
        self.init_ui()

    # ------------------------------------------------------------------
    # GIAO DIỆN
    # ------------------------------------------------------------------
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("🌱 TẠO PHIÊN HỌC MỚI")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2e7d32; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Tên Môn Học
        h_subject = QHBoxLayout()
        label_subject = QLabel("Môn Học / Hoạt Động:")
        label_subject.setFixedWidth(150)
        h_subject.addWidget(label_subject)
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("VD: Lập trình Python, Ôn thi Giải tích...")
        h_subject.addWidget(self.subject_input)
        layout.addLayout(h_subject)

        # Thời lượng
        h_duration = QHBoxLayout()
        label_duration = QLabel("Thời Lượng (Phút):")
        label_duration.setFixedWidth(150)
        h_duration.addWidget(label_duration)
        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 480)
        self.duration_input.setValue(25)
        h_duration.addWidget(self.duration_input)
        layout.addLayout(h_duration)

        # Study Zone
        layout.addWidget(QLabel("Study Zone (Khai báo các từ khóa tiêu đề cửa sổ hợp lệ):"))
        self.zone_input = QTextEdit()
        self.zone_input.setPlaceholderText(
            "Nhập các từ khóa, mỗi từ khóa trên 1 dòng.\nVí dụ:\nword\nchrome\nvscode\ngithub"
        )
        layout.addWidget(self.zone_input)

        # Nút Bắt đầu
        self.start_btn = QPushButton("BẮT ĐẦU TRỒNG CÂY")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white;
                font-weight: bold; font-size: 16px;
                padding: 12px; border-radius: 5px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #a5d6a7; color: #e0e0e0; }
        """)
        self.start_btn.clicked.connect(self._on_start)
        layout.addWidget(self.start_btn)
        self.setLayout(layout)

    # ------------------------------------------------------------------
    # LOGIC BẮT ĐẦU PHIÊN
    # ------------------------------------------------------------------
    def _on_start(self):
        subject = self.subject_input.text().strip()
        duration = self.duration_input.value()
        keywords_raw = self.zone_input.toPlainText().strip()

        if not subject:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên môn học / hoạt động.")
            return
        if not keywords_raw:
            QMessageBox.warning(self, "Thiếu Study Zone",
                                "Vui lòng khai báo ít nhất 1 từ khóa cho Study Zone.")
            return

        keywords = [kw.strip() for kw in keywords_raw.splitlines() if kw.strip()]

        # --- Lưu Session vào DB ---
        self._session_id = create_session(subject, duration, keywords)
        self._current_subject = subject
        self._target_mins = duration

        # --- Vô hiệu hoá nút ---
        self.start_btn.setEnabled(False)
        self.start_btn.setText("ĐANG HỌC... 🌿")

        # --- Khởi động Tracker, lắng nghe sự kiện xao nhãng ---
        self.tracker_thread = FocusTrackerThread(keywords)
        self.tracker_thread.distraction_recorded.connect(self._on_distraction_recorded)
        self.tracker_thread.start()

        # --- Khởi động TreeWidget ---
        self.tree_widget = TreeWidget(
            duration_minutes=duration,
            subject=subject,
            on_finish_callback=self._on_session_finished,
        )
        screen: QScreen = QApplication.primaryScreen()
        geo = screen.availableGeometry()
        self.tree_widget.move(
            geo.right() - self.tree_widget.width() - 20,
            geo.bottom() - self.tree_widget.height() - 20,
        )
        self.tree_widget.show()

    # ------------------------------------------------------------------
    # SLOT: Nhận tín hiệu xao nhãng từ Tracker → Lưu vào DB
    # ------------------------------------------------------------------
    def _on_distraction_recorded(self, app_name: str, duration_seconds: int):
        """
        Được gọi khi người dùng QUAY LẠI study zone sau khi xao nhãng.
        Lưu distraction nếu duration >= 10s.
        """
        print(f"[DEBUG] _on_distraction_recorded called: app={app_name}, duration={duration_seconds}s")
        if self._session_id is not None:
            save_distraction(self._session_id, app_name, duration_seconds)
            print(f"[DEBUG] Saved to DB: session_id={self._session_id}, app={app_name}, duration={duration_seconds}s")

    # ------------------------------------------------------------------
    # CALLBACK: Phiên kết thúc (từ TreeWidget)
    # ------------------------------------------------------------------
    def _on_session_finished(self, elapsed_seconds: int):
        """Được gọi khi người dùng bấm ✕ hoặc hết giờ đếm ngược."""

        # 1. Lưu distraction đang diễn ra (nếu có) trước khi dừng tracker
        if self.tracker_thread and self.tracker_thread.isRunning():
            app_name, duration = self.tracker_thread.get_pending_distraction()
            if app_name and self._session_id is not None:
                # Lưu distraction chưa hoàn thành nếu >= 10s
                print(f"[DEBUG] Session ending - saving pending distraction: app={app_name}, duration={duration}s")
                save_distraction(self._session_id, app_name, duration)
                print(f"[DEBUG] Saved to DB: session_id={self._session_id}, app={app_name}, duration={duration}s")

        # 2. Dừng Tracker
        if self.tracker_thread and self.tracker_thread.isRunning():
            self.tracker_thread.stop()
            self.tracker_thread = None

        # 3. Lấy thống kê xao nhãng để tính thời gian thực học
        stats = get_distraction_stats(self._session_id) if self._session_id else {}
        total_distraction = stats.get("total_seconds", 0)

        # 4. Tính thời gian thực học = Tổng thời gian - Thời gian xao nhãng
        actual_study_seconds = max(0, elapsed_seconds - total_distraction)

        print(f"[DEBUG] Session summary: elapsed={elapsed_seconds}s, distraction={total_distraction}s, actual_study={actual_study_seconds}s")

        # 5. Tính trạng thái (logic giống SummaryDialog)
        target_seconds = self._target_mins * 60
        distraction_threshold = target_seconds // 2  # 50% thời gian khai báo
        status = (
            "success" if (
                elapsed_seconds >= target_seconds and
                total_distraction < distraction_threshold
            ) else "failed"
        )

        # 6. Cập nhật DB (lưu actual_study_seconds - chính xác)
        if self._session_id is not None:
            close_session(self._session_id, actual_study_seconds, status)

        self._session_id = None

        # 7. Hiển thị màn hình Tổng kết
        dialog = SummaryDialog(
            subject=self._current_subject,
            target_mins=self._target_mins,
            elapsed_seconds=elapsed_seconds,
            distraction_stats=stats,
            parent=self.window(),
        )
        dialog.exec()

        # 8. Khôi phục nút bắt đầu
        self.start_btn.setEnabled(True)
        self.start_btn.setText("BẮT ĐẦU TRỒNG CÂY")
