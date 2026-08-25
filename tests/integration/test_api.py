"""Integration tests for API endpoints."""
import unittest
from src.server.main import SmartDeepSeekServer

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.server = SmartDeepSeekServer()

    def test_code_update(self):
        result = self.server.handle_code_update("print('hello')", "python")
        self.assertEqual(result["status"], "success")
        self.assertIn("block_id", result)

    def test_version_history(self):
        self.server.handle_code_update("code1", "python")
        result = self.server.get_version_history()
        self.assertEqual(result["status"], "success")
        self.assertIn("blocks", result)

    def test_error_statistics(self):
        # Track an error first so there's data
        self.server.error_tracker.track_error("bad code", "TypeError: bad", "python")
        result = self.server.get_error_statistics()
        self.assertIsNotNone(result)
        self.assertIn("total_errors", result)
        self.assertEqual(result["total_errors"], 1)

    def test_full_chat(self):
        chat_data = {
            "messages": [
                {"id": 1, "role": "user", "content": "Write a function", "codeBlocks": []},
                {"id": 2, "role": "assistant", "content": "Here is code",
                 "codeBlocks": [{"code": "def hello(): pass", "language": "python"}]}
            ]
        }
        result = self.server.handle_full_chat(chat_data)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["blocks_processed"], 1)

if __name__ == "__main__":
    unittest.main()
