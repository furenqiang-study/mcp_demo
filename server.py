"""
最小化 HTTP MCP 服务器
只包含最基本的功能
"""
import asyncio
import logging
import uvicorn
from typing import Any, Dict, List
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mcp.server import Server
from tag_images import start_tag
import json
from address_encode import start_encode
from rain_forecast import start_forecast
from mysql_db_tool import query_mysql_pymysql
from pg_db_tool import query_pg
from weather_query import get_weather
from gfsToTif import start_transform
from strToArray import convert_str_to_array
from xinanjiang_model import XAJ_model
from water_height_capacity import water_caculate
from forestry_code_query import query_forestry_code



# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """最小化 HTTP MCP 服务器"""

    # 创建服务器
    server = Server("minimal-http-mcp")

    # 定义工具
    @server.list_tools()
    async def list_tools() -> List[Dict[str, Any]]:
        return [
            {
                "name": "标注图片",
                "description": "标注图片",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "image_data": {"type": "string", "description": "图片下载地址数组"},
                        "box_points": {"type": "string", "description": "json字符串"},
                        "api_key": {"type": "string", "description": "api_key"},
                        "chat_id": {"type": "string", "description": "chat_id"},
                        "agent_id": {"type": "string", "description": "agent_id"},
                        "model": {"type": "string", "description": "model"}
                    },
                    "required": ["image_data","box_points","api_key","chat_id","agent_id"]
                }
            },
            {
                "name": "地理编码",
                "description": "标注图片",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string", "description": "地址"}
                    },
                    "required": ["address"]
                }
            },
            {
                "name": "降雨预报",
                "description": "降雨预报",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "token": {"type": "string", "description": "token"},
                        "name": {"type": "string", "description": "name"},
                        "start_time": {"type": "string", "description": "%Y-%m-%d %H:%M:%S"},
                    },
                    "required": ["token","name","start_time"]
                }
            },
            {
                "name": "mysql数据库查询",
                "description": "mysql数据库查询",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string", "description": "sql"},
                        "host": {"type": "string", "description": "host"},
                        "dbname": {"type": "string", "description": "dbname"},
                        "user": {"type": "string", "description": "user"},
                        "password": {"type": "string", "description": "password"},
                        "port": {"type": "number", "description": "port"}
                    },
                    "required": ["sql","host","dbname","user","password","port"]
                }
            },
            {
                "name": "pg数据库查询",
                "description": "pg数据库查询",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string", "description": "sql"},
                        "host": {"type": "string", "description": "host"},
                        "dbname": {"type": "string", "description": "dbname"},
                        "user": {"type": "string", "description": "user"},
                        "password": {"type": "string", "description": "password"},
                        "port": {"type": "number", "description": "port"},
                        "options": {"type": "string", "description": "-c search_path=myschema"}
                    },
                    "required": ["sql","host","dbname","user","password","port"]
                }
            },
            {
                "name": "天气查询",
                "description": "天气查询",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "经纬度字符串，如 '116.40387,39.91489'"},
                        "hours": {"type": "number", "description": "小时数"}
                    },
                    "required": ["location","hours"]
                }
            },
            {
                "name": "gfs转tif",
                "description": "gfs转tif",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "hours": {"type": "number", "description": "小时数"},
                        "area": {"type": "string", "description": "四至范围 {'topLat':'50','leftLon':'110','rightLon':'125','bottomLat':'20'}"}
                    },
                    "required": ["area","hours"]
                }
            },
            {
                "name": "str转array",
                "description": "str转array",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input_str": {"type": "string", "description": "input_str (str): 表示数组的字符串（如\"[1, 2, 3]\"或\"['a','b','c']\"）"}
                    },
                    "required": ["input_str"]
                }
            },
            {
                "name": "新安江模型(横山水库)",
                "description": "新安江模型(横山水库)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "param": {"type": "string", "description": "json字符串 {\"P\":[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],\"TM\":24}"}
                    },
                    "required": ["parm"]
                }
            }
            ,
            {
                "name": "水库水位库容互查",
                "description": "水库水位库容互查",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mode": {"type": "number","description": "0水位,1库容"},
                        "value": {"type": "number","description": "数值,浮点型"}
                    },
                    "required": ["mode","value"]
                }
            },
            {
                "name": "查询林业码",
                "description": "查询林业码",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "forestryCode": {"type": "string", "description": "林业码"}
                    },
                    "required": ["forestryCode"]
                }
            }
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        if name == "标注图片":
            image_data = arguments.get("image_data", [])
            box_points = arguments.get("box_points", "")
            api_key = arguments.get("api_key", "")
            chat_id = arguments.get("chat_id", "")
            agent_id = arguments.get("agent_id", "")
            model = arguments.get("model", "Qwen")
            print(arguments)
            result = start_tag(image_data, box_points, api_key, chat_id, agent_id, model)
            print(f"reuslt type:{type(result)}")
            return [{"type": "text", "text": json.dumps(result,ensure_ascii=False)}]
        elif name == "地理编码":
            address = arguments.get("address", "")
            result = start_encode(address)
            print(f"reuslt type:{type(result)}")
            return [{"type": "text", "text": result}]
        elif name == "降雨预报":
            token = arguments.get("token", "")
            name = arguments.get("name", "")
            start_time = arguments.get("start_time", "")
            result = start_forecast(token,name,start_time)
            print(f"reuslt type:{type(result)}")
            return [{"type": "text", "text": result}]
        elif name == "mysql数据库查询":
            sql = arguments.get("sql", "")
            host = arguments.get("host", "")
            dbname = arguments.get("dbname", "")
            user = arguments.get("user", "")
            password = arguments.get("password", "")
            port = arguments.get("port", "")
            result = query_mysql_pymysql(sql,host,dbname,user,password,port)
            print(f"reuslt type:{type(result)}")
            return [{"type": "text", "text": json.dumps(result,ensure_ascii=False)}]
        elif name == "pg数据库查询":
            sql = arguments.get("sql", "")
            host = arguments.get("host", "")
            dbname = arguments.get("dbname", "")
            user = arguments.get("user", "")
            password = arguments.get("password", "")
            port = arguments.get("port", "")
            options = arguments.get("options", "")
            result = query_pg(sql,host,dbname,user,password,port,options)
            print(f"reuslt type:{type(result)}")
            return [{"type": "text", "text": json.dumps(result,ensure_ascii=False)}]
        elif name == "天气查询":
            location = arguments.get("location", "")
            hours = arguments.get("hours", 3)
            result = get_weather(location,hours)
            print(f"reuslt type:{type(result)}")
            return [{"type": "text", "text": result}]
        elif name == "gfs转tif":
            area = arguments.get("area", "")
            hours = arguments.get("hours", 3)
            result = start_transform(hours,area)
            print(f"reuslt type:{type(result)}")
            return [{"type": "text", "text": json.dumps(result,ensure_ascii=False)}]
        elif name == "str转array":
            input_str = arguments.get("input_str", "")
            result = convert_str_to_array(input_str)
            print(f"reuslt type:{type(result)}")
            return [{"type": "text", "text": json.dumps(result,ensure_ascii=False)}]
        elif name == "新安江模型(横山水库)":
            param = arguments.get("param", "")
            result = XAJ_model(param)
            print(f"reuslt type:{type(result)}")
            return [{"type": "text", "text": json.dumps(result,ensure_ascii=False)}]
        elif name == "水库水位库容互查":
            mode = arguments.get("mode", 0)
            value = arguments.get("value", 1.0)
            result = water_caculate(mode,value)
            print(f"reuslt type:{type(result)}")
            return [{"type": "text", "text": json.dumps(result,ensure_ascii=False)}]
        elif name == "查询林业码":
            forestryCode = arguments.get("forestryCode", "")
            result = query_forestry_code(forestryCode)
            print(f"reuslt type:{type(result)}")
            return [{"type": "text", "text": json.dumps(result,ensure_ascii=False)}]
        return [{"type": "text", "text": f"Unknown tool: {name}"}]

    # 创建 FastAPI 应用
    app = FastAPI(title="Minimal MCP Server")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/mcp")
    async def handle_mcp(request: Request):
        """处理 MCP 请求"""
        try:
            data = await request.json()
            method = data.get("method", "")
            params = data.get("params", {})
            request_id = data.get("id", 1)

            logger.info(f"收到 MCP 请求: {method}")

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "serverInfo": {
                            "name": "Minimal MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }

            elif method == "tools/list":
                tools = await list_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                }

            elif method == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = await call_tool(tool_name, arguments)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": result}
                }

            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

            return JSONResponse(content=response)

        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1) if 'data' in locals() else 1,
                    "error": {"code": -32603, "message": str(e)}
                }
            )

    # 启动服务器
    logger.info("🚀 启动最小化 HTTP MCP 服务器...")
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server_uvicorn = uvicorn.Server(config)

    try:
        await server_uvicorn.serve()
    except KeyboardInterrupt:
        logger.info("👋 服务器已停止")


if __name__ == "__main__":
    asyncio.run(main())