import sqlite3
import uuid
from datetime import datetime

class MemoryStorage(object):

    db = "/dev/shm/burn.db"

    def set_capacity(self, capacity):
        self.capacity = capacity

    def __init__(self, capacity):
        self.capacity = capacity
        self.conn = sqlite3.connect(self.db)
        c = self.conn.cursor()
        c.execute("create table if not exists storage (key NVARCHAR(100) PRIMARY KEY, value TEXT, expiry DATE, created DATE)")
        self.conn.commit()

        # Expire on every new object creation => so every request.
        self.expire()

    def get(self, key):
        c = self.conn.cursor()
        c.execute("SELECT value, expiry FROM storage WHERE key = ?", (str(key),))
        res = c.fetchone()
        return res

    def put(self, value, expiry):
        c = self.conn.cursor()
        if self.size() >= self.capacity:
            c.execute("DELETE FROM storage WHERE created = (SELECT MIN(created) FROM storage)")
        key = uuid.uuid4()
        c.execute("INSERT INTO storage (key, value, expiry, created) VALUES (?, ?, ?, ?)", (str(key),value, expiry, datetime.now()))
        self.conn.commit()
        return key

    def delete(self, key):
        c = self.conn.cursor()
        c.execute("DELETE FROM storage WHERE key = ?", (str(key),))
        self.conn.commit()

    def clear(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM storage")
        self.conn.commit()

    def size(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM storage")
        return c.fetchone()[0]

    def expire(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM storage WHERE expiry < ?", (datetime.utcnow(), ))
        self.conn.commit()
