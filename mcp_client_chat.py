# Your own Claude Desktop clone
from fastmcp import Client
from mcp_server import mcp
import asyncio

async def chat():
    print("Your MCP Agent (type 'quit' to exit)\n")
    async with Client(mcp) as client:
        while True:
            q = input("You: ")
            if q == "quit": break
            result = await client.call_tool("search_knowledge", {"query": q})
            print(f"Agent: {result.data}\n")

asyncio.run(chat())