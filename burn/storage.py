import os
import sqlite3
import uuid
from datetime import datetime
import hashlib

class StorageException(Exception):
    def __init__(self, message):
        super().__init__(message)
        

class Storage(object):
    def set_capacity(self, capacity):
        self.capacity = capacity

    def __init__(self, capacity, attachment_path, database_file):
        try:
            os.makedirs(attachment_path)
        except:
            pass
        self.attachment_path = attachment_path
        self.capacity = capacity
        self.conn = sqlite3.connect(database_file)
        c = self.conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("""create table if not exists storage (
            key NVARCHAR(100) PRIMARY KEY,
            value TEXT,
            expiry DATE,
            created DATE,
            burn_after_reading BIT,
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
        c.execute("""
            create table if not exists file_attachments (
                storage_key NVARCHAR(100),
                key NVARCHAR(100),                
                FOREIGN KEY(storage_key) REFERENCES storage(key)
                    ON DELETE CASCADE
            )""")
        self.conn.commit()

    
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
            SELECT value, expiry, anonymize_ip_salt, burn_after_reading FROM storage
            WHERE key = ?
            """, (str(key),))
        res = c.fetchone()

        if not res:
            return res

        # Burn After Reading enabled.
        if res[3]:
            self.delete(key)
            return res

        self._add_visited_log(c, key, ip, 0, res[2])

        return res

    
    def put(self, value, expiry, anonymize_ip=True, ip=None, burn_after_reading=False):
        c = self.conn.cursor()
        # Enforce capacity by removing the oldest entry. Todo: remove this and abort instead.
        if self.size() >= self.capacity:
            raise StorageException("Storage is full.")

        key = uuid.uuid4()
        salt = None
        if anonymize_ip:
            salt = str(uuid.uuid4())
        c.execute("""
            INSERT INTO storage (key, value, expiry, created, anonymize_ip_salt, burn_after_reading)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (str(key), value, expiry, datetime.utcnow(), salt, burn_after_reading))

        self._add_visited_log(c, key, ip, True, salt)
        self.conn.commit()
        return key

    
    def delete(self, key):
        self.delete_attachments(key)
        c = self.conn.cursor()
        c.execute("DELETE FROM storage WHERE key = ?", (str(key),))
        self.conn.commit()

    
    def clear(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM storage")
        self.clear_attachments()
        self.conn.commit()

    
    def size(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM storage")
        return c.fetchone()[0]

    
    def expire(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM storage WHERE expiry < ?", (datetime.utcnow(), ))
        self.conn.commit()

    
    def get_attachment(self, key):
        path = os.path.join(self.attachment_path, str(key))
        with open(path) as _file:
            content = _file.read()
        return content

    
    def get_attachments(self, key):
        c = self.conn.cursor()
        res = c.execute("""
            SELECT key FROM file_attachments
            WHERE storage_key = ?
            """, (str(key),))

        files = [row[0] for row in res]
        return files

    
    def put_attachments(self, storage_key, file_array):
        c = self.conn.cursor()
        # Write the files.
        for file_content in file_array:
            key = str(uuid.uuid4())
            path = os.path.join(self.attachment_path, key)
            with open(path, "w") as _file:
                _file.write(file_content)

            # Save to db
            c.execute("""
                INSERT INTO file_attachments (storage_key, key)
                VALUES (?, ?)
                """, (str(storage_key), key))
        self.conn.commit()

    
    def delete_attachments(self, key):
        c = self.conn.cursor()
        c.execute("SELECT key FROM file_attachments WHERE storage_key = ?", (str(key),))
        res = c.fetchall()
        for row in res:
            path = os.path.join(self.attachment_path, row[0])
            os.remove(path)
        c.execute("DELETE FROM file_attachments WHERE storage_key = ?", (str(key),))
        self.conn.commit()

    
    def clear_attachments(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM file_attachments")
        self.conn.commit()
        for key in os.listdir(self.attachment_path):
            path = os.path.join(self.attachment_path, key)
            os.remove(path)
        