from app.infrastructure.bm25 import BM25Searcher
from app.infrastructure.vector_store import VectorStoreService
from app.schemas.source import SourceDocument


def test_bm25_searcher():
    searcher = BM25Searcher()
    docs = [
        SourceDocument(
            id="d1",
            title="Transformer Scaling Laws",
            content="Empirical analysis of compute-optimal language model training and parameters scaling.",
            source_type="user_doc"
        ),
        SourceDocument(
            id="d2",
            title="Photosynthesis in Plants",
            content="Biological solar energy conversion mechanics in chloroplast cells.",
            source_type="user_doc"
        )
    ]

    searcher.index_documents(docs)
    results = searcher.search(query="language model scaling", top_k=2)

    assert len(results) > 0
    top_doc, score = results[0]
    assert top_doc.id == "d1"
    assert score > 0.0


def test_vector_store_hybrid_search_and_health():
    vstore = VectorStoreService(collection_name="test_temp_collection")
    docs = [
        SourceDocument(
            id="vs1",
            title="FastAPI Microservices",
            content="Building asynchronous high-throughput REST APIs using Python and FastAPI framework.",
            source_type="user_doc"
        ),
        SourceDocument(
            id="vs2",
            title="Deep RL for Robotics",
            content="Proximal policy optimization for multi-joint robotic arm manipulation in physics simulators.",
            source_type="user_doc"
        )
    ]

    vstore.add_documents(docs)

    # Health check
    health = vstore.health_check()
    assert health["status"] in ["healthy", "ready"]
    assert health["in_memory_bm25_documents"] >= 2

    # Hybrid Search
    res = vstore.hybrid_search(query="FastAPI REST APIs", top_k=2, alpha=0.5)
    assert len(res) > 0
    assert res[0].id == "vs1"
    assert res[0].score > 0.0


import uuid

def test_vector_store_deduplication():
    vstore = VectorStoreService(collection_name="test_dedup_collection")
    unique_id = f"unique_doc_{uuid.uuid4().hex[:6]}"
    doc = SourceDocument(
        id=unique_id,
        title="Deduplication Test",
        content="Testing duplicate document prevention in vector store registry.",
        source_type="user_doc"
    )

    initial_count = len(vstore.in_memory_docs)
    vstore.add_documents([doc])
    assert len(vstore.in_memory_docs) == initial_count + 1

    # Adding the identical doc again should not duplicate
    vstore.add_documents([doc])
    assert len(vstore.in_memory_docs) == initial_count + 1
