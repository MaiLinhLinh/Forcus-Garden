"""
Fuzzy keyword matcher using RapidFuzz.
Separated from tracker.py for modularity (file size < 200 lines).

Phase 1: Basic RapidFuzz integration ✅
Phase 2: Text normalization pipeline ✅
Phase 3: Alias dictionary system ✅
"""
from rapidfuzz import process, fuzz
from core.normalizer import TextNormalizer
from core.alias_manager import AppAliasManager


class KeywordMatcher:
    """Flexible keyword matching with RapidFuzz."""

    def __init__(self, keywords, threshold=85):
        """
        Initialize keyword matcher.

        Args:
            keywords: List of user-defined keywords
            threshold: Fuzzy match threshold (0-100), default 85
        """
        self.raw_keywords = keywords
        self.threshold = threshold
        self.normalizer = TextNormalizer()
        self.alias_manager = AppAliasManager()
        self._build_patterns()

    def _build_patterns(self):
        """
        Pre-process keywords with normalization and aliases.

        Phase 3: Added alias expansion for common app variations
        Creates expanded pattern list for comprehensive matching.
        """
        self._patterns = set()

        for kw in self.raw_keywords:
            # Get all variations (original + aliases)
            variations = self.alias_manager.get_all_variations(kw)

            # Normalize each variation and add to patterns
            for variation in variations:
                normalized = self.normalizer.normalize(variation)
                self._patterns.add(normalized)

        self._patterns = list(self._patterns)

    def is_match(self, title: str) -> bool:
        """
        Check if title matches any keyword.

        Args:
            title: Window title to check

        Returns:
            True if title matches any keyword, False otherwise
        """
        if not title:
            return False

        # Phase 2: Use quick normalization for performance
        normalized_title = self.normalizer.quick_normalize(title)

        # Fast path: exact substring first (performance optimization)
        for pattern in self._patterns:
            if pattern in normalized_title:
                return True

        # Fuzzy matching for partial matches (only for longer titles)
        if len(normalized_title) >= 4:
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
                pass

        return False
