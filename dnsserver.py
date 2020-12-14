
# NOTE: This is your final list of servers
# ec2-18-207-254-152.compute-1.amazonaws.com      Origin server (running Web server on port 8080)
# ec2-34-238-192-84.compute-1.amazonaws.com       N. Virginia (34.238.192.84)
# ec2-13-231-206-182.ap-northeast-1.compute.amazonaws.com Tokyo  (13.231.206.182)
# ec2-13-239-22-118.ap-southeast-2.compute.amazonaws.com  Sydney (13.239.22.118)
# ec2-34-248-209-79.eu-west-1.compute.amazonaws.com       Ireland (34.248.209.79)
# ec2-18-231-122-62.sa-east-1.compute.amazonaws.com       Sao Paulo (18.231.122.62)
# ec2-3-101-37-125.us-west-1.compute.amazonaws.com        N. California (3.101.37.125)

# https://tools.ietf.org/html/rfc1035

    # +---------------------+
    # |        Header       |
    # +---------------------+
    # |       Question      | the question for the name server
    # +---------------------+
    # |        Answer       | RRs answering the question
    # +---------------------+
    # |      Authority      | RRs pointing toward an authority
    # +---------------------+
    # |      Additional     | RRs holding additional information
    # +---------------------+

    # header:
    #                                 1  1  1  1  1  1
    #   0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                      ID                       |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                    QDCOUNT                    |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                    ANCOUNT                    |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                    NSCOUNT                    |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                    ARCOUNT                    |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+


    # question section
    #                                  1  1  1  1  1  1
    #   0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                                               |
    # /                     QNAME                     /
    # /                                               /
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                     QTYPE                     |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                     QCLASS                    |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+


    # ans section:
    #                                 1  1  1  1  1  1
    #   0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                                               |
    # /                                               /
    # /                      NAME                     /
    # |                                               |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                      TYPE                     |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                     CLASS                     |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                      TTL                      |
    # |                                               |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                   RDLENGTH                    |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
    # /                     RDATA                     /
    # /                                               /
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
import socket
import sys
from find_host import get_min_ec2_loc
from struct import pack, unpack
import time
#-p <port> -n <name>
PORT = int(sys.argv[2])
DOMAIN_NAME = str(sys.argv[4])
BUF_SIZE = 1024
DNS_DOMAIN_NAME = ""
ANS_END_IDX = 0
TWO_EC2_IP = []
CACHE = {}
CACHE_TIME = 180
MAX_CACHE_SIZE = 5000
DOT = 32
def build_server():
    server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    # server.bind(("",PORT))
    return server



# oricess header of the DNS packet, return the finished header packet
def process_header(data):
    # print(data)
    dns_header_data  = data[0:12]
    # print(dns_header_data)
    [id, flag, qdcount,ancount,nscount, arcount] = unpack('!HHHHHH',dns_header_data)
    # print(flag)
    ancount = 1
    flag = 0x8180 #33152
    # print(flag)
    head_packet = pack('!HHHHHH',id,flag,qdcount,ancount,nscount,arcount)
    return head_packet
    # return 

# find the domain of the DNS packet, mark the domian name end index   
def findDomain(data):
    dns_question_data = data[12:]
    i = 1
    name = ""
    while True:
        d = dns_question_data[i]
        if d == 0:
            break
        if d < DOT:
            name+= "."
        else:
            name = name + chr(dns_question_data[i])
        i = i+1
    # set to global variable
    global DNS_DOMAIN_NAME
    DNS_DOMAIN_NAME = name
    global ANS_END_IDX
    ANS_END_IDX = i+5
    # domin = dns_question_data[0: i+1]
    # tpye_and_classify = dns_question_data[i+1:i+5]
    return

# process_question part of the DNS packet
def process_question(data):
    # if data >= 12:
    index = ANS_END_IDX
    # print(index)
    dns_question_data = data[12:12+index]
    # print(dns_question_data)
    return dns_question_data
    # return

# process answer part of the DNS packet, return answer part
def process_answer(ec2_ip_addr):
    rname = 0xC00C #49164
    ttype =0x0001
    rclass = 0x0001
    ttl = 60
    rdata = socket.inet_aton(ec2_ip_addr)
    
    rlength = len(rdata)
    # print(rlength)
    
    ans_packet = pack('!HHHLH4s',rname,ttype,rclass,ttl,rlength,rdata)
    return ans_packet


# pack all sections of DNS packet and retun a finish packet ready to send to client
def pack_all(ec2_ip_addr,data):
    header = process_header(data)
    findDomain(data)
    question = process_question(data)
    answer = process_answer(ec2_ip_addr)
    
    return header+ question + answer + data[12+ ANS_END_IDX:]


# create http requst to HTTP server
def gengrate_request_2http(ec2_ip):
    path = "/testing-" + ec2_ip
    request = "GET " + path + " HTTP/1.1"
    print(request)
    return request

# send requst, get the RTT from the ec2 server, return the rtt from the receive message
def create_socket_for_http(ec2_ip):
    print("***********creating socket", ec2_ip)
    httpsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    httpsocket.connect((ec2_ip,PORT))
    httpsocket.sendall(gengrate_request_2http(ec2_ip).encode())
    print("successfully sent")
    while True:
        print("test")
        rtt_raw = httpsocket.recv(BUF_SIZE).decode()
        print("result", rtt_raw)
        print("**********************")
        index = rtt_raw.find("min/avg/max/stddev = ")
        # if index != -1:
        start_index = index+ len("min/avg/max/stddev = ")
        rtt = rtt_raw[start_index,start_index+4]
        print("rtt parse", rtt)
        break
    httpsocket.close()
    return rtt

# return a list of two rtt that represent the top two ec2ip rrt time
def get_rtt_for_top2(TWO_EC2_IP):
    result = ""
    rtts = []
    for ec2_ip in TWO_EC2_IP:
        rtt = create_socket_for_http(ec2_ip)
        rtts.append[rtt]
    return rtts

# decide the best two server 
def get_best_ec2_client():
    rtts = get_rtt_for_top2(TWO_EC2_IP)
    if rtts[0] > rtts[1]:
        return TWO_EC2_IP[1]
    return TWO_EC2_IP[0]


#update global variable cache
def add2_cache(client_ip_addr, best_ec2_ip):
    CACHE[client_ip_addr] = [best_ec2_ip,time.time()]


# update time for specific ip address in cache
def update_cache(client_ip_addr):
    CACHE[client_ip_addr][1] = time.time()




#  initilize the program
def starter():
    # initialize server
    server_socket = build_server()
    if PORT  < 40000 or PORT > 65535:
        print("port must within 40000 -65535")
        return
    server_socket.bind(("",PORT))
    
    while 1:
        print("running")

        data = server_socket.recvfrom(BUF_SIZE)
        packet = data[0]
        # print("running1")
        client_addr = data[1]
        # print(client_addr)
        client_ip_addr = data[1][0]

        #same client ip for dnslookup will be saved for 3 mins in cache
        #so it will direction return a ec2 ip to clinet instead of lookup again
        if client_ip_addr in CACHE.keys():
            if(time.time() - CACHE[client_ip_addr][1] < CACHE_TIME):
                response_packet = pack_all(CACHE[client_ip_addr][0],packet)
                server_socket.sendto(response_packet,client_addr)
                #update cache
                update_cache(client_ip_addr)
                continue
        ##############
        # print("running2")
        # header = unpack("!HHHHHH",packet[0:12])
        #get the best ec2 ip address
       
        global TWO_EC2_IP
        TWO_EC2_IP = get_min_ec2_loc(client_ip_addr)
        # print(TWO_EC2_IP)
        best_ec2_server = TWO_EC2_IP[0]

        # best_ec2_server = get_best_ec2_client()
        #add to cache
        add2_cache(client_ip_addr,best_ec2_server)
        # print("best")
        # print(best_ec2_ip)
        # pack the udp meesage  
        response_packet = pack_all(best_ec2_server,packet)
        
    
        if DNS_DOMAIN_NAME != DOMAIN_NAME:
            print("domain names are different")
            continue
        # send back

        server_socket.sendto(response_packet,client_addr)
       

if __name__ == "__main__":
    starter()
    
