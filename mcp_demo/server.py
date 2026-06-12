from datetime import datetime
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("mcp-demo")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@mcp.tool()
def current_time(timezone: str = "Asia/Shanghai") -> str:
    """Return the current time for an IANA timezone, for example Asia/Shanghai."""
    try:
        now = datetime.now(ZoneInfo(timezone))
    except Exception as exc:
        raise ValueError(f"Invalid timezone: {timezone}") from exc

    return now.strftime("%Y-%m-%d %H:%M:%S %Z")


@mcp.resource("demo://intro")
def intro() -> str:
    """A tiny resource exposed by this MCP server."""
    return (
        "This is a minimal MCP demo server. "
        "It exposes tools named add and current_time."
    )


if __name__ == "__main__":
    mcp.run()
