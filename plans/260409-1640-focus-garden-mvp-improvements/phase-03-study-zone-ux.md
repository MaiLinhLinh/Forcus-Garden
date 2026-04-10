---
# Phase 3: Study Zone UX Improvements (Hybrid Approach)

## Context Links
- Brainstorm decisions: `plans/reports/brainstorm-decisions-260409-1640-user-resolutions.md`
- Current input: `ui/create_session_widget.py` (lines 57-63)
- User decision: Hybrid (Templates + Auto-detect)

## Overview
**Priority**: P2
**Status**: pending
**Description**: Improve Study Zone input with predefined templates and auto-detection of open windows

## Key Insights

### Current UX Problem
Users must manually type all keywords:
- Error-prone (typos, wrong window titles)
- Time-consuming (2-5 minutes per session)
- No guidance on valid formats

### Hybrid Solution
1. **Templates**: Pre-defined common study apps (YouTube, Google Docs, VS Code, etc.)
2. **Auto-detect**: Scan open windows and let user select
3. **Manual edit**: Still allows full customization

## Requirements

### Functional
- Template selection auto-fills keywords
- Auto-detect lists all open windows
- User can merge templates + detected windows
- Manual editing always available
- Vietnamese UI

### Non-functional
- Detection completes within 2 seconds
- Templates easy to extend

## Architecture

### Template Definition
```python
# core/constants.py (new file)
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
    },
    "Zoom": {
        "keywords": ["Zoom Meeting", "zoom.us"],
        "icon": "📹",
        "description": "Học trực tuyến trên Zoom"
    }
}
```

### Window Detection
```python
# utils/window_detector.py (new file)
import pygetwindow as gw
from typing import List, Dict

def get_open_windows() -> List[Dict[str, str]]:
    """Get list of all visible windows"""
    windows = gw.getAllWindows()
    result = []
    seen_titles = set()

    for w in windows:
        if w.title and w.visible and w.title.strip():
            # Deduplicate by title
            if w.title not in seen_titles:
                result.append({
                    "title": w.title,
                    "app": _extract_app_name(w.title)
                })
                seen_titles.add(w.title)

    return result

def _extract_app_name(title: str) -> str:
    """Extract app name from window title"""
    # Heuristic: split by first " - " or " — "
    for sep in [" - ", " — "]:
        if sep in title:
            return title.split(sep)[-1].strip()
    return title.strip()[:30]  # Truncate if no separator
```

### UI Component Design
```python
# ui/study_zone_input.py (new file)
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QComboBox, QPushButton, QTextEdit,
                             QListWidget, QListWidgetItem, QDialog,
                             QCheckBox, QDialogButtonBox)
from PyQt6.QtCore import Qt
from core.constants import STUDY_ZONE_TEMPLATES
from utils.window_detector import get_open_windows

class StudyZoneInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Template selection
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Mẫu có sẵn:"))
        self.template_combo = QComboBox()
        self.template_combo.addItem("-- Chọn mẫu --", None)
        for name, data in STUDY_ZONE_TEMPLATES.items():
            self.template_combo.addItem(
                f"{data['icon']} {name}",  # Display text
                data                        # User data
            )
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        template_layout.addWidget(self.template_combo)
        layout.addLayout(template_layout)

        # Auto-detect button
        detect_layout = QHBoxLayout()
        self.detect_btn = QPushButton("🔍 Phát hiện cửa sổ đang mở")
        self.detect_btn.clicked.connect(self._detect_windows)
        detect_layout.addWidget(self.detect_btn)
        detect_layout.addStretch()
        layout.addLayout(detect_layout)

        # Keyword editor
        layout.addWidget(QLabel("Từ khóa Study Zone (mỗi dòng một từ khóa):"))
        self.keyword_edit = QTextEdit()
        self.keyword_edit.setPlaceholderText(
            "Nhập từ khóa thủ công hoặc chọn mẫu/phát hiện cửa sổ ở trên\n"
            "Ví dụ:\nword\nchrome\nvscode"
        )
        layout.addWidget(self.keyword_edit)

        self.setLayout(layout)

    def _on_template_changed(self, index):
        """Auto-fill keywords from template"""
        data = self.template_combo.currentData()
        if data:
            current_text = self.keyword_edit.toPlainText().strip()
            new_keywords = "\n".join(data["keywords"])

            if current_text:
                # Append with separator
                self.keyword_edit.setPlainText(f"{current_text}\n{new_keywords}")
            else:
                self.keyword_edit.setPlainText(new_keywords)

    def _detect_windows(self):
        """Show dialog with open windows checklist"""
        windows = get_open_windows()
        dialog = WindowSelectDialog(windows, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = dialog.get_selected_keywords()
            current_text = self.keyword_edit.toPlainText().strip()

            if current_text:
                self.keyword_edit.setPlainText(f"{current_text}\n{selected}")
            else:
                self.keyword_edit.setPlainText(selected)

    def get_keywords(self) -> List[str]:
        """Return list of keywords from text edit"""
        text = self.keyword_edit.toPlainText()
        return [kw.strip() for kw in text.splitlines() if kw.strip()]


class WindowSelectDialog(QDialog):
    """Dialog for selecting open windows"""

    def __init__(self, windows: List[Dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chọn cửa sổ học tập")
        self.setFixedSize(500, 400)
        self.checkboxes = {}

        layout = QVBoxLayout(self)

        # Instructions
        info = QLabel("Chọn các cửa sổ bạn sử dụng để học:")
        layout.addWidget(info)

        # Window list
        self.list_widget = QListWidget()
        for win in windows:
            item = QListWidgetItem(
                f"📄 {win['app']}\n   {win['title'][:50]}"
            )
            item.setData(Qt.ItemDataRole.UserRole, win['title'])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selected_keywords(self) -> str:
        """Get selected window titles as keywords"""
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                title = item.data(Qt.ItemDataRole.UserRole)
                # Use app name as keyword
                selected.append(_extract_app_name(title))
        return "\n".join(selected)
```

## Related Code Files

### Modify
- `ui/create_session_widget.py` - Replace `self.zone_input` with `StudyZoneInput` widget

### Create
- `core/constants.py` - Define `STUDY_ZONE_TEMPLATES`
- `utils/window_detector.py` - `get_open_windows()`, `_extract_app_name()`
- `ui/study_zone_input.py` - New input widget with templates + detect
- `utils/__init__.py` - Package init

### Delete
- None

## Implementation Steps

1. **Create constants file**
   - Define 5-7 common templates
   - Include Vietnamese descriptions
   - Use emoji icons for visual appeal

2. **Create window detector utility**
   - Use `pygetwindow.getAllWindows()`
   - Filter for visible, titled windows
   - Extract app names with heuristics
   - Handle edge cases (empty titles, duplicates)

3. **Create StudyZoneInput widget**
   - Template dropdown with icons
   - Auto-detect button
   - Keyword text area
   - Merge logic for combining sources

4. **Create window selection dialog**
   - List all detected windows
   - Checkboxes for selection
   - Show full title in tooltip
   - OK/Cancel buttons

5. **Integrate into CreateSessionWidget**
   - Replace `QTextEdit` zone_input with `StudyZoneInput`
   - Update keyword extraction logic
   - Test full flow

6. **Test scenarios**
   - Template only
   - Detect only
   - Template + Detect
   - Manual + Template
   - All three combined

## Todo List
- [ ] Create core/constants.py with templates
- [ ] Create utils/window_detector.py
- [ ] Create ui/study_zone_input.py
- [ ] Implement template dropdown
- [ ] Implement auto-detect button
- [ ] Implement window selection dialog
- [ ] Integrate into CreateSessionWidget
- [ ] Test template selection
- [ ] Test window detection
- [ ] Test combined workflow

## Success Criteria
- [ ] Template selection auto-fills keywords
- [ ] Auto-detect lists all open windows
- [ ] User can select multiple windows
- [ ] Selected windows merge into keyword list
- [ ] Manual editing still works
- [ ] Input time < 2 minutes

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Window title variations | Medium | Multiple keywords per template |
| pygetwindow cross-platform | Medium | Test on Windows target |
| Too many windows detected | Low | Limit to top 20 windows |

## Security Considerations
- Window titles may contain sensitive info
- Only show to user, not logged or transmitted

## Next Steps
- **Dependencies**: None (independent feature)
- **Blocks**: None
- **Follows**: Phase 4 (Multi-monitor support)
