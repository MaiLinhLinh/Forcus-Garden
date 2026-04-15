"""
Test Edge/Zalo browser detection issue.
Investigate actual window title formats and parsing behavior.
"""
import unittest
import sys
import os

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from core.browser_parser import BrowserTitleParser
from core.matcher import KeywordMatcher


class TestEdgeZaloDetection(unittest.TestCase):
    """Test Edge browser and Zalo app detection."""

    def setUp(self):
        self.parser = BrowserTitleParser()

    def test_edge_browser_patterns(self):
        """Test various Edge browser title patterns."""
        test_cases = [
            # Standard Edge titles
            ("Zalo - Microsoft Edge", ("Zalo", True)),
            ("Facebook - Microsoft Edge", ("Facebook", True)),
            ("GitHub - Microsoft Edge", ("GitHub", True)),

            # Edge with pipe separator
            ("Zalo | Microsoft Edge", ("Zalo", True)),
            ("Facebook | Microsoft Edge", ("Facebook", True)),

            # Edge with extra spaces
            ("Zalo  -  Microsoft Edge", ("Zalo", True)),

            # Edge without site name (just browser)
            ("Microsoft Edge", ("Microsoft Edge", True)),
            ("Microsoft Edge - Settings", ("Microsoft Edge - Settings", True)),
        ]

        for title, expected in test_cases:
            result = self.parser.parse(title)
            self.assertEqual(result, expected,
                           f"Failed for title: '{title}'. Expected {expected}, got {result}")

    def test_zalo_app_patterns(self):
        """Test Zalo desktop app (non-browser) patterns."""
        test_cases = [
            # Zalo desktop app (not in browser)
            ("Zalo", (None, False)),
            ("Zalo - Chat", (None, False)),
            ("Zalo PC", (None, False)),

            # Zalo in different browsers
            ("Zalo - Google Chrome", ("Zalo", True)),
            ("Zalo - Mozilla Firefox", ("Zalo", True)),
            ("Zalo - Opera", ("Zalo", True)),
        ]

        for title, expected in test_cases:
            result = self.parser.parse(title)
            self.assertEqual(result, expected,
                           f"Failed for title: '{title}'. Expected {expected}, got {result}")

    def test_edge_detection_only(self):
        """Test Edge browser detection using is_browser method."""
        edge_titles = [
            "Zalo - Microsoft Edge",
            "Microsoft Edge",
            "Microsoft Edge - In Private",
            "Some Site | Microsoft Edge",
        ]

        for title in edge_titles:
            self.assertTrue(self.parser.is_browser(title),
                          f"Failed to detect Edge browser in: '{title}'")

    def test_keyword_matching_with_zalo(self):
        """Test keyword matching behavior with Zalo-related titles."""
        # Create matcher with common study apps
        study_apps = ["vscode", "chrome", "github", "stackoverflow", "notepad"]
        matcher = KeywordMatcher(study_apps, threshold=85)

        # Test cases: (title, should_match)
        test_cases = [
            # Study apps - should match
            ("Visual Studio Code - main.py", True),
            ("GitHub - Google Chrome", True),
            ("Stack Overflow - Mozilla Firefox", True),

            # Zalo - should NOT match (not in study apps)
            ("Zalo", False),
            ("Zalo - Microsoft Edge", False),
            ("Zalo - Chat", False),

            # Other distractions - should NOT match
            ("Facebook - Microsoft Edge", False),
            ("YouTube - Google Chrome", False),
        ]

        for title, expected in test_cases:
            result = matcher.is_match(title)
            self.assertEqual(result, expected,
                           f"Failed for title: '{title}'. Expected {expected}, got {result}")

    def test_integration_edge_zalo_scenario(self):
        """Test complete integration scenario with Edge/Zalo."""
        # Simulate the tracking workflow
        study_keywords = ["vscode", "chrome", "github"]
        matcher = KeywordMatcher(study_keywords, threshold=90)

        # Scenario 1: User switches from VSCode to Zalo in Edge
        vscode_title = "Visual Studio Code - main.py"
        zalo_edge_title = "Zalo - Microsoft Edge"

        # VSCode should be valid (study zone)
        parsed_vscode, is_vscode_browser = self.parser.parse(vscode_title)
        if is_vscode_browser and parsed_vscode:
            is_vscode_valid = matcher.is_match(parsed_vscode)
        else:
            is_vscode_valid = matcher.is_match(vscode_title)

        self.assertTrue(is_vscode_valid, "VSCode should be detected as study zone")

        # Zalo in Edge should be invalid (distraction)
        parsed_zalo, is_zalo_browser = self.parser.parse(zalo_edge_title)
        if is_zalo_browser and parsed_zalo:
            is_zalo_valid = matcher.is_match(parsed_zalo)
            # Also test fallback to full title
            is_zalo_valid_fallback = matcher.is_match(zalo_edge_title)
        else:
            is_zalo_valid = matcher.is_match(zalo_edge_title)
            is_zalo_valid_fallback = is_zalo_valid

        self.assertFalse(is_zalo_valid, "Zalo should be detected as distraction")
        self.assertFalse(is_zalo_valid_fallback, "Zalo full title should also be distraction")

        print(f"\nDEBUG: VSCode parsing:")
        print(f"  Title: {vscode_title}")
        print(f"  Parsed: {parsed_vscode}, Is browser: {is_vscode_browser}")
        print(f"  Is valid: {is_vscode_valid}")

        print(f"\nDEBUG: Zalo in Edge parsing:")
        print(f"  Title: {zalo_edge_title}")
        print(f"  Parsed: {parsed_zalo}, Is browser: {is_zalo_browser}")
        print(f"  Is valid (parsed): {is_zalo_valid}")
        print(f"  Is valid (fallback): {is_zalo_valid_fallback}")

    def test_real_world_edge_titles(self):
        """Test with real-world Edge title formats."""
        # These are examples of what Edge titles might look like
        real_world_titles = [
            # Common patterns
            "Zalo - Microsoft Edge",
            "Facebook - Microsoft Edge",
            "YouTube - Microsoft Edge",

            # With page titles
            "Some Page Title - Zalo - Microsoft Edge",
            "Login | Zalo - Microsoft Edge",

            # Edge variations
            "Zalo - Microsoft Edge Sidebar",
            "Zalo (1) - Microsoft Edge",
        ]

        for title in real_world_titles:
            parsed, is_browser = self.parser.parse(title)
            print(f"Title: '{title}'")
            print(f"  -> Parsed: {parsed}, Is browser: {is_browser}")

            # Should always detect as browser
            self.assertTrue(is_browser,
                          f"Failed to detect browser in: '{title}'")


def run_edge_zalo_tests():
    """Run Edge/Zalo detection tests."""
    print("=== EDGE/ZALO DETECTION TEST SUITE ===\n")

    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEdgeZaloDetection))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n=== TEST RESULTS ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.wasSuccessful():
        print("\n✅ ALL EDGE/ZALO DETECTION TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED - Issues detected in Edge/Zalo handling")

    return result


if __name__ == '__main__':
    result = run_edge_zalo_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
