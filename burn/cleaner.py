from .storage import Storage
import os
import logging


def main():
    capacity = os.environ.get('BURN_MAX_STORAGE', 65536)
    data_path = os.environ.get('BURN_DATA_PATH', "/dev/shm/burn/")
    database_file = os.path.join(data_path, "burn.db")
    files_path = os.path.join(data_path, 'files/')
    store = Storage(capacity, files_path, database_file)
    store.expire()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
