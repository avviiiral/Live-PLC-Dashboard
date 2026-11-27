import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class PersistentEventQueue:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS pending_events ("
                "event_id TEXT PRIMARY KEY, payload TEXT NOT NULL, "
                "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            )

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(self.path, timeout=20)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def enqueue(self, event):
        with self._connection() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO pending_events(event_id, payload) VALUES(?, ?)",
                (event["id"], json.dumps(event)),
            )

    def peek(self, limit=100):
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT payload FROM pending_events "
                "ORDER BY created_at, rowid LIMIT ?",
                (limit,),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def acknowledge(self, event_id):
        with self._connection() as connection:
            connection.execute(
                "DELETE FROM pending_events WHERE event_id = ?", (event_id,)
            )

    def size(self):
        with self._connection() as connection:
            return connection.execute(
                "SELECT COUNT(*) FROM pending_events"
            ).fetchone()[0]
