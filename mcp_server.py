# mcp_server.py - FIXED VERSION using fastmcp
from fastmcp import FastMCP
from rag import search, add_document, add_document_chunks, list_documents, collection
from tools.router import decide_tool

mcp = FastMCP("hello-agent")

@mcp.tool()
def search_knowledge(query: str) -> str:
    from agent import ask_agent
    result = ask_agent(query, use_ai_router=False)
    return result['answer']

@mcp.tool()
def decide_router_tool(question: str) -> str:
    """Decides which tool to use: refund, mission, privacy, calculator, search"""
    tool = decide_tool(question)
    return f"Should use: {tool}"

@mcp.tool()
def get_brain_status() -> str:
    """Returns how many documents agent knows and their IDs"""
    ids = list_documents()
    count = collection.count()
    return f"Brain has {count} docs/chunks. IDs: {ids}"

@mcp.tool()
def calculator(expression: str) -> str:
    """Evaluates math expression like '2+2*3' or '100/4'"""
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def add_knowledge(text: str, doc_id: str) -> str:
    """Add new knowledge to persistent brain. text=content, doc_id=filename"""
    if len(text) > 1000:
        num = add_document_chunks(text, doc_id)
        return f"Added {doc_id} as {num} chunks, saved to disk."
    else:
        add_document(text, doc_id)
        return f"Added {doc_id}, saved to disk."

if __name__ == "__main__":
    mcp.run()