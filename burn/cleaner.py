from .storage import Storage 
import os

def main():
    capacity = os.environ.get('BURN_MAX_STORAGE', 65536)
    database_file = os.environ.get('BURN_DATABASE_FILE', "/dev/shm/burn.db")
    attachment_path = os.environ.get('BURN_ATTACHMENTS_PATH', "/dev/shm/burn-attachment/")
    store = Storage(capacity, attachment_path, database_file)
    store.expire() 

if __name__ == "__main__":
    main()