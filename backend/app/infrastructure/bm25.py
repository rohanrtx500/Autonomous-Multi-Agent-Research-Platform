import re
from typing import List, Tuple
from loguru import logger
from app.schemas.source import SourceDocument

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None


def tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


class BM25Searcher:
    def __init__(self):
        self.documents: List[SourceDocument] = []
        self.bm25: bool = None
        self.corpus_tokens: List[List[str]] = []

    def index_documents(self, docs: List[SourceDocument]):
        if not docs:
            return
        self.documents = docs
        self.corpus_tokens = [tokenize(doc.content) for doc in docs]
        if BM25Okapi:
            self.bm25 = BM25Okapi(self.corpus_tokens)
            logger.info(f"Indexed {len(docs)} documents into BM25 engine")
        else:
            logger.warning("rank_bm25 not installed, falling back to simple keyword matcher")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[SourceDocument, float]]:
        if not self.documents:
            return []

        query_tokens = tokenize(query)
        if self.bm25 and BM25Okapi:
            scores = self.bm25.get_scores(query_tokens)
            scored_docs = list(zip(self.documents, [float(s) for s in scores]))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return scored_docs[:top_k]
        else:
            # Simple keyword frequency fallback search
            scored_docs = []
            for doc, tokens in zip(self.documents, self.corpus_tokens):
                score = sum(1.0 for q in query_tokens if q in tokens)
                scored_docs.append((doc, score))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return scored_docs[:top_k]
