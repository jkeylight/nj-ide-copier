"""Tests for CodeAnalyzer."""
import unittest
from src.core.code_analyzer import CodeAnalyzer

class TestCodeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CodeAnalyzer()

    def test_extract_imports(self):
        result = self.analyzer.analyze_python_code("import os\nfrom pathlib import Path")
        self.assertEqual(result["status"], "success")
        self.assertIn("os", result["imports"])

    def test_extract_functions(self):
        result = self.analyzer.analyze_python_code("def hello():\n    return 1")
        self.assertEqual(len(result["functions"]), 1)
        self.assertEqual(result["functions"][0]["name"], "hello")

    def test_syntax_error(self):
        result = self.analyzer.analyze_python_code("def broken(")
        self.assertEqual(result["status"], "error")

if __name__ == "__main__":
    unittest.main()
