"""
Stretch Feature: Hybrid Search (Semantic + BM25)
Combines ChromaDB cosine similarity with BM25 keyword ranking via Reciprocal Rank Fusion.
"""

import json
import re
import os
from rank_bm25 import BM25Okapi


class HybridSearcher:
    def __init__(self, chunks_path="chunks.json", chroma_collection=None):
        """
        Initialize hybrid searcher.
        - chunks_path: path to chunks.json
        - chroma_collection: existing ChromaDB collection for semantic search
        """
        with open(chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        self.chroma_collection = chroma_collection
        self.chunk_map = {f"{c['filename'].replace(' ', '_')}_{c['chunk_index']}": c for c in self.chunks}

        # Build BM25 index
        self.tokenized_corpus = [self._tokenize(c["text"]) for c in self.chunks]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        print(f"BM25 index built with {len(self.chunks)} documents.")

    @staticmethod
    def _tokenize(text: str) -> list:
        """Simple tokenization: lowercase, strip punctuation, split on whitespace."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return text.split()

    def bm25_search(self, query: str, top_k: int = 10) -> list:
        """Return top-k chunks ranked by BM25."""
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            results.append({
                "id": f"{chunk['filename'].replace(' ', '_')}_{chunk['chunk_index']}",
                "text": chunk["text"],
                "source": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "bm25_score": float(scores[idx])
            })
        return results

    def semantic_search(self, query: str, model, top_k: int = 10) -> list:
        """Return top-k chunks ranked by ChromaDB semantic search."""
        query_embedding = model.encode([query]).tolist()
        results = self.chroma_collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        semantic_results = []
        for i in range(top_k):
            source = results["metadatas"][0][i]["source"]
            chunk_index = results["metadatas"][0][i]["chunk_index"]
            doc_id = f"{source.replace(' ', '_')}_{chunk_index}"
            semantic_results.append({
                "id": doc_id,
                "text": results["documents"][0][i],
                "source": source,
                "chunk_index": chunk_index,
                "distance": results["distances"][0][i]
            })
        return semantic_results

    def hybrid_search(self, query: str, model, top_k: int = 5, rrf_k: int = 60) -> list:
        """
        Fuse semantic and BM25 results using Reciprocal Rank Fusion (RRF).
        score = sum(1 / (rrf_k + rank)) across all result lists.
        """
        semantic_results = self.semantic_search(query, model, top_k=top_k * 2)
        bm25_results = self.bm25_search(query, top_k=top_k * 2)

        # Build RRF scores
        rrf_scores = {}
        doc_info = {}

        # Semantic ranks (lower distance = better = rank 1)
        for rank, doc in enumerate(semantic_results, start=1):
            doc_id = doc["id"]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (rrf_k + rank)
            doc_info[doc_id] = doc

        # BM25 ranks (higher score = better = rank 1)
        for rank, doc in enumerate(bm25_results, start=1):
            doc_id = doc["id"]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (rrf_k + rank)
            if doc_id not in doc_info:
                doc_info[doc_id] = doc

        # Sort by RRF score descending
        sorted_ids = sorted(rrf_scores.keys(), key=lambda did: rrf_scores[did], reverse=True)

        final_results = []
        for doc_id in sorted_ids[:top_k]:
            info = doc_info[doc_id]
            final_results.append({
                "text": info["text"],
                "source": info["source"],
                "chunk_index": info["chunk_index"],
                "rrf_score": rrf_scores[doc_id]
            })

        return final_results
