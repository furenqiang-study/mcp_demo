# MCP 标准化工具 Demo

这是一个基于 Node.js 和 TypeScript 开发的 Model Context Protocol (MCP) 标准化工具演示项目。

## 功能说明

该项目实现了一个 MCP 服务器，提供了数字提取和图表汇总功能。主要功能包括：

- 从文本中提取数字
- 统计数字出现频率
- 生成图表数据（支持柱状图、饼图、折线图）
- 遵循 MCP 协议，支持与 AI 代理进行交互

## 技术栈

- **Node.js** - 运行环境
- **TypeScript** - 编程语言
- **Express.js** - Web 框架
- **Zod** - Schema 验证库
- **@modelcontextprotocol/sdk** - MCP SDK

## 安装步骤

### 1. 克隆或进入项目目录

```bash
d: cd work\MyVueProject\2025\my_mcp_demo
```

### 2. 安装依赖

```bash
npm install
```

## 使用方法

### 启动服务

#### 开发模式（使用 ts-node）

```bash
npm run dev
```

#### 编译并启动（生产模式）

```bash
# 编译 TypeScript 代码
npm run build

# 启动编译后的代码
npm start
```

服务启动后，会在以下地址运行：
- MCP 端点：http://localhost:3000/mcp
- 健康检查：http://localhost:3000/health

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
    "name": "extract_numbers",
    "arguments": {
      "content": "测试数据 111、222、333",
      "chartType": "bar"
    }
  }
}
```

调用数字提取和图表汇总工具。

## 工具列表

### extract_numbers

**名称**：extract_numbers
**标题**：数字提取与图表汇总
**描述**：检查用户输入的内容中是否有数字，如果有，就将数字都提取出来，用图表进行汇总

**输入参数**：
- `content` (string)：要检查的用户输入内容
- `chartType` (string, 可选)：图表类型，支持 "bar"、"pie"、"line"，默认为 "bar"

**输出结果**：
- 提取的数字列表
- 数字出现频率统计
- 生成的图表数据

## 开发说明

### 项目结构

```
my_mcp_demo/
├── src/
│   └── simple-mcp-server.ts  # 主 MCP 服务器实现
├── dist/                      # 编译后的 JavaScript 文件
├── package.json               # 项目配置
├── tsconfig.json              # TypeScript 配置
└── README.md                  # 项目说明文档
```

### 编译代码

```bash
npm run build
```

### 代码检查

```bash
# 检查 TypeScript 类型
npm run typecheck

# 检查代码风格
npm run lint
```

## MCP 协议

本项目遵循 MCP (Model Context Protocol) 协议，该协议用于 AI 代理与外部工具进行交互。

主要支持的 MCP 方法：
- `initialize` - 初始化连接
- `tools/list` - 获取工具列表
- `tools/call` - 调用工具

## 部署

### 本地部署

按照上述使用方法启动服务即可。

### 生产部署

1. 编译代码：`npm run build`
2. 使用 PM2 或其他进程管理器启动服务：

```bash
npm install -g pm2
npm run build
npm start
```

## 许可证

MIT

## 联系方式

如有问题或建议，欢迎提出 Issue 或 Pull Request。