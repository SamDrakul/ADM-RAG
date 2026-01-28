import os, glob
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

KNOW_DIR = os.getenv("KNOW_DIR", "data/knowledge")
CHROMA_DIR = os.getenv("CHROMA_DIR", "data/chroma")
COLLECTION = os.getenv("CHROMA_COLLECTION", "admin_knowledge")
MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

def chunk_text(text: str, chunk_size=900, overlap=150):
    text = " ".join(text.split())
    out, i = [], 0
    while i < len(text):
        j = min(len(text), i + chunk_size)
        out.append(text[i:j])
        i = max(0, j - overlap)
        if j == len(text):
            break
    return out

def ingest_knowledge():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    col = client.get_or_create_collection(COLLECTION, embedding_function=embed_fn)

    files = glob.glob(os.path.join(KNOW_DIR, "**/*.txt"), recursive=True)
    ids, docs, metas = [], [], []

    for path in files:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        for k, ch in enumerate(chunk_text(text)):
            ids.append(f"{path}::chunk{k}")
            docs.append(ch)
            metas.append({"source": path, "chunk": k})

    if ids:
        col.upsert(ids=ids, documents=docs, metadatas=metas)

    return {"knowledge_sources": len(files), "knowledge_chunks": len(ids)}

if __name__ == "__main__":
    print(ingest_knowledge())
