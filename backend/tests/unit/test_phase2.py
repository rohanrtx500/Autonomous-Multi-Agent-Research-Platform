import os
import pytest
from app.infrastructure.document_loader import DocumentLoaderService
from app.infrastructure.bm25 import BM25Searcher
from app.infrastructure.vector_store import VectorStoreService
from app.schemas.source import SourceDocument


def test_document_loader_chunking(tmp_path):
    file_path = tmp_path / "sample.txt"
    content = "Paragraph 1: Introduction to AI Agents.\n\nParagraph 2: Long-form reasoning in LangGraph.\n\nParagraph 3: Autonomous RAG pipeline architecture."
    file_path.write_text(content, encoding="utf-8")

    loader = DocumentLoaderService(chunk_size=100, chunk_overlap=20)
    docs = loader.load_file(str(file_path))

    assert len(docs) > 0
    assert docs[0].source_type == "user_doc"
    assert "Paragraph 1" in docs[0].content


def test_bm25_searcher():
    doc1 = SourceDocument(
        id="d1", title="Doc 1", content="Transformer models and attention mechanism in neural networks.", source_type="user_doc"
    )
    doc2 = SourceDocument(
        id="d2", title="Doc 2", content="Convolutional neural networks for image classification tasks.", source_type="user_doc"
    )
    searcher = BM25Searcher()
    searcher.index_documents([doc1, doc2])

    results = searcher.search("attention mechanism transformer", top_k=1)
    assert len(results) == 1
    assert results[0][0].id == "d1"


def test_vector_store_hybrid_search():
    store = VectorStoreService(collection_name="test_collection")
    doc1 = SourceDocument(
        id="d1", title="Doc 1", content="LangGraph multi-agent execution framework with state graph.", source_type="user_doc"
    )
    doc2 = SourceDocument(
        id="d2", title="Doc 2", content="FastAPI backend web services for REST APIs.", source_type="user_doc"
    )
    store.add_documents([doc1, doc2])

    results = store.hybrid_search("LangGraph state graph multi-agent", top_k=1)
    assert len(results) == 1
    assert results[0].id == "d1"
