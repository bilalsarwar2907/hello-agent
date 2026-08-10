from vector_db import add_document
import os

def handle_upload(file_path):
    text = open(file_path, encoding="utf-8", errors="ignore").read()
    doc_id = os.path.basename(file_path)
    n = add_document(text, doc_id)
    return f"Added {doc_id}: {n} chunks"