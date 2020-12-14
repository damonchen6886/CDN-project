

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

# for performace, we hardcode the EC2 latitude and longtitude by maunnly lookedup from the API above.
EC2_IP_LOCATION= {
  "ec2-34-238-192-84.compute-1.amazonaws.com":[-77.4874, 39.0438],
"ec2-13-231-206-182.ap-northeast-1.compute.amazonaws.com":[139.692, 35.6895],
"ec2-13-239-22-118.ap-southeast-2.compute.amazonaws.com":[151.2002, -33.8591],
"ec2-34-248-209-79.eu-west-1.compute.amazonaws.com":[-6.26031, 53.3498],
"ec2-18-231-122-62.sa-east-1.compute.amazonaws.com":[-46.6333, -23.5505],
"ec2-3-101-37-125.us-west-1.compute.amazonaws.com":[-121.895, 37.3394]  
}
import requests
import json
import math

# get the latitude and longitude from the external api
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

# calculate the distance based on geo location and return top 2 ec2 server ip
def get_min_ec2_loc(ip_addr):
    ip_loc = get_lat_lon(ip_addr)
    ec2_lat_lot = []
    result = {}
    top_two_ec2 = []
    for key, value in EC2_IP.items():
        ec2_lat_lot = EC2_IP_LOCATION[key]
        # ec2_lat_lot = get_lat_lon(value)
        # print("ec2_lat_lot",ec2_lat_lot)
        distance =cal_distance(ip_loc[0],ip_loc[1],ec2_lat_lot[0],ec2_lat_lot[1])
        result[distance] = value
    print("result = ",result)
    keys =sorted(result)
    # print(keys)
    top_two_ec2.append(result[keys[0]])
    top_two_ec2.append(result[keys[1]])
    # print(top_two_ec2)
    # print(shortest_ec2_ip)
    return top_two_ec2

# calculate the geolocation based on latitude and longitude  
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