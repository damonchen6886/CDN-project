import threading
import os
import gzip
import socket
import urllib.request
import traceback
import subprocess
import sys
from util import *

LIMIT_10MB = 10485760
PORT = int(sys.argv[2])
ORIGIN = sys.argv[4]
MY_CACHE_FOLDER = 'myCache'
MY_CACHE_FOLDER_PATH = 'myCache/'



def parsePort(port, origin):
    if port < 40000 or port > 65535:
        sys.exit('Wrong port number.')
    else:
        return True


class CacheHandler:

    def __init__(self):

        self.lock = threading.Lock()
        

        self.cached_data = self.generate_cache_folder()  # (hashed_filename, hitcount)

    def generate_cache_folder(self):
        with self.lock:
            if not os.path.exists(MY_CACHE_FOLDER):
                return []               
            else:
                return list(map(lambda x: (x, 1), os.listdir(MY_CACHE_FOLDER)))
                
                

    def get(self, path):
        with self.lock:
            file_name = hashing_path(path)

            for item in self.cached_data:

                if file_name == item[0]:
                    # move to the head of the list
                    self.cached_data.append((file_name, item[1] + 1))
                    self.cached_data.remove(item)
                    try:
                        file = gzip.open(MY_CACHE_FOLDER_PATH + file_name, 'rb')
                        content = file.read()
                        file.close()
                        print('cache hit ------ ', self.cached_data)
                        return content
                    except:
                        self.cached_data.remove(item)
                        os.remove(MY_CACHE_FOLDER_PATH + file_name)
                        return None

            return None

    def set(self, path, data):
        with self.lock:
            file_name = hashing_path(path)

            # if file_name in self.cached_data:
            #     self.cached_data.remove(file_name)
            temp_file = gzip.open(file_name + '.temp', 'wb')
            temp_file.write(data)
            temp_file.close()
            data_size = os.path.getsize(file_name + '.temp')
            if data_size > LIMIT_10MB:
                os.remove(file_name + '.temp')
                return
            else:
                while self.is_full(data_size):
                    self.cached_data.sort(key=lambda x: x[1])
                    discard = self.cached_data.pop(0)[0]
                    os.remove(MY_CACHE_FOLDER_PATH + discard)

                os.remove(file_name + '.temp')
                file = gzip.open(MY_CACHE_FOLDER_PATH + file_name, 'wb')
                file.write(data)
                file.close()
                self.cached_data.append((file_name, 1))
                print('cache update ------', self.cached_data)

    def is_full(self, data_size):
        cache = os.listdir(MY_CACHE_FOLDER)
        total = 0
        for f in cache:
            total += os.path.getsize(MY_CACHE_FOLDER_PATH + f)

        total += data_size
        return total >= LIMIT_10MB



def getHttpPath(request):
    fields = request.rstrip('\r\n\r\n').split('\r\n')
    get_requests = fields[0].split(' ')
    if (get_requests[0] == 'GET'):
        path = get_requests[1]
        return path
    return



def fetch_from_server(url):
    q = 'http://' + url

    try:
        print(q)
        response = urllib.request.urlopen(q)
        # Grab the header and content from the server req
        response_headers = response.info().__str__()
        content = response.read()
        if response.code != 200:
            raise Exception('code != 200')
        print(response.code)
        response_headers = 'HTTP/1.1 200 OK\r\n' + response_headers

        # print(content)
        return response_headers, content
    except Exception as e:
        print(e)
        return None


class HttpServer:
    def __init__(self):
        self.http_server = ''       
        self.check_rtt = '/testing-'
        self.cache_handler = CacheHandler()

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
        print('connection established')
        while True:
            try:
                client_socket, address = self.http_server.accept()
                http_request = client_socket.recv(1024).decode()

 
                if self.check_rtt not in getHttpPath(http_request):
                    print('--------------- GET -------------')
                
                    load_from_cache = self.cache_handler.get(getHttpPath(http_request))
                    if load_from_cache is not None:
                        print('Fetched successfully from cache.')
                        response_headers = 'HTTP/1.1 200 OK\r\nContent-Length: ' + str(len(load_from_cache)) + '\r\n\r\n'
                        data = response_headers.encode() + load_from_cache
                    else:
                        url = ORIGIN + ':8080' + getHttpPath(http_request)
                        print('Not in cache. Fetching from server.')
                        headers, file_from_server = fetch_from_server(url)
                        
                        if file_from_server is not None:
                            self.cache_handler.set(getHttpPath(http_request), file_from_server)
                            data = (headers + '\r\n').encode() + file_from_server
                        else:
                            data = None
                    client_socket.sendall(data)
                    client_socket.close()
                    

                else:
                    print('----------- measure ------------')
                    rtt_rqst = self.scamper_rtt(getHttpPath(http_request))
                    print('rtt', rtt_rqst)
                    client_socket.sendall(rtt_rqst.encode())
                    client_socket.close()
                    print('---------- finish measure -------')
                   
            except KeyboardInterrupt:
                self.http_server.close()
                return
            except Exception as e:
                print(e)



if __name__ == "__main__":
    input_port = int(sys.argv[2])
    input_origin = sys.argv[4]
    if parsePort(input_port,input_origin):
        if(os.path.exists(MY_CACHE_FOLDER)):
            server = HttpServer()
            server.server_start(input_port, input_origin)
            print('listening...')
            server.running_server()
        else:
            os.mkdir(MY_CACHE_FOLDER)
            server = HttpServer()
            server.server_start(input_port, input_origin)
            print('listening...')
            server.running_server()

        

    # run the server: python HttpServer.py 50004 ec2-18-207-254-152.compute-1.amazonaws.com
    # use replica to test: wget ec2-34-238-192-84.compute-1.amazonaws.com:50004/wiki/Main_Page