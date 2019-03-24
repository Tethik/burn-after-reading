import datetime
from time import sleep
import os
import shutil
from io import StringIO
import uuid
from unittest import TestCase
from burn.storage import Storage, StorageException

class TestStorage(TestCase):

    def setUp(self):
        self.db_location = "/tmp/burn-test.db"
        self.file_path = "/tmp/burn-test-attachment/"
        try:
            os.remove(self.db_location)
        except:
            pass
        Storage.db = self.db_location
        

    def tearDown(self):
        shutil.rmtree(self.file_path)
        os.remove(self.db_location)
        

    def test_create(self):
        store = Storage(3, self.file_path, self.db_location)
        store.clear()
        store.create("secret message", datetime.datetime.now(), False, "123123123")
        self.assertEqual(store.size(), 1)


    def test_get(self):
        store = Storage(3, self.file_path, self.db_location)
        store.clear()
        key = store.create("secret message", datetime.datetime.now(), False, "123123123")
        self.assertEqual(store.get(key, "127.0.0.1")["content"], "secret message")


    def test_capacity(self):
        testcapacity = 50
        store = Storage(testcapacity, self.file_path, self.db_location)
        store.clear()
        first_key = None
        for i in range(testcapacity):
            key = store.create("secret message", datetime.datetime.now(), False, "123123123")
            if not first_key:
                first_key = key
            self.assertEqual(store.size(), i+1)

        # self.assertEqual(store.get(first_key)[0], "asd0")
        try:        
            store.create("secret message", datetime.datetime.now(), False, "123123123")
            self.fail("Should raise exception")
        except StorageException:
            pass


    def test_delete(self):
        store = Storage(3, self.file_path, self.db_location)
        store.clear()
        _id = store.create("secret message", datetime.datetime.now(), False, "127.0.0.1")
        self.assertEqual(store.size(), 1)
        store.delete(_id)
        self.assertEqual(store.size(), 0)
        self.assertEqual(store.get(id, "127.0.0.1"), None)


    def test_expiry(self):
        store = Storage(3, self.file_path, self.db_location)
        store.clear()
        now = datetime.datetime.utcnow() + datetime.timedelta(0, 3)
        _id = store.create("secret message", now, False, "127.0.0.1")        
        self.assertEqual(store.size(), 1)
        for _ in range(100):
            store.expire()
            self.assertEqual(store.size(), 1)
            self.assertNotEqual(store.get(_id, "127.0.0.1"), None)
        sleep(3)
        store.expire()
        self.assertEqual(store.size(), 0)
        self.assertEqual(store.get(_id, "127.0.0.1"), None)


    def test_sqli(self):
        store = Storage(3, self.file_path, self.db_location)
        store.create("secret message", datetime.datetime.now(), False, "127.0.0.1")
        store.create("secret message", datetime.datetime.now(), False, "127.0.0.2")
        self.assertEqual(store.get("asd' UNION SELECT * FROM lulz", "127.0.0.1"), None)

    # def test_capacity_actual_size(self):
    #     try:
    #         os.remove(Storage.db)
    #     except:
    #         pass
    #
    #     size = 2
    #     maxsize = 65536
    #     longmsg = "A"*2048
    #
    #     store = Storage(size)
    #     store.clear()
    #
    #     while size <= maxsize:
    #         store.set_capacity(size)
    #         while store.size() < size:
    #             store.put(longmsg, datetime.datetime.now())
    #         statinfo = os.stat(Storage.db)
    #         print(size, str(statinfo.st_size / 1024) + " kb", str(statinfo.st_size / 1024 / 1024) + " mb")
    #         size *= 2
    #         self.assertTrue(statinfo.st_size / 1024 / 1024 < 400)
    #
    #     store.clear()

    def test_visitor_log_delete(self):
        store = Storage(3, self.file_path, self.db_location)
        store.clear()
        key = store.create("secret message", datetime.datetime.utcnow() + datetime.timedelta(0, 3),
                        False, "127.0.0.1")
        visitors = store.list_visitors(key)
        self.assertEqual(visitors[0][0], "127.0.0.1")

        store.get(key, ip="127.0.0.2")
        visitors = store.list_visitors(key)
        self.assertEqual(visitors[0][0], "127.0.0.1")
        self.assertEqual(visitors[1][0], "127.0.0.2")

        store.delete(key)
        self.assertEqual(store.list_visitors(key), [])

    
    def test_get_non_existent(self):
        uid = str(uuid.uuid4())
        store = Storage(3, self.file_path, self.db_location)
        store.clear()
        store.get(uid, "127.0.0.2")

    
    def test_burn_after_reading(self):
        store = Storage(3, self.file_path, self.db_location)
        store.clear()
        key = store.create("secret message", datetime.datetime.now(), False, "127.0.0.1", burn_after_reading=True)
        self.assertEqual(store.size(), 1)
        self.assertNotEqual(store.get(key, "127.0.0.1"), None)
        self.assertEqual(store.get(key, "127.0.0.1"), None)
        self.assertEqual(store.size(), 0) # Burn should have kicked in


    def test_clear_also_removes_files(self):
        store = Storage(10, self.file_path, self.db_location)
        store.create("secret message", datetime.datetime.now(), False, "127.0.0.1", burn_after_reading=True)                
        self.assertGreater(len(os.listdir(self.file_path)), 0)
        store.clear()
        self.assertEqual(len(os.listdir(self.file_path)), 0)


