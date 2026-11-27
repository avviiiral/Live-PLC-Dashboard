import tempfile,unittest
from pathlib import Path
from collector.storage.queue import PersistentEventQueue
class QueueTests(unittest.TestCase):
 def test_disk_queue(self):
  with tempfile.TemporaryDirectory() as d:
   p=str(Path(d)/'q.sqlite3');q=PersistentEventQueue(p);q.enqueue({'id':'one','x':2});q=PersistentEventQueue(p);self.assertEqual(q.size(),1);self.assertEqual(q.peek()[0]['x'],2);q.acknowledge('one');self.assertEqual(q.size(),0)
