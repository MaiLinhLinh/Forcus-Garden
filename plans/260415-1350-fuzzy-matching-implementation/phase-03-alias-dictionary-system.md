# Phase 03: Alias Dictionary System

## Context Links
- [Research Report](../reports/researcher-260415-1350-fuzzy-string-matching.md)
- [Phase 01](./phase-01-setup-rapidfuzz-integration.md)
- [Phase 02](./phase-02-text-normalization-pipeline.md)
- [Implementation Plan](../plan.md)

## Overview
**Priority**: High
**Current Status**: Pending
**Description**: Implement alias dictionary system to handle common app name variations and improve matching accuracy for user-defined keywords.

## Key Insights
- Common aliases needed: "vscode" → "visual studio code", "chrome" → "google chrome"
- Bidirectional mapping: find both "vscode" matches and "visual studio code" matches
- Vietnamese language aliases important for local users
- User-defined aliases should be persistent

## Requirements
- **Functional**: Support predefined and user-defined aliases
- **Non-functional**: Efficient lookup with caching
- **Performance**: Sub-millisecond alias lookup time

## Architecture
```
AliasSystem class → Predefined aliases → User-defined aliases → Bidirectional mapping → Keyword variations
```

## Related Code Files
- **Create**: `core/alias-system.py` - Alias dictionary module
- **Modify**: `database/models.py` - Add alias storage
- **Create**: `tests/test_alias_system.py` - Alias system tests
- **Create**: `ui/alias_editor.py` - UI for alias management (future)

## Implementation Steps

1. **Create AppAliasSystem class**
   ```python
   class AppAliasSystem:
       def __init__(self):
           self.aliases = {
               "vscode": ["visual studio code", "vs code"],
               "chrome": ["google chrome", "googlechromium"],
               # ... more predefined aliases
           }
           self.custom_aliases = {}
           self.variations_cache = {}

       def get_all_variations(self, keyword):
           # Get all variations including predefined and custom aliases
           return variations

       def add_custom_alias(self, alias, main_keyword):
           # Add user-defined alias
           pass

       def save_aliases(self):
           # Persist aliases to database
           pass

       def load_aliases(self):
           # Load aliases from database
           pass
   ```

2. **Implement predefined aliases**
   - Development tools (VSCode, PyCharm, IntelliJ)
   - Browsers (Chrome, Firefox, Edge)
   - Communication apps (Discord, Slack)
   - Office apps (Word, Excel, PowerPoint)
   - Common Vietnamese apps

3. **Add custom alias support**
   - User-defined alias mapping
   - Persistence to database
   - Real-time loading without restart

4. **Implement variation caching**
   - Pre-compute all keyword variations
   - Cache normalized variations
   - Clear cache when aliases change

5. **Integrate with tracker**
   - Use alias system to expand keyword list
   - Apply variations before fuzzy matching
   - Handle alias updates in real-time

## Todo List
- [ ] Create AppAliasSystem class
- [ ] Implement predefined aliases for common apps
- [ ] Add custom alias management
- [ ] Implement variation caching
- [ ] Integrate with tracker.py
- [ ] Add alias persistence to database
- [ ] Create alias system tests
- [ ] Test Vietnamese alias support

## Success Criteria
- ✅ Common app aliases working (vscode → visual studio code)
- ✅ User can add custom aliases
- ✅ Aliases persisted across sessions
- ✅ Fast lookup with caching
- ✅ All alias tests passing
- ✅ Vietnamese language aliases supported

## Risk Assessment
- **High**: Circular alias references - Mitigation: Validation on addition
- **Medium**: Memory usage with many aliases - Mitigation: Cache size limits
- **Low**: Performance impact - Mitigation: Pre-computation and caching

## Security Considerations
- No security risks identified
- User aliases are stored locally

## Next Steps
- Complete Phase 03 implementation
- Proceed to Phase 04: Fuzzy Matching Implementation