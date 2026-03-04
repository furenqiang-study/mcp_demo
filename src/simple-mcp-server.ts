import express from 'express';
const { Request, Response } = express;
import * as z from 'zod/v4';

const app = express();
const PORT = 3000;

// 添加 CORS 支持
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }

  next();
});

// 配置 JSON 解析中间件
app.use(express.json());

// MCP 服务器元信息
const serverInfo = {
  name: 'mcp-standardizer',
  description: 'A Node.js MCP standardization tool',
  version: '1.0.0'
};

// 工具定义
const tools = {
  extract_numbers: {
    title: '数字提取与图表汇总',
    description: '检查用户输入的内容中是否有数字，如果有，就将数字都提取出来，用图表进行汇总',
    inputSchema: z.object({
      content: z.string().describe('要检查的用户输入内容'),
      chartType: z.enum(['bar', 'pie', 'line']).optional().describe('图表类型，默认为柱状图')
    }),
    execute: async (params: any) => {
      const { content, chartType = 'bar' } = params;

      // 添加调用日志
      console.log(`[MCP] 调用 extract_numbers 工具`);
      console.log(`[MCP] 输入参数: content=${content}, chartType=${chartType}`);

      try {
        // 提取所有数字
        const numbers = content.match(/\d+(\.\d+)?/g)?.map(Number) || [];
        const scaledNumbers = numbers.map((num: number) => num + 10);
        if (numbers.length === 0) {
          return {
            success: true,
            hasNumbers: false,
            message: 'No numbers found in the input'
          };
        }

        // 统计数字出现频率
        const numberCount: Record<number, number> = {};
        numbers.forEach((num: number) => {
          numberCount[num] = (numberCount[num] || 0) + 1;
        });

        // 生成图表数据
        const chartData = {
          labels: Object.keys(numberCount).map(Number),
          datasets: [{
            label: 'Number Frequency',
            data: Object.values(numberCount),
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        };

        const result = {
          success: true,
          hasNumbers: true,
          numbers,
          numberCount,
          chartType,
          chartData,
          scaledNumbers
        };

        // 添加结果日志
        console.log(`[MCP] extract_numbers 工具执行成功`);
        console.log(`[MCP] 提取到的数字: ${numbers.join(', ')}`);
        console.log(`[MCP] 图表类型: ${chartType}`);


        return result;
      } catch (error) {
        const errorResult = { success: false, error: `Failed to extract numbers: ${(error as Error).message}` };

        // 添加错误日志
        console.error(`[MCP] extract_numbers 工具执行失败: ${(error as Error).message}`);

        return errorResult;
      }
    }
  }
};

// MCP GET 请求处理（用于浏览器访问和健康检查）
app.get('/mcp', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    message: 'MCP endpoint is running',
    serverInfo,
    availableMethods: ['POST'],
    availableTools: Object.keys(tools)
  });
});

// MCP POST 端点
app.post('/mcp', async (req: Request, res: Response) => {
  const { jsonrpc, id, method, params } = req.body;

  if (jsonrpc !== '2.0') {
    return res.status(400).json({ jsonrpc: '2.0', error: { code: -32600, message: 'Invalid Request' }, id });
  }

  // 处理初始化请求
  if (method === 'initialize') {
    return res.json({
      "jsonrpc": "2.0",
      "id": id,
      "result": {
        "protocolVersion": "2024-11-05",
        "serverInfo": serverInfo,
        "capabilities": {
          "toolExecution": {
            "supported": true
          }
        }
      }
    });
  }

  // 处理工具调用请求
  if (method === 'tools/call') {
    const { name: toolName, arguments: args } = params;

    if (!tools[toolName as keyof typeof tools]) {
      return res.json({
        "jsonrpc": "2.0",
        "id": id,
        "error": { "code": -32601, "message": `Tool not found: ${toolName}` }
      });
    }

    try {
      const result = await tools[toolName as keyof typeof tools].execute(args);

      // 构建符合要求的响应格式
      const textResult = JSON.stringify(result);
      const contentItem = {
        "type": "text",
        "text": textResult
      };

      return res.json({
        "jsonrpc": "2.0",
        "id": id,
        "result": {
          "content": [contentItem]
        }
      });
    } catch (error) {
      const errorMessage = `Failed to extract numbers: ${(error as Error).message}`;
      const textResult = JSON.stringify({ error: errorMessage });
      const contentItem = {
        "type": "text",
        "text": textResult
      };

      return res.json({
        "jsonrpc": "2.0",
        "id": id,
        "result": {
          "content": [contentItem]
        }
      });
    }
  }

  // 处理其他请求
  if (method === 'tools/list') {
    return res.json({
      jsonrpc: '2.0',
      id,
      result: {
        tools: Object.entries(tools).map(([name, tool]) => ({
          name,
          title: tool.title,
          description: tool.description,
          inputSchema: {
            type: "object",
            properties: {
              content: {
                type: "string",
                description: "要检查的用户输入内容"
              },
              chartType: {
                type: "string",
                enum: ["bar", "pie", "line"],
                description: "图表类型，默认为柱状图",
                default: "bar"
              }
            },
            required: ["content"]
          }
        }))
      }
    });
  }

  return res.json({
    jsonrpc: '2.0',
    id,
    error: { code: -32601, message: `Method not found: ${method}` }
  });
});

// 健康检查端点
app.get('/health', (_, res) => {
  res.json({ status: 'ok', serverInfo });
});

app.listen(PORT, () => {
  console.log(`MCP Standardization Tool running on http://localhost:${PORT}`);
  console.log(`MCP endpoint: http://localhost:${PORT}/mcp`);
  console.log(`Health check: http://localhost:${PORT}/health`);
});