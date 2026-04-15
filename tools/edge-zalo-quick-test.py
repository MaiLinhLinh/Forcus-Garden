"""
Quick test script for real-time Edge/Zalo window detection.
Use this to test actual window titles on your system.
"""
import sys
import os

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import pygetwindow as gw
    from core.browser_parser import BrowserTitleParser
    from core.matcher import KeywordMatcher

    print("=== REAL-TIME EDGE/ZALO WINDOW DETECTION ===\n")

    # Initialize components
    parser = BrowserTitleParser()
    study_keywords = ["vscode", "chrome", "github"]  # Adjust as needed
    matcher = KeywordMatcher(study_keywords, threshold=85)

    print(f"Study keywords: {study_keywords}\n")

    # Get all windows
    windows = gw.getAllWindows()

    # Filter for Edge and Zalo windows
    edge_zalo_windows = [
        w for w in windows
        if w.title and ('edge' in w.title.lower() or 'zalo' in w.title.lower())
    ]

    if not edge_zalo_windows:
        print("No Edge or Zalo windows found.")
        print("\nAll active windows:")
        for w in windows[:10]:  # Show first 10
            if w.title:
                print(f"  - {w.title}")
    else:
        print(f"Found {len(edge_zalo_windows)} Edge/Zalo window(s):\n")

        for window in edge_zalo_windows:
            title = window.title
            parsed_site, is_browser = parser.parse(title)

            # Test matching
            if is_browser and parsed_site:
                is_valid = matcher.is_match(parsed_site)
                if not is_valid:
                    is_valid = matcher.is_match(title)
            else:
                is_valid = matcher.is_match(title)

            status = "[STUDY ZONE]" if is_valid else "[DISTRACTION]"

            print(f"Window: {title}")
            print(f"  Parsed: {parsed_site}, Is browser: {is_browser}")
            print(f"  Status: {status}")
            print()

    print("\n=== TESTING COMMON PATTERNS ===\n")

    # Test common patterns
    test_patterns = [
        "Zalo - Microsoft Edge",
        "Facebook - Microsoft Edge",
        "GitHub - Google Chrome",
        "Visual Studio Code",
        "Zalo",  # Desktop app
    ]

    for pattern in test_patterns:
        parsed_site, is_browser = parser.parse(pattern)

        if is_browser and parsed_site:
            is_valid = matcher.is_match(parsed_site)
            if not is_valid:
                is_valid = matcher.is_match(pattern)
        else:
            is_valid = matcher.is_match(pattern)

        status = "[STUDY ZONE]" if is_valid else "[DISTRACTION]"

        print(f"Pattern: {pattern}")
        print(f"  Parsed: {parsed_site}, Browser: {is_browser}")
        print(f"  Status: {status}")
        print()

except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease install required packages:")
    print("  pip install pygetwindow rapidfuzz")
except Exception as e:
    print(f"Error: {e}")
