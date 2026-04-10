# Brainstorm Report: Focus Garden MVP Improvements

**Date**: 2026-04-09
**Context**: Cải thiện và làm rõ chức năng dự án app desktop Focus Garden

---

## 1. Current State Analysis

### ✅ Đã Implement (Khá Hoàn Chỉnh)
- **Database**: SQLAlchemy + SQLite
  - User, Session, StudyZone, Distraction models
  - Repository pattern với `session_repo.py`
- **Core Tracking**: `FocusTrackerThread` (QThread)
  - Poll active window mỗi 1s bằng `pygetwindow`
  - 10s buffer trước khi count là xao nhãng
  - Emit `distraction_alert` signal
- **UI Components**:
  - MainWindow: 2 tabs ("Trồng Cây", "Lịch Sử")
  - CreateSessionWidget: Form tạo phiên
  - TreeWidget: Floating widget, draggable, always-on-top
  - SummaryDialog: Màn hình tổng kết
- **Workflow**: Tạo phiên → Tracker → Tree → Summary → Done

### ❌ Vấn Phát Hiện

#### Critical Bug: Distraction Duration Tracking
**Vấn đề**: Tracker không track chính xác tổng thời gian xao nhãng

**Hiện tại**:
```python
# tracker.py line 48-52
if elapsed == self.buffer_seconds:
    self.distraction_alert.emit(active_window.title, elapsed)
elif elapsed > self.buffer_seconds and (elapsed - self.buffer_seconds) % 30 == 0:
    self.distraction_alert.emit(active_window.title, elapsed)
```

**Sai ở đâu**:
- Chỉ emit alert tại 10s, 40s, 70s, 100s...
- **KHÔNG ghi nhận khi user quay lại Study Zone**
- Nếu user xao nhãng 25s rồi quay lại: chỉ ghi nhận 10s, mất 15s
- `save_distraction()` chỉ gọi khi alert fire, không có "end time"

**Nên làm**:
- Ghi nhận `distraction_start_time` khi bắt đầu xao nhãng
- Khi quay lại Study Zone: tính `end_time - start_time` → save accurate duration
- Track theo **events**: "distraction_started" và "distraction_ended"

#### UX Issues (User Feedback)

**1. Study Zone Input - Rất Tệ**
- User không hiểu nhập gì
- Examples không rõ ràng
- **Critical requirement**: User muốn chọn **specific tab**, không chỉ app
  - Ví dụ: "YouTube tab cụ thể", không chỉ "Chrome"
  - Current implementation chỉ match keywords in window title

**2. Tree Widget Placement**
- Vị trí mặc định góc phải dưới có thể can thiệp vào việc
- User không biết có thể drag được (không có visual cue)
- Không có option lưu vị trí cho lần sau

**3. Visual Design**
- Màu sắc, font, spacing cần cải thiện
- Không có consistent design system

---

## 2. Proposed Solutions

### A. Distraction Tracking Fix (Priority 1)

**Approach**: Event-based tracking với state machine

```python
# States: FOCUSING → DISTRACTED
# Events: left_study_zone, returned_to_study_zone

class FocusTrackerThread(QThread):
    def __init__(self, allowed_keywords, parent=None):
        super().__init__(parent)
        self.state = "FOCUSING"
        self.distraction_start_time = None
        self.last_distraction_duration = 0

    def run(self):
        while not self.isInterruptionRequested():
            is_valid = self._check_window_valid()

            if is_valid and self.state == "DISTRACTED":
                # User quay lại: save distraction duration
                duration = int(time.time() - self.distraction_start_time)
                if duration >= self.buffer_seconds:
                    self.distraction_recorded.emit(app_name, duration)
                self.state = "FOCUSING"
                self.distraction_start_time = None

            elif not is_valid and self.state == "FOCUSING":
                # User bắt đầu xao nhãng
                self.state = "DISTRACTED"
                self.distraction_start_time = time.time()

            time.sleep(1)
```

**Pros**:
- Track chính xác 100% thời gian
- State machine rõ ràng, dễ debug
- Không cần emit nhiều alerts

**Cons**:
- Phải refactor tracker code
- Cần test kỹ edge cases

---

### B. Study Zone UX Improvement (Priority 2)

**User Requirement**: Select specific tab, not just app

**Challenge**:
- `pygetwindow` chỉ get active window title
- Không thể list tất cả tabs trong browser
- Browser tabs không exposed qua OS-level APIs

**Possible Solutions**:

#### Option 1: Enhanced Keyword Matching (Realistic for MVP)
- Cải thiện input UX với predefined apps
- Hướng dẫn user nhập specific keywords
- Examples rõ ràng hơn

**Implementation**:
```python
# Predefined templates
PREDEFINED_TEMPLATES = {
    "YouTube": ["youtube - ", "youtube.com"],
    "Google Docs": ["docs.google.com", "- Google Docs"],
    "VS Code": ["Visual Studio Code", "VS Code"],
    "Notion": ["Notion", "notion.so"],
}

# UI: Dropdown để chọn template
# Khi chọn: auto-fill keywords vào text area
# User có thể edit/add keywords
```

**Pros**:
- Dễ implement với current architecture
- Giúp user hiểu rõ hơn cần nhập gì
- Flexible với custom keywords

**Cons**:
- Vẫn dựa trên keyword matching
- Không thể detect specific tab 100%

#### Option 2: Browser Extension (Best UX, High Effort)
- Build browser extension để list open tabs
- Extension communicate với desktop app
- User select specific tabs từ real list

**Pros**:
- UX tuyệt vời: select real tabs
- Accuracy 100%

**Cons**:
- Phải build extension (Chrome/Firefox)
- Communication phức tạp (extension → native app)
- Out of MVP scope

#### Option 3: Auto-detect Open Windows (Middle Ground)
- List tất cả open windows khi tạo session
- User select from real list (not browser tabs, but windows)
- Save window titles vào Study Zone

**Implementation**:
```python
import pygetwindow as gw

def get_all_open_windows():
    windows = gw.getAllWindows()
    return [(w.title, w.title.lower()) for w in windows if w.title]

# UI: Checklist của open windows
# User check哪些 windows hợp lệ
```

**Pros**:
- Real data, không đoán
- Dễ implement
- Hỗ trợ multi-window apps (VS Code, Word)

**Cons**:
- Vẫn không detect browser tabs
- User phải select lại mỗi lần (không persistent)

**Recommendation cho MVP**: **Option 1 + Option 3 hybrid**
- Predefined templates cho common apps
- Auto-detect open windows để suggest
- Flexible keyword editing

---

### C. Tree Widget UX Improvements (Priority 3)

**Issues**:
- Placement không phù hợp
- Không có visual drag cue
- Không save position

**Solutions**:

1. **Smart Placement**:
   - Detect screen size
   - Avoid overlapping với taskbar/dock
   - Remember last position

2. **Visual Improvements**:
   - Add drag handle icon
   - Show position indicator when dragging
   - Add "Reset Position" button

3. **Collapse State Persistence**:
   - Remember collapsed/expanded
   - Auto-collapse on hover (optional)

---

### D. History Tab Implementation (Priority 4)

**Basic List Requirements**:
- List tất cả sessions
- Columns: Date, Subject, Target, Actual, Status, Distractions
- Pagination hoặc scroll
- Click để xem details

**Implementation**:
```python
# history_widget.py
class HistoryWidget(QWidget):
    def __init__(self):
        # QTableWidget để display sessions
        # Query từ DB: SELECT * FROM sessions ORDER BY started_at DESC
        # Color code: success = green, failed = orange
```

---

## 3. Updated Functional Specs

### Study Zone (Improved)
**Input Method**:
1. **Predefined Apps Dropdown**:
   - YouTube, Google Docs, VS Code, Notion, Stack Overflow, etc.
   - Khi chọn: auto-fill keywords

2. **Auto-detect Open Windows**:
   - Button "Detect Open Windows"
   - Show checklist of open windows
   - User check哪些 hợp lệ

3. **Manual Keyword Input**:
   - Text area để edit/add custom keywords
   - Examples rõ ràng:
     ```
     Examples:
     - YouTube: "youtube - ", "youtube.com"
     - Docs: "docs.google.com", "Google Docs"
     - VS Code: "Visual Studio Code", ".py -"
     ```

### Distraction Tracking (Fixed)
**Behavior**:
- Track theo events: started → ended
- Calculate accurate duration
- Save to DB với proper timestamps

**Database Schema** (no change needed):
```python
class Distraction(Base):
    app_name: str        # Tên app xao nhãng
    duration_seconds: int  # **Accurate** total duration
    timestamp: datetime    # Khi distraction STARTED
```

### Tree Widget (UX Improved)
**Features**:
- Smart initial placement
- Draggable with visual cue
- Remember last position
- Collapse state persistent
- **Silent mode**: No feedback during distraction (user requirement)

### History Tab (New)
**Display**:
- Table format: Date | Subject | Target | Actual | Status | Distractions
- Color coding for status
- Click row → show detail dialog
- Filter by date range (optional)

---

## 4. Implementation Priorities

### Phase 1: Critical Fixes (Must Have)
1. **Fix distraction tracking bug** → Event-based state machine
2. **Improve Study Zone UX** → Predefined templates + auto-detect
3. **Implement History Tab** → Basic list view

### Phase 2: UX Improvements (Should Have)
4. **Tree Widget placement** → Smart positioning + persistence
5. **Visual design polish** → Consistent colors, fonts, spacing

### Phase 3: Nice to Have (Future)
6. **Advanced analytics** → Charts, streaks, statistics
7. **Browser extension** → Specific tab selection
8. **Idle detection** → Mouse/keyboard inactivity

---

## 5. Technical Debt & Risks

### Current Issues
1. **No error handling** in tracker thread (bare `except: pass`)
2. **Database connection** per query (inefficient)
3. **No logging** for debugging
4. **Hardcoded values** (10s buffer, no config)
5. **User authentication** planned but not used (user_id nullable)

### Recommendations
- Add logging module
- Implement connection pooling
- Add config file for constants
- Graceful error handling in tracker
- Consider future auth implementation

---

## 6. Open Questions

1. **Distraction threshold**: 10s buffer có hợp lý? Có nên configurable?
2. **Multi-monitor support**: Tree widget trên màn hình nào?
3. **Session resumption**: Nếu app crash, có recover session không?
4. **Data export**: User có muốn export data không?
5. **Language**: Vietnamese only hay i18n support?

---

## 7. Success Metrics

### MVP Success Criteria
- [ ] Distraction tracking accurate (±5%)
- [ ] Study Zone input clarity (user testing < 2min to understand)
- [ ] History tab displays all sessions correctly
- [ ] No crashes in normal usage
- [ ] Tree widget placement acceptable

### Future Metrics
- User retention (daily active users)
- Average session completion rate
- Distraction reduction over time

---

## Next Steps

User cần:
1. Review và feedback về proposed solutions
2. Quyết định approach cho Study Zone UX (Option 1 vs Option 3)
3. Approve implementation priorities

Sau khi approved:
- Run `/ck:plan` với context này để tạo detailed implementation plan
- Implement Phase 1 (Critical Fixes)
- Testing và iteration
- Document và deploy

---

**Unresolved Questions**:
- Multi-monitor support?
- Config file for constants?
- Crash recovery mechanism?
