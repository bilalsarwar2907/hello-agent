# test_mcp.py - Tests MCP server without Node.js
from fastmcp import Client
import asyncio
from mcp_server import mcp

async def test():
    async with Client(mcp) as client:
        # List tools
        tools = await client.list_tools()
        print("Tools found:", [t.name for t in tools])
        
        # Test search_knowledge
        result = await client.call_tool("search_knowledge", {"query": "return address"})
        print("\nsearch_knowledge result:", result)
        
        # Test brain status
        result2 = await client.call_tool("get_brain_status", {})
        print("\nBrain status:", result2)

asyncio.run(test())