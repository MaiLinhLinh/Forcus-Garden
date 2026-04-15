import time
import pygetwindow as gw
from PyQt6.QtCore import QThread, pyqtSignal
from core.matcher import KeywordMatcher
from core.browser_parser import BrowserTitleParser

class FocusTrackerThread(QThread):
    """
    Luồng chạy ngầm (Background Thread) tách biệt khỏi giao diện người dùng.
    Nhiệm vụ: Liên tục quét hệ điều hành mỗi giây 1 lần để xem người dùng
    đang focus vào cửa sổ nào. Nếu không hợp lệ, ghi đếm số lần xao nhãng.

    State Machine: FOCUSING <-> DISTRACTED
    - Chỉ lưu distraction khi chuyển từ DISTRACTED -> FOCUSING
    - Hoặc khi session kết thúc mà đang ở trạng thái DISTRACTED
    """

    # State constants
    STATE_FOCUSING = "FOCUSING"
    STATE_DISTRACTED = "DISTRACTED"

    # Whitelist: These window titles are always considered valid (not distractions)
    # This prevents the app's own window from being detected as a distraction
    WHITELIST_TITLES = [
        "focus garden",
        "dashboard",
        "create session",
        "session summary",
    ]

    # Signal gửi trạng thái real-time: (Đang xao nhãng True/False, Tiêu đề app hiện tại)
    status_updated = pyqtSignal(bool, str)

    # Signal gửi khi distraction hoàn thành: (app_name, duration_seconds)
    # Chỉ emit khi người dùng QUAY LẠI study zone (hoặc session kết thúc)
    distraction_recorded = pyqtSignal(str, int)

    def __init__(self, allowed_keywords, parent=None):
        super().__init__(parent)
        # Phase 1: Use KeywordMatcher instead of simple list
        # OLD: self.allowed_keywords = [kw.strip().lower() for kw in allowed_keywords if kw.strip()]
        # NEW: Fuzzy matching with RapidFuzz
        self.matcher = KeywordMatcher(allowed_keywords, threshold=90)
        # Phase 4: Add browser title parser
        self.browser_parser = BrowserTitleParser()
        self.buffer_seconds = 5  # Chỉ lưu distraction >= 5 giây (reduced from 10s)

        # State machine variables
        self.state = self.STATE_FOCUSING
        self.distraction_start_time = None
        self._distraction_app_name = ""  # Lưu tên app xao nhãng (KHÔNG thay đổi khi quay lại)
        self._is_saved = False  # FLAG: Đã lưu distraction này chưa?

    def run(self):
        """Main tracking loop với state machine logic."""
        while not self.isInterruptionRequested():
            try:
                active_window = gw.getActiveWindow()
                if active_window and active_window.title:
                    current_app_name = active_window.title
                    title = active_window.title

                    # Check whitelist first (app's own windows should never be distractions)
                    title_lower = title.lower()
                    is_whitelisted = any(whitelist_term in title_lower for whitelist_term in self.WHITELIST_TITLES)

                    if is_whitelisted:
                        is_valid = True  # Whitelisted windows are always valid
                    else:
                        # Phase 4: Parse browser titles for better matching
                        parsed_site, is_browser = self.browser_parser.parse(title)
                        if is_browser:
                            # Use extracted site name for matching, or full title if extraction failed
                            title_to_check = parsed_site if parsed_site else title
                            is_valid = self.matcher.is_match(title_to_check)
                        else:
                            # Non-browser or couldn't parse - use full title
                            is_valid = self.matcher.is_match(title)

                    # === TRANSITION: DISTRACTED -> FOCUSING ===
                    # Người dùng quay lại study zone
                    if is_valid and self.state == self.STATE_DISTRACTED:
                        duration = int(time.time() - self.distraction_start_time)
                        if duration >= self.buffer_seconds and not self._is_saved:
                            # Lưu app xao nhãng (đã lưu từ trước, không phải app hiện tại)
                            print(f"[DEBUG] Emitting distraction_recorded: {self._distraction_app_name}, {duration}s")
                            self.distraction_recorded.emit(self._distraction_app_name, duration)
                            self._is_saved = True  # Đánh dấu đã lưu

                        # Reset về focusing
                        self.state = self.STATE_FOCUSING
                        self.distraction_start_time = None
                        self._distraction_app_name = ""
                        self.status_updated.emit(False, current_app_name)

                    # === TRANSITION: FOCUSING -> DISTRACTED ===
                    # Người dùng rời khỏi study zone
                    elif not is_valid and self.state == self.STATE_FOCUSING:
                        self.state = self.STATE_DISTRACTED
                        self.distraction_start_time = time.time()
                        self._distraction_app_name = current_app_name  # Lưu tên app xao nhãng NGAY LẬP TỨC
                        self._is_saved = False  # Reset flag - distraction mới chưa lưu
                        self.status_updated.emit(True, current_app_name)

                    # === STAY IN DISTRACTED ===
                    # Đang xao nhãng tiếp tục
                    elif not is_valid and self.state == self.STATE_DISTRACTED:
                        # Check if user switched to a different distraction app
                        if current_app_name != self._distraction_app_name:
                            # Save previous distraction if it was long enough
                            duration = int(time.time() - self.distraction_start_time)
                            if duration >= self.buffer_seconds and not self._is_saved:
                                print(f"[DEBUG] App switch detected - Saving previous distraction: {self._distraction_app_name}, {duration}s")
                                self.distraction_recorded.emit(self._distraction_app_name, duration)
                                self._is_saved = True

                            # Start tracking new distraction app
                            self._distraction_app_name = current_app_name
                            self.distraction_start_time = time.time()
                            self._is_saved = False  # Reset flag for new distraction

                        # Update status (UI hiển thị real-time)
                        self.status_updated.emit(True, current_app_name)

                    # === STAY IN FOCUSING ===
                    # Đường học hiệu quả tiếp tục
                    elif is_valid and self.state == self.STATE_FOCUSING:
                        self.status_updated.emit(False, current_app_name)

                # Nếu active_window là None (lock screen, desktop trắng, ...)
                # Giữ nguyên state hiện tại, không emit signal
            except Exception as e:
                print(f"[DEBUG] Exception in tracker: {e}")
                pass

            time.sleep(1)  # Nhịp đập: 1 giây quét 1 lần

    def get_pending_distraction(self):
        """
        Lấy thông tin distraction đang diễn ra (nếu có).
        Được gọi khi session kết thúc để lưu distraction chưa hoàn thành.

        Returns:
            tuple: (app_name, duration_seconds) hoặc (None, 0) nếu không có
        """
        print(f"[DEBUG] ===== get_pending_distraction =====")
        print(f"[DEBUG] Current state: {self.state}")
        print(f"[DEBUG] distraction_start_time: {self.distraction_start_time}")
        print(f"[DEBUG] _is_saved: {self._is_saved}")
        print(f"[DEBUG] _distraction_app_name: {self._distraction_app_name}")

        if self.state == self.STATE_DISTRACTED and self.distraction_start_time and not self._is_saved:
            duration = int(time.time() - self.distraction_start_time)
            print(f"[DEBUG] Calculated duration: {duration}s, buffer: {self.buffer_seconds}s")

            if duration >= self.buffer_seconds:
                print(f"[DEBUG] Pending distraction FOUND: {self._distraction_app_name}, {duration}s")
                return (self._distraction_app_name, duration)
            else:
                print(f"[DEBUG] Duration too short to save")
        else:
            print(f"[DEBUG] No pending distraction (state={self.state}, has_start_time={bool(self.distraction_start_time)}, is_saved={self._is_saved})")

        print(f"[DEBUG] ===== END get_pending_distraction =====")
        return (None, 0)

    def stop(self):
        """Hàm dừng luồng Tracking an toàn khi phiên học kết thúc"""
        self.requestInterruption()
        self.wait()
