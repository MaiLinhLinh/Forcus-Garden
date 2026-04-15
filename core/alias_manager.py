"""
Alias system for application name variations.
Maps user-friendly keywords to actual window titles.

Users often type abbreviations ("vscode") but titles show full names
("Visual Studio Code"). This system bridges that gap.
"""
from typing import Dict, List


class AppAliasManager:
    """Manage application name aliases."""

    def __init__(self):
        """
        Initialize alias manager with built-in alias dictionary.

        Covers common development tools, browsers, office apps,
        and communication platforms with Vietnamese support.
        """
        # Built-in alias dictionary
        self.aliases: Dict[str, List[str]] = {
            # Development Tools
            "vscode": ["visual studio code", "vs code", "visualstudio"],
            "vs": ["visual studio", "visualstudio"],
            "idea": ["intellij idea", "jetbrains idea", "intellij"],
            "pycharm": ["pycharm", "jetbrains pycharm"],
            "sublime": ["sublime text", "sublimetext"],

            # Browsers
            "chrome": ["google chrome", "chromium"],
            "firefox": ["mozilla firefox", "firefox", "mozilla"],
            "edge": ["microsoft edge", "edge chromium"],
            "opera": ["opera gx", "opera browser"],

            # Communication
            "discord": ["discord", "discord canary", "discord ptb"],
            "slack": ["slack", "slack desktop"],

            # Office Apps (Vietnamese/English)
            "word": ["microsoft word", "word 2019", "word 2021", "word 2023"],
            "excel": ["microsoft excel", "excel 2019", "excel 2021"],
            "powerpoint": ["microsoft powerpoint", "ppt", "powerpoint"],

            # Vietnamese Apps
            "zoom": ["zoom meeting", "zoom rooms"],
            "teams": ["microsoft teams", "teams"],
            "zalo": ["zalo", "zalo pc"],  # Vietnamese messaging app
        }

    def get_all_variations(self, keyword: str) -> List[str]:
        """
        Get all possible variations for a keyword.

        Returns original keyword + aliases + reverse aliases.
        This ensures that "vscode" finds "Visual Studio Code" and
        "Visual Studio Code" finds "vscode".

        Args:
            keyword: The keyword to expand

        Returns:
            List of all possible variations
        """
        normalized_kw = keyword.strip().lower()
        variations = {normalized_kw}

        # Add direct aliases
        if normalized_kw in self.aliases:
            for alias in self.aliases[normalized_kw]:
                variations.add(alias)

        # Add reverse: find keywords that have this as alias
        for kw, aliases in self.aliases.items():
            if normalized_kw in [a.lower() for a in aliases]:
                variations.add(kw)
                for alias in aliases:
                    variations.add(alias.lower())

        return list(variations)
