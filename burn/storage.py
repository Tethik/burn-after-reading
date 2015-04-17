import sqlite3
import uuid
from datetime import datetime

class MemoryStorage(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.conn = sqlite3.connect("/dev/shm/burn.db")
        c = self.conn.cursor()
        c.execute("create table if not exists storage (key NVARCHAR(100) PRIMARY KEY, value TEXT, created DATE)")
        self.conn.commit()


    def get(self, key):
        c = self.conn.cursor()
        c.execute("SELECT value FROM storage WHERE key = ?", (str(key),))
        res = c.fetchone()
        if res:
            return res[0]
        return res

    def put(self, value):
        c = self.conn.cursor()
        if self.length() >= self.capacity:
            c.execute("DELETE FROM storage WHERE created = (SELECT MIN(created) FROM storage)")
        key = uuid.uuid4()
        c.execute("INSERT INTO storage (key, value, created) VALUES (?, ?, ?)", (str(key),value,datetime.now()))
        self.conn.commit()
        return key

    def clear(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM storage")
        self.conn.commit()

    def length(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM storage")
        return c.fetchone()[0]
