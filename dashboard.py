import streamlit as st
st.set_page_config(page_title="hello-agent", layout="centered")
st.title("🤖 hello-agent")
st.caption("Pure Python Dashboard - Phase 10: Final | Router + RAG + MCP")

from agent import ask_agent
from rag import add_document, list_documents, add_document_chunks, collection
import PyPDF2
import shutil

# ==========================================
# SIDEBAR 1: Quick Buttons
# ==========================================
st.sidebar.title("Quick Buttons")
if st.sidebar.button("Refund Policy"):
    st.session_state["q"] = "what is refund policy"
if st.sidebar.button("Mission"):
    st.session_state["q"] = "what is your mission"
if st.sidebar.button("Privacy"):
    st.session_state["q"] = "privacy policy"

# ==========================================
# SIDEBAR 2: Settings
# ==========================================
st.sidebar.divider()
st.sidebar.title("Settings")
use_ai_router = st.sidebar.checkbox("Use AI Router", value=False)
st.sidebar.caption(f"Mode: {'AI Router' if use_ai_router else 'Keyword Router'}")

# ==========================================
# SIDEBAR 3: Brain Status (NEW - Phase 10)
# ==========================================
st.sidebar.divider()
st.sidebar.title("🧠 Brain Status")
count = collection.count()
st.sidebar.metric("Total Chunks/Docs in Memory", count)

docs = list_documents()
st.sidebar.write(f"Knows {len(set(docs))} files:")
st.sidebar.code("\n".join(set(docs)) if docs else "No docs yet")

if st.sidebar.button("🗑️ Clear Brain"):
    shutil.rmtree("./chroma_db", ignore_errors=True)
    st.sidebar.success("Brain cleared! Restart app.")
    st.rerun()

# ==========================================
# SIDEBAR 4: Train Agent
# ==========================================
st.sidebar.divider()
st.sidebar.title("📚 Train Agent")
uploaded_file = st.sidebar.file_uploader("Upload file", type=["txt", "pdf"])

if uploaded_file is not None:
    doc_id = uploaded_file.name
    doc_text = ""

    if doc_id.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                doc_text += text + "\n"
    else:
        doc_text = uploaded_file.read().decode("utf-8")

    st.sidebar.caption(f"Size: {len(doc_text)} chars")

    if st.sidebar.button(f"Learn {doc_id}"):
        if len(doc_text) > 1000:
            num_chunks = add_document_chunks(doc_text, doc_id, chunk_size=800)
            st.sidebar.success(f"Learned {doc_id} as {num_chunks} chunks!")
        else:
            add_document(doc_text, doc_id)
            st.sidebar.success(f"Learned: {doc_id}")
        st.rerun()

# ==========================================
# MAIN: Ask Agent
# ==========================================
import asyncio
from fastmcp import Client
from mcp_server import mcp

async def ask_via_mcp(question: str):
    async with Client(mcp) as client:
        result = await client.call_tool("search_knowledge", {"query": question})
        return result.data

question = st.text_input("Ask something:", value=st.session_state.get("q",""))
use_mcp = st.checkbox("Use MCP Server (test)", value=True)

if st.button("Send") and question:
    if use_mcp:
        st.info("Calling via MCP: search_knowledge")
        with st.spinner("MCP searching brain..."):
            mcp_answer = asyncio.run(ask_via_mcp(question))
        st.write(f"**Router:** MCP -> search_knowledge")
        st.success(mcp_answer)
    else:
        result = ask_agent(question, use_ai_router=use_ai_router)
        st.write(f"**Router:** {result['tool']}")
        st.success(result['answer'])
        with st.expander("Show Context used"):
            st.write(result['context'])
    
    st.session_state["q"] = ""