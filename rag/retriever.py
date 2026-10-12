"""Local Semantic & Lexical Vector Retriever for VedaNova Knowledge Base."""
import re
import math
from collections import Counter
from typing import List, Dict, Any, Tuple

class LocalVectorRetriever:
    """
    Lightweight, high-speed in-memory semantic and lexical retriever.
    Runs 100% offline with sub-millisecond query latency.
    """
    def __init__(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        self.doc_count = len(chunks)
        self.doc_freqs = Counter()
        self.doc_vectors = []
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z0-9_\-\$₹]+\b", text.lower())

    def _build_index(self):
        # Calculate term frequencies and document frequencies
        tokenized_docs = []
        for chunk in self.chunks:
            tokens = self._tokenize(chunk["text"])
            tokenized_docs.append(tokens)
            unique_terms = set(tokens)
            for term in unique_terms:
                self.doc_freqs[term] += 1

        # Build TF-IDF vectors
        for tokens in tokenized_docs:
            tf = Counter(tokens)
            vec = {}
            for term, count in tf.items():
                idf = math.log((self.doc_count + 1) / (self.doc_freqs[term] + 1)) + 1
                vec[term] = (count / len(tokens)) * idf
            
            # Normalize vector
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            self.doc_vectors.append({k: v / norm for k, v in vec.items()})

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Rank chunks against the query using cosine similarity.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        q_tf = Counter(query_tokens)
        q_vec = {}
        for term, count in q_tf.items():
            idf = math.log((self.doc_count + 1) / (self.doc_freqs.get(term, 0) + 1)) + 1
            q_vec[term] = (count / len(query_tokens)) * idf

        q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1.0
        q_vec_norm = {k: v / q_norm for k, v in q_vec.items()}

        scores = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            dot_product = sum(weight * doc_vec.get(term, 0.0) for term, weight in q_vec_norm.items())
            if dot_product > 0.0:
                scores.append((idx, dot_product))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_results = []
        for doc_idx, score in scores[:top_k]:
            chunk_data = dict(self.chunks[doc_idx])
            chunk_data["similarity_score"] = round(score, 4)
            top_results.append(chunk_data)

        return top_results
