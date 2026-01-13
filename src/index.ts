import express from 'express';
import { MCPServer } from './mcp-server.js';
import { formatDataConfig, validateDataConfig, cleanDataConfig } from './standardization-tools.js';
import { createHttpServerTransport } from '@modelcontextprotocol/sdk/server/express';

const PORT = 3000;

// 创建 Express 应用
const app = express();

// 创建 MCP 服务器实例
const mcpServer = new MCPServer();

// 注册标准化工具
mcpServer.registerTool(
  formatDataConfig.name,
  formatDataConfig.config,
  formatDataConfig.handler
);

mcpServer.registerTool(
  validateDataConfig.name,
  validateDataConfig.config,
  validateDataConfig.handler
);

mcpServer.registerTool(
  cleanDataConfig.name,
  cleanDataConfig.config,
  cleanDataConfig.handler
);

// 创建 HTTP 服务器传输并连接
const transport = createHttpServerTransport(app, {
  path: '/mcp'
});

// 连接 MCP 服务器
mcpServer.mcpInstance.connect(transport).then(() => {
  console.log('MCP server connected to HTTP transport');
});

// 启动 Express 服务器
app.listen(PORT, () => {
  console.log(`MCP Standardization Tool running on http://localhost:${PORT}`);
  console.log(`MCP endpoint: http://localhost:${PORT}/mcp`);
});