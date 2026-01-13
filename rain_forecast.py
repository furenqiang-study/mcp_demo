import requests
import uuid
from datetime import datetime


# 降雨预报
def start_forecast(token, name, start_time):
    base_url = "http://t1.zjsophon.com:10000/hydraulic-server"
    url = base_url + "/core/busi/exec"
    headers = {
        "Content-Type": "application/json",
        "tenant": "default",
        "application": "platform",
        "token": token
    }
    # 按照对应的格式解析
    dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

    # 转时间戳（秒级）
    timestamp = dt.timestamp()
    random_id = str(uuid.uuid4())
    data = {
        "dir": "business",
        "modelId": "rainfallForecast",
        "menuId": "rainfallForecast",
        "datasetId": "2",
        "condition": {
            "code": random_id,
            "name": name,
            "mockObjectId": "1",
            "startTime": int(timestamp * 1000),
            "simDuration": 3,
            "op": "save"
        }
    }

    response = requests.post(url, headers=headers, json=data)
    url_query = base_url + "/core/busi/query"
    data_query = {
        "datasetIds": [
            "1"
        ],
        "condition": {
            "1": {
                "id": response.json()['datas']['2.1']
            }
        },
        "dir": "business",
        "modelId": "rainfallForecast",
        "menuId": "rainfallForecast",
        "buttonId": "search"
    }
    response_query = requests.post(url_query, headers=headers, json=data_query)
    return response_query.json()