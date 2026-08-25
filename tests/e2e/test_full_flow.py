"""End-to-end test for the full DeepSeek to IDE flow."""
import unittest
import tempfile
import shutil
from pathlib import Path
from src.core.version_manager import CodeVersionManager, CodeStatus
from src.core.error_tracker import ErrorTracker

class TestFullFlow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.vm = CodeVersionManager(self.temp_dir)
        self.et = ErrorTracker()

    def test_error_fix_flow(self):
        # Step 1: Code with error
        block1 = self.vm.add_or_update_block(
            "process(data) raise TypeError bad",
            "python",
            error_info={"message": "TypeError: bad"}
        )
        self.et.track_error("code", "TypeError", "python")
        self.assertEqual(block1.versions[-1].status, CodeStatus.ERROR)

        # Step 2: Fixed code (similar enough to match same block)
        block2 = self.vm.add_or_update_block(
            "process(data) return data fixed",
            "python"
        )
        self.assertEqual(block1.block_id, block2.block_id)
        self.assertEqual(len(block2.versions), 2)

    def test_version_export(self):
        self.vm.add_or_update_block("code v1", "python")
        self.vm.add_or_update_block("code v2", "python")
        path = self.vm.export_history("json")
        self.assertTrue(path.exists())
        import json
        data = json.loads(path.read_text())
        self.assertEqual(len(data["blocks"]), 1)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
