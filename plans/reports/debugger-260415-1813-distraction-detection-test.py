"""
Test distraction detection when Zalo is NOT in allowed list.
This simulates the actual bug: Zalo should be detected as distraction.
"""
import sys
sys.path.insert(0, '.')

from core.matcher import KeywordMatcher

def test_distraction_detection():
    """Test that Zalo is NOT matched when not in allowed list."""
    print("=" * 80)
    print("DISTRACTION DETECTION TEST - Zalo NOT in allowed list")
    print("=" * 80)

    # Simulate allowed keywords (study zone apps)
    allowed_keywords = ["vscode", "chrome", "edge"]

    # Test with different thresholds
    for threshold in [70, 80, 85, 90]:
        print(f"\n--- Threshold: {threshold}% ---")
        matcher = KeywordMatcher(allowed_keywords, threshold=threshold)

        # Test cases: Zalo should NOT match (it's a distraction)
        zalo_titles = [
            "Zalo",
            "Zalo - Some Message",
            "zalo",
            "Zalo Chat",
        ]

        print("Zalo titles (should NOT match):")
        for title in zalo_titles:
            result = matcher.is_match(title)
            status = "FAIL" if result else "OK"
            print(f"  {status} '{title}' -> {result} (should be False)")

        # Test cases: Edge should match (it's allowed)
        edge_titles = [
            "Microsoft Edge",
            "Edge - Some Tab",
        ]

        print("Edge titles (should match):")
        for title in edge_titles:
            result = matcher.is_match(title)
            status = "OK" if result else "FAIL"
            print(f"  {status} '{title}' -> {result} (should be True)")

def test_browser_title_parsing():
    """Test browser title parsing with Edge."""
    print("\n" + "=" * 80)
    print("BROWSER TITLE PARSING TEST")
    print("=" * 80)

    from core.browser_parser import BrowserTitleParser

    parser = BrowserTitleParser()

    # Test Edge titles
    edge_titles = [
        "GitHub - project | Visual Studio Code - Microsoft Edge",
        "YouTube - Music - Microsoft Edge",
        "Zalo - Microsoft Edge",
        "new tab - Microsoft Edge",
    ]

    print("\nEdge title parsing:")
    for title in edge_titles:
        site, is_browser = parser.parse(title)
        print(f"  '{title[:50]}...'")
        print(f"    -> site: '{site}', is_browser: {is_browser}")

def test_zalo_edge_case():
    """Test specific Zalo/Edge edge cases."""
    print("\n" + "=" * 80)
    print("ZALO/EDGE EDGE CASE TEST")
    print("=" * 80)

    # Allowed: vscode, edge
    # Distraction: zalo
    allowed_keywords = ["vscode", "edge"]
    matcher = KeywordMatcher(allowed_keywords, threshold=90)

    test_cases = [
        # Zalo should NOT match
        ("Zalo", False, "Direct Zalo"),
        ("Zalo - Chat", False, "Zalo with chat"),
        ("zalo", False, "Lowercase zalo"),

        # Edge should match
        ("Microsoft Edge", True, "Full Edge name"),
        ("Edge - Tab", True, "Edge with tab"),
        ("new tab - Microsoft Edge", True, "Edge at end"),

        # Edge browser tabs
        ("GitHub - Visual Studio Code - Microsoft Edge", True, "VSCode in Edge"),
        ("Zalo - Microsoft Edge", True, "Zalo in Edge tab (should match Edge)"),
    ]

    print("\nEdge cases:")
    for title, should_match, description in test_cases:
        result = matcher.is_match(title)
        status = "OK" if result == should_match else "FAIL"
        print(f"  {status} {description}")
        print(f"      '{title[:50]}...' -> {result} (expected: {should_match})")

if __name__ == "__main__":
    test_distraction_detection()
    test_browser_title_parsing()
    test_zalo_edge_case()
