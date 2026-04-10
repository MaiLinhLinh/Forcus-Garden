---
# Phase 2: History Tab Implementation

## Context Links
- Brainstorm decisions: `plans/reports/brainstorm-decisions-260409-1640-user-resolutions.md`
- Current stub: `ui/history_widget.py`
- Database models: `database/models.py`

## Overview
**Priority**: P1 (High)
**Status**: pending
**Description**: Replace stub with functional history table displaying all sessions

## Key Insights

### Current State
`ui/history_widget.py` is a stub:
- Only shows placeholder text "Chưa có phiên học nào được ghi nhận."
- Uses `QListWidget` (not suitable for tabular data)

### Required Implementation
- Use `QTableWidget` for tabular display
- Query sessions from database
- Format dates in Vietnamese locale
- Color-coded status (green = success, red = failed)

## Requirements

### Functional
- Display all sessions in table format
- Columns: Date, Subject, Target, Actual, Status
- Newest sessions first
- Color-coded status
- Optional: Click row for details (defer to post-MVP)

### Non-functional
- Load data on tab switch (not on app start)
- Handle empty state gracefully
- Vietnamese date format

## Architecture

### UI Design
```
+------------------------------------------------------------------+
|  📜 LỊCH SỬ CỦA BẠN                                               |
+------------------------------------------------------------------+--------+--------+
|  Ngày              | Môn học    | Mục tiêu | Thực tế | Trạng thái         |
+------------------------------------------------------------------+--------+--------+
|  09/04/26 15:30    | Python     | 25 phút  | 23 phút | ❌                 |
|  09/04/26 14:00    | Toán       | 30 phút  | 30 phút | ✅                 |
|  08/04/26 20:00    | Tiếng Anh | 20 phút  | 15 phút | ❌                 |
+------------------------------------------------------------------+--------+--------+
```

### Database Query
```python
# database/session_repo.py - Add new function
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

### Widget Implementation
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

    def load_sessions(self):
        """Load sessions from DB and populate table"""
        sessions = get_all_sessions()
        self.table.setRowCount(len(sessions))

        for row, session in enumerate(sessions):
            # Format date
            date_str = session.started_at.strftime("%d/%m %H:%M")
            # Status with color
            status_text = "✅" if session.status == "success" else "❌"

            self.table.setItem(row, 0, QTableWidgetItem(date_str))
            self.table.setItem(row, 1, QTableWidgetItem(session.subject))
            # ... more columns
```

## Related Code Files

### Modify
- `ui/history_widget.py` - Replace stub with table implementation
- `database/session_repo.py` - Add `get_all_sessions()` function

### Create
- None

### Delete
- None

## Implementation Steps

1. **Add database function**
   - Add `get_all_sessions()` to `session_repo.py`
   - Query sessions ordered by `started_at DESC`
   - Return list with limit default 100

2. **Implement HistoryWidget table**
   - Replace `QListWidget` with `QTableWidget`
   - Set column headers (Vietnamese)
   - Implement `load_sessions()` method
   - Format dates as `DD/MM HH:MM`

3. **Add status color coding**
   - Success row: light green background
   - Failed row: light red/orange background
   - Use ✅/❌ emojis in status column

4. **Handle empty state**
   - If no sessions, show message row
   - "Chưa có phiên học nào. Hãy bắt đầu học nhé!"

5. **Refresh on tab switch**
   - Override `showEvent()` to reload data
   - Ensures fresh data when tab is opened

6. **Style the table**
   - Alternating row colors
   - Readable font sizes
   - Column width adjustments

## Todo List
- [ ] Add get_all_sessions() to session_repo.py
- [ ] Replace QListWidget with QTableWidget in history_widget.py
- [ ] Set up column headers
- [ ] Implement load_sessions() method
- [ ] Format Vietnamese dates
- [ ] Add status color coding
- [ ] Handle empty state
- [ ] Add refresh on tab switch
- [ ] Style table for readability

## Success Criteria
- [ ] All sessions display in table
- [ ] Newest sessions at top
- [ ] Status correctly color-coded
- [ ] Empty state handled gracefully
- [ ] Data refreshes when tab opens

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Large dataset performance | Low | Limit to 100 sessions |
| Date formatting locale | Low | Use strftime with custom format |

## Security Considerations
- None (local read-only)

## Next Steps
- **Dependencies**: Phase 1 (need accurate distraction data)
- **Blocks**: None (independent feature)
- **Follows**: Phase 3 (Study Zone UX)

## Optional Enhancements (Post-MVP)
- Click row → detail dialog
- Filter by subject
- Export to CSV (user said not needed)
- Pagination for >100 sessions
