import tempfile
import unittest
from pathlib import Path

from collector.storage.queue import PersistentEventQueue


class QueueTests(unittest.TestCase):
    def test_disk_queue(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "q.sqlite3")
            queue = PersistentEventQueue(path)
            queue.enqueue({"id": "one", "x": 2})
            reopened = PersistentEventQueue(path)
            self.assertEqual(reopened.size(), 1)
            self.assertEqual(reopened.peek()[0]["x"], 2)
            reopened.acknowledge("one")
            self.assertEqual(reopened.size(), 0)
