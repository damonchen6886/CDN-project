import sys
import os
import socket
import json
import urllib.request
import subprocess
import re
import argparse
import json
import threading
import time
import hashlib

# Attribute: https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json

MAX_10MB = 10485760


CACHE_DIR = 'myCache'

PORT = int(sys.argv[2])
ORIGIN = sys.argv[4]


def parsePort(port, origin):
    if port < 40000 or port > 65535:
        sys.exit('Wrong port number.')
    return port, origin


def getHttpPath(request):
    fields = request.rstrip('\r\n\r\n').split('\r\n')
    get_requests = fields[0].split(' ')
    if (get_requests[0] == 'GET'):
        path = get_requests[1]
        return path
    return


def bytes_to_json(json_text):
    return convert_to_byte(
        json.loads(json_text, object_hook=convert_to_byte),
        ignore_dicts=True
    )


def convert_to_byte(data, ignore_dicts=False):

    if isinstance(data, bytes):
        return data.encode('utf-8')

    if isinstance(data, list):
        return [convert_to_byte(item, ignore_dicts=True) for item in data]


    if isinstance(data, dict) and not ignore_dicts:
        return {
            convert_to_byte(key, ignore_dicts=True): convert_to_byte(value, ignore_dicts=True)
            for key, value in data.items()
        }
    return data


class CachedData:


    def __init__(self, listofURL, dataContent, cacheHit):
        self.listofURL= listofURL
        self.dataContent = dataContent
        self.cache_hit = cacheHit

   

class CacheStorage:


    def __init__(self):
        self.lock = threading.Lock()
        self.cache_dir = 'myCache'
        self.cacheData = self.visit_cache()

          
    def read(self):

        curData = open(self.cache_dir + '/' , 'r').read
        curData.close()
        return curData

    def write(self, data):
        curData = open(self.cache_dir + '/', 'w')
        curData.write(data)
        curData.close()
        return



    def visit_cache(self):
        with self.lock:
            try:
                curCacheList = []         
                for x in bytes_to_json(CacheStorage().read()):
                    curCacheList.append(CachedData(x['listofURL'], x['dataContent'], x['cache_hit']))
                return curCacheList
            except:
                return []



    def add_to_cache(self, url, data):
        in_cache = False
        
        for pendingData in self.cacheData:
            if url in pendingData.listofURL:
                in_cache = True
                pendingData.cache_hit += 1
                if pendingData.data == "":
                    pendingData.data = data

            elif pendingData.data == data:
                in_cache = True
                pendingData.cache_hit += 1
                pendingData.listofURL.append(url)

        if not in_cache:
            pendingData = CachedData([url], data, 1)
            self.cacheData.append(pendingData)

        
        
        self.cacheData = sorted(self.cacheData, key=lambda a: a.cache_hit, reverse=True)
        jsonStr = self.convert_to_json()
    
        curCacheSize = sys.getsizeof(jsonStr)
        
        if curCacheSize > MAX_10MB:
            
            extra_bytes = curCacheSize - MAX_10MB
            for udata in reversed(self.cacheData):
                if udata.data != "":
                    extra_bytes -= sys.getsizeof(udata.data)
                    udata.data = ""
                if extra_bytes <= 0:
                    break

    
        CacheStorage().write(self.convert_to_json())

    def check_cache(self, url):
        for pendingData in self.cacheData:           
            if pendingData.data != "" and url in pendingData.listofURL:
                return True
        return False

    def convert_to_json(self):
        myList = []
        for i in self.cacheData:
            myList.append(i.decode('utf-8').__dict__)

        return json.dumps(myList)
        
    

class HTTPServer(object):


    def __init__(self):
        self.http_server = ''
        self.check_rtt = '/testing-'
        self.local_cache = CacheStorage()
        


    def server_start(self):
        self.http_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.http_server.bind(('', PORT))






    def httprequest_handler(self, url):
        prefix = "http://"
        data = ''
        data_in_cache = self.local_cache.check_cache(url)
        if not data_in_cache:
            wholeURL = prefix + url
            data = urllib.request.urlopen(wholeURL).read()

        return data

    def request_with_rtt(self, request):
        
        client_ip = request[len(self.check_rtt):]
        result = subprocess.check_output(["scamper", "-c", "ping -c 1", "-i", client_ip])
        return result



    def listen_to_server(self):
        self.http_server.listen(1)
        while True:
            try:
                client_socket, client_address = self.http_server.accept()
                http_request = client_socket.recv(1024).decode()
                request_path = getHttpPath(http_request)
                if self.check_rtt not in request_path:
                    url = ORIGIN + ":8080" + request_path
                    data = self.httprequest_handler(url)
                    client_socket.sendall(data)
                    client_socket.close()
                    self.local_cache.add_to_cache(url, data)
                else:
                    rtt = self.request_with_rtt(request_path)
                    client_socket.sendall(rtt)
                    client_socket.close()


            except KeyboardInterrupt:
                self.http_server.close()
                return
            except Exception as e:
                print(e)



if __name__ == '__main__':
    PORT, ORIGIN = parsePort(PORT, ORIGIN)
    os.system("mkdir -p myCache")
    os.system("rm -f myCache/*")
    http_server = HTTPServer()
    http_server.server_start()
    print('listening...')
    http_server.listen_to_server()
