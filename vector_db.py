# ============================================================
#  SECTION 1: IMPORTS & CONFIGURATION
# ============================================================
import os
import chromadb
from chromadb.utils import embedding_functions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chroma_db")
MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
#  SECTION 2: DATABASE & COLLECTION SETUP
#  (Classes used: SentenceTransformerEmbeddingFunction,
#   PersistentClient, Collection)
# ============================================================

# 1. Embedding function – turns text into vectors
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=MODEL_NAME
)

# 2. PersistentClient – manages the database on disk
client = chromadb.PersistentClient(path=DB_PATH)

# 3. Collection – the actual table that stores & searches chunks
collection = client.get_or_create_collection(
    name="docs",
    embedding_function=emb_fn
)


# ============================================================
#  SECTION 3: CORE FUNCTIONS – WHAT THEY DO & WHICH CLASSES THEY CALL
# ============================================================

# ------------------------------------------------------------------
# FUNCTION 1: chunk_text()
# ------------------------------------------------------------------
# WHAT: Splits long text into small, overlapping pieces so that
#       the database can handle small units and keep context.
# INPUT:  text (string), optional size/overlap.
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
    return chunks


# ------------------------------------------------------------------
# FUNCTION 2: add_document()
# ------------------------------------------------------------------
# WHAT: Takes a full document, chops it into chunks (using chunk_text),
#       gives each chunk a unique ID, and adds them to the Collection.
# INPUT:  text (string), doc_id (string, e.g., "article_1").
# OUTPUT: number of chunks added (int).
# CALLS:  collection.add()  ← this is a method of the Collection class.
#         The Collection internally uses emb_fn to embed every chunk.
# ------------------------------------------------------------------
def add_document(text, doc_id):
    chunks = chunk_text(text)
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)   # <-- Collection class
    return len(chunks)


# ------------------------------------------------------------------
# FUNCTION 3: search_db()
# ------------------------------------------------------------------
# WHAT: Takes your search question, embeds it (automatically via the
#       Collection), finds the top 'n' most similar stored chunks,
#       and returns them as a single combined string.
# INPUT:  query (string), optional n (number of results).
# OUTPUT: matched text chunks joined with separators, or empty string.
# CALLS:  collection.query()  ← this is a method of the Collection class.
#         The Collection internally uses emb_fn to embed your query
#         and compares it against all stored embeddings.
# ------------------------------------------------------------------
def search_db(query, n=3):
    res = collection.query(query_texts=[query], n_results=n)   # <-- Collection class
    if res["documents"]:
        return "\n\n---\n\n".join(res["documents"][0])
    return ""


# ============================================================
#  SECTION 4: QUICK START (run this file to test)
# ============================================================
if __name__ == "__main__":
    # Add a sample document
    add_document(
        "Machine learning is a subset of AI. Deep learning uses neural networks.",
        "ml_intro"
    )
    print("✅ Added.")

    # Search
    results = search_db("What is deep learning?")
    if results:
        print("\n🔍 Found:\n", results)