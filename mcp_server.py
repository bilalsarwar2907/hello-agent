# mcp_server.py - FIXED VERSION using vector_db
from fastmcp import FastMCP
from vector_db import search_db, add_document, collection
from tools.router import decide_tool

mcp = FastMCP("hello-agent")

# helper to mimic old functions
def list_documents():
    try:
        data = collection.get()
        ids = data.get("ids", [])
        return [i.rsplit("_", 1)[0] for i in ids]
    except:
        return []

def add_document_chunks(text, doc_id, chunk_size=800):
    return add_document(text, doc_id)

@mcp.tool
def search_knowledge(query: str) -> str:
    """Search brain for relevant docs"""
    return search_db(query, n=3)

@mcp.tool
def decide_tool_mcp(user_input: str) -> str:
    """Decide which tool to use"""
    return decide_tool(user_input)

@mcp.tool
def add_knowledge(text: str, doc_id: str) -> str:
    """Add new document to brain"""
    n = add_document(text, doc_id)
    return f"Added {doc_id} with {n} chunks"

@mcp.tool
def list_knowledge() -> str:
    """List all docs in brain"""
    docs = set(list_documents())
    return f"Brain has {len(docs)} files: {', '.join(docs)}"

if __name__ == "__main__":
    mcp.run()