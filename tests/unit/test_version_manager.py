"""Tests for CodeVersionManager."""
import tempfile
import unittest
from pathlib import Path
from src.core.version_manager import CodeVersionManager, CodeStatus

class TestVersionManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = CodeVersionManager(self.temp_dir)

    def test_create_new_block(self):
        block = self.manager.add_or_update_block("print('hello')", "python")
        self.assertIsNotNone(block.block_id)
        self.assertEqual(len(block.versions), 1)
        self.assertEqual(block.versions[0].status, CodeStatus.ORIGINAL)

    def test_update_existing_block(self):
        b1 = self.manager.add_or_update_block("print('hello')", "python")
        b2 = self.manager.add_or_update_block("print('hello world')", "python")
        self.assertEqual(b1.block_id, b2.block_id)
        self.assertEqual(len(b2.versions), 2)

    def test_identify_block(self):
        block = self.manager.add_or_update_block("code1", "python")
        found = self.manager.identify_block("code1", "python")
        self.assertEqual(found, block.block_id)

    def test_error_fix_detection(self):
        block = self.manager.add_or_update_block("process(data) TypeError bad", "python",
            error_info={"message": "TypeError"})
        self.assertEqual(block.versions[-1].status, CodeStatus.ERROR)
        block2 = self.manager.add_or_update_block("process(data) TypeError fixed", "python")
        self.assertIn(block2.versions[-1].status, [CodeStatus.FIXED, CodeStatus.MODIFIED])

    def test_revert(self):
        # Use similar strings that will match as same block
        block = self.manager.add_or_update_block("original code version one", "python")
        block = self.manager.add_or_update_block("original code version two", "python")
        self.assertTrue(self.manager.revert_to_version(block.block_id, "v1"))
        block = self.manager.get_block(block.block_id)
        self.assertEqual(len(block.versions), 3)
        self.assertEqual(block.versions[-1].status, CodeStatus.REFACTORED)

    def test_similarity(self):
        sim = self.manager.calculate_similarity("hello world", "hello world!")
        self.assertGreater(sim, 0.8)
        sim2 = self.manager.calculate_similarity("hello", "xyz")
        self.assertLess(sim2, 0.5)

    def test_export_json(self):
        self.manager.add_or_update_block("code", "python")
        path = self.manager.export_history("json")
        self.assertTrue(path.exists())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
