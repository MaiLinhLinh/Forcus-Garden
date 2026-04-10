# Brainstorm Follow-up: User Decisions & Resolutions

**Date**: 2026-04-09
**Follow-up to**: brainstorm-260409-1554-focus-garden-mvp-improvements.md

---

## User Decisions Summary

### ✅ Answered Questions

| # | Question | Decision | Notes |
|---|----------|----------|-------|
| 1 | **Distraction threshold** | 10s, không config | Keep hardcoded for MVP |
| 2 | **Multi-monitor support** | Tree trên tất cả màn hình | Show tree widget on all monitors |
| 3 | **Session resumption** | Không recover | No crash recovery needed |
| 4 | **Data export** | Không cần | Data stays in SQLite only |
| 5 | **Study Zone UX** | **Hybrid approach** | Templates + Auto-detect windows |
| 6 | **Config file** | Hardcoded is fine | No config file needed |
| 7 | **Language** | Vietnamese only | No i18n needed for MVP |
| 8 | **Phase 1 Priority** | Distraction tracking + History Tab | Study Zone UX deferred |

---

## Updated Implementation Plan

### Phase 1: Critical Fixes (MVP Must-Have)

#### 1. Fix Distraction Tracking Bug ⭐ **HIGHEST PRIORITY**
**Problem**: Current implementation không track chính xác total duration

**Solution**: Event-based state machine
```python
# States: FOCUSING ↔ DISTRACTED
# Events: left_study_zone, returned_to_study_zone

class FocusTrackerThread(QThread):
    def __init__(self, allowed_keywords, parent=None):
        super().__init__(parent)
        self.state = "FOCUSING"
        self.distraction_start_time = None
        self.buffer_seconds = 10  # Hardcoded per user decision

    def run(self):
        while not self.isInterruptionRequested():
            is_valid = self._check_window_valid()

            # State transitions
            if is_valid and self.state == "DISTRACTED":
                # User returned: save accurate duration
                duration = int(time.time() - self.distraction_start_time)
                if duration >= self.buffer_seconds:
                    self.distraction_recorded.emit(app_name, duration)
                self.state = "FOCUSING"

            elif not is_valid and self.state == "FOCUSING":
                # User started distraction
                self.state = "DISTRACTED"
                self.distraction_start_time = time.time()
```

**Files to modify**:
- `core/tracker.py` - Refactor to state machine
- `database/session_repo.py` - Ensure save_distraction() handles accurate duration
- `ui/create_session_widget.py` - Update signal handling

**Acceptance criteria**:
- [ ] Distraction duration accurate ±5%
- [ ] State transitions work correctly
- [ ] No double-counting distractions

---

#### 2. Implement History Tab ⭐ **HIGH PRIORITY**
**Requirement**: Basic list view của tất cả sessions

**UI Design**:
```
┌─────────────────────────────────────────────────────┐
│  📜 Lịch Sử Của Bạn                                  │
├─────────────────────────────────────────────────────┤
│  Date          │ Subject │ Target │ Actual │ Status │
├─────────────────────────────────────────────────────┤
│  09/04 15:30   │ Python  │ 25min  │ 23min  │ ✅     │
│  09/04 14:00   │ Math    │ 30min  │ 30min  │ ✅     │
│  08/04 20:00   │ English │ 20min  │ 15min  │ ❌     │
└─────────────────────────────────────────────────────┘
```

**Implementation**:
```python
# ui/history_widget.py
class HistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Ngày", "Môn học", "Mục tiêu", "Thực tế", "Trạng thái"
        ])
        self._load_sessions()

    def _load_sessions(self):
        # Query: SELECT * FROM sessions ORDER BY started_at DESC
        # Populate table with color-coded status
```

**Database query needed**:
```python
# database/session_repo.py
def get_all_sessions(limit: int = 100) -> List[Session]:
    """Get all sessions ordered by date (newest first)"""
    db = get_db()
    try:
        return db.query(Session)\
                 .order_by(Session.started_at.desc())\
                 .limit(limit)\
                 .all()
    finally:
        db.close()
```

**Acceptance criteria**:
- [ ] Display all sessions in table
- [ ] Color-coded status (green = success, orange = failed)
- [ ] Click row → show detail dialog (optional for MVP)
- [ ] Pagination or scroll for >100 sessions

---

### Phase 2: UX Improvements (Post-MVP)

#### 3. Study Zone UX Improvements (Hybrid Approach)
**Decision**: User chọn **Hybrid** = Templates + Auto-detect

**Implementation Plan**:

**Step 1**: Predefined Templates
```python
# constants.py
STUDY_ZONE_TEMPLATES = {
    "YouTube": {
        "keywords": ["youtube - ", "youtube.com"],
        "icon": "📺",
        "description": "Học trên YouTube"
    },
    "Google Docs": {
        "keywords": ["docs.google.com", "- Google Docs"],
        "icon": "📄",
        "description": "Làm việc trên Google Docs"
    },
    "VS Code": {
        "keywords": ["Visual Studio Code", "VS Code"],
        "icon": "💻",
        "description": "Lập trình trên VS Code"
    },
    "Notion": {
        "keywords": ["Notion", "notion.so"],
        "icon": "📝",
        "description": "Ghi chú trên Notion"
    }
}
```

**Step 2**: Auto-detect Open Windows
```python
# utils/window_detector.py
import pygetwindow as gw

def get_open_windows() -> List[dict]:
    """Get list of all open windows"""
    windows = gw.getAllWindows()
    return [
        {
            "title": w.title,
            "app": _extract_app_name(w.title)
        }
        for w in windows
        if w.title and w.visible
    ]

def _extract_app_name(title: str) -> str:
    """Extract app name from window title"""
    # Heuristic: split by first " - " or " — "
    for sep in [" - ", " — "]:
        if sep in title:
            return title.split(sep)[-1]
    return title
```

**Step 3**: UI Component
```python
# ui/study_zone_input.py
class StudyZoneInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Template selection
        self.template_combo = QComboBox()
        self.template_combo.addItems(STUDY_ZONE_TEMPLATES.keys())
        self.template_combo.currentTextChanged.connect(self._apply_template)

        # Auto-detect button
        self.detect_btn = QPushButton("🔍 Phát hiện cửa sổ mở")
        self.detect_btn.clicked.connect(self._detect_windows)

        # Keyword editor
        self.keyword_edit = QTextEdit()

    def _apply_template(self, template_name: str):
        """Auto-fill keywords from template"""
        template = STUDY_ZONE_TEMPLATES[template_name]
        keywords = "\n".join(template["keywords"])
        self.keyword_edit.setPlainText(keywords)

    def _detect_windows(self):
        """Show checklist of open windows"""
        windows = get_open_windows()
        # Show dialog with checkboxes
        # User selects which windows are valid
        # Merge selected titles into keyword_edit
```

**Acceptance criteria**:
- [ ] Templates auto-fill keywords correctly
- [ ] Auto-detect lists all open windows
- [ ] User can merge templates + detected windows
- [ ] Manual editing still works

---

#### 4. Tree Widget Multi-Monitor Support
**Decision**: Tree widget hiển thị trên **tất cả màn hình**

**Implementation Options**:

**Option A**: Single Widget, Cloned Positions
```python
# Position tree on each monitor
screens = QApplication.screens()
for screen in screens:
    geo = screen.availableGeometry()
    tree = TreeWidget(...)
    tree.move(
        geo.right() - tree.width() - 20,
        geo.bottom() - tree.height() - 20
    )
    tree.show()
```

**Option B**: One Widget per Monitor (Better UX)
```python
class TreeWidgetManager:
    def __init__(self, duration, subject):
        self.widgets = []
        for screen in QApplication.screens():
            widget = TreeWidget(duration, subject, screen)
            self.widgets.append(widget)
            widget.show()

    def close_all(self):
        for widget in self.widgets:
            widget.close()
```

**Acceptance criteria**:
- [ ] Tree appears on all monitors
- [ ] Independent collapse/expand per monitor
- [ ] Sync timer state across all instances

---

## Technical Decisions

### Constants (Hardcoded per user request)
```python
# core/constants.py
DISTRACTION_BUFFER_SECONDS = 10
TRACKER_POLL_INTERVAL_MS = 1000
DISTRACTION_ALERT_INTERVAL_SECONDS = 30
```

### Language (Vietnamese only)
- No i18n framework needed
- All UI strings in Vietnamese
- No language switching UI

### No Crash Recovery
- Sessions lost if app crashes
- Simpler implementation
- Acceptable for MVP

### No Data Export
- SQLite only
- No CSV/JSON export
- Data stays local

---

## Updated Priority Order

### Sprint 1: Core Functionality
1. ✅ Fix distraction tracking bug
2. ✅ Implement History Tab

### Sprint 2: UX Improvements
3. ✅ Study Zone UX (Hybrid approach)
4. ✅ Tree Widget multi-monitor support

### Sprint 3: Polish
5. Visual design improvements
6. Error handling & logging
7. Code refactoring

---

## Implementation Complexity Assessment

| Feature | Complexity | Est. Time | Risk |
|---------|-----------|-----------|------|
| Fix distraction tracking | Medium | 4-6h | Medium |
| History Tab | Low | 2-3h | Low |
| Study Zone Hybrid | High | 8-12h | High |
| Multi-monitor Tree | Medium | 4-6h | Medium |

**Total MVP**: ~18-27 hours

---

## Success Metrics (Updated)

### MVP Success Criteria
- [ ] Distraction tracking accurate (±5%)
- [ ] History tab displays all sessions
- [ ] Study Zone input time < 2 minutes
- [ ] Tree widget visible on all monitors
- [ ] No crashes in normal usage
- [ ] Vietnamese UI throughout

### Post-MVP Metrics
- User study time increase
- Distraction reduction
- Session completion rate

---

## Open Questions (All Resolved ✅)

- [x] Distraction threshold: **10s, hardcoded**
- [x] Multi-monitor: **Show on all monitors**
- [x] Crash recovery: **Not needed**
- [x] Data export: **Not needed**
- [x] Study Zone UX: **Hybrid approach**
- [x] Config file: **Hardcoded is fine**
- [x] Language: **Vietnamese only**

---

## Next Steps

User has 2 options:

1. **Self-implementation**: Use this report as implementation guide
2. **Create detailed plan**: Run `/ck:plan` để generate detailed implementation phases

If choosing option 2, the plan will include:
- Phase 1: Fix distraction tracking
- Phase 2: Implement History Tab
- Phase 3: Study Zone UX improvements
- Phase 4: Multi-monitor tree widget
- Phase 5: Testing & polish

---

**Report Status**: ✅ All open questions resolved
**Ready for**: Implementation planning or coding
