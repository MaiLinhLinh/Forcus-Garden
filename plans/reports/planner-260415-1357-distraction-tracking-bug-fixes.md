# Distraction Tracking Bug Fixes - Planner Summary

**Date**: 2026-04-15
**Plan**: `plans/260415-1357-distraction-tracking-bug-fixes/`
**Status**: Complete

## Executive Summary

Created detailed implementation plan for fixing two critical bugs in Focus Garden distraction tracking:

1. **Fuzzy String Matching**: "vscode" doesn't match "Visual Studio Code"
2. **Browser Tab Detection**: "Facebook and 3 other tabs" - no individual tab detection

## Solution Approach

### Bug 1: Fuzzy Matching
- **Library**: RapidFuzz (10-100x faster than fuzzywuzzy)
- **Architecture**: Modular design with 3 new files
  - `core/matcher.py` - KeywordMatcher with RapidFuzz
  - `core/normalizer.py` - TextNormalizer for Vietnamese/English
  - `core/alias-manager.py` - AppAliasManager for common variations

### Bug 2: Browser Title Parsing
- **Approach**: Smart regex-based parsing (practical, no extension needed)
- **Module**: `core/browser-parser.py` - Extract site names from browser titles
- **Support**: Chrome, Firefox, Edge, Opera, Brave, Vivaldi

## Implementation Plan Structure

```
plans/260415-1357-distraction-tracking-bug-fixes/
├── plan.md                          # Overview (60 lines)
├── phase-01-rapidfuzz-integration.md
├── phase-02-text-normalization-pipeline.md
├── phase-03-alias-dictionary-system.md
├── phase-04-browser-title-parsing.md
└── phase-05-testing-calibration.md
```

## Phase Summary

| Phase | Focus | Est. Time | Key Deliverables |
|-------|-------|-----------|------------------|
| 1 | RapidFuzz Integration | 2-3h | `core/matcher.py` |
| 2 | Text Normalization | 1-1.5h | `core/normalizer.py` |
| 3 | Alias System | 1h | `core/alias-manager.py` |
| 4 | Browser Parsing | 1-1.5h | `core/browser-parser.py` |
| 5 | Testing & Calibration | 1h | Test suite, threshold tuning |

**Total Effort**: 5-7 hours

## Key Design Decisions

1. **RapidFuzz over fuzzywuzzy**: Performance + Unicode support
2. **Smart parsing over browser extensions**: Practical for immediate fix
3. **85% fuzzy threshold**: Balanced starting point
4. **Modular structure**: Each file <200 lines (project requirement)

## File Modifications

### New Files (4)
- `core/matcher.py` - KeywordMatcher class
- `core/normalizer.py` - TextNormalizer class
- `core/alias-manager.py` - AppAliasManager class
- `core/browser-parser.py` - BrowserTitleParser class

### Modified Files (1)
- `core/tracker.py` - Integrate new modules, preserve state machine

### Preserved
- State machine logic (FOCUSING <-> DISTRACTED)
- 1-second polling interval
- All signal emissions
- Database integration

## Success Criteria

- [ ] "vscode" matches "Visual Studio Code"
- [ ] "chrome" matches browser windows with actual site titles
- [ ] Vietnamese text supported correctly
- [ ] No performance degradation (1s polling)
- [ ] All existing state machine logic preserved
- [ ] All source files <200 lines

## Unresolved Questions

1. Optimal fuzzy threshold for Vietnamese/English mixed content (needs testing)
2. Common Vietnamese apps missing from alias dictionary (extensible)
3. Browser updates changing title format (patterns are stable)

## Research References

- Fuzzy matching: `plans/reports/researcher-260415-1350-fuzzy-string-matching.md`
- Browser detection: `plans/reports/researcher-260415-1350-browser-tab-detection.md`

## Next Steps

Implementation should proceed in sequential order (Phase 1 -> 5), with testing after each phase to ensure no regression.
