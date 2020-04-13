import os
import sqlite3
import uuid
from datetime import datetime
import hashlib
import shutil
import logging

logger = logging.getLogger("storage")


class StorageException(Exception):
    def __init__(self, message):
        super().__init__(message)


class Storage(object):
    def __init__(self, capacity, storage_path, database_file):
        os.makedirs(storage_path, exist_ok=True)
        self.storage_path = storage_path
        self.capacity = capacity
        logger.debug(f"Database stored at {database_file}")
        self.conn = sqlite3.connect(database_file)
        c = self.conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute(
            """create table if not exists storage (
            key NVARCHAR(100) PRIMARY KEY,
            path NVARCHAR(256),
            expiry DATE,
            created DATE,
            burn_after_reading BIT,
            anonymize_ip_salt NVARCHAR(100)
        )"""
        )
        c.execute(
            """
            create table if not exists visitors (
                storage_key NVARCHAR(100),
                ip NVARCHAR(100),
                visited DATE,
                creator BIT,
                FOREIGN KEY(storage_key) REFERENCES storage(key)
                    ON DELETE CASCADE
            )"""
        )
        self.conn.commit()

    def _add_visited_log(self, c, key, ip, creator, salt):
        if salt != None:
            ip = hashlib.sha256((salt + ip).encode()).hexdigest()
        c.execute(
            """
            INSERT INTO visitors (storage_key, ip, visited, creator)
            VALUES (?, ?, ?, ?)""",
            (str(key), ip, datetime.utcnow(), creator),
        )
        self.conn.commit()

    def list_visitors(self, key):
        c = self.conn.cursor()
        c.execute(
            """
            SELECT ip, visited, creator FROM visitors
            WHERE storage_key = ?
        """,
            (str(key),),
        )
        return c.fetchall()

    def get(self, key, ip) -> dict:
        c = self.conn.cursor()

        c.execute(
            """
            SELECT path, expiry, anonymize_ip_salt, burn_after_reading FROM storage
            WHERE key = ?
            """,
            (str(key),),
        )
        res = c.fetchone()

        if not res:
            return res

        path, expiry, anonymize_ip_salt, burn_after_reading = res
        content = open(path).read()

        if burn_after_reading:
            self.delete(key)
        else:
            self._add_visited_log(c, key, ip, 0, anonymize_ip_salt)

        return {
            "path": path,
            "expiry": expiry,
            "burn_after_reading": burn_after_reading,
            "content": content,
        }

    def create(
        self,
        content: str,
        expiry: datetime,
        anonymize_ip: bool,
        ip,
        burn_after_reading: bool = False,
    ):
        c = self.conn.cursor()

        if self.size() >= self.capacity:
            raise StorageException("Storage is full.")

        # Save content as a file.
        path = os.path.join(self.storage_path, str(uuid.uuid4()))

        key = str(uuid.uuid4())
        salt = None
        if anonymize_ip:
            salt = str(uuid.uuid4())

        with open(path, "w") as fp:
            fp.write(content)

        c.execute(
            """
            INSERT INTO storage (key, path, expiry, created, anonymize_ip_salt, burn_after_reading)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (key, path, expiry, datetime.utcnow(), salt, burn_after_reading),
        )

        self._add_visited_log(c, key, ip, True, salt)
        self.conn.commit()
        return key

    def _remove_file(self, path):
        try:
            os.remove(path)
        except FileNotFoundError:
            logger.warn(f"Tried to remove non-existent file at {path}")

    def delete(self, key):
        c = self.conn.cursor()
        res = c.execute("SELECT path FROM storage WHERE key = ?", (str(key),))
        if not res:
            return
        path = res.fetchone()[0]
        self._remove_file(path)
        c.execute("DELETE FROM storage WHERE key = ?", (str(key),))
        self.conn.commit()

    def clear(self):
        c = self.conn.cursor()
        res = c.execute("SELECT path FROM storage")
        for row in res.fetchall():
            self._remove_file(row[0])
        c.execute("DELETE FROM storage")
        self.conn.commit()

    def size(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM storage")
        return c.fetchone()[0]

    def expire(self):
        c = self.conn.cursor()
        date = datetime.utcnow()
        res = c.execute("SELECT path FROM storage WHERE expiry < ?", (date,))
        rows = res.fetchall()
        logger.info(f'Expiring {len(rows)} documents from the storage')
        for row in rows:
            logger.info(f'Deleting {row[0]}')
            self._remove_file(row[0])
        c.execute("DELETE FROM storage WHERE expiry < ?", (date,))
        self.conn.commit()
