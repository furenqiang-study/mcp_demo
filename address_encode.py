# encoding:utf-8
import requests

# 地理编码
# 接口地址
url = "https://api.map.baidu.com/geocoding/v3"

# 此处填写你在控制台-应用管理-创建应用后获取的AK
ak = "Q3qn7q8reD6M6NXMd2TalqnOpcfeFvD6"

def start_encode(address:str):
    params = {
        "address": address,
        "output": "json",
        "ak": ak,

    }
    response = requests.get(url=url, params=params)
    if response:
        lng = response.json()['result']['location']['lng']
        lat = response.json()['result']['location']['lat']
        return str(f"{lng:.6f}")+','+str(f"{lat:.6f}")
    else:
        return None