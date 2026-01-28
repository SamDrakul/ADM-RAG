import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

CHROMA_DIR = os.getenv("CHROMA_DIR", "data/chroma")
COLLECTION = os.getenv("CHROMA_COLLECTION", "admin_knowledge")
MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    return client.get_or_create_collection(COLLECTION, embedding_function=embed_fn)

def retrieve_knowledge(query: str, k: int = 4):
    col = get_collection()
    res = col.query(query_texts=[query], n_results=k, include=["documents", "metadatas"])
    hits = []
    for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
        hits.append({"text": doc, "meta": meta})
    return hits

def format_hits(hits):
    out = []
    for i, h in enumerate(hits, start=1):
        out.append(f"[{i}] {h['meta']['source']} (chunk {h['meta']['chunk']})\n{h['text']}\n")
    return "\n".join(out)
