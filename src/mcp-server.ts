import { McpServer } from '@modelcontextprotocol/sdk/server/mcp';
import { RegisteredTool, AnyToolHandler } from '@modelcontextprotocol/sdk/server/mcp';

export class MCPServer {
  private mcp: McpServer;

  constructor() {
    this.mcp = new McpServer({
      name: 'mcp-standardizer',
      description: 'A Node.js MCP standardization tool',
      version: '1.0.0'
    });
  }

  public registerTool<InputArgs = undefined>(
    name: string,
    config: {
      title?: string;
      description?: string;
      inputSchema?: any;
      outputSchema?: any;
      annotations?: any;
      _meta?: Record<string, unknown>;
    },
    handler: AnyToolHandler<InputArgs>
  ): RegisteredTool {
    return this.mcp.registerTool(name, config, handler as any);
  }

  public get mcpInstance() {
    return this.mcp;
  }
}