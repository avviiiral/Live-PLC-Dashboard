import json,sqlite3
from pathlib import Path
class PersistentEventQueue:
 def __init__(self,path):
  self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
  with sqlite3.connect(self.path) as c:c.execute('CREATE TABLE IF NOT EXISTS pending_events(event_id TEXT PRIMARY KEY,payload TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
 def enqueue(self,event):
  with sqlite3.connect(self.path) as c:c.execute('INSERT OR IGNORE INTO pending_events(event_id,payload) VALUES(?,?)',(event['id'],json.dumps(event)))
 def peek(self,limit=100):
  with sqlite3.connect(self.path) as c:rows=c.execute('SELECT payload FROM pending_events ORDER BY created_at,rowid LIMIT ?',(limit,)).fetchall()
  return [json.loads(x[0]) for x in rows]
 def acknowledge(self,event_id):
  with sqlite3.connect(self.path) as c:c.execute('DELETE FROM pending_events WHERE event_id=?',(event_id,))
 def size(self):
  with sqlite3.connect(self.path) as c:return c.execute('SELECT COUNT(*) FROM pending_events').fetchone()[0]
