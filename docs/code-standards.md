# Code Standards - Focus Garden

## Overview

This document outlines the coding standards and conventions used in the Focus Garden project. The project follows modern Python development practices with emphasis on modularity, performance, and maintainability.

## Core Principles

### 1. YAGNI (You Aren't Gonna Need It)
- Build only what's needed for current requirements
- Avoid over-engineering solutions
- Focus on immediate problem solving
- Keep code simple and direct

### 2. KISS (Keep It Simple, Stupid)
- Prefer simple solutions over complex ones
- Write readable, maintainable code
- Avoid unnecessary abstraction
- Choose straightforward algorithms

### 3. DRY (Don't Repeat Yourself)
- Eliminate code duplication
- Create reusable components
- Use shared utilities and patterns
- Implement common functionality once

## File Size Management

### Maximum File Size: 200 Lines
All code modules must be under 200 lines for optimal context management.

### Modular Architecture Strategy
```
core/
├── matcher.py         # Fuzzy matching (87 lines)
├── normalizer.py      # Text normalization (87 lines)
├── alias-manager.py   # Alias system (80 lines)
├── browser-parser.py  # Browser parsing (98 lines)
└── tracker.py         # State machine (under 200 lines)
```

### Modularization Guidelines
1. **Single Responsibility**: Each module handles one specific task
2. **Loose Coupling**: Minimal dependencies between modules
3. **High Cohesion**: Related functionality grouped together
4. **Composition Over Inheritance**: Use composition for complex widgets

## Naming Conventions

### Python Files
- Use kebab-case for file names (e.g., `alias-manager.py`)
- Descriptive names that explain the module's purpose
- No abbreviations unless universally understood

### Classes
- Use PascalCase for class names
- Follow noun naming convention
- Add clear docstrings

```python
class KeywordMatcher:           # ✅ Good
class FuzzyMatchEngine:        # ✅ Good
class text_normalizer:          # ❌ Should be TextNormalizer
class matchUtils:               # ❌ Should be MatchUtils
```

### Methods and Functions
- Use snake_case for method names
- Use imperative verbs for actions
- Keep method names concise but descriptive

```python
def is_match(self, title):          # ✅ Good
def build_patterns(self):          # ✅ Good
def normalize_text(self):          # ✅ Good
def match_keyword():               # ❌ Missing object context
def IsMatch():                     # ❌ Should be snake_case
```

### Variables and Parameters
- Use snake_case for variables
- Use descriptive names
- Avoid single-letter variables except in loops

```python
threshold = 85                    # ✅ Good
fast_patterns = set()             # ✅ Good
parsed_site, is_browser = parser.parse(title)  # ✅ Good
t = 85                            # ❌ Should be threshold
patterns = []                     # ❌ Too generic; use specific names
```

## Documentation Standards

### Docstring Format
Use Google-style docstrings for all public classes and methods.

```python
class KeywordMatcher:
    """Flexible keyword matching with RapidFuzz.

    Implements fuzzy matching for distraction detection with
    customizable threshold and alias expansion.

    Attributes:
        raw_keywords (List[str]): Original user-defined keywords
        threshold (int): Fuzzy match threshold (0-100)
    """

    def is_match(self, title: str) -> bool:
        """Check if title matches any keyword.

        Args:
            title: Window title to check

        Returns:
            True if title matches any keyword, False otherwise
        """
```

### Inline Comments
- Comment complex logic, not obvious code
- Explain why, not what
- Keep comments updated with code changes

```python
# Fast path: exact substring first (performance optimization)
for pattern in self._patterns:
    if pattern in normalized_title:
        return True

# Fuzzy matching for partial matches (only for longer titles)
if len(normalized_title) >= 4:
    result = process.extractOne(...)
```

### Module Documentation
Each module should have:
- Module-level docstring explaining purpose
- Key features and capabilities
- Dependencies and requirements
- Usage examples

## Code Quality Guidelines

### Readability
- Use clear, descriptive variable names
- Avoid magic numbers; use constants
- Keep line length under 100 characters
- Use proper whitespace and indentation

```python
# ✅ Good
RAPIDFUZZ_THRESHOLD = 85
MIN_FUZZY_LENGTH = 4

# ❌ Bad
threshold = 85
min_len = 4
```

### Error Handling
- Use try-catch for expected errors
- Provide meaningful error messages
- Fail gracefully with fallbacks
- Log errors appropriately

```python
try:
    result = process.extractOne(
        normalized_title,
        self._patterns,
        scorer=fuzz.WRatio,
        score_cutoff=self.threshold
    )
    return result is not None
except Exception:
    # Fallback to exact matching if fuzzy fails
    return False
```

### Type Hints
- Use type hints for all public methods
- Include return types
- Use specific types (e.g., `str`, `int`, `bool`)
- Optional types with `Optional[]`

```python
from typing import List, Dict, Tuple, Optional

def get_all_variations(self, keyword: str) -> List[str]:
    """Get all possible variations for a keyword.

    Args:
        keyword: The keyword to expand

    Returns:
        List of all possible variations
    """
    pass

def parse(self, title: str) -> Tuple[Optional[str], bool]:
    """Parse browser window title.

    Args:
        title: Window title to parse

    Returns:
        (site_name, is_browser): Site name if found, whether this is a browser
    """
    pass
```

### Performance Standards

#### Fast Path Optimization
```python
# Fast path: exact substring first (performance critical)
for pattern in self._patterns:
    if pattern in normalized_title:
        return True
```

#### Memory Efficiency
```python
# Use sets for O(1) lookups
self._patterns = set()
# Convert to list after building
self._patterns = list(self._patterns)
```

#### Algorithmic Complexity
- Aim for O(1) or O(n) time complexity
- Avoid nested loops where possible
- Use efficient data structures
- Profile performance-critical sections

## Testing Standards

### Test File Structure
- Test files should mirror module structure
- Use descriptive test method names
- Test both happy path and edge cases
- Include performance tests for critical methods

```python
class TestRapidFuzzyMatching(unittest.TestCase):
    """Test fuzzy matching functionality."""

    def setUp(self):
        self.matcher = KeywordMatcher(["vscode", "chrome", "idea"], threshold=85)

    def test_exact_substring_match(self):
        """Test exact substring matching (fast path)."""
        # Should match
        self.assertTrue(self.matcher.is_match("Visual Studio Code - main.py"))
```

### Test Coverage Requirements
- 100% line coverage for core modules
- Integration tests for module interactions
- Performance tests for speed requirements
- Edge case testing for error conditions

### Test Naming
- Use descriptive test method names
- Test individual features clearly
- Document expected behavior in test names
- Use consistent naming pattern

```python
def test_exact_substring_match(self):      # ✅ Good
def test_fuzzy_match_threshold_85(self):   # ✅ Good
def test_negative_cases_different_app(self): # ✅ Good
def test_vscode_matching(self):           # ❌ Too generic
```

## Design Patterns

### 1. Single Responsibility Principle
Each class should have only one reason to change.

```python
# ✅ Good separation of concerns
class TextNormalizer:      # Only text normalization
class KeywordMatcher:     # Only keyword matching
class BrowserParser:       # Only browser title parsing
class AppAliasManager:     # Only alias management
```

### 2. Composition Pattern
Use composition instead of inheritance for complex behaviors.

```python
class KeywordMatcher:
    def __init__(self, keywords, threshold=85):
        self.normalizer = TextNormalizer()
        self.alias_manager = AppAliasManager()
```

### 3. Strategy Pattern
Different matching strategies based on context.

```python
# Fast path: exact substring first
if pattern in normalized_title:
    return True

# Fuzzy path: RapidFuzz for partial matches
if len(normalized_title) >= 4:
    result = process.extractOne(...)
```

### 4. Factory Pattern
For creating complex objects with configuration.

```python
# Simple factory pattern for different matcher types
def create_matcher(match_type="fuzzy", **kwargs):
    if match_type == "fuzzy":
        return KeywordMatcher(**kwargs)
    elif match_type == "exact":
        return ExactMatcher(**kwargs)
```

## Security Standards

### Input Validation
- Validate all external inputs
- Sanitize user-provided data
- Handle malformed data gracefully
- Use type hints to enforce expected types

```python
def is_match(self, title: str) -> bool:
    """Check if title matches any keyword."""
    if not title:
        return False
    # Additional validation as needed
```

### Data Protection
- No hardcoded secrets in code
- Use environment variables for sensitive data
- Validate database queries
- Handle user data securely

### Performance Security
- Prevent denial of service through excessive processing
- Use rate limiting if applicable
- Monitor resource usage
- Implement timeouts for long operations

## Integration Standards

### Module Dependencies
- Keep dependencies minimal and well-documented
- Use clear interfaces between modules
- Avoid circular dependencies
- Document version requirements

### Database Standards
- Use parameterized queries to prevent injection
- Handle database connection failures gracefully
- Implement proper connection pooling
- Use transactions for data consistency

### UI Standards
- Separate UI logic from business logic
- Use proper event handling
- Implement responsive design principles
- Follow platform-specific UI guidelines

## Code Review Checklist

### Before Review
- [ ] File size under 200 lines
- [ ] All type hints present and correct
- [ ] Comprehensive docstrings
- [ ] Appropriate error handling
- [ ] Performance considerations addressed
- [ ] Test coverage meets requirements
- [ ] Code follows naming conventions
- [ ] No hardcoded secrets

### During Review
- [ ] Readability and maintainability
- [ ] Algorithm efficiency
- [ ] Error handling completeness
- [ ] Security considerations
- [ ] Performance impact
- [ ] Documentation clarity
- [ ] Integration with existing code
- [ ] Future maintainability

### After Review
- [ ] All issues addressed
- [ ] Test updated if needed
- [ ] Documentation updated
- [ ] Performance verified
- [ ] Integration tested

## Continuous Integration

### Automated Testing
- Run all tests before commits
- Include performance tests
- Check code style and formatting
- Validate documentation completeness

### Quality Metrics
- Maintain 100% test coverage
- Keep files under 200 lines
- Maintain performance targets
- Enforce code standards consistently

### Build Verification
- Compile without errors
- Pass all unit tests
- Pass integration tests
- Meet performance benchmarks

---

*Last Updated: April 15, 2026*
*Version: 2.0.0*
*Status: Code standards documented for modular architecture*