---
# Phase 4: Multi-monitor Tree Widget Support

## Context Links
- Brainstorm decisions: `plans/reports/brainstorm-decisions-260409-1640-user-resolutions.md`
- Current tree: `ui/tree_widget.py`
- Current spawn: `ui/create_session_widget.py` (lines 112-124)

## Overview
**Priority**: P2
**Status**: pending
**Description**: Display tree widget on all connected monitors simultaneously

## Key Insights

### Current Behavior
Tree widget only appears on primary monitor:
```python
screen: QScreen = QApplication.primaryScreen()
geo = screen.availableGeometry()
self.tree_widget.move(geo.right() - 20, geo.bottom() - 20)
```

### User Decision
"Tree trên tất cả màn hình" - Show tree widget on all monitors

### Implementation Options
1. **Single widget, cloned positions** - Doesn't work (one widget = one window)
2. **One widget per monitor** - Correct approach, independent instances

## Requirements

### Functional
- Tree appears on all monitors
- Each instance independent (collapse/expand per monitor)
- Timer state synchronized across instances
- Close all when session ends

### Non-functional
- Position in bottom-right corner of each monitor
- Maintain existing drag behavior per instance

## Architecture

### Tree Widget Manager
```python
# ui/tree_widget_manager.py (new file)
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from ui.tree_widget import TreeWidget

class TreeWidgetManager(QObject):
    """Manages multiple tree widget instances across monitors"""

    def __init__(self, duration_minutes: int, subject: str,
                 on_finish_callback=None):
        super().__init__()
        self.widgets = []
        self.duration_minutes = duration_minutes
        self.subject = subject
        self.on_finish_callback = on_finish_callback

    def spawn_on_all_screens(self):
        """Create tree widget on each monitor"""
        screens = QApplication.screens()

        for screen in screens:
            widget = TreeWidget(
                duration_minutes=self.duration_minutes,
                subject=self.subject,
                on_finish_callback=self._on_any_finish,
                screen=screen  # Pass screen for positioning
            )
            self._position_widget(widget, screen)
            self.widgets.append(widget)
            widget.show()

    def _position_widget(self, widget, screen):
        """Position widget in bottom-right of screen"""
        geo = screen.availableGeometry()
        widget.move(
            geo.right() - widget.width() - 20,
            geo.bottom() - widget.height() - 20
        )

    def _on_any_finish(self, elapsed_seconds: int):
        """Handle finish from any widget - close all"""
        self.close_all()
        if self.on_finish_callback:
            self.on_finish_callback(elapsed_seconds)

    def close_all(self):
        """Close all widget instances"""
        for widget in self.widgets:
            widget.close()
        self.widgets.clear()
```

### Modified TreeWidget
```python
# ui/tree_widget.py - Modified __init__
class TreeWidget(QWidget):
    def __init__(self, duration_minutes: int, subject: str,
                 on_finish_callback=None, screen=None):
        super().__init__(parent=None)

        self.total_seconds = duration_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.subject = subject
        self.on_finish_callback = on_finish_callback
        self.is_collapsed = False

        # Window flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(160, 220)

        # Position based on screen if provided
        if screen:
            geo = screen.availableGeometry()
            self.move(
                geo.right() - self.width() - 20,
                geo.bottom() - self.height() - 20
            )

        self._build_ui()
        self._start_timer()
```

### Integration
```python
# ui/create_session_widget.py - Modified spawn
from ui.tree_widget_manager import TreeWidgetManager

class CreateSessionWidget(QWidget):
    # ...

    def _on_start(self):
        # ... existing code ...

        # --- Use Manager for multi-monitor support ---
        self.tree_manager = TreeWidgetManager(
            duration_minutes=duration,
            subject=subject,
            on_finish_callback=self._on_session_finished
        )
        self.tree_manager.spawn_on_all_screens()
```

## Related Code Files

### Modify
- `ui/tree_widget.py` - Add `screen` parameter to `__init__`
- `ui/create_session_widget.py` - Use `TreeWidgetManager` instead of direct widget

### Create
- `ui/tree_widget_manager.py` - Manager class for multi-monitor widgets

### Delete
- None

## Implementation Steps

1. **Create TreeWidgetManager**
   - `__init__`: Store duration, subject, callback
   - `spawn_on_all_screens()`: Loop through `QApplication.screens()`
   - `_position_widget()`: Bottom-right positioning per screen
   - `_on_any_finish()`: Forward callback and close all
   - `close_all()`: Cleanup all instances

2. **Modify TreeWidget.__init__**
   - Add optional `screen` parameter
   - If screen provided, position immediately
   - Remove positioning responsibility from caller

3. **Update CreateSessionWidget**
   - Replace `self.tree_widget` with `self.tree_manager`
   - Change spawn call to use manager
   - Remove manual positioning code

4. **Test scenarios**
   - Single monitor (primary only)
   - Dual monitor (left-right)
   - Triple monitor
   - Different screen resolutions
   - Close from any instance

5. **Verify behaviors**
   - Each widget collapses independently
   - Drag works per instance
   - Timer syncs across all instances
   - Close button on any widget ends session

## Todo List
- [ ] Create ui/tree_widget_manager.py
- [ ] Implement spawn_on_all_screens()
- [ ] Implement _position_widget()
- [ ] Implement _on_any_finish() and close_all()
- [ ] Modify TreeWidget.__init__ to accept screen
- [ ] Update CreateSessionWidget to use manager
- [ ] Test single monitor
- [ ] Test dual monitor
- [ ] Test close from any instance
- [ ] Verify independent collapse/expand

## Success Criteria
- [ ] Tree appears on all monitors
- [ ] Each instance positioned bottom-right
- [ ] Close on any instance closes all
- [ ] Timer synchronized across instances
- [ ] Independent collapse/expand per instance

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Screen detection issues | Low | Qt handles this reliably |
| Performance with many monitors | Low | Max ~4 monitors typical |
| Desynced timers | Low | All start simultaneously |

## Security Considerations
- None (local UI)

## Next Steps
- **Dependencies**: None (independent feature)
- **Blocks**: None
- **Follows**: Testing and polish phase

## Optional Enhancements (Post-MVP)
- Per-monitor positioning preferences
- Option to show on primary only
- Different tree stages per monitor (visual variety)
