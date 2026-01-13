import requests
import json

def start_transform(hours,sz):
    data = json.loads(sz)
    server_url = "http://t1.zjsophon.com:14000/zz0/gfs-tif/run_test"
    result =requests.post(server_url,json={"topLat":data['topLat'],"leftLon":data['leftLon'],"rightLon":data['rightLon'],"bottomLat":data['bottomLat'],"hours":int(hours)})
    # print(result.json())
    return result.json()

# gfsToTif(50,110,125,20,3)

# print(start_transform(3,"{\"topLat\":50,\"leftLon\":110,\"rightLon\":125,\"bottomLat\":20}"))
print(start_transform(3,"{\"topLat\":50,\"leftLon\":110,\"rightLon\":125,\"bottomLat\":20}"))