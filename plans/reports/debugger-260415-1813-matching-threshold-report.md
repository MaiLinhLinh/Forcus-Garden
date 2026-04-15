# Debugger Report: Fuzzy Matching Threshold Analysis

**Date**: 2026-04-15 18:13
**Issue**: Investigate if 90% threshold prevents distraction detection
**Status**: ✅ RESOLVED - Not a threshold issue

## Executive Summary

**Root Cause**: NOT a threshold problem. The matching logic works correctly at all thresholds (70-95%).

**Key Findings**:
- Zalo matching works perfectly at 90% threshold
- Alias system correctly handles "edge" → "Microsoft Edge"
- Browser parser correctly extracts site names from Edge titles
- **Real issue**: When Zalo opens in Edge browser, it MATCHES because "edge" is in allowed keywords

## Test Results

### 1. Threshold Sensitivity (70-95%)
**Result**: All thresholds work correctly

```
Allowed: ["vscode", "edge", "chrome"]
Test: "Zalo" window titles

70% threshold: Zalo = False ✓
80% threshold: Zalo = False ✓
85% threshold: Zalo = False ✓
90% threshold: Zalo = False ✓
95% threshold: Zalo = False ✓
```

### 2. Alias Coverage
**Result**: Aliases work correctly

```
"edge" → ["microsoft edge", "edge chromium", "edge"]
"zalo" → ["zalo"]
```

**Missing Alias**: "Zalo" has NO Vietnamese aliases defined

### 3. Browser Title Parsing
**Result**: Parser extracts correct site names

```
"Zalo - Microsoft Edge" → site: "Zalo", is_browser: True
"YouTube - Music - Microsoft Edge" → site: "YouTube - Music", is_browser: True
"GitHub - project | Visual Studio Code - Microsoft Edge" → site: "GitHub - project | Visual Studio Code", is_browser: True
```

### 4. Critical Discovery - Edge Browser Issue
**Result**: ✅ CONFIRMED - This is the bug!

```
Allowed: ["vscode", "edge"]
Test: "Zalo - Microsoft Edge"

Matcher result: True (MATCHES!)
Expected: False (Should be distraction)

Why it matches:
1. Browser parser extracts: site="Zalo", is_browser=True
2. Matcher tests "Zalo" against allowed keywords
3. No match for "Zalo"
4. Matcher falls back to full title: "Zalo - Microsoft Edge"
5. Full title contains "edge" → MATCHES!
```

## The Actual Bug

**Location**: `core/tracker.py` lines 54-64

**Problem**:
```python
# Phase 4: Parse browser titles for better matching
parsed_site, is_browser = self.browser_parser.parse(title)
if is_browser and parsed_site:
    # Use extracted site name for matching
    is_valid = self.matcher.is_match(parsed_site)
    # Fall back to full title if no match
    if not is_valid:
        is_valid = self.matcher.is_match(title)  # ← BUG HERE
```

**Why it's wrong**:
- When Zalo opens in Edge: title="Zalo - Microsoft Edge"
- Parser extracts: site="Zalo"
- Matcher tests "Zalo" → False (correct)
- Falls back to full title "Zalo - Microsoft Edge" → True (WRONG!)
- Full title contains "edge" which is allowed

**Impact**: Any website opened in Edge browser will match if "edge" is allowed, regardless of content.

## Solutions

### Option 1: Remove Fallback (Recommended)
**File**: `core/tracker.py` lines 54-64

```python
# BEFORE
parsed_site, is_browser = self.browser_parser.parse(title)
if is_browser and parsed_site:
    is_valid = self.matcher.is_match(parsed_site)
    if not is_valid:
        is_valid = self.matcher.is_match(title)  # Remove this
else:
    is_valid = self.matcher.is_match(title)

# AFTER
parsed_site, is_browser = self.browser_parser.parse(title)
if is_browser and parsed_site:
    is_valid = self.matcher.is_match(parsed_site)
else:
    is_valid = self.matcher.is_match(title)
```

**Rationale**: If we parse a browser title, trust the parser. Don't fall back to full title.

### Option 2: Smart Fallback
Only fall back if the site name is generic (new tab, blank, etc.)

```python
GENERIC_SITES = {"new tab", "blank", "about:blank", "start"}

parsed_site, is_browser = self.browser_parser.parse(title)
if is_browser and parsed_site:
    if parsed_site.lower() in GENERIC_SITES:
        # Fall back for generic sites
        is_valid = self.matcher.is_match(title)
    else:
        # Trust the parser for specific sites
        is_valid = self.matcher.is_match(parsed_site)
else:
    is_valid = self.matcher.is_match(title)
```

### Option 3: Add Zalo Alias (Quick Fix)
**File**: `core/alias_manager.py` line 46

```python
# Vietnamese Apps
"zoom": ["zoom meeting", "zoom rooms"],
"teams": ["microsoft teams", "teams"],
"zalo": ["zalo", "zalo chat", "zalo pc"],  # Add this
```

**Note**: This doesn't fix the Edge bug, only helps if user adds "zalo" to allowed list.

## Threshold Analysis

**Current**: 90% threshold in `tracker.py` line 34
**Default**: 85% threshold in `matcher.py` line 17

**Finding**: 90% is appropriate. No change needed.

- Exact substring match (line 68-70): Handles "Zalo", "Microsoft Edge"
- Fuzzy match (line 72-84): Only for partial matches, threshold 90% is fine
- Test shows all thresholds 70-95% work correctly for exact matches

## Recommendations

1. **Immediate Fix**: Implement Option 1 (remove fallback)
   - Simplest solution
   - Fixes Edge browser bug
   - No performance impact

2. **Add Zalo Alias**: Implement Option 3
   - Helps Vietnamese users
   - Low effort, high value

3. **Consider Browser-Specific Logic**: Future enhancement
   - Different handling for browser vs non-browser apps
   - Browser: Only match parsed site name
   - Non-browser: Match full title

## Test Files Created

1. `plans/reports/debugger-260415-1813-matching-threshold-test.py`
   - Tests threshold sensitivity (70-95%)
   - Tests alias coverage
   - Tests exact vs fuzzy matching

2. `plans/reports/debugger-260415-1813-distraction-detection-test.py`
   - Tests Zalo as distraction (not in allowed list)
   - Tests Edge browser parsing
   - Tests critical Zalo/Edge edge case

## Unresolved Questions

None - Root cause identified and confirmed.

## Files Analyzed

- `core/matcher.py` - Threshold logic, fuzzy matching
- `core/alias_manager.py` - Alias definitions
- `core/tracker.py` - Main tracking logic, bug location
- `core/browser_parser.py` - Browser title parsing

## Next Steps

1. Fix the fallback logic in `tracker.py`
2. Add Zalo to alias dictionary
3. Run integration tests to verify fix
4. Test with real Zalo/Edge usage scenarios
