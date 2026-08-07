# Architecture & System Design Guide - ResearchMind AI

This document details the architectural principles, state graph specifications, retrieval engine design, and evaluation benchmarks underlying **ResearchMind AI**.

---

## 1. Multi-Agent System Design

ResearchMind AI decomposes research into 13 autonomous, specialized agents operating within a compiled **LangGraph `StateGraph`**:

| Agent Name | Primary Responsibility | Input State Keys | Output State Keys |
| --- | --- | --- | --- |
| **Planner Agent** | Query decomposition into sub-tasks | `objective` | `sub_tasks`, `status` |
| **Paper Retrieval Agent** | Academic paper search (arXiv + Semantic Scholar) | `objective` | `retrieved_papers` |
| **Web Research Agent** | Web & documentation search via Tavily API | `objective` | `retrieved_web_sources` |
| **GitHub Research Agent** | GitHub open-source repository & code search | `objective` | `retrieved_github_repos` |
| **Document Retrieval Agent** | Hybrid vector + BM25 search over user documents | `objective` | `retrieved_user_docs` |
| **Knowledge Synthesizer** | Multi-source evidence fusion & deduplication | All retrieved data | `synthesized_knowledge` |
| **Comparison Agent** | Structured method, metric, & dataset matrix | `synthesized_knowledge` | `method_comparisons` |
| **Research Gap Analyzer** | Open problems & research limitations analysis | `synthesized_knowledge` | `research_gaps` |
| **Experiment Planner** | Step-by-step empirical experiment design | `method_comparisons` | `experiment_plan` |
| **Writer Agent** | Publication-quality long-form markdown report generation | All state components | `draft_report`, `final_report_markdown` |
| **Critic Agent** | Fact & structural review | `draft_report` | `critic_feedback` |
| **Citation Verification Agent** | Grounding verification against source evidence | `retrieved_papers`, `draft_report` | `citation_verification` |
| **Evaluation Agent** | Faithfulness, relevance, & confidence metrics | All state components | `evaluation_metrics`, `status` |

---

## 2. Hybrid Retrieval Engine (Dense + BM25)

ResearchMind AI implements a hybrid retrieval pipeline combining:
1. **Dense Vector Embeddings** (ChromaDB / Qdrant): Captures semantic similarity.
2. **Lexical Keyword Search** (Rank-BM25): Captures exact technical code symbols and formulas.
3. **Reciprocal Rank Fusion (RRF)**: Merges dense and lexical result sets via weighted score normalization:

\[
\text{Score}(d) = \alpha \cdot \text{DenseScore}(d) + (1 - \alpha) \cdot \text{BM25Score}(d)
\]

---

## 3. Self-Critique & Refinement Loop

The system features a self-correction mechanism. If the **Evaluation Agent** detects a `confidence_score < 0.75` or the **Critic Agent** flags structural issues, the conditional edge `should_continue_or_refine` routes the state back to the **Writer Agent** with feedback for up to `max_iterations` (default: 2).

---

## 4. REST API Specifications

- `POST /api/v1/research`: Run synchronous/asynchronous multi-agent research workflow.
- `POST /api/v1/upload`: Upload PDF/DOCX/TXT files to ChromaDB + BM25 index.
- `GET /api/v1/papers`: Query retrieved paper metadata.
- `GET /api/v1/status`: Query active execution graph status.
- `GET /api/v1/metrics`: System evaluation metrics telemetry.
- `GET /api/v1/health`: Health check endpoint.
