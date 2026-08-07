# ResearchMind AI: An Autonomous Multi-Agent AI Research Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-purple.svg)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production-emerald.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14_App_Router-black.svg)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**ResearchMind AI** is an enterprise-grade autonomous AI research platform designed to execute end-to-end scientific and engineering research workflows. Instead of acting as a standard conversational chatbot, ResearchMind AI operates like a team of specialized AI research scientists.

---

## 🌟 Key Highlights & Engineering Features

- **Advanced LangGraph Workflows**: Orchestrates 13 independent specialized sub-agents with parallel fan-out execution, state machine graph compilation, and conditional critique refinement loops.
- **Parallel Multi-Source Retrieval**: Integrates **arXiv API**, **Semantic Scholar API**, **Tavily Web Search**, **GitHub REST API**, and local user document vector search.
- **Hybrid Dense + Lexical RAG**: Combines vector embeddings (**ChromaDB / Qdrant**) with **BM25 keyword search** and Reciprocal Rank Fusion.
- **Multi-Format Document Ingestion**: Ingests **PDF, DOCX, TXT, MD, CSV, HTML, PPTX** with boundary-aware paragraph text chunking.
- **Method Matrix & Research Gap Analysis**: Automatically constructs comparative matrices across competing techniques, identifies open research gaps, and designs step-by-step empirical A/B experiments.
- **Publication-Quality Long-Form Reports**: Generates structured Markdown research papers with executive summaries, problem statements, key findings, and verifiable citations.
- **RAGAS Evaluation & Telemetry Benchmark**: Computes quantitative **Faithfulness**, **Relevance**, **Grounding**, and **Confidence** scores on every research run.
- **Modern Next.js 14 Dashboard**: Real-time multi-agent execution timeline, live node stream, knowledge base manager, metrics telemetry dashboard, and interactive architecture visualization.

---

## 🏗️ Multi-Agent Architecture

```mermaid
graph TD
    Start([Start Research Objective]) --> Planner[Planner Agent]
    Planner --> FanOut{Parallel Fan-Out Retrieval}
    FanOut --> PaperAgent[Paper Agent: arXiv & Semantic Scholar]
    FanOut --> WebAgent[Web Agent: Tavily API]
    FanOut --> GitHubAgent[GitHub Agent: Repository Search]
    FanOut --> DocAgent[Vector Retrieval Agent: Hybrid ChromaDB + BM25]
    
    PaperAgent --> Synthesizer[Knowledge Synthesizer Agent]
    WebAgent --> Synthesizer
    GitHubAgent --> Synthesizer
    DocAgent --> Synthesizer
    
    Synthesizer --> CompAgent[Comparison Agent]
    CompAgent --> GapAgent[Research Gap Analyzer]
    GapAgent --> ExpAgent[Experiment Planner]
    ExpAgent --> WriterAgent[Writer Agent]
    WriterAgent --> CriticAgent[Critic Agent]
    CriticAgent --> CitationAgent[Citation Verification Agent]
    CitationAgent --> EvalAgent[Evaluation Agent]
    
    EvalAgent --> QualityCheck{Confidence >= 75% & Approved?}
    QualityCheck -- No --> Refine[Report Refinement Loop]
    Refine --> WriterAgent
    QualityCheck -- Yes --> End([Publication-Ready Research Output])
```

---

## 💻 Tech Stack

- **Core & Orchestration**: Python 3.12, LangGraph, LangChain Core, Pydantic v2
- **Backend API**: FastAPI, Uvicorn, Pydantic Settings, Loguru, Rich
- **Retrieval & Vector Search**: ChromaDB / Qdrant, Rank-BM25, PyPDF, Python-Docx, Python-PPTX
- **APIs & Models**: OpenAI (GPT-4o/4.1), Groq (Llama 3.3 70B), Google Gemini, Tavily API, arXiv API, Semantic Scholar API, GitHub REST API
- **Frontend App**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons, Framer Motion, React Markdown
- **DevOps & Testing**: Docker, Docker Compose, Pytest, Pytest-Asyncio, Ruff, Black, Mypy, GitHub Actions

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.12+
- Node.js v18+ & npm
- Git

### 1. Clone & Set Up Backend

```bash
cd backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

### 2. Run Backend Server & Test Suite

```bash
# Run automated pytest suite
pytest

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

FastAPI Swagger API docs will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Set Up & Launch Frontend

```bash
cd ../frontend
npm install
npm run dev
```

The Next.js research workspace will be available at [http://localhost:3000](http://localhost:3000).

---

## 🐳 Docker Deployment

To spin up the full production stack including Qdrant, Redis, FastAPI Backend, and Next.js Frontend:

```bash
docker-compose up --build -d
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
