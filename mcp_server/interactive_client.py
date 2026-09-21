import asyncio
import json
import shlex
import sys

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


URL = "http://127.0.0.1:8765/sse"


def _print_help() -> None:
    print(
        """
Commands:
  help                         Show this help
  tools                        List MCP tools
  files                        Call list_study_files
  read <filename>              Call read_study_file
  calc <expression>            Call calculate
  call <tool> <json-args>      Call any MCP tool with JSON args
  quit                         Exit

Examples:
  files
  read sample_notes.txt
  calc 2 + 3 * 4
  call calculate {"expression": "10 / 2"}
""".strip()
    )


def _print_tool_result(result) -> None:
    for content in result.content:
        text = getattr(content, "text", None)
        if text is not None:
            print(text)
        else:
            print(content)


async def _prompt() -> str:
    return await asyncio.to_thread(input, "\nmcp> ")


async def main() -> int:
    print(f"Connecting to Smart Tutor MCP at {URL} ...")
    try:
        async with sse_client(URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("Connected. Type 'help' for commands.")
                _print_help()

                while True:
                    try:
                        line = (await _prompt()).strip()
                    except (EOFError, KeyboardInterrupt):
                        print("\nExiting MCP client.")
                        return 0

                    if not line:
                        continue

                    command, _, rest = line.partition(" ")
                    command = command.lower()
                    rest = rest.strip()

                    try:
                        if command in {"quit", "exit"}:
                            print("Goodbye.")
                            return 0
                        if command in {"help", "?"}:
                            _print_help()
                            continue
                        if command == "tools":
                            tools_result = await session.list_tools()
                            for tool in tools_result.tools:
                                description = f" - {tool.description}" if tool.description else ""
                                print(f"{tool.name}{description}")
                            continue
                        if command == "files":
                            result = await session.call_tool("list_study_files", {})
                            _print_tool_result(result)
                            continue
                        if command == "read":
                            if not rest:
                                print("Usage: read <filename>")
                                continue
                            parts = shlex.split(rest)
                            result = await session.call_tool(
                                "read_study_file", {"filename": parts[0]}
                            )
                            _print_tool_result(result)
                            continue
                        if command == "calc":
                            if not rest:
                                print("Usage: calc <expression>")
                                continue
                            result = await session.call_tool("calculate", {"expression": rest})
                            _print_tool_result(result)
                            continue
                        if command == "call":
                            tool_name, _, json_args = rest.partition(" ")
                            if not tool_name:
                                print("Usage: call <tool> <json-args>")
                                continue
                            args = json.loads(json_args or "{}")
                            result = await session.call_tool(tool_name, args)
                            _print_tool_result(result)
                            continue

                        print(f"Unknown command: {command}. Type 'help' for commands.")
                    except Exception as exc:
                        print(f"Error: {exc}")
    except Exception as exc:
        print(f"Connection error: {exc}", file=sys.stderr)
        print("Make sure the Smart Tutor MCP Server window is running.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
