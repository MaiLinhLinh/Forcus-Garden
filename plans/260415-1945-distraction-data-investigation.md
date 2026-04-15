# Distraction Data Discrepancy Investigation Plan

**Date:** 2026-04-15
**Status:** In Progress - Awaiting user testing with enhanced logging
**Priority:** High - Data accuracy issue

## Problem Statement

User reported data inconsistency in distraction tracking:
- **Stats show:** 5 distractions, 59 seconds total
- **UI displays:** 3 distractions, 47 seconds total
- **Missing:** 2 distractions (12 seconds unaccounted for)
- **Missing apps:** Discord and others not appearing

## Root Cause Analysis

### Database Layer ✅ Verified
- `get_distraction_stats()` correctly retrieves all records
- No filtering issues in database queries
- Data integrity checks added

### Potential Root Causes

1. **App Switch Race Condition** (Most Likely)
   - User switches between distraction apps rapidly
   - Some distractions don't meet 5-second buffer threshold
   - State machine loses track of short distractions

2. **Pending Distraction Loss** (Second Most Likely)
   - Session ends while user is distracted
   - `get_pending_distraction()` may not capture correctly
   - Last distraction not saved to database

3. **Data Corruption in Transit** (Less Likely)
   - Issue between database query and UI display
   - Signal emission timing problems
   - Thread safety concerns

## Validation Enhancements Added

### 1. Database Layer (`session_repo.py`)
```python
# Added data integrity checks in get_distraction_stats()
- Validates count == details length
- Validates total_seconds == sum of detail seconds
- Logs all distractions with full details
```

### 2. Session Management (`create_session_widget.py`)
```python
# Added validation before passing to UI
- Checks data consistency before SummaryDialog creation
- Logs all stats being passed
- Warns if count/total mismatch detected
```

### 3. UI Display (`summary_dialog.py`)
```python
# Added validation upon data receipt
- Checks received data consistency
- Logs expected vs actual values
- Alerts if data is missing
```

## Testing Protocol for User

### Test Scenario 1: Normal Distractions
1. Start a 5-minute session
2. Open Discord for 10 seconds
3. Return to study zone
4. Open YouTube for 8 seconds
5. Return to study zone
6. Open Zalo for 6 seconds
7. Return to study zone
8. Let session complete naturally

**Expected:** All 3 distractions appear in summary with correct times

### Test Scenario 2: Rapid App Switching
1. Start a 5-minute session
2. Open Discord (3 seconds) - should NOT be saved (< 5s buffer)
3. Switch to YouTube (7 seconds)
4. Switch to Facebook (4 seconds) - should NOT be saved
5. Switch to Zalo (8 seconds)
6. Return to study zone
7. Let session complete

**Expected:** Only YouTube (7s) and Zalo (8s) saved

### Test Scenario 3: Session End While Distracted
1. Start a 5-minute session
2. Open Discord for 15 seconds
3. While still in Discord, click X to end session
4. Check summary dialog

**Expected:** Discord (15s) should be saved as pending distraction

### Test Scenario 4: Browser Tab Switching
1. Start session with "chrome" in study zone
2. Open GitHub in Chrome (should be valid)
3. Switch to Facebook tab in same Chrome window (should be distraction)
4. Switch back to GitHub
5. Open YouTube in new tab (should be distraction)
6. Return to study zone
7. End session

**Expected:** Facebook and YouTube should be tracked separately

## Debug Output Analysis

When running tests, check console output for:

### Valid Flow ✅
```
[DEBUG] save_distraction: app='Discord', duration=10s
[DEBUG] Distraction saved successfully to DB
[DEBUG] get_distraction_stats: Total distractions found in DB: 3
[DEBUG] Summary: count=3, total_seconds=24
[DEBUG] Details list length: 3
[DEBUG] VALIDATION PASSED: count=3 == details length=3
[DEBUG] VALIDATION PASSED: total_seconds=24 == sum details=24
```

### Invalid Flow ❌ (Will show errors)
```
[DEBUG] get_distraction_stats: Total distractions found in DB: 5
[DEBUG] Summary: count=5, total_seconds=59
[DEBUG] Details list length: 5
[DEBUG] VALIDATION FAILED: count=5 != details length=3
[ERROR] CRITICAL: Missing 2 distraction(s) from display!
```

## Next Steps

### For User:
1. Run the application with enhanced logging
2. Perform test scenarios above
3. Copy console output when issue occurs
4. Report findings with:
   - Which test scenario was run
   - Full console debug output
   - Screenshot of summary dialog
   - List of apps opened during session

### For Developer:
Once user provides logs:
1. Analyze exact point where data diverges
2. Identify specific distraction(s) being lost
3. Implement targeted fix based on findings
4. Regression test all scenarios
5. Deploy fix with validation warnings

## Potential Fixes (Pending Root Cause)

### Fix A: Improve State Machine
```python
# Add transition logging
def _log_state_transition(self, from_state, to_state, reason):
    print(f"[DEBUG] State: {from_state} -> {to_state} ({reason})")

# Ensure all transitions are logged
```

### Fix B: Pending Distraction Enhancement
```python
# Save all pending distractions regardless of duration
# Let UI decide what to display vs what to filter
```

### Fix C: Data Consistency Checks
```python
# Add automatic repair if mismatch detected
# Re-query database if count doesn't match details
```

## Files Modified

- `database/session_repo.py` - Enhanced validation & logging
- `ui/create_session_widget.py` - Pre-UI validation
- `ui/summary_dialog.py` - Receipt validation
- `core/tracker.py` - Enhanced state machine logging (already done by debugger)

## Success Criteria

- ✅ All validation checks pass without errors
- ✅ Count matches details list length
- ✅ Total seconds matches sum of detail seconds
- ✅ All distractions appear in UI
- ✅ No data loss in any test scenario

## Unresolved Questions

1. **Exact reproduction:** Which scenario triggers the bug?
2. **App type correlation:** Does it happen more with browsers vs native apps?
3. **Duration correlation:** Do longer sessions have more issues?
4. **Buffer threshold:** Is 5-second buffer appropriate?

---

**Status:** Awaiting user test results with enhanced logging
**Next Action:** Analyze user logs to identify root cause
**Estimated Fix Time:** 1-2 hours after root cause identification
