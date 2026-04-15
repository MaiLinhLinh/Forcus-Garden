"""
Diagnostic tool for Edge/Zalo browser detection issues.
Tests with actual window titles and browser parsing behavior.
"""
import sys
import os

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.browser_parser import BrowserTitleParser
from core.matcher import KeywordMatcher


def test_edge_zalo_detection():
    """Test Edge/Zalo detection with common scenarios."""
    print("=== EDGE/ZALO BROWSER DETECTION DIAGNOSTIC ===\n")

    # Initialize components
    parser = BrowserTitleParser()

    # Test scenarios
    test_scenarios = [
        {
            "name": "Edge with Zalo",
            "title": "Zalo - Microsoft Edge",
            "description": "User opens Zalo in Edge browser"
        },
        {
            "name": "Edge with Facebook",
            "title": "Facebook - Microsoft Edge",
            "description": "User opens Facebook in Edge browser"
        },
        {
            "name": "Zalo Desktop App",
            "title": "Zalo",
            "description": "User opens Zalo desktop app (not in browser)"
        },
        {
            "name": "Chrome with GitHub",
            "title": "GitHub - Google Chrome",
            "description": "User opens GitHub in Chrome (study zone)"
        },
        {
            "name": "VSCode",
            "title": "Visual Studio Code - main.py",
            "description": "User working in VSCode (study zone)"
        },
        {
            "name": "Edge with YouTube",
            "title": "YouTube - Microsoft Edge",
            "description": "User opens YouTube in Edge (distraction)"
        }
    ]

    # Run tests
    print("Testing browser parser:\n")
    for scenario in test_scenarios:
        parsed_site, is_browser = parser.parse(scenario["title"])

        print(f"Scenario: {scenario['name']}")
        print(f"  Title: {scenario['title']}")
        print(f"  Description: {scenario['description']}")
        print(f"  Parsed site: {parsed_site}")
        print(f"  Is browser: {is_browser}")
        print()

    # Test keyword matching
    print("\n=== KEYWORD MATCHING TEST ===\n")
    study_keywords = ["vscode", "chrome", "github", "stackoverflow"]
    matcher = KeywordMatcher(study_keywords, threshold=85)

    print(f"Study keywords: {study_keywords}\n")

    for scenario in test_scenarios:
        title = scenario["title"]
        parsed_site, is_browser = parser.parse(title)

        # Simulate tracker logic
        if is_browser and parsed_site:
            is_valid = matcher.is_match(parsed_site)
            if not is_valid:
                is_valid_fallback = matcher.is_match(title)
            else:
                is_valid_fallback = True
        else:
            is_valid = matcher.is_match(title)
            is_valid_fallback = is_valid

        status = "[STUDY ZONE]" if is_valid else "[DISTRACTION]"

        print(f"Title: {title}")
        print(f"  Parsed: {parsed_site}, Is browser: {is_browser}")
        print(f"  Match result: {status}")
        if is_browser and parsed_site:
            print(f"  Parsed match: {matcher.is_match(parsed_site)}")
            print(f"  Fallback match: {is_valid_fallback}")
        print()


def test_user_scenario():
    """Test a complete user scenario."""
    print("\n=== USER SCENARIO SIMULATION ===\n")

    # User workflow
    workflow = [
        ("User starts working", "Visual Studio Code - project.py", True),
        ("User checks documentation", "GitHub - Google Chrome", True),
        ("User gets distracted by Zalo", "Zalo - Microsoft Edge", False),
        ("User gets distracted by Facebook", "Facebook - Microsoft Edge", False),
        ("User returns to work", "Visual Studio Code - project.py", True),
    ]

    parser = BrowserTitleParser()
    study_keywords = ["vscode", "chrome", "github"]
    matcher = KeywordMatcher(study_keywords, threshold=85)

    print(f"Study keywords: {study_keywords}\n")

    for step, title, should_be_valid in workflow:
        parsed_site, is_browser = parser.parse(title)

        if is_browser and parsed_site:
            is_valid = matcher.is_match(parsed_site)
            if not is_valid:
                is_valid = matcher.is_match(title)
        else:
            is_valid = matcher.is_match(title)

        expected = "[STUDY ZONE]" if should_be_valid else "[DISTRACTION]"
        actual = "[STUDY ZONE]" if is_valid else "[DISTRACTION]"
        match = "[PASS]" if is_valid == should_be_valid else "[FAIL]"

        print(f"{step}")
        print(f"  Title: {title}")
        print(f"  Parsed: {parsed_site}, Browser: {is_browser}")
        print(f"  Expected: {expected}")
        print(f"  Actual: {actual}")
        print(f"  Result: {match}")
        print()


def main():
    """Run all diagnostic tests."""
    test_edge_zalo_detection()
    test_user_scenario()

    print("\n=== DIAGNOSTIC COMPLETE ===")
    print("\nIf Edge/Zalo detection is still failing:")
    print("1. Check your study keywords configuration")
    print("2. Verify actual Edge window titles match test patterns")
    print("3. Test with real Edge/Zalo windows using pygetwindow")


if __name__ == "__main__":
    main()
