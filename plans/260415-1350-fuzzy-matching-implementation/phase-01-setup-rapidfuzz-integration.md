# Phase 01: Setup and RapidFuzz Integration

## Context Links
- [Research Report](../reports/researcher-260415-1350-fuzzy-string-matching.md)
- [Implementation Plan](../plan.md)

## Overview
**Priority**: High
**Current Status**: Pending
**Description**: Install RapidFuzz library and create basic integration framework for fuzzy string matching.

## Key Insights
- RapidFuzz is 10-100x faster than fuzzywuzzy
- Best performance for 1000+ checks per second requirement
- Better Unicode support for Vietnamese text
- Low memory footprint (<10MB for typical usage)

## Requirements
- **Functional**: Install RapidFuzz library with performance optimizations
- **Non-functional**: Maintain 1-second interval in background thread
- **Performance**: Minimal CPU/memory overhead

## Architecture
```
Current: Exact substring matching → FocusTrackerThread
New: RapidFuzz fuzzy matching → FocusTrackerThread with integration layer
```

## Related Code Files
- **Modify**: `core/tracker.py` - Add RapidFuzz integration
- **Create**: `requirements.txt` - Add RapidFuzz dependency
- **Create**: `tests/test_fuzzy_matching.py` - Basic integration tests

## Implementation Steps

1. **Add RapidFuzz to requirements**
   ```bash
   pip install rapidfuzz
   ```
   - Update `requirements.txt` to include `rapidfuzz>=3.0.0`

2. **Import RapidFuzz in tracker.py**
   ```python
   from rapidfuzz import process, fuzz
   ```

3. **Create basic fuzzy matching function**
   ```python
   def fuzzy_match(self, title, keywords, threshold=85):
       result = process.extractOne(title, keywords, scorer=fuzz.WRatio)
       return result and result[1] >= threshold
   ```

4. **Replace exact matching with fuzzy matching**
   - Replace `any(kw in title for kw in self.allowed_keywords)`
   - Use fuzzy_match with 85% threshold

5. **Add performance monitoring**
   - Log match performance
   - Track false positives/negatives

## Todo List
- [ ] Install RapidFuzz library
- [ ] Update requirements.txt
- [ ] Import RapidFuzz in tracker.py
- [ ] Create basic fuzzy matching function
- [ ] Replace exact matching logic
- [ ] Add performance logging
- [ ] Create basic test script

## Success Criteria
- ✅ RapidFuzz installed and working
- ✅ Fuzzy matching replaces exact substring matching
- ✅ No breaking changes to existing functionality
- ✅ Performance maintained at 1-second intervals
- ✅ Basic tests passing

## Risk Assessment
- **High**: Performance degradation - Mitigation: Benchmark before/after
- **Medium**: False positives - Mitigation: Test with threshold tuning
- **Low**: Unicode issues - Mitigation: Test with Vietnamese text

## Security Considerations
- No security risks identified
- Library is well-established and maintained

## Next Steps
- Complete Phase 01 implementation
- Proceed to Phase 02: Text Normalization Pipeline