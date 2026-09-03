import asyncio
import sys
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def main():
    url = "http://127.0.0.1:8765/sse"
    print(f"Connecting to MCP server at {url}...")
    try:
        async with sse_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("\n1. Listing available MCP tools...")
                tools_result = await session.list_tools()
                for tool in tools_result.tools:
                    print(f" - Tool: {tool.name}")
                    print(f"   Description: {tool.description}")

                print("\n2. Calling list_study_files()...")
                res1 = await session.call_tool("list_study_files", {})
                for content in res1.content:
                    print(content.text)

                print("\n3. Calling read_study_file('sample_notes.txt')...")
                res2 = await session.call_tool("read_study_file", {"filename": "sample_notes.txt"})
                for content in res2.content:
                    print(content.text)

                print("\n4. Calling calculate('2 + 3 * 4')...")
                res3 = await session.call_tool("calculate", {"expression": "2 + 3 * 4"})
                for content in res3.content:
                    print(f"Result: {content.text}")

                print("\nSUCCESS: All 3 MCP tools verified working!")
    except Exception as e:
        print(f"Connection error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
