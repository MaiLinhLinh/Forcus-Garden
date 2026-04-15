"""
Smart browser title parser.
Extracts meaningful site names from browser window titles.

Solves the "Facebook and 3 other tabs" problem by parsing
browser window titles to extract actual site information.
"""
import re
from typing import Optional, Tuple


class BrowserTitleParser:
    """Parse browser window titles to extract site names."""

    # Browser patterns: "Site - Browser" or "Site | Browser"
    BROWSER_PATTERNS = [
        r'(.+?)\s*[-|]\s*Google Chrome',
        r'(.+?)\s*[-|]\s*Mozilla Firefox',
        r'(.+?)\s*[-|]\s*Microsoft Edge',
        r'(.+?)\s*[-|]\s*Opera',
        r'(.+?)\s*[-|]\s*Brave',
        r'(.+?)\s*[-|]\s*Vivaldi',
    ]

    # Grouped tab patterns (match these to detect browser)
    GROUPED_PATTERNS = [
        r'(.+?) and \d+ other tabs',  # Extract site name before "and X other tabs"
        r'(.+?) and \d+ more tabs',   # Extract site name before "and X more tabs"
        r'\d+ tabs',
    ]

    # Browser keywords for detection
    BROWSER_KEYWORDS = [
        'google chrome', 'chrome',
        'mozilla firefox', 'firefox',
        'microsoft edge', 'edge',
        'opera', 'opera gx',
        'brave', 'vivaldi',
    ]

    def __init__(self):
        """Initialize parser with compiled regex patterns."""
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.BROWSER_PATTERNS
        ]
        self._compiled_grouped = [
            re.compile(p, re.IGNORECASE) for p in self.GROUPED_PATTERNS
        ]

    def parse(self, title: str) -> Tuple[Optional[str], bool]:
        """
        Parse browser window title.

        Args:
            title: Window title to parse

        Returns:
            (site_name, is_browser): Site name if found, whether this is a browser
        """
        if not title:
            return (None, False)

        title_lower = title.lower()

        # Check if this is a grouped tabs title FIRST (priority)
        for pattern in self._compiled_grouped:
            match = pattern.search(title)
            if match:
                site = match.group(1).strip() if match.groups() else None
                return (site, True)  # Return extracted site name or None

        # Try to extract site name from standard format
        for pattern in self._compiled_patterns:
            match = pattern.search(title)
            if match:
                site = match.group(1).strip()
                return (site, True)

        # Check if title contains browser keywords
        for keyword in self.BROWSER_KEYWORDS:
            if keyword in title_lower:
                return (title, True)  # Return full title as site name

        return (None, False)

    def is_browser(self, title: str) -> bool:
        """
        Quick check if title is from a browser.

        Args:
            title: Window title to check

        Returns:
            True if title appears to be from a browser
        """
        if not title:
            return False

        title_lower = title.lower()
        return any(kw in title_lower for kw in self.BROWSER_KEYWORDS)
