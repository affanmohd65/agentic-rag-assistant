"""
Hybrid search combining BM25 (keyword) + Vector (semantic) + Reranking.
Modern RAG approach for better retrieval quality.
"""
import os
import re
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import chromadb
from sentence_transformers import CrossEncoder
import hashlib
from loguru import logger

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", ".chroma")
VECTOR_DIM = 384


class HashingEmbeddingFunction(chromadb.EmbeddingFunction):
    """Lightweight embedding: bag-of-words hashing (dependency-free)."""

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


class HybridSearchEngine:
    """
    Hybrid search combining:
    1. BM25 (keyword-based ranking)
    2. Vector search (semantic similarity)
    3. Reranking (cross-encoder ranking)
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = self.client.get_or_create_collection(
            name="docs",
            embedding_function=HashingEmbeddingFunction()
        )
        self.bm25_index = None
        self.reranker = None
        self._load_reranker()
        self._build_bm25_index()

    def _load_reranker(self):
        """Load reranker model (small, fast)."""
        try:
            # Use a small, fast reranker model
            self.reranker = CrossEncoder('cross-encoder/mxbai-rerank-xsmall-v1')
            logger.info("Reranker loaded: mxbai-rerank-xsmall-v1")
        except Exception as e:
            logger.warning(f"Reranker not available: {e}. Using vector search only.")
            self.reranker = None

    def _build_bm25_index(self):
        """Build BM25 index from all documents in collection."""
        try:
            results = self.collection.get()
            if results['documents']:
                # Tokenize documents for BM25
                tokenized = [doc.lower().split() for doc in results['documents']]
                self.bm25_index = BM25Okapi(tokenized)
                self.bm25_docs = results['documents']
                self.bm25_ids = results['ids']
                logger.info(f"BM25 index built with {len(tokenized)} documents")
        except Exception as e:
            logger.warning(f"BM25 indexing failed: {e}")
            self.bm25_index = None

    def bm25_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search using BM25 (keyword-based)."""
        if not self.bm25_index:
            return []

        try:
            query_tokens = query.lower().split()
            scores = self.bm25_index.get_scores(query_tokens)
            
            # Get top-k indices
            top_indices = sorted(
                range(len(scores)),
                key=lambda i: scores[i],
                reverse=True
            )[:top_k]
            
            results = []
            for idx in top_indices:
                if scores[idx] > 0:  # Only include if score > 0
                    results.append({
                        "id": self.bm25_ids[idx],
                        "text": self.bm25_docs[idx],
                        "score": scores[idx],
                        "method": "bm25"
                    })
            return results
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []

    def vector_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search using vector similarity (semantic)."""
        try:
            if self.collection.count() == 0:
                return []
            
            results = self.collection.query(
                query_texts=[query],
                n_results=min(top_k, self.collection.count())
            )
            
            documents = results.get("documents", [[]])[0]
            ids = results.get("ids", [[]])[0]
            distances = results.get("distances", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            
            # Convert distances to similarity scores (0-1)
            search_results = []
            for doc, doc_id, distance, metadata in zip(documents, ids, distances, metadatas):
                similarity = 1 / (1 + distance)  # Convert distance to similarity
                search_results.append({
                    "id": doc_id,
                    "text": doc,
                    "score": similarity,
                    "method": "vector",
                    "metadata": metadata
                })
            return search_results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    def rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rerank results using cross-encoder."""
        if not self.reranker or not results:
            return results

        try:
            # Prepare pairs for reranking
            pairs = [[query, result["text"]] for result in results]
            
            # Get reranking scores
            scores = self.reranker.predict(pairs)
            
            # Attach scores and sort
            for result, score in zip(results, scores):
                result["rerank_score"] = float(score)
            
            # Sort by rerank score
            results.sort(key=lambda x: x.get("rerank_score", x["score"]), reverse=True)
            return results
        except Exception as e:
            logger.warning(f"Reranking failed: {e}. Using original order.")
            return results

    def hybrid_search(self, query: str, top_k: int = 3, use_reranking: bool = True) -> List[Dict]:
        """
        Hybrid search:
        1. BM25 + Vector search in parallel
        2. Combine and deduplicate results
        3. Rerank using cross-encoder
        """
        # Execute both searches
        bm25_results = self.bm25_search(query, top_k=top_k * 2)
        vector_results = self.vector_search(query, top_k=top_k * 2)
        
        # Combine and deduplicate by ID
        seen_ids = set()
        combined = []
        
        # Add BM25 results first (keyword matches are often more direct)
        for result in bm25_results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                combined.append(result)
        
        # Add vector results
        for result in vector_results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                combined.append(result)
        
        # Limit to top_k before reranking
        combined = combined[:top_k * 2]
        
        # Rerank if available
        if use_reranking and self.reranker:
            combined = self.rerank_results(query, combined)
        
        # Return top_k
        return combined[:top_k]

    def ingest_document(self, text: str, doc_id: str, metadata: Dict = None) -> int:
        """Ingest a single document."""
        try:
            chunks = self._chunk_text(text)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}-{i}"
                self.collection.add(
                    documents=[chunk],
                    ids=[chunk_id],
                    metadatas=[{"source": doc_id, "chunk": i, **(metadata or {})}]
                )
            
            # Rebuild BM25 index
            self._build_bm25_index()
            logger.info(f"Ingested document {doc_id} with {len(chunks)} chunks")
            return len(chunks)
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            return 0

    def _chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunks.append(" ".join(words[start:end]))
            start += chunk_size - overlap
        return chunks if chunks else [text]


# Global instance
search_engine = None


def get_search_engine() -> HybridSearchEngine:
    """Get or initialize the hybrid search engine."""
    global search_engine
    if search_engine is None:
        search_engine = HybridSearchEngine()
    return search_engine
