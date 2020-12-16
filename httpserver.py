import sys
import os
import threading
import gzip
import socket
import urllib.request
import subprocess
from util import *

"""
Use global variables to reduce redundancy
"""
LIMIT_10MB = 10485760
# LIMIT_1MB = 10485760 / 25
PORT = int(sys.argv[2])
ORIGIN = sys.argv[4]
MY_CACHE_FOLDER = 'myCache'
MY_CACHE_FOLDER_PATH = 'myCache/'
NEWLINE = '\r\n\r\n'
HALFNEWLINE = '\r\n'
READBINARY = 'rb'
WRITEBINARY = 'wb'
DATFILE = '.dat'
HTTP200 = 'HTTP/1.1 200 OK'

"""
check if the port number is valid
"""
def parsePort(port, origin):
    if port < 40000 or port > 65535:
        sys.exit('Wrong port number.')
    else:
        return True



"""
A class that represents local cache and its methods
"""
class LocalCache:

    def __init__(self):

        self.lock = threading.Lock()
        self.cur_cache = self.generateCacheFolder()

    """
    check the folder to create local cache folder and return a list of key:value pairs.
    key is the name of the file
    value represents cache hit count
    """
    def generateCacheFolder(self):
        with self.lock:
            if not os.path.exists(MY_CACHE_FOLDER):
                return None
            else:
                return list(map(lambda x: (x, 1), os.listdir(MY_CACHE_FOLDER)))


    """
    modify local cache depends on total size
    """
    def writeToLocalCache(self, path, data):
        with self.lock:

            file = gzip.open(hashing_path(path) + DATFILE, WRITEBINARY)
            file.write(data)
            
            file.close()
            get_size = os.path.getsize(hashing_path(path) + DATFILE)
            if get_size > LIMIT_10MB:
                os.remove(hashing_path(path) + DATFILE)
                return
            else:
                total_size = 0
                cache = os.listdir(MY_CACHE_FOLDER)
                for each_cache in cache:
                    total_size += os.path.getsize(MY_CACHE_FOLDER_PATH + each_cache)
                total_size += get_size

                while total_size >= LIMIT_10MB:
                    self.cur_cache.sort(key=lambda x: x[1], reverse = True)
                    # print("popping from")
                    file_to_remove = self.cur_cache.pop()[0]
                    # print("ggggggggggggggggggggggggggggggggggggggggg")
                    # print(self.cur_cache)
                    # print("removing--------------------",file_to_remove)
                    total_size -= os.path.getsize(MY_CACHE_FOLDER_PATH + file_to_remove + '.gz')
                    # print("totalsize =======================",total_size)
                    os.remove(MY_CACHE_FOLDER_PATH + file_to_remove + '.gz')
                    

                os.remove(hashing_path(path) + DATFILE)
                temp = gzip.open(MY_CACHE_FOLDER_PATH + hashing_path(path) + '.gz', WRITEBINARY)
                temp.write(data)
                temp.close()
                self.cur_cache.append((hashing_path(path), 1))
                # print('============================================')
                # print('changes made to local cache', self.cur_cache)
                # print('============================================')

    """
    taverse local cache to see if cache exists
    """
    def visitLocalCache(self, path):
        with self.lock:

            for cache in self.cur_cache:

                if hashing_path(path) == cache[0]:
                    self.cur_cache.append((hashing_path(path), cache[1] + 1))
                    self.cur_cache.remove(cache)
                    try:
                        # print("111111111111111111111111111111111111")
                        # print(MY_CACHE_FOLDER_PATH + hashing_path(path))
                        # print("adsadsadasdsadadasdddddddddddd")
                        # print("visitedlocalcache ", MY_CACHE_FOLDER_PATH + hashing_path(path) + '.gz')
                        file = gzip.open(MY_CACHE_FOLDER_PATH + hashing_path(path) + '.gz', READBINARY) 
                        # print("!!!!!!!!!!!!!!!!!!!!!!2222")
                        getfile = file.read()
                        # print("222222222222222222222222222222222222")
                        file.close()
                        # print('============================================')
                        # print('cache found in local cache ', self.cur_cache)
                        # print('============================================')
                        return getfile
                    except Exception as e:
                        print(e)
                        # print("3333333333333333333333333333333333333")
                        self.cur_cache.remove(cache)
                        # print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
                        os.remove(MY_CACHE_FOLDER_PATH + hashing_path(path) + '.gz')
                        return None

            return None






"""
A class that represents http server
"""
class HttpServer:
    def __init__(self):
        self.http_server = ''
        self.check_rtt = '/testing-'
        self.local_cache = LocalCache()

    def server_start(self, port, origin):
        self.http_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.http_server.bind(('', port))
        self.origin = origin

    def scamper_rtt(self, path):
        client_ip = path[len(self.check_rtt):]
        result = subprocess.check_output(["scamper", "-c", "ping -c 1", "-i", client_ip])

        return result

    def running_server(self):
        self.http_server.listen(1)
        # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        # print('connection established')
        # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        while True:
            try:
                client_socket, address = self.http_server.accept()
                http_request = client_socket.recv(1024).decode('utf-8')
                if self.check_rtt not in getHttpPath(http_request):

                    judge_cache = self.local_cache.visitLocalCache(getHttpPath(http_request))
                    
                    if judge_cache is None:
                        url = ORIGIN + ':8080' + getHttpPath(http_request)
                        # print('******************************')
                        # print('not found in local cache, pinging server...')
                        # print('******************************')
                        
                        parsed_url = 'http://' + url

                        server_response = urllib.request.urlopen(parsed_url)

                        
                        if server_response.code != 200:
                            print('HTTP code != 200')

                        
                        content = server_response.read()
                        if content is None:
                            data = None

                        else:
                            self.local_cache.writeToLocalCache(getHttpPath(http_request), content)
                            data = (HTTP200 + HALFNEWLINE + server_response.info().__str__() + HALFNEWLINE).encode('utf-8') + content
                        
                    else:
                        # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                        # print('fetched from local cache.')
                        # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                        response_headers = HTTP200 + HALFNEWLINE + 'Content-Length: ' + str(len(judge_cache)) + NEWLINE
                        data = response_headers.encode('utf-8') + judge_cache

                    client_socket.sendall(data)
                    client_socket.close()


                else:
                    rtt = self.scamper_rtt(getHttpPath(http_request))
                    # print('rtt', rtt)
                    client_socket.sendall(rtt)
                    # print("rtt sent!!!!!********")
                    client_socket.close()

            except KeyboardInterrupt:
                self.http_server.close()
                return
            except Exception as e:
                print(e)


if __name__ == "__main__":
    input_port = int(sys.argv[2])
    input_origin = sys.argv[4]
    if parsePort(input_port, input_origin):
        if (os.path.exists(MY_CACHE_FOLDER)):
            server = HttpServer()
            server.server_start(input_port, input_origin)
            # print('listening1...')
            server.running_server()
        else:
            os.mkdir(MY_CACHE_FOLDER)
            server = HttpServer()
            server.server_start(input_port, input_origin)
            # print('listening1...')
            server.running_server()

    
