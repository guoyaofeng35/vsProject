# MCP Demo

这是一个最小可运行的 Python MCP 示例，包含：

- `server.py`：基于 `FastMCP` 的 MCP 服务端
- `client.py`：通过 stdio 启动服务端并调用 MCP 工具的客户端

## 安装

```powershell
cd D:\vsProject\mcp_demo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 运行

```powershell
python client.py
```

你会看到客户端列出 MCP 服务端暴露的工具，然后调用：

- `add`
- `current_time`
- `demo://intro` resource

## 在支持 MCP 的客户端中配置

如果你的客户端支持 stdio MCP server，可以配置类似：

```json
{
  "mcpServers": {
    "mcp-demo": {
      "command": "python",
      "args": ["D:\\vsProject\\mcp_demo\\server.py"]
    }
  }
}
```
