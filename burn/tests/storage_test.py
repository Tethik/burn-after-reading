from unittest import TestCase
from burn.storage import MemoryStorage

class TestMemoryStorage(TestCase):

    def test_put(self):
        store = MemoryStorage(3)
        store.put("hej", "asd")
        self.assertEqual(store.length(), 1)

    def test_get(self):
        store = MemoryStorage(3)
        store.put("hej", "asd")
        self.assertEqual(store.get("hej"), "asd")

    def test_capacity(self):
        testcapacity = 50
        store = MemoryStorage(testcapacity)
        for i in range(testcapacity):
            store.put(i, "asd"+str(i))
            self.assertEqual(store.length(), i+1)

        for i in range(testcapacity):
            self.assertEqual(store.get(i), "asd"+str(i))

        self.assertEqual(store.get(0), "asd0")
        store.put(testcapacity+1, "asd"+str(testcapacity+1))
        self.assertEqual(store.get(0), None)
