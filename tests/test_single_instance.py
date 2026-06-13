import tempfile
import unittest
from pathlib import Path

from neurogate_usage_overlay.single_instance import SingleInstanceLock


class SingleInstanceLockTest(unittest.TestCase):
    def test_second_lock_is_rejected_until_first_is_released(self):
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "overlay.lock"
            first = SingleInstanceLock(lock_path)
            second = SingleInstanceLock(lock_path)

            self.assertTrue(first.acquire())
            self.assertFalse(second.acquire())

            first.release()

            self.assertTrue(second.acquire())
            second.release()
