---
# Phase 1: Fix Distraction Tracking Bug

## Context Links
- Brainstorm decisions: `plans/reports/brainstorm-decisions-260409-1640-user-resolutions.md`
- Current tracker: `core/tracker.py`
- Session repo: `database/session_repo.py`

## Overview
**Priority**: P1 (Highest)
**Status**: pending
**Description**: Refactor distraction tracking to use event-based state machine for accurate duration recording

## Key Insights

### Current Bug Analysis
Current implementation in `core/tracker.py`:
- Emits `distraction_alert` at `elapsed == buffer_seconds` (10s)
- Emits again every 30s thereafter
- **Problem**: Duration saved is always 10s or multiples of 30s, NOT actual distraction time
- **Missing**: No event when user RETURNS to study zone

### Root Cause
Tracker only saves distraction when alert fires, not when distraction actually ends. Need to:
1. Track state: `FOCUSING` vs `DISTRACTED`
2. Save duration on state transition `DISTRACTED` → `FOCUSING`
3. Only save if duration >= 10s buffer

## Requirements

### Functional
- Track state transitions between focusing and distracted
- Record accurate distraction duration when user returns
- Only count distractions >= 10 seconds
- Prevent double-counting

### Non-functional
- Maintain 1-second polling interval
- Thread-safe signal emission
- Minimal UI changes required

## Architecture

### State Machine Design
```
     +-------------------+
     |                   v
[FOCUSING] <---> [DISTRACTED]
     ^               |
     |               | (duration >= 10s)
     |               v
     +--------- [SAVE_DISTRACTION]
```

### Code Structure
```python
class FocusTrackerThread(QThread):
    # States
    STATE_FOCUSING = "FOCUSING"
    STATE_DISTRACTED = "DISTRACTED"

    # New signal for completed distraction
    distraction_recorded = pyqtSignal(str, int)  # (app_name, duration_seconds)

    def __init__(self, allowed_keywords, parent=None):
        self.state = self.STATE_FOCUSING
        self.distraction_start_time = None
        self.buffer_seconds = 10  # Hardcoded per user decision
```

### State Transitions
```python
def run(self):
    while not self.isInterruptionRequested():
        is_valid = self._check_window_valid()
        current_app = self._get_active_window_title()

        # Transition: DISTRACTED -> FOCUSING
        if is_valid and self.state == self.STATE_DISTRACTED:
            duration = int(time.time() - self.distraction_start_time)
            if duration >= self.buffer_seconds:
                self.distraction_recorded.emit(current_app, duration)
            self.state = self.STATE_FOCUSING
            self.distraction_start_time = None

        # Transition: FOCUSING -> DISTRACTED
        elif not is_valid and self.state == self.STATE_FOCUSING:
            self.state = self.STATE_DISTRACTED
            self.distraction_start_time = time.time()

        # Status update for UI (real-time feedback)
        is_distracted = (self.state == self.STATE_DISTRACTED)
        self.status_updated.emit(is_distracted, current_app)
```

## Related Code Files

### Modify
- `core/tracker.py` - Refactor to state machine, add `distraction_recorded` signal
- `ui/create_session_widget.py` - Connect to new signal, handle `distraction_recorded`
- `database/session_repo.py` - Verify `save_distraction()` handles accurate duration (already correct)

### Create
- None

### Delete
- None

## Implementation Steps

1. **Backup current tracker.py**
   - Copy existing implementation as reference

2. **Add state machine to tracker.py**
   - Define state constants
   - Add `distraction_recorded` signal
   - Refactor `run()` method with state transitions
   - Remove old `distraction_alert` logic (replace with status updates only)

3. **Update create_session_widget.py**
   - Change signal connection from `distraction_alert` to `distraction_recorded`
   - Update `_on_distraction_alert()` to handle new signal signature

4. **Test state transitions**
   - Test: Valid -> Invalid (within 10s) -> Valid (no save)
   - Test: Valid -> Invalid (>10s) -> Valid (save accurate duration)
   - Test: Multiple distractions in sequence

5. **Edge cases**
   - Window title becomes None (lock screen) - maintain current state
   - Session ends while distracted - save pending distraction

## Todo List
- [ ] Backup current tracker.py implementation
- [ ] Add state constants to FocusTrackerThread
- [ ] Add distraction_recorded signal
- [ ] Refactor run() with state machine logic
- [ ] Update create_session_widget.py signal connection
- [ ] Test distraction < 10s (should not save)
- [ ] Test distraction > 10s (should save accurate duration)
- [ ] Test session end while distracted
- [ ] Verify no double-counting

## Success Criteria
- [ ] Distraction duration accurate ±5%
- [ ] Only distractions >= 10s are recorded
- [ ] No double-counting of same distraction
- [ ] Status updates still work for real-time UI feedback
- [ ] Session end captures pending distraction

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| State machine complexity | Medium | Keep simple 2-state design |
| Lost distraction on crash | Low | User decided no recovery needed |
| Signal timing issues | Low | Use Qt's thread-safe signals |

## Security Considerations
- None (local app, no network)

## Next Steps
- **Dependencies**: None (can start immediately)
- **Blocks**: Phase 2 (History Tab needs accurate data)
- **Follows**: Phase 2 implementation
