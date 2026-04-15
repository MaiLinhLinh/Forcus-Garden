from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QPushButton, QTextEdit,
                             QMessageBox, QApplication, QFrame)
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import Qt
import re

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
        # Outer layout centers the form card
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Card container ────────────────────────────────────────────
        card = QFrame()
        card.setFixedWidth(560)
        card.setStyleSheet("""
            QFrame {
                background-color: #232a3e;
                border-radius: 16px;
                border: 1px solid rgba(74, 222, 128, 0.12);
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(10)

        # ── Header ────────────────────────────────────────────────────
        icon_label = QLabel("🌱")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; background: transparent; border: none; padding: 0; margin: 0;")
        layout.addWidget(icon_label)

        title_label = QLabel("Tạo Phiên Học Mới")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px; font-weight: bold; color: #4ade80;
            background: transparent; border: none;
            padding: 0; margin: 0;
        """)
        layout.addWidget(title_label)

        subtitle = QLabel("Khai báo mục tiêu và bắt đầu trồng cây 🌿")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 13px; color: #94a3b8;
            background: transparent; border: none;
            padding: 0; margin-bottom: 8px;
        """)
        layout.addWidget(subtitle)

        # ── Divider ───────────────────────────────────────────────────
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: rgba(74, 222, 128, 0.15); max-height: 1px; border: none;")
        layout.addWidget(divider)
        layout.addSpacing(6)

        # ── Tên Môn Học ───────────────────────────────────────────────
        label_subject = QLabel("📚  Môn Học / Hoạt Động")
        label_subject.setStyleSheet("font-size: 13px; font-weight: 600; color: #cbd5e1; background: transparent; border: none;")
        layout.addWidget(label_subject)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("VD: Lập trình Python, Ôn thi Giải tích...")
        self.subject_input.setMinimumHeight(42)
        layout.addWidget(self.subject_input)
        layout.addSpacing(4)

        # ── Thời lượng ────────────────────────────────────────────────
        label_duration = QLabel("⏱️  Thời Lượng (Phút)")
        label_duration.setStyleSheet("font-size: 13px; font-weight: 600; color: #cbd5e1; background: transparent; border: none;")
        layout.addWidget(label_duration)

        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 480)
        self.duration_input.setValue(25)
        self.duration_input.setMinimumHeight(42)
        self.duration_input.setSuffix("  phút")
        layout.addWidget(self.duration_input)
        layout.addSpacing(4)

        # ── Study Zone ────────────────────────────────────────────────
        label_zone = QLabel("🛡️  Study Zone")
        label_zone.setStyleSheet("font-size: 13px; font-weight: 600; color: #cbd5e1; background: transparent; border: none;")
        layout.addWidget(label_zone)

        zone_hint = QLabel("Chỉ các app trong danh sách mới được phép · Mỗi từ khóa trên 1 dòng")
        zone_hint.setStyleSheet("font-size: 11px; color: #64748b; background: transparent; border: none; margin-bottom: 2px;")
        layout.addWidget(zone_hint)

        self.zone_input = QTextEdit()
        self.zone_input.setPlaceholderText(
            "💡 Tên app nên dùng: vscode, chrome, word, python\n"
            "❌ Không nên dùng tên dự án cụ thể\n\n"
            "Ví dụ:\n"
            "vscode\n"
            "chrome\n"
            "github\n"
            "python"
        )
        self.zone_input.setMinimumHeight(120)
        self.zone_input.setMaximumHeight(160)
        layout.addWidget(self.zone_input)

        layout.addSpacing(8)

        # ── Nút Bắt đầu ──────────────────────────────────────────────
        self.start_btn = QPushButton("🌱  BẮT ĐẦU TRỒNG CÂY")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: #052e16;
                font-weight: bold;
                font-size: 16px;
                padding: 14px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4ade80;
            }
            QPushButton:pressed {
                background-color: #16a34a;
            }
            QPushButton:disabled {
                background-color: #1e3a2f;
                color: #4ade80;
                border: 1px solid rgba(74, 222, 128, 0.25);
            }
        """)
        self.start_btn.clicked.connect(self._on_start)
        layout.addWidget(self.start_btn)

        outer.addWidget(card)

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

        # Validate keywords for common mistakes
        suspicious_keywords = []
        for kw in keywords:
            # Check for overly specific patterns
            if len(kw) > 15:  # Very long keywords are likely project names
                suspicious_keywords.append(f"'{kw}' (quá dài)")
            elif re.match(r'^[A-Z][a-z]+$', kw) and len(kw) > 5:  # Proper nouns
                suspicious_keywords.append(f"'{kw}' (tên riêng)")

        if suspicious_keywords:
            msg = "Cảnh báo: Các từ khóa sau có thể quá cụ thể:\n\n"
            msg += "\n".join(f"  • {kw}" for kw in suspicious_keywords)
            msg += "\n\n💡 Nên dùng tên app chung như: vscode, chrome, word, python"
            msg += "\n\nBạn có muốn tiếp tục không?"
            reply = QMessageBox.question(
                self, "Cảnh báo Study Zone",
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # --- Lưu Session vào DB ---
        self._session_id = create_session(subject, duration, keywords)
        self._current_subject = subject
        self._target_mins = duration

        # --- Vô hiệu hoá nút ---
        self.start_btn.setEnabled(False)
        self.start_btn.setText("🌿  ĐANG HỌC...")

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
        print(f"[DEBUG] ===== _on_session_finished called =====")
        print(f"[DEBUG] elapsed_seconds={elapsed_seconds}")

        # 1. Lưu distraction đang diễn ra (nếu có) trước khi dừng tracker
        if self.tracker_thread and self.tracker_thread.isRunning():
            app_name, duration = self.tracker_thread.get_pending_distraction()
            if app_name and self._session_id is not None:
                # Lưu distraction chưa hoàn thành nếu >= 10s
                print(f"[DEBUG] Session ending - saving pending distraction: app={app_name}, duration={duration}s")
                save_distraction(self._session_id, app_name, duration)
                print(f"[DEBUG] Saved to DB: session_id={self._session_id}, app={app_name}, duration={duration}s")
            else:
                print(f"[DEBUG] No pending distraction to save (app_name={app_name}, session_id={self._session_id})")

        # 2. Dừng Tracker
        if self.tracker_thread and self.tracker_thread.isRunning():
            self.tracker_thread.stop()
            self.tracker_thread = None
            print(f"[DEBUG] Tracker stopped")

        # 3. Lấy thống kê xao nhãng để tính thời gian thực học
        print(f"[DEBUG] Fetching distraction stats from DB...")
        stats = get_distraction_stats(self._session_id) if self._session_id else {}
        total_distraction = stats.get("total_seconds", 0)
        distraction_count = stats.get("count", 0)

        print(f"[DEBUG] Stats received: count={distraction_count}, total_seconds={total_distraction}")
        print(f"[DEBUG] Details list length: {len(stats.get('details', []))}")

        # 4. Tính thời gian thực học = Tổng thời gian - Thời gian xao nhãng
        actual_study_seconds = max(0, elapsed_seconds - total_distraction)

        print(f"[DEBUG] Session summary calculation:")
        print(f"[DEBUG]   elapsed={elapsed_seconds}s")
        print(f"[DEBUG]   distraction={total_distraction}s")
        print(f"[DEBUG]   actual_study={actual_study_seconds}s")

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
            print(f"[DEBUG] Session closed in DB with status={status}")

        self._session_id = None

        # 7. Hiển thị màn hình Tổng kết
        print(f"[DEBUG] Creating SummaryDialog with stats...")

        # VALIDATION: Ensure data consistency before passing to UI
        details_list = stats.get('details', [])
        expected_count = stats.get('count', 0)
        actual_count = len(details_list)
        expected_total = stats.get('total_seconds', 0)
        actual_total = sum(d['seconds'] for d in details_list)

        print(f"[DEBUG] Passing to SummaryDialog:")
        print(f"[DEBUG]   - count={distraction_count}, total_seconds={total_distraction}")
        print(f"[DEBUG]   - details list length: {actual_count}")
        print(f"[DEBUG]   - sum of detail seconds: {actual_total}")

        # Data integrity validation
        if expected_count != actual_count:
            print(f"[ERROR] VALIDATION FAILED: count={expected_count} != details length={actual_count}!")
            print(f"[ERROR] This indicates a data consistency issue!")
        if expected_total != actual_total:
            print(f"[ERROR] VALIDATION FAILED: total_seconds={expected_total} != sum details={actual_total}!")
            print(f"[ERROR] This indicates a calculation error!")

        print(f"[DEBUG] Details to be passed: {details_list}")

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
        self.start_btn.setText("🌱  BẮT ĐẦU TRỒNG CÂY")
        print(f"[DEBUG] ===== _on_session_finished completed =====")
