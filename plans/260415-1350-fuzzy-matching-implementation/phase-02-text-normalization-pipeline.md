# Phase 02: Text Normalization Pipeline

## Context Links
- [Research Report](../reports/researcher-260415-1350-fuzzy-string-matching.md)
- [Phase 01](./phase-01-setup-rapidfuzz-integration.md)
- [Implementation Plan](../plan.md)

## Overview
**Priority**: High
**Current Status**: Pending
**Description**: Implement comprehensive text normalization pipeline to handle Vietnamese characters, Unicode normalization, and case consistency.

## Key Insights
- Vietnamese diacritics need proper Unicode normalization (NFC)
- Special characters should be removed while preserving Vietnamese characters
- Performance optimization through caching is crucial
- Normalization must be consistent between keywords and window titles

## Requirements
- **Functional**: Handle Vietnamese text normalization correctly
- **Non-functional**: Maintain performance with cached normalization
- **Performance**: Sub-millisecond normalization time with caching

## Architecture
```
TextNormalizer class → Unicode normalization → Case conversion → Special char removal → Caching
```

## Related Code Files
- **Create**: `core/text-normalizer.py` - Text normalization module
- **Modify**: `core/tracker.py` - Integrate normalization pipeline
- **Create**: `tests/test_normalization.py` - Normalization tests

## Implementation Steps

1. **Create TextNormalizer class**
   ```python
   class TextNormalizer:
       def __init__(self):
           self.unicode_normalizer = unicodedata.normalize
           self.cache = {}
           self.cache_size = 1000

       def normalize(self, text):
           # Unicode normalization (NFC)
           # Lowercase conversion
           # Special character removal
           # Whitespace normalization
           return normalized_text

       def normalize_cached(self, text):
           # Use cache for better performance
           if text in self.cache:
               return self.cache[text]

           result = self.normalize(text)
           self.cache[text] = result
           return result
   ```

2. **Handle Vietnamese characters specifically**
   - Preserve Vietnamese diacritics (à, á, ả, ã, ạ, etc.)
   - Handle Unicode combining characters
   - Test with Vietnamese app names

3. **Implement caching strategy**
   - LRU cache for recent text
   - Memory-efficient storage
   - Clear cache on keyword changes

4. **Integrate with tracker**
   - Normalize all keywords during initialization
   - Normalize window titles on each check
   - Use normalized text for fuzzy matching

## Todo List
- [ ] Create TextNormalizer class
- [ ] Implement Unicode normalization (NFC)
- [ ] Add case conversion and special char removal
- [ ] Implement caching system
- [ ] Add Vietnamese character support
- [ ] Integrate with tracker.py
- [ ] Create normalization tests

## Success Criteria
- ✅ Vietnamese text normalized correctly
- ✅ Performance <1ms per normalization with caching
- ✅ Consistent normalization between keywords and titles
- ✅ No memory leaks with caching
- ✅ All normalization tests passing

## Risk Assessment
- **High**: Unicode normalization breaking Vietnamese text - Mitigation: Test with real Vietnamese data
- **Medium**: Performance issues with normalization - Mitigation: Implement caching
- **Low**: Memory usage too high - Mitigation: Cache size limits

## Security Considerations
- No security risks identified
- Text normalization is safe operation

## Next Steps
- Complete Phase 02 implementation
- Proceed to Phase 03: Alias Dictionary System