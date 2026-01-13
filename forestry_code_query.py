import requests

url = 'http://t1.zjsophon.com:10000/zz0/forestry-server/core/busi/exec'

def query_forestry_code(forestryCode:str):
  data = {
    "condition": {
      "op": "busiRelationForMaxkb",
      "forestryCode": forestryCode
    },
    "dir": "operationShow",
    "modelId": "operationInfo",
    "datasetId": 1
  }

  response = requests.post(url,
                           headers={'Content-Type': 'application/json', 'application': 'platform', 'tenant': 'default'},
                           json=data)
  return response.text