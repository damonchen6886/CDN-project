
# NOTE: This is your final list of servers
# ec2-18-207-254-152.compute-1.amazonaws.com      Origin server (running Web server on port 8080)
# ec2-34-238-192-84.compute-1.amazonaws.com       N. Virginia
# ec2-13-231-206-182.ap-northeast-1.compute.amazonaws.com Tokyo
# ec2-13-239-22-118.ap-southeast-2.compute.amazonaws.com  Sydney
# ec2-34-248-209-79.eu-west-1.compute.amazonaws.com       Ireland
# ec2-18-231-122-62.sa-east-1.compute.amazonaws.com       Sao Paulo
# ec2-3-101-37-125.us-west-1.compute.amazonaws.com        N. California

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
#-p <port> -n <name>
PORT = int(sys.argv[2])
DOMAIN_NAME = str(sys.argv[4])
BUF_SIZE = 1024
DNS_DOMAIN_NAME = ""
ANS_END_IDX = 0
def build_server():
    server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    # server.bind(("",PORT))
    return server




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
    

# def findDomain(data):
#     dns_question_data = data[12:]
#     domain_length = unpack("!B",dns_question_data[0])

def findDomain(data):
    dns_question_data = data[12:]
    i = 1
    name = ""
    while True:
        d = dns_question_data[i]
        if d == 0:
            break
        if d < 32:
            name+= "."
        else:
            name = name + chr(dns_question_data[i])
        i = i+1
    
    global DNS_DOMAIN_NAME
    DNS_DOMAIN_NAME = name
    global ANS_END_IDX
    ANS_END_IDX = i+5
    # domin = dns_question_data[0: i+1]
    # tpye_and_classify = dns_question_data[i+1:i+5]
    return

def process_question(data):
    # if data >= 12:
    index = ANS_END_IDX
    # print(index)
    dns_question_data = data[12:12+index]
    # print(dns_question_data)
    return dns_question_data
    # return


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



def pack_all(ec2_ip_addr,data):
    header = process_header(data)
    findDomain(data)
    question = process_question(data)
    answer = process_answer(ec2_ip_addr)
    
    return header+ question + answer + data[12+ ANS_END_IDX:]


#  needs: best_ec2_ip  data[0](bytes)  address(host, port)
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
        client_ip_addr = data[1][0]
        # print("running2")
        # header = unpack("!HHHHHH",packet[0:12])
        #get the best ec2 ip address
        best_ec2_server = get_min_ec2_loc(client_ip_addr)

        # pack the udp meesage  
        response_packet = pack_all(best_ec2_server,packet)
        
       
        if DNS_DOMAIN_NAME != DOMAIN_NAME:
            print("domain names are different")
            continue
        # send back
        server_socket.sendto(response_packet,client_addr)
       

if __name__ == "__main__":
    starter()
    
