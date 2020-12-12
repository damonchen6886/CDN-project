import hashlib

def hashing_path(path):
    m = hashlib.md5()
    m.update(path.encode('utf-8'))
    return m.hexdigest()