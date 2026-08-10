# ============================================================
# SECTION 1: IMPORTS & CONFIGURATION
# ============================================================
import os
import chromadb
from chromadb.utils import embedding_functions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chroma_db")
MODEL_NAME = "all-MiniLM-L6-v2"

# Optional streamlit caching — only if running in streamlit
try:
    import streamlit as st
    cache_decorator = st.cache_resource
except:
    # when running python main.py / python -c, no streamlit context
    def cache_decorator(func):
        return func

# ============================================================
# SECTION 2: DATABASE & COLLECTION SETUP
# (Classes used: SentenceTransformerEmbeddingFunction,
# PersistentClient, Collection)
# ============================================================

@cache_decorator
def get_collection():
    # 1. Embedding function – turns text into vectors
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=MODEL_NAME
    )
    # 2. PersistentClient – manages the database on disk
    client = chromadb.PersistentClient(path=DB_PATH)
    # 3. Collection – the actual table that stores & searches chunks
    col = client.get_or_create_collection(
        name="docs",
        embedding_function=emb_fn
    )
    return col

collection = get_collection()

# ============================================================
# SECTION 3: CORE FUNCTIONS – WHAT THEY DO & WHICH CLASSES THEY CALL
# ============================================================

# ------------------------------------------------------------------
# FUNCTION 1: chunk_text()
# ------------------------------------------------------------------
# WHAT: Splits long text into small, overlapping pieces so that
# the database can handle small units and keep context.
# INPUT: text (string), optional size/overlap.
# OUTPUT: list of strings (chunks).
# CALLS: No classes – pure Python string slicing.
# ------------------------------------------------------------------
def chunk_text(text, size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
        if start >= len(text):
            break
    return chunks

# ------------------------------------------------------------------
# FUNCTION 2: add_document()
# ------------------------------------------------------------------
# WHAT: Takes a full document, chops it into chunks (using chunk_text),
# gives each chunk a unique ID, and adds them to the Collection.
# INPUT: text (string), doc_id (string, e.g., "article_1").
# OUTPUT: number of chunks added (int).
# CALLS: collection.add() <- method of Collection class.
# ------------------------------------------------------------------
def add_document(text, doc_id):
    chunks = chunk_text(text)
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    # clean old ids if exist
    try:
        collection.delete(ids=ids)
    except:
        pass
    collection.add(documents=chunks, ids=ids)
    return len(chunks)

# ------------------------------------------------------------------
# FUNCTION 3: search_db()
# ------------------------------------------------------------------
# WHAT: Takes your search question, embeds it, finds top 'n'
# most similar chunks, returns them.
# INPUT: query (string), optional n.
# OUTPUT: matched text joined, or empty string.
# CALLS: collection.query() <- method of Collection class.
# ------------------------------------------------------------------
def search_db(query, n=3):
    if collection.count() == 0:
        return "No docs in brain"
    res = collection.query(query_texts=[query], n_results=n)
    if res["documents"] and res["documents"][0]:
        return "\n\n---\n\n".join(res["documents"][0])
    return ""

# ============================================================
# SECTION 4: QUICK START (run this file to test)
# ============================================================
if __name__ == "__main__":
    add_document(
        "Machine learning is a subset of AI. Deep learning uses neural networks.",
        "ml_intro"
    )
    print("✅ Added.")
    results = search_db("What is deep learning?")
    print("\n🔍 Found:\n", results)