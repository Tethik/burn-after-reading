from queue import Queue

class MemoryStorage(object):
    def __init__(self, capacity):
        self.queue = Queue(capacity)
        self.storage = dict()

    def get(self, key):
        return self.storage.get(key)

    def put(self, key, value):
        if self.queue.full():
            todel = self.queue.get()
            del self.storage[todel]
        self.storage[key] = value
        self.queue.put(key)

    def cleanup(self):
        pass

    def length(self):
        return len(self.storage)
