"""
Test matching behavior with real window titles and thresholds.
"""
import sys
sys.path.insert(0, '.')

from core.matcher import KeywordMatcher
from core.alias_manager import AppAliasManager

# Real-world window titles to test
test_cases = [
    # Zalo cases
    ("Zalo", ["zalo"]),
    ("Zalo - Some Message", ["zalo"]),
    ("zalo", ["zalo"]),
    ("Zalo ", ["zalo"]),

    # Edge cases
    ("Microsoft Edge", ["edge"]),
    ("Edge - Some Tab", ["edge"]),
    ("new tab - Microsoft Edge", ["edge"]),

    # Browser tab cases
    ("GitHub - project | Visual Studio Code - Microsoft Edge", ["vscode"]),
    ("YouTube - Music - Microsoft Edge", ["chrome"]),
]

def test_threshold_sensitivity():
    """Test different threshold values with real titles."""
    thresholds = [70, 75, 80, 85, 90, 95]

    print("=" * 80)
    print("THRESHOLD SENSITIVITY TEST")
    print("=" * 80)

    for threshold in thresholds:
        print(f"\n--- Threshold: {threshold}% ---")
        matcher = KeywordMatcher(["zalo", "edge", "vscode"], threshold=threshold)

        for title, keywords in test_cases:
            result = matcher.is_match(title)
            expected = any(kw in title.lower() for kw in keywords)
            status = "OK" if result == expected else "FAIL"
            print(f"{status} '{title[:50]}...' -> {result} (expected: {expected})")

def test_alias_coverage():
    """Test if aliases cover common variations."""
    print("\n" + "=" * 80)
    print("ALIAS COVERAGE TEST")
    print("=" * 80)

    alias_manager = AppAliasManager()

    # Test Zalo variations
    print("\n--- Zalo Variations ---")
    zalo_variations = alias_manager.get_all_variations("zalo")
    print(f"Zalo variations: {zalo_variations}")
    print(f"Has 'zalo': {'zalo' in zalo_variations}")
    print(f"Has 'Zalo': {'zalo' in [v.lower() for v in zalo_variations]}")

    # Test Edge variations
    print("\n--- Edge Variations ---")
    edge_variations = alias_manager.get_all_variations("edge")
    print(f"Edge variations: {edge_variations}")
    print(f"Has 'microsoft edge': {'microsoft edge' in edge_variations}")

def test_exact_vs_fuzzy():
    """Test exact matching vs fuzzy matching."""
    print("\n" + "=" * 80)
    print("EXACT VS FUZZY MATCHING TEST")
    print("=" * 80)

    matcher = KeywordMatcher(["zalo", "edge"], threshold=90)

    # Test exact substring match
    print("\n--- Exact Substring Tests ---")
    exact_tests = [
        ("Zalo", True),
        ("zalo", True),
        ("Zalo - Chat", True),
        ("Microsoft Edge", True),
        ("Some Edge Tab", True),
        ("edge", True),
    ]

    for title, expected in exact_tests:
        result = matcher.is_match(title)
        status = "OK" if result == expected else "FAIL"
        print(f"{status} '{title}' -> {result} (expected: {expected})")

    # Test fuzzy match (near misses)
    print("\n--- Fuzzy Match Tests (threshold=90) ---")
    fuzzy_tests = [
        ("Zalo ", True),  # Extra space
        ("Zalo", True),   # Case match
        ("Microsoft Edge", True),
        ("edge chromium", True),
    ]

    for title, expected in fuzzy_tests:
        result = matcher.is_match(title)
        status = "OK" if result == expected else "FAIL"
        print(f"{status} '{title}' -> {result} (expected: {expected})")

if __name__ == "__main__":
    test_threshold_sensitivity()
    test_alias_coverage()
    test_exact_vs_fuzzy()
