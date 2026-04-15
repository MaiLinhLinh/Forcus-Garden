"""
Text normalization for Vietnamese and English.
Handles Unicode, case, and whitespace normalization.

This module ensures consistent text matching across different
character encodings and formatting variations.
"""
import unicodedata
import re


class TextNormalizer:
    """Normalize text for consistent matching."""

    def __init__(self):
        """
        Initialize normalizer with Vietnamese diacritic ranges.

        Vietnamese diacritics need special handling to preserve
        meaning while enabling case-insensitive matching.
        """
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

        Args:
            text: Input text to normalize

        Returns:
            Normalized text string
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
        Used in the hot path of window title matching.

        Args:
            text: Input text to normalize

        Returns:
            Normalized text string
        """
        if not text:
            return ""
        return unicodedata.normalize('NFC', text.lower()).strip()
