import hashlib
NEWLINE = '\r\n\r\n'
HALFNEWLINE = '\r\n'


def hashing_path(path):
    hashing = hashlib.md5()
    hashing.update(path.encode('utf-8'))
    return hashing.hexdigest()

def getHttpPath(request):
    fields = request.rstrip(NEWLINE).split(HALFNEWLINE)
    get_requests = fields[0].split(' ')
    if (get_requests[0] == 'GET'):
        path = get_requests[1]
        return path
    return


