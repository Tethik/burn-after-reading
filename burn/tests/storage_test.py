from unittest import TestCase
from burn.storage import MemoryStorage
import datetime
from time import sleep

class TestMemoryStorage(TestCase):

    def test_put(self):
        store = MemoryStorage(3)
        store.clear()
        store.put("asd", datetime.datetime.now())
        self.assertEqual(store.length(), 1)

    def test_get(self):
        store = MemoryStorage(3)
        store.clear()
        key = store.put("asd", datetime.datetime.now())
        self.assertEqual(store.get(key), "asd")

    def test_capacity(self):
        testcapacity = 50
        store = MemoryStorage(testcapacity)
        store.clear()
        first_key = None
        for i in range(testcapacity):
            key = store.put("asd"+str(i), datetime.datetime.now())
            if not first_key:
                first_key = key
            self.assertEqual(store.length(), i+1)

        self.assertEqual(store.get(first_key), "asd0")
        store.put("asd"+str(testcapacity+1), datetime.datetime.now())
        self.assertEqual(store.get(first_key), None)

    def test_delete(self):
        store = MemoryStorage(3)
        store.clear()
        id = store.put("asd", datetime.datetime.now())
        self.assertEqual(store.length(), 1)
        store.delete(id)
        self.assertEqual(store.length(), 0)
        self.assertEqual(store.get(id), None)

    def test_expiry(self):
        store = MemoryStorage(3)
        store.clear()
        now = datetime.datetime.utcnow() + datetime.timedelta(0,3)
        id = store.put("asd", now)
        self.assertEqual(store.length(), 1)
        for _ in range(100):
            store.expire()
            self.assertEqual(store.length(), 1)
            self.assertNotEqual(store.get(id), None)
        sleep(3)
        store.expire()
        self.assertEqual(store.length(), 0)
        self.assertEqual(store.get(id), None)
