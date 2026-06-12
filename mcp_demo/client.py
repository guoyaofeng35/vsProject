import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_PATH = Path(__file__).with_name("server.py")


def print_tool_result(title: str, result) -> None:
    print(f"\n{title}")
    for item in result.content:
        text = getattr(item, "text", None)
        print(text if text is not None else item)


async def main() -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )

    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            add_result = await session.call_tool("add", {"a": 20, "b": 22})
            print_tool_result("add(20, 22):", add_result)

            time_result = await session.call_tool(
                "current_time",
                {"timezone": "Asia/Shanghai"},
            )
            print_tool_result("current_time(Asia/Shanghai):", time_result)

            resource = await session.read_resource("demo://intro")
            print("\nResource demo://intro:")
            for item in resource.contents:
                print(item.text)


if __name__ == "__main__":
    asyncio.run(main())
