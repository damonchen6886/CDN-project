#R = 6371; // km
# distance = Math.acos(Math.sin(lat1)*Math.sin(lat2) +
# Math.cos(lat1)*Math.cos(lat2) *
# Math.cos(lon2-lon1)) * R;


# NOTE: This is your final list of servers
# ec2-18-207-254-152.compute-1.amazonaws.com      Origin server (running Web server on port 8080)
# ec2-34-238-192-84.compute-1.amazonaws.com       N. Virginia
# ec2-13-231-206-182.ap-northeast-1.compute.amazonaws.com Tokyo
# ec2-13-239-22-118.ap-southeast-2.compute.amazonaws.com  Sydney
# ec2-34-248-209-79.eu-west-1.compute.amazonaws.com       Ireland
# ec2-18-231-122-62.sa-east-1.compute.amazonaws.com       Sao Paulo
# ec2-3-101-37-125.us-west-1.compute.amazonaws.com        N. California


EC2_IP = {
"ec2-34-238-192-84.compute-1.amazonaws.com":"34.238.192.84",
"ec2-13-231-206-182.ap-northeast-1.compute.amazonaws.com":"13.231.206.182",
"ec2-13-239-22-118.ap-southeast-2.compute.amazonaws.com":"13.239.22.118",
"ec2-34-248-209-79.eu-west-1.compute.amazonaws.com":"34.248.209.79",
"ec2-18-231-122-62.sa-east-1.compute.amazonaws.com":"18.231.122.62",
"ec2-3-101-37-125.us-west-1.compute.amazonaws.com":"3.101.37.125"}
#attributes：https://blog.ip2location.com/knowledge-base/find-distance-between-2-ips-using-bash/
# IP api: 
#api:http://ip-api.com/json
import requests
import json
import math
def get_lat_lon(ip_addr):
    try:
        url = "http://ip-api.com/json/"+ip_addr
        payload = {}
        files = []
        headers= {}
        response = requests.request("GET", url, headers=headers, data = payload, files = files)
    except:
        print("wrong ip address")
    content = response.json()
    if response.status_code == 200:
        result = []
        result.append(content['lon'])
        result.append(content['lat'])
        # print(result)
        return result
    else:
        return ""


def get_min_ec2_loc(ip_addr):
    ip_loc = get_lat_lon(ip_addr)
    
    min_dis = float('inf')
    ec2_lat_lot = []
    shortest_ec2_ip = ''
    for key, value in EC2_IP.items():
        ec2_lat_lot = get_lat_lon(value)
        distance =cal_distance(ip_loc[0],ip_loc[1],ec2_lat_lot[0],ec2_lat_lot[1])
        # print(distance)
        if min_dis > distance:
            shortest_ec2_ip = value
            min_dis = distance
    # print(shortest_ec2_ip)
    return shortest_ec2_ip


def cal_distance(lat1,lon1,lat2,lon2):
    # attributes: 
    # https://stackoverflow.com/questions/19412462
    # /getting-distance-between-two-points-based-on-latitude-longitude/
    # 43211266#43211266
    R = 6371; # km
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlat = lat2 -lat1
    dlon = lon2 -lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# print(get_min_ec2_loc("2601:182:c77f:97b0:a82d:d10a:263f:ea9d"))