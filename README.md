# MCP 服务器 Python 版

这是一个基于 Python 开发的 Model Context Protocol (MCP) 服务器项目，提供了多种实用工具供 AI 代理调用。

## 项目概述

该项目实现了一个完整的 MCP 服务器，支持与 AI 代理进行交互，提供了多种工具服务。主要功能包括：

- 地址编码转换
- 林业码查询
- GFS 数据转 TIF 格式
- 数据库查询（MySQL/PostgreSQL）
- 降雨预报
- 字符串转数组
- 图片标注
- 水库水位库容互查
- 天气查询
- 新安江模型计算

## 技术栈

- **Python** - 主要开发语言
- **FastAPI** - Web 框架
- **uvicorn** - ASGI 服务器
- **mcp.server** - MCP 服务器 SDK

## 安装步骤

### 1. 克隆或进入项目目录

```bash
cd D:\work\MyVueProject\2025\my_mcp_demo
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 启动服务器

```bash
python server.py
```

服务器将在 `http://localhost:8000` 上运行。

### API 接口

#### 1. 健康检查

```bash
GET /health
```

返回服务器状态信息。

#### 2. MCP 初始化

```bash
POST /mcp
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "initialize"
}
```

返回 MCP 服务器的元信息和能力。

#### 3. 工具列表

```bash
POST /mcp
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/list"
}
```

返回可用的工具列表。

#### 4. 调用工具

```bash
POST /mcp
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/call",
  "params": {
    "name": "地理编码",
    "arguments": {
      "address": "北京市海淀区中关村"
    }
  }
}
```

调用指定工具并返回结果。

## 工具示例：地理编码

### 功能说明

将中文地址转换为地理坐标（经纬度）。

### 输入参数

- `address` (string)：要编码的中文地址

### 输出结果

- 包含经纬度信息的地理编码结果

### 调用示例

```json
{
  "jsonrpc": "2.0",
  "id": "123",
  "method": "tools/call",
  "params": {
    "name": "地理编码",
    "arguments": {
      "address": "北京市海淀区中关村"
    }
  }
}
```

## 项目结构

```
my_mcp_demo/
├── server.py                    # 主 MCP 服务器
├── address_encode.py            # 地址编码工具
├── forestry_code_query.py       # 林业码查询工具
├── gfsToTif.py                  # GFS 转 TIF 工具
├── mysql_db_tool.py             # MySQL 数据库查询工具
├── pg_db_tool.py                # PostgreSQL 数据库查询工具
├── rain_forecast.py             # 降雨预报工具
├── strToArray.py                # 字符串转数组工具
├── tag_images.py                # 图片标注工具
├── water_height_capacity.py     # 水库水位库容互查工具
├── weather_query.py             # 天气查询工具
├── xinanjiang_model.py          # 新安江模型计算工具
├── requirements.txt             # 依赖列表
├── dockerfile                   # Docker 配置
└── README.md                    # 项目说明文档
```

## Docker 部署

### 1. 构建镜像

```bash
docker build -t mcp-server .
```

### 2. 运行容器

```bash
docker run -p 8000:8000 mcp-server
```

## 许可证

MIT

## 联系方式

如有问题或建议，欢迎提出 Issue 或 Pull Request。