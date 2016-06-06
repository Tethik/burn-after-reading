from unittest import TestCase
from burn.storage import MemoryStorage
import datetime
from time import sleep
import os
import uuid

class TestMemoryStorage(TestCase):

    def setUp(self):
        self.db_location = "/tmp/burn-test.db"
        try:
            os.remove(self.db_location)
        except:
            pass
        MemoryStorage.db = self.db_location

    def test_put(self):
        store = MemoryStorage(3)
        store.clear()
        store.put("asd", datetime.datetime.now())
        self.assertEqual(store.size(), 1)

    def test_get(self):
        store = MemoryStorage(3)
        store.clear()
        key = store.put("asd", datetime.datetime.now())
        self.assertEqual(store.get(key)[0], "asd")

    def test_capacity(self):
        testcapacity = 50
        store = MemoryStorage(testcapacity)
        store.clear()
        first_key = None
        for i in range(testcapacity):
            key = store.put("asd"+str(i), datetime.datetime.now())
            if not first_key:
                first_key = key
            self.assertEqual(store.size(), i+1)

        self.assertEqual(store.get(first_key)[0], "asd0")
        store.put("asd"+str(testcapacity+1), datetime.datetime.now())
        self.assertEqual(store.get(first_key), None)

    def test_delete(self):
        store = MemoryStorage(3)
        store.clear()
        id = store.put("asd", datetime.datetime.now())
        self.assertEqual(store.size(), 1)
        store.delete(id)
        self.assertEqual(store.size(), 0)
        self.assertEqual(store.get(id), None)

    def test_expiry(self):
        store = MemoryStorage(3)
        store.clear()
        now = datetime.datetime.utcnow() + datetime.timedelta(0,3)
        id = store.put("asd", now)
        self.assertEqual(store.size(), 1)
        for _ in range(100):
            store.expire()
            self.assertEqual(store.size(), 1)
            self.assertNotEqual(store.get(id), None)
        sleep(3)
        store.expire()
        self.assertEqual(store.size(), 0)
        self.assertEqual(store.get(id), None)

    def test_sqli(self):
        store = MemoryStorage(3)
        store.put("asd", datetime.datetime.now())
        store.put("asd",  datetime.datetime.now())
        self.assertEqual(store.get("asd' UNION SELECT * FROM lulz"), None)

    def test_capacity_actual_size(self):
        try:
            os.remove(MemoryStorage.db)
        except:
            pass

        size = 2
        maxsize = 65536
        longmsg = "A"*2048

        store = MemoryStorage(size)
        store.clear()

        while size <= maxsize:
            store.set_capacity(size)
            while store.size() < size:
                store.put(longmsg, datetime.datetime.now())
            statinfo = os.stat(MemoryStorage.db)
            print(size, str(statinfo.st_size / 1024) + " kb", str(statinfo.st_size / 1024 / 1024) + " mb")
            size *= 2
            self.assertTrue(statinfo.st_size / 1024 / 1024 < 400)

        store.clear()

    def test_visitor_log_delete(self):
        store = MemoryStorage(3)
        store.clear()
        key = store.put("asd", datetime.datetime.utcnow() + datetime.timedelta(0,3), "127.0.0.1")
        visitors = store.list_visitors(key)
        self.assertEqual(visitors[0][0], "127.0.0.1")

        store.get(key, "127.0.0.2")
        visitors = store.list_visitors(key)
        self.assertEqual(visitors[0][0], "127.0.0.1")
        self.assertEqual(visitors[1][0], "127.0.0.2")

        store.delete(key)
        self.assertEqual(store.list_visitors(key), [])

    def test_get_non_existent(self):
        u = str(uuid.uuid4())
        store = MemoryStorage(3)
        store.clear()
        store.get(u, "127.0.0.2")
