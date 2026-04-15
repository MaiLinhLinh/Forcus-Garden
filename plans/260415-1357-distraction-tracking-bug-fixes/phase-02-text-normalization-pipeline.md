---
# Phase 2: Text Normalization Pipeline

## Context Links
- Research: `plans/reports/researcher-260415-1350-fuzzy-string-matching.md`
- Phase 1: `phase-01-rapidfuzz-integration.md`
- Current matcher: `core/matcher.py` (created in Phase 1)

## Overview
**Priority**: P1
**Status**: completed
**Description**: Add text normalization for Vietnamese/English consistency before matching
**Progress**: 100% Complete ✅

## Key Insights
- Vietnamese diacritics need special handling (a, à, á, a, ã, a)
- Unicode NFC normalization for compatibility
- Case folding for case-insensitive matching
- Whitespace normalization for clean matching

## Requirements

### Functional
- Normalize Vietnamese characters (preserve diacritics)
- Convert to lowercase
- Normalize whitespace
- Remove special characters (except Vietnamese diacritics)

### Non-functional
- Minimal performance overhead
- Caching for repeated titles
- File under 200 lines

## Architecture

### New Module: `core/normalizer.py`
```python
"""
Text normalization for Vietnamese and English.
Handles Unicode, case, and whitespace normalization.
"""
import unicodedata
import re

class TextNormalizer:
    """Normalize text for consistent matching."""

    def __init__(self):
        # Vietnamese diacritic ranges (keep these)
        self.vietnamese_ranges = [
            (0x1EA0, 0x1EF9),  # Vietnamese extended
            (0x00C0, 0x017F),  # Latin extended
        ]

        # Pattern: keep letters, numbers, Vietnamese diacritics, spaces
        self.keep_pattern = re.compile(r'[a-zA-Z0-9\s\u1EA0-\u1EF9\u00C0-\u017F]')

        # Simple whitespace normalizer
        self.ws_pattern = re.compile(r'\s+')

    def normalize(self, text: str) -> str:
        """
        Full normalization pipeline.

        Steps:
        1. Unicode NFC (canonical composition)
        2. Lowercase
        3. Remove unwanted special chars
        4. Normalize whitespace
        """
        if not text:
            return ""

        # Step 1: Unicode NFC normalization
        normalized = unicodedata.normalize('NFC', text)

        # Step 2: Lowercase (Vietnamese-aware)
        normalized = normalized.lower()

        # Step 3: Remove unwanted special characters
        # Keep only: letters, numbers, Vietnamese diacritics, spaces
        cleaned = ''.join(
            c if self.keep_pattern.match(c) else ' '
            for c in normalized
        )

        # Step 4: Normalize whitespace
        result = self.ws_pattern.sub(' ', cleaned).strip()

        return result

    def quick_normalize(self, text: str) -> str:
        """
        Fast normalization for production use.
        Skips special char removal for speed.
        """
        if not text:
            return ""
        return unicodedata.normalize('NFC', text.lower()).strip()
```

### Updated: `core/matcher.py`
```python
from core.normalizer import TextNormalizer

class KeywordMatcher:
    def __init__(self, keywords, threshold=85):
        self.raw_keywords = keywords
        self.threshold = threshold
        self.normalizer = TextNormalizer()
        self._build_patterns()

    def _build_patterns(self):
        """Pre-process keywords with normalization."""
        self._patterns = [
            self.normalizer.normalize(kw)
            for kw in self.raw_keywords
        ]

    def is_match(self, title: str) -> bool:
        """Check if title matches any keyword."""
        if not title:
            return False

        # Normalize title
        normalized_title = self.normalizer.quick_normalize(title)

        # Fast path: exact substring
        for pattern in self._patterns:
            if pattern in normalized_title:
                return True

        # Fuzzy matching
        if len(normalized_title) >= 4:
            result = process.extractOne(
                normalized_title,
                self._patterns,
                scorer=fuzz.WRatio,
                score_cutoff=self.threshold
            )
            return result is not None

        return False
```

## Related Code Files

### Modify
- `core/matcher.py` - Integrate TextNormalizer

### Create
- `core/normalizer.py` - New TextNormalizer class

### Delete
- None

## Implementation Steps

1. **Create `core/normalizer.py`**
   - Implement TextNormalizer class
   - Add `normalize()` method (full pipeline)
   - Add `quick_normalize()` method (for performance)
   - Handle Vietnamese diacritics correctly
   - Keep file under 200 lines

2. **Update `core/matcher.py`**
   - Import TextNormalizer
   - Create normalizer instance in `__init__`
   - Use normalizer in `_build_patterns()`
   - Use `quick_normalize()` in `is_match()`
   - Keep file under 200 lines

3. **Test Vietnamese support**
   - Test: "Trình duyệt Chrome" matches "chrome"
   - Test: "word" matches "Microsoft Word"
   - Test: Diacritics preserved correctly

## Todo List
- [x] Create core/normalizer.py
- [x] Add Unicode NFC normalization
- [x] Add Vietnamese diacritic handling
- [x] Add whitespace normalization
- [x] Update core/matcher.py to use normalizer
- [x] Test Vietnamese text normalization
- [x] Test English text normalization
- [x] Verify performance with 1s polling

**Test Results**: All normalization tests passed ✅
**File Size**: core/normalizer.py: 86 lines (<200 lines) ✅
**Performance**: No degradation, fast path implementation ✅

## Success Criteria
- [x] Vietnamese characters handled correctly ✅
- [x] Case-insensitive matching works ✅
- [x] Whitespace variation doesn't affect matching ✅
- [x] Performance degradation < 5% ✅
- [x] core/normalizer.py < 200 lines ✅
- [x] core/matcher.py still < 200 lines ✅

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-normalization loses matches | Low | Keep quick_normalize for production |
| Vietnamese diacritics broken | Medium | Test with real Vietnamese text |
| Performance regression | Low | Use quick_normalize in hot path |

## Security Considerations
- None (local app, text processing only)

## Next Steps
- **Dependencies**: Phase 1 (RapidFuzz integration)
- **Blocks**: Phase 3 (alias system needs normalization)
- **Follows**: Phase 3 implementation
