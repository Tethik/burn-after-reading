import sqlite3
import uuid
from datetime import datetime
import hashlib

class MemoryStorage(object):
    def set_capacity(self, capacity):
        self.capacity = capacity        

    def __init__(self, capacity, database_file):
        self.db = database_file
        self.capacity = capacity
        self.conn = sqlite3.connect(self.db)
        c = self.conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("""create table if not exists storage (
            key NVARCHAR(100) PRIMARY KEY,
            value TEXT,
            expiry DATE,
            created DATE,
            anonymize_ip_salt NVARCHAR(100)
        )""")
        c.execute("""
            create table if not exists visitors (
                storage_key NVARCHAR(100),
                ip NVARCHAR(100),
                visited DATE,
                creator BIT,
                FOREIGN KEY(storage_key) REFERENCES storage(key)
                    ON DELETE CASCADE
            )""")
        self.conn.commit()

        # Expire on every new object creation => so every request.
        self.expire()

    def _add_visited_log(self, c, key, ip, creator, salt):
        if ip != None:
            if salt != None:                
                ip = hashlib.sha256((salt + ip).encode()).hexdigest()
            c.execute("""
             INSERT INTO visitors (storage_key, ip, visited, creator)
             VALUES (?, ?, ?, ?)""",
             (str(key), ip, datetime.utcnow(), creator))
            self.conn.commit()

    def list_visitors(self, key):
        c = self.conn.cursor()
        c.execute("""
            SELECT ip, visited, creator FROM visitors
            WHERE storage_key = ?
        """, (str(key),))
        return c.fetchall()

    def get(self, key, ip=None):
        c = self.conn.cursor()

        c.execute("""
            SELECT value, expiry, anonymize_ip_salt FROM storage
            WHERE key = ?
            """, (str(key),))
        res = c.fetchone()

        if not res:
            return res

        self._add_visited_log(c, key, ip, 0, res[2])

        return res

    def put(self, value, expiry, anonymize_ip = True, ip = None):
        c = self.conn.cursor()
        # Enforce capacity by removing the oldest entry
        if self.size() >= self.capacity:
            c.execute("""
                DELETE FROM storage
                WHERE created = (SELECT MIN(created) FROM storage)
                """)
        key = uuid.uuid4()
        salt = None
        if anonymize_ip:
            salt = str(uuid.uuid4())
        c.execute("""
            INSERT INTO storage (key, value, expiry, created, anonymize_ip_salt)
            VALUES (?, ?, ?, ?, ?)""", (str(key), value, expiry, datetime.utcnow(), salt))

        self._add_visited_log(c, key, ip, 1, salt)
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
