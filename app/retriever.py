"""
Chunking + embedding + vector retrieval, using Chroma (local, free, no API key).
Mirrors the ingestion -> chunking -> embeddings -> vector search pattern used
in the Clinical Decision Support project, but fully open-source/local here.
"""
import hashlib
import os
import re
try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

import chromadb

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", ".chroma")
VECTOR_DIM = 256


class HashingEmbeddingFunction(chromadb.EmbeddingFunction):
    """
    Lightweight, dependency-free embedding function: hashes each word into
    one of VECTOR_DIM buckets (the "hashing trick"), giving a bag-of-words
    vector with no model download and no torch/onnx dependency. Good
    enough to demo retrieval end-to-end offline.

    Swap this for OpenAI/Cohere embeddings or sentence-transformers in a
    real deployment for much better semantic retrieval quality — the
    reason to call that out explicitly in an interview is that it shows
    you made a deliberate tradeoff (portability/zero-cost demo vs.
    retrieval quality), not that you didn't know better options exist.
    """

    def name(self) -> str:
        return "hashing-bow-v1"

    def __call__(self, input: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in input]

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * VECTOR_DIM
        words = re.findall(r"[a-z0-9]+", text.lower())
        for w in words:
            idx = int(hashlib.md5(w.encode()).hexdigest(), 16) % VECTOR_DIM
            vec[idx] += 1.0
        norm = sum(v * v for v in vec) ** 0.5
        return [v / norm for v in vec] if norm > 0 else vec


def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(name="docs", embedding_function=HashingEmbeddingFunction())


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def ingest_file(file_path: str) -> int:
    """Ingest a single document file. Supports .txt and .pdf files."""
    collection = _get_collection()
    count = 0
    
    if not os.path.isfile(file_path):
        return 0
    
    fname = os.path.basename(file_path)
    text = None
    
    # Handle text files
    if fname.endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            return 0
    
    # Handle PDF files
    elif fname.endswith(".pdf") and HAS_PDF:
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception:
            return 0
    
    if text and text.strip():
        for i, chunk in enumerate(chunk_text(text)):
            collection.add(
                documents=[chunk],
                ids=[f"{fname}-{i}"],
                metadatas=[{"source": fname, "chunk": i}],
            )
            count += 1
    
    return count


def ingest_directory(directory: str) -> int:
    """Ingest documents from a directory. Supports .txt and .pdf files."""
    collection = _get_collection()
    count = 0
    
    if not os.path.isdir(directory):
        return 0
    
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if not os.path.isfile(fpath):
            continue
            
        text = None
        
        # Handle text files
        if fname.endswith(".txt"):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception:
                continue
        
        # Handle PDF files
        elif fname.endswith(".pdf") and HAS_PDF:
            try:
                with open(fpath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except Exception:
                continue
        
        if text and text.strip():
            for i, chunk in enumerate(chunk_text(text)):
                collection.add(
                    documents=[chunk],
                    ids=[f"{fname}-{i}"],
                    metadatas=[{"source": fname, "chunk": i}],
                )
                count += 1
    
    return count


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    results = collection.query(query_texts=[query], n_results=min(top_k, collection.count()))
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    return [{"text": d, "source": m.get("source")} for d, m in zip(docs, metas)]
