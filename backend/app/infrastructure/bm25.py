import re
from loguru import logger

from app.schemas.source import SourceDocument

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


class BM25Searcher:
    def __init__(self):
        self.documents: list[SourceDocument] = []
        self.bm25 = None
        self.corpus_tokens: list[list[str]] = []

    def index_documents(self, docs: list[SourceDocument]):
        if not docs:
            return
        self.documents = list(docs)
        self.corpus_tokens = [tokenize(doc.content) for doc in docs]
        if BM25Okapi:
            try:
                self.bm25 = BM25Okapi(self.corpus_tokens)
                logger.info(f"Indexed {len(docs)} documents into BM25 engine")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Failed to initialize BM25Okapi: {e}")
                self.bm25 = None
        else:
            logger.warning("rank_bm25 not installed, falling back to simple keyword matcher")

    def search(self, query: str, top_k: int = 5) -> list[tuple[SourceDocument, float]]:
        if not self.documents:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        if self.bm25 and BM25Okapi:
            scores = self.bm25.get_scores(query_tokens)
            # In small corpora (e.g. N <= 2), BM25 IDF can mathematically evaluate to 0.0.
            # Blend with term frequency to ensure non-zero relevance scores for exact matches.
            max_score = max(scores, default=0.0)
            if max_score <= 0.0:
                scored_docs = []
                for doc, tokens in zip(self.documents, self.corpus_tokens):
                    tf_score = sum(1.0 for q in query_tokens if q in tokens)
                    scored_docs.append((doc, float(tf_score)))
                scored_docs.sort(key=lambda x: x[1], reverse=True)
                return scored_docs[:top_k]

            scored_docs = list(zip(self.documents, [float(s) for s in scores]))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return scored_docs[:top_k]
        else:
            # Simple keyword frequency fallback search
            scored_docs = []
            for doc, tokens in zip(self.documents, self.corpus_tokens):
                score = sum(1.0 for q in query_tokens if q in tokens)
                scored_docs.append((doc, float(score)))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return scored_docs[:top_k]
