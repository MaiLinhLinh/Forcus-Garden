# Focus Garden MVP Improvements - Implementation Plan

**Date**: 2026-04-09
**Planner**: planner
**Plan Location**: `plans/260409-1640-focus-garden-mvp-improvements/`

---

## Executive Summary

Comprehensive implementation plan for Focus Garden MVP improvements based on user brainstorm decisions. Plan addresses critical distraction tracking bug and adds UX enhancements for Vietnamese student users.

**Total Effort**: 18-27 hours
**Priority**: P1 (Phases 1-2), P2 (Phases 3-4)

---

## User Decisions Applied

| Decision | Value | Implementation |
|----------|-------|----------------|
| Distraction buffer | 10s, hardcoded | Phase 1 |
| Multi-monitor | Tree on all screens | Phase 4 |
| Crash recovery | Not needed | N/A |
| Data export | Not needed | N/A |
| Study Zone UX | Hybrid (Templates + Auto-detect) | Phase 3 |
| Config file | Hardcoded is fine | Constants file |
| Language | Vietnamese only | UI strings only |

---

## Phase Breakdown

### Phase 1: Fix Distraction Tracking Bug (4-6h) ⭐ HIGHEST PRIORITY

**Problem**: Current implementation saves inaccurate distraction durations (always 10s or multiples of 30s)

**Solution**: Event-based state machine
- States: `FOCUSING` ↔ `DISTRACTED`
- Save duration on `DISTRACTED` → `FOCUSING` transition
- Only save if duration >= 10s buffer

**Files**:
- Modify: `core/tracker.py`, `ui/create_session_widget.py`
- New signal: `distraction_recorded(app_name, duration_seconds)`

**Key Code Pattern**:
```python
if is_valid and self.state == "DISTRACTED":
    duration = int(time.time() - self.distraction_start_time)
    if duration >= self.buffer_seconds:
        self.distraction_recorded.emit(current_app, duration)
    self.state = "FOCUSING"
```

---

### Phase 2: History Tab Implementation (2-3h) ⭐ HIGH PRIORITY

**Problem**: Stub implementation shows placeholder text only

**Solution**: Functional table view with database query

**UI**:
```
+-----------+------------+----------+----------+------------+
| Ngày      | Môn học    | Mục tiêu | Thực tế | Trạng thái |
+-----------+------------+----------+----------+------------+
| 09/04 15:30| Python    | 25 phút  | 23 phút  | ❌         |
| 09/04 14:00| Toán      | 30 phút  | 30 phút  | ✅         |
+-----------+------------+----------+----------+------------+
```

**Files**:
- Modify: `ui/history_widget.py`, `database/session_repo.py`
- New function: `get_all_sessions(limit=100)`

**Features**:
- Newest sessions first
- Color-coded status
- Refresh on tab open
- Empty state handling

---

### Phase 3: Study Zone UX (Hybrid Approach) (8-12h)

**Problem**: Manual keyword entry is error-prone and time-consuming

**Solution**: Templates + Auto-detection + Manual edit

**Templates**:
- YouTube, Google Docs, VS Code, Notion, Zoom
- Emoji icons + Vietnamese descriptions

**Auto-detect**:
```python
def get_open_windows() -> List[Dict]:
    windows = pygetwindow.getAllWindows()
    return [{"title": w.title, "app": extract_app(w.title)} for w in windows]
```

**Files**:
- Create: `core/constants.py`, `utils/window_detector.py`, `ui/study_zone_input.py`
- Modify: `ui/create_session_widget.py`

**Workflow**:
1. Select template → auto-fills keywords
2. Click "Phát hiện cửa sổ" → checklist of open windows
3. Merge selections + manual edit
4. Start session

---

### Phase 4: Multi-monitor Tree Widget (4-6h)

**Problem**: Tree only shows on primary monitor

**Solution**: One widget instance per monitor

**Files**:
- Create: `ui/tree_widget_manager.py`
- Modify: `ui/tree_widget.py`, `ui/create_session_widget.py`

**Key Code**:
```python
class TreeWidgetManager:
    def spawn_on_all_screens(self):
        for screen in QApplication.screens():
            widget = TreeWidget(..., screen=screen)
            self._position_widget(widget, screen)
            widget.show()
```

**Features**:
- Independent collapse/expand per monitor
- Sync timer state across instances
- Close any instance → closes all

---

## File Structure Summary

### New Files
```
core/
  constants.py              # Study zone templates

utils/
  window_detector.py        # get_open_windows()
  __init__.py

ui/
  study_zone_input.py       # Template + detect widget
  tree_widget_manager.py    # Multi-monitor manager
```

### Modified Files
```
core/tracker.py                    # State machine refactor
database/session_repo.py           # Add get_all_sessions()
ui/history_widget.py               # Table implementation
ui/create_session_widget.py        # Integrate new widgets
ui/tree_widget.py                  # Screen parameter
```

---

## Success Metrics

### MVP Criteria
- [ ] Distraction tracking accurate ±5%
- [ ] History tab displays all sessions
- [ ] Study Zone input time < 2 minutes
- [ ] Tree widget visible on all monitors
- [ ] No crashes in normal usage
- [ ] Vietnamese UI throughout

---

## Implementation Order

**Sprint 1** (6-9h):
1. Phase 1: Fix distraction tracking
2. Phase 2: History Tab

**Sprint 2** (12-18h):
3. Phase 3: Study Zone UX
4. Phase 4: Multi-monitor Tree

**Sprint 3** (Polish):
5. Testing
6. Visual design
7. Error handling

---

## Technical Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| State pattern | 2-state machine | Simple, sufficient |
| Database limit | 100 sessions | Prevents UI lag |
| Window detection | pygetwindow | Already in use |
| Multi-monitor | Qt screens API | Built-in, reliable |
| Constants | Hardcoded | User approved |

---

## Unresolved Questions

None - all user questions resolved in brainstorm phase.

---

## Next Steps

1. Review and approve plan
2. Create implementation branch
3. Begin Phase 1 implementation
4. Test after each phase

---

**Report Status**: ✅ Ready for implementation
**Plan Path**: `plans/260409-1640-focus-garden-mvp-improvements/`
