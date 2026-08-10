# rag.py - PHASE 7 - Persistent Brain
import chromadb
import os
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
client = chromadb.PersistentClient(path=DB_PATH)

# ==========================================
# SECTION 1: Persistent Client - Saves to disk!
# ==========================================
# Before: chromadb.Client() -> memory only, dies on restart
# Now: PersistentClient -> saves to folder./chroma_db
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection("policy")

print(f"Brain loaded from disk. Knows: {collection.count()} docs")

# ==========================================
# SECTION 2: Load Initial Knowledge (only once ever)
# ==========================================
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "policy.txt"), "r", encoding="utf-8") as f:
        text = f.read()
    existing = collection.get(ids=["policy1"])
    if not existing['ids']:
        collection.add(documents=[text], ids=["policy1"])
        print("Initial policy.txt loaded into persistent brain.")
except Exception as e:
    print(f"RAG load note: {e}")

# ==========================================
# SECTION 3: Search by meaning (Embeddings)
# ==========================================
def search(query):
    results = collection.query(query_texts=[query], n_results=2)
    if results['documents'] and results['documents'][0]:
        return "\n\n".join(results['documents'][0])
    return "No relevant docs found."

# ==========================================
# SECTION 4: Train / Learn
# ==========================================
def add_document(doc_text, doc_id):
    try:
        collection.add(documents=[doc_text], ids=[doc_id])
        print(f"Learned new doc: {doc_id} - SAVED TO DISK")
        return True
    except:
        try:
            collection.update(ids=[doc_id], documents=[doc_text])
            print(f"Updated: {doc_id} - SAVED TO DISK")
            return True
        except Exception as e:
            print(f"Failed: {e}")
            return False

def list_documents():
    data = collection.get()
    return data['ids']

# ==========================================
# SECTION 6: Chunking (NEW - Phase 8A)
# Splits large text into small pieces before embedding
# Why? Embedding model can't handle 50 pages at once
# ==========================================
def add_document_chunks(doc_text, doc_id, chunk_size=500):
    """
    Splits doc_text into chunks of 500 chars and embeds each chunk
    doc_id = "manual.pdf" -> creates ids like "manual.pdf_chunk_0", "manual.pdf_chunk_1"
    """
    chunks = []
    for i in range(0, len(doc_text), chunk_size):
        chunk = doc_text[i:i+chunk_size]
        if len(chunk.strip()) > 20: # skip tiny empty chunks
            chunks.append(chunk)

    print(f"Splitting {doc_id} into {len(chunks)} chunks")

    # Add each chunk as separate doc with unique ID
    for idx, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_chunk_{idx}"
        try:
            collection.add(documents=[chunk], ids=[chunk_id])
        except:
            collection.update(ids=[chunk_id], documents=[chunk])

    return len(chunks)    