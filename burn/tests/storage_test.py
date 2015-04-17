from unittest import TestCase
from burn.storage import MemoryStorage

class TestMemoryStorage(TestCase):

    def test_put(self):
        store = MemoryStorage(3)
        store.clear()
        store.put("asd")
        self.assertEqual(store.length(), 1)

    def test_get(self):
        store = MemoryStorage(3)
        store.clear()
        key = store.put("asd")
        self.assertEqual(store.get(key), "asd")

    def test_capacity(self):
        testcapacity = 50
        store = MemoryStorage(testcapacity)
        store.clear()
        first_key = None
        for i in range(testcapacity):
            key = store.put("asd"+str(i))
            if not first_key:
                first_key = key
            self.assertEqual(store.length(), i+1)

        self.assertEqual(store.get(first_key), "asd0")
        store.put("asd"+str(testcapacity+1))
        self.assertEqual(store.get(first_key), None)
