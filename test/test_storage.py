import datetime
from time import sleep
import os
import shutil
import uuid
from unittest import TestCase
from burn.storage import Storage

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

    def test_put(self):
        store = Storage(3, self.file_path, self.db_location)
        store.clear()
        store.put("asd", datetime.datetime.now())
        self.assertEqual(store.size(), 1)

    def test_get(self):
        store = Storage(3, self.file_path, self.db_location)
        store.clear()
        key = store.put("asd", datetime.datetime.now())
        self.assertEqual(store.get(key)[0], "asd")

    def test_capacity(self):
        testcapacity = 50
        store = Storage(testcapacity, self.file_path, self.db_location)
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
        store = Storage(3, self.file_path, self.db_location)
        store.clear()
        _id = store.put("asd", datetime.datetime.now())
        self.assertEqual(store.size(), 1)
        store.delete(_id)
        self.assertEqual(store.size(), 0)
        self.assertEqual(store.get(id), None)

    def test_expiry(self):
        store = Storage(3, self.file_path, self.db_location)
        store.clear()
        now = datetime.datetime.utcnow() + datetime.timedelta(0, 3)
        _id = store.put("asd", now)
        self.assertEqual(store.size(), 1)
        for _ in range(100):
            store.expire()
            self.assertEqual(store.size(), 1)
            self.assertNotEqual(store.get(_id), None)
        sleep(3)
        store.expire()
        self.assertEqual(store.size(), 0)
        self.assertEqual(store.get(_id), None)

    def test_sqli(self):
        store = Storage(3, self.file_path, self.db_location)
        store.put("asd", datetime.datetime.now())
        store.put("asd", datetime.datetime.now())
        self.assertEqual(store.get("asd' UNION SELECT * FROM lulz"), None)

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
        key = store.put("asd", datetime.datetime.utcnow() + datetime.timedelta(0, 3),
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
        key = store.put("asd", datetime.datetime.now(), burn_after_reading=True)
        self.assertEqual(store.size(), 1)
        self.assertEqual(store.get(key)[0], "asd")
        self.assertEqual(store.get(key), None)
        self.assertEqual(store.size(), 0) # Burn should have kicked in

    def test_put_and_get_with_file_attachments(self):
        store = Storage(10, self.file_path, self.db_location)
        store.clear()
        key = store.put("asd", datetime.datetime.now(), burn_after_reading=True)
        files = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        store.put_attachments(key, files)

        files_from_storage = store.get_attachments(key)
        self.assertEqual(len(files_from_storage), len(files))
        for _f in files_from_storage:
            content = store.get_attachment(_f)
            self.assertIn(content, files)

    def test_delete_with_file_attachments(self):
        store = Storage(10, self.file_path, self.db_location)
        store.clear()
        key = store.put("asd", datetime.datetime.now(), burn_after_reading=True)
        files = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        store.put_attachments(key, files)

        store.delete_attachments(key)
        files_from_storage = store.get_attachments(key)
        self.assertEqual(files_from_storage, [])

    def test_get_empty_file_attachments(self):
        store = Storage(10, self.file_path, self.db_location)
        store.clear()
        key = store.put("asd", datetime.datetime.now(), burn_after_reading=True)
        files_from_storage = store.get_attachments(key)
        self.assertEqual(files_from_storage, [])

    def test_clear_also_removes_files(self):
        store = Storage(10, self.file_path, self.db_location)
        key = store.put("asd", datetime.datetime.now(), burn_after_reading=True)
        files = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        store.put_attachments(key, files)
        self.assertGreater(len(os.listdir(self.file_path)), 0)
        store.clear()
        self.assertEqual(len(os.listdir(self.file_path)), 0)


