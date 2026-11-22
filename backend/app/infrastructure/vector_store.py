import os
from typing import Any

from loguru import logger

from app.core.config import settings
from app.infrastructure.bm25 import BM25Searcher
from app.schemas.source import SourceDocument

try:
    import chromadb
except ImportError:
    chromadb = None


class VectorStoreService:
    def __init__(self, collection_name: str = "researchmind_docs"):
        self.collection_name = collection_name
        self.bm25_searcher = BM25Searcher()
        self.in_memory_docs: list[SourceDocument] = []
        self.client = None
        self.collection = None

        if chromadb:
            try:
                os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
                self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
                self.collection = self.client.get_or_create_collection(name=self.collection_name)
                logger.info(f"Initialized ChromaDB persistent client at: {settings.CHROMA_PERSIST_DIR}")
                self._hydrate_from_chroma()
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Failed to initialize ChromaDB persistent client: {e}. Falling back to memory vector store.")
                self.client = None

    def _hydrate_from_chroma(self):
        """Restores persisted documents from ChromaDB into the in-memory registry and BM25 index."""
        if not self.collection:
            return

        try:
            data = self.collection.get()
            if data and data.get("ids"):
                ids = data["ids"]
                docs = data.get("documents", [])
                metadatas = data.get("metadatas", [])
                loaded_docs = []
                for doc_id, content, meta in zip(ids, docs, metadatas):
                    meta = meta or {}
                    loaded_docs.append(
                        SourceDocument(
                            id=doc_id,
                            title=meta.get("title", doc_id),
                            content=content or "",
                            source_type=meta.get("source_type", "user_doc"),
                            url=meta.get("url", ""),
                            author=meta.get("author", ""),
                            metadata=meta
                        )
                    )
                self.in_memory_docs = loaded_docs
                self.bm25_searcher.index_documents(self.in_memory_docs)
                logger.info(f"Hydrated {len(loaded_docs)} documents from persistent ChromaDB collection.")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Could not hydrate vector store from ChromaDB: {e}")

    def add_documents(self, documents: list[SourceDocument]):
        """Adds documents to both in-memory BM25 index and persistent ChromaDB collection."""
        if not documents:
            return

        # Deduplicate against current in-memory documents
        existing_ids = {doc.id for doc in self.in_memory_docs}
        new_docs = [doc for doc in documents if doc.id not in existing_ids]

        if not new_docs:
            logger.info("All provided documents already exist in the vector store.")
            return

        self.in_memory_docs.extend(new_docs)
        self.bm25_searcher.index_documents(self.in_memory_docs)

        if self.collection:
            try:
                ids = [doc.id for doc in new_docs]
                contents = [doc.content for doc in new_docs]
                metadatas = [
                    {
                        "title": doc.title,
                        "file_name": doc.metadata.get("file_name", doc.title),
                        "source_type": doc.source_type,
                        "url": doc.url or "",
                        "author": doc.author or "",
                    }
                    for doc in new_docs
                ]
                batch_size = 5
                for i in range(0, len(ids), batch_size):
                    b_ids = ids[i : i + batch_size]
                    b_contents = contents[i : i + batch_size]
                    b_metas = metadatas[i : i + batch_size]
                    self.collection.add(ids=b_ids, documents=b_contents, metadatas=b_metas)
                    import gc
                    gc.collect()
                logger.info(f"Successfully committed {len(new_docs)} documents to ChromaDB collection.")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"ChromaDB batch embedding warning: {e}. Documents remain indexed in BM25 lexical store.")

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        source_type_filter: str | None = None,
        alpha: float = 0.5
    ) -> list[SourceDocument]:
        """
        Hybrid search combining Dense vector similarity (ChromaDB) and BM25 Lexical search.
        alpha=1.0 uses purely vector search, alpha=0.0 uses purely BM25.
        """
        if not self.in_memory_docs and not self.collection:
            return []

        bm25_results = self.bm25_searcher.search(query, top_k=top_k * 2)

        # Dense / ChromaDB results
        chroma_docs: dict[str, float] = {}
        chroma_raw_map: dict[str, SourceDocument] = {}

        if self.collection:
            try:
                where_clause = {"source_type": source_type_filter} if source_type_filter else None
                count = self.collection.count()
                if count > 0:
                    query_res = self.collection.query(
                        query_texts=[query],
                        n_results=min(top_k * 2, count),
                        where=where_clause
                    )
                    if query_res and query_res.get("ids") and query_res["ids"]:
                        matched_ids = query_res["ids"][0]
                        matched_docs = query_res.get("documents", [[]])[0] if query_res.get("documents") else []
                        matched_metas = query_res.get("metadatas", [[]])[0] if query_res.get("metadatas") else []
                        distances = query_res["distances"][0] if query_res.get("distances") else [0.5] * len(matched_ids)

                        for idx, (doc_id, dist) in enumerate(zip(matched_ids, distances)):
                            chroma_docs[doc_id] = max(0.0, 1.0 - float(dist))
                            # Reconstruct document if not in in_memory_docs
                            meta = matched_metas[idx] if idx < len(matched_metas) and matched_metas[idx] else {}
                            content = matched_docs[idx] if idx < len(matched_docs) else ""
                            chroma_raw_map[doc_id] = SourceDocument(
                                id=doc_id,
                                title=meta.get("title", doc_id),
                                content=content,
                                source_type=meta.get("source_type", "user_doc"),
                                url=meta.get("url", ""),
                                author=meta.get("author", ""),
                                metadata=meta
                            )
            except Exception as e:  # noqa: BLE001
                logger.warning(f"ChromaDB search query failed: {e}")

        # Combine scores using Reciprocal Rank Fusion / Weighted Sum
        combined_scores: dict[str, float] = {}
        doc_map: dict[str, SourceDocument] = {doc.id: doc for doc in self.in_memory_docs}
        doc_map.update(chroma_raw_map)

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

    def list_documents(self) -> list[dict[str, Any]]:
        """Returns summarized metadata for all unique user documents indexed in the vector store."""
        docs_summary: dict[str, dict[str, Any]] = {}
        for doc in self.in_memory_docs:
            if doc.source_type != "user_doc":
                continue
            name = doc.metadata.get("file_name")
            if not name:
                name = doc.title.split(" (Part ")[0] if " (Part " in doc.title else doc.title
            if name not in docs_summary:
                ext = os.path.splitext(name)[1].lstrip(".").upper() or "DOC"
                docs_summary[name] = {
                    "name": name,
                    "type": ext,
                    "sections": 0,
                    "source_type": doc.source_type,
                    "date": "Indexed in Vector DB"
                }
            docs_summary[name]["sections"] += 1
        return list(docs_summary.values())

    def delete_document(self, filename: str) -> int:
        """Deletes all chunks associated with a specific filename from ChromaDB and in-memory indexes."""
        matched_ids = [
            doc.id for doc in self.in_memory_docs
            if doc.metadata.get("file_name") == filename
            or doc.title.startswith(filename)
            or doc.id.startswith(f"{filename}_chunk_")
        ]
        if not matched_ids:
            return 0

        if self.collection:
            try:
                batch_size = 100
                for i in range(0, len(matched_ids), batch_size):
                    self.collection.delete(ids=matched_ids[i:i + batch_size])
                logger.info(f"Deleted {len(matched_ids)} chunks for '{filename}' from ChromaDB.")
            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to delete chunks for '{filename}' from ChromaDB: {e}")

        matched_set = set(matched_ids)
        self.in_memory_docs = [doc for doc in self.in_memory_docs if doc.id not in matched_set]
        self.bm25_searcher.index_documents(self.in_memory_docs)
        return len(matched_ids)

    def health_check(self) -> dict[str, Any]:
        """Returns health telemetry for vector database and lexical index."""
        chroma_ok = False
        persisted_count = 0
        if self.collection:
            try:
                persisted_count = self.collection.count()
                chroma_ok = True
            except Exception:  # noqa: BLE001
                chroma_ok = False

        status = "healthy" if chroma_ok or len(self.in_memory_docs) > 0 else "ready"
        return {
            "status": status,
            "chroma_connected": chroma_ok,
            "persisted_documents_count": persisted_count,
            "in_memory_bm25_documents": len(self.in_memory_docs)
        }
