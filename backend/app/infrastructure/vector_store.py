import os
from typing import List, Optional, Dict, Any
from loguru import logger
from app.core.config import settings
from app.schemas.source import SourceDocument
from app.infrastructure.bm25 import BM25Searcher

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except ImportError:
    chromadb = None


class VectorStoreService:
    def __init__(self, collection_name: str = "researchmind_docs"):
        self.collection_name = collection_name
        self.bm25_searcher = BM25Searcher()
        self.in_memory_docs: List[SourceDocument] = []
        self.client = None
        self.collection = None

        if chromadb:
            try:
                os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
                self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
                self.collection = self.client.get_or_create_collection(name=self.collection_name)
                logger.info(f"Initialized ChromaDB persistent client at: {settings.CHROMA_PERSIST_DIR}")
            except Exception as e:
                logger.warning(f"Failed to initialize ChromaDB persistent client: {e}. Falling back to memory vector store.")
                self.client = None

    def add_documents(self, documents: List[SourceDocument]):
        if not documents:
            return

        self.in_memory_docs.extend(documents)
        self.bm25_searcher.index_documents(self.in_memory_docs)

        if self.collection:
            try:
                ids = [doc.id for doc in documents]
                contents = [doc.content for doc in documents]
                metadatas = [
                    {
                        "title": doc.title,
                        "source_type": doc.source_type,
                        "url": doc.url or "",
                        "author": doc.author or "",
                    }
                    for doc in documents
                ]
                self.collection.add(ids=ids, documents=contents, metadatas=metadatas)
                logger.info(f"Added {len(documents)} documents to ChromaDB collection")
            except Exception as e:
                logger.error(f"Error adding documents to ChromaDB: {e}")

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        source_type_filter: Optional[str] = None,
        alpha: float = 0.5
    ) -> List[SourceDocument]:
        """
        Hybrid search combining Dense vector similarity (ChromaDB) and BM25 Lexical search.
        alpha=1.0 uses purely vector search, alpha=0.0 uses purely BM25.
        """
        bm25_results = self.bm25_searcher.search(query, top_k=top_k * 2)
        
        # Dense / ChromaDB results
        chroma_docs: Dict[str, float] = {}
        if self.collection:
            try:
                where_clause = {"source_type": source_type_filter} if source_type_filter else None
                query_res = self.collection.query(
                    query_texts=[query],
                    n_results=min(top_k * 2, self.collection.count() or 1),
                    where=where_clause
                )
                if query_res and query_res.get("ids"):
                    matched_ids = query_res["ids"][0]
                    distances = query_res["distances"][0] if "distances" in query_res and query_res["distances"] else [0.5] * len(matched_ids)
                    for doc_id, dist in zip(matched_ids, distances):
                        # Convert distance to similarity score
                        chroma_docs[doc_id] = max(0.0, 1.0 - float(dist))
            except Exception as e:
                logger.warning(f"ChromaDB search failed: {e}")

        # Combine scores using Reciprocal Rank Fusion / Weighted Sum
        combined_scores: Dict[str, float] = {}
        doc_map: Dict[str, SourceDocument] = {doc.id: doc for doc in self.in_memory_docs}

        # BM25 scores normalized
        max_bm25 = max([score for _, score in bm25_results], default=1.0) or 1.0
        for doc, score in bm25_results:
            if source_type_filter and doc.source_type != source_type_filter:
                continue
            norm_bm25 = score / max_bm25
            combined_scores[doc.id] = (1 - alpha) * norm_bm25

        # Chroma scores
        for doc_id, dense_score in chroma_docs.items():
            current = combined_scores.get(doc_id, 0.0)
            combined_scores[doc_id] = current + (alpha * dense_score)

        # Sort and return top_k
        sorted_ids = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for doc_id, score in sorted_ids:
            if doc_id in doc_map:
                doc_obj = doc_map[doc_id].model_copy()
                doc_obj.score = round(score, 4)
                results.append(doc_obj)
        
        return results
