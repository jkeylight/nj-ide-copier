"""Tests for ErrorTracker."""
import unittest
from src.core.error_tracker import ErrorTracker

class TestErrorTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = ErrorTracker()

    def test_classify_syntax_error(self):
        self.assertEqual(self.tracker.classify_error("SyntaxError: invalid syntax"), "syntax_error")

    def test_classify_type_error(self):
        self.assertEqual(self.tracker.classify_error("TypeError: 'int' not iterable"), "type_error")

    def test_suggest_fix(self):
        self.assertIsNotNone(self.tracker.suggest_fix("syntax_error"))

    def test_track_and_stats(self):
        self.tracker.track_error("code", "TypeError: bad", "python")
        stats = self.tracker.get_error_statistics()
        self.assertEqual(stats["total_errors"], 1)

if __name__ == "__main__":
    unittest.main()
