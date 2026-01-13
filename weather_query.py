# 工具内容（Python）—— 大模型开发平台专用
import requests

BAIDU_WEATHER_URL = "https://api.map.baidu.com/weather/v1/"
AK = "Q3qn7q8reD6M6NXMd2TalqnOpcfeFvD6"   # ← 换成有效 AK

def get_weather(location: str, hours: int) -> str:
    """
    查询未来 hours 小时的逐小时降雨量
    :param location: 经纬度字符串，如 "116.40387,39.91489"
    :param hours:    查询时长，整数，1~24
    :return:         字典 {时间点: 降雨量(mm)}
    """
    params = {"location": location.strip(), "data_type": "all", "ak": AK}
    resp = requests.get(BAIDU_WEATHER_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != 0:
        return {"error": data.get("message")}

    # 取未来 24 小时数据
    # forecast_hours = data["result"]["forecasts"][0]["hours"]
    forecast_hours = data["result"]["forecast_hours"]
    # # 仅保留前 hours 条
    # result = {
    #     h["data_time"]: float(h["prec_1h"])
    #     for h in forecast_hours[:hours]
    # }
    # return result
    # 仅保留前 hours 条
    prec_1h_list = [float(h["prec_1h"]) for h in forecast_hours[:hours]]
    # tm_count = sum(1 for p in prec_1h_list if p > 0)

    # result = {"P": prec_1h_list, "TM": tm_count}
    result = {"P": prec_1h_list, "TM": hours}
    return str(result)