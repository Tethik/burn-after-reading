

class MemoryStorage(object):
    storage = dict()

    def get(self, key):
        return self.storage.get(key)

    def put(self, key, value):
        self.storage[key] = value

    def cleanup():
        pass
