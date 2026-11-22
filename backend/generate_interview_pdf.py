import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = r"D:\Projects-Personal\researchmind-ai\Autonomous_Research_Platform_Interview_Guide.pdf"


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (on pages after cover)
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "Autonomous Multi-Agent Research Platform - Technical Interview Master Guide")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 30, footer_text)
        self.drawString(54, 30, "CONFIDENTIAL & PROPRIETARY - INTERVIEW PREPARATION COMPENDIUM")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 42, 8.5 * 72 - 54, 42)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#0F172A")
    ACCENT = colors.HexColor("#2563EB")
    TEXT_DARK = colors.HexColor("#1E293B")
    TEXT_MUTED = colors.HexColor("#475569")
    BG_BOX = colors.HexColor("#F8FAFC")
    BORDER_BOX = colors.HexColor("#CBD5E1")
    SUCCESS = colors.HexColor("#059669")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=PRIMARY,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=ACCENT,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=ACCENT,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    q_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=PRIMARY,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    ans_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    story = []

    # -------------------------------------------------------------
    # COVER / HEADER BANNER
    # -------------------------------------------------------------
    story.append(Paragraph("Autonomous Multi-Agent Research Platform", title_style))
    story.append(Paragraph("System Architecture, Tech Stack Deep-Dive & Master Interview Preparation Compendium", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=0, spaceAfter=12))

    # Metric Highlight Bar
    stat_data = [
        [
            Paragraph("<b>13 Specialized Agents</b><br/><font color='#64748B' size='7'>LangGraph State Machine</font>", body_style),
            Paragraph("<b>Hybrid Dense + Lexical</b><br/><font color='#64748B' size='7'>ChromaDB + BM25 RRF</font>", body_style),
            Paragraph("<b>Mathematical Verification</b><br/><font color='#64748B' size='7'>Zero Fabricated Metrics</font>", body_style),
            Paragraph("<b>100% Test Pass Rate</b><br/><font color='#64748B' size='7'>32/32 Pytest Suites</font>", body_style),
        ]
    ]
    stat_table = Table(stat_data, colWidths=[125, 125, 130, 124])
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_BOX),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_BOX),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_BOX),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------
    # SECTION 1: PROJECT EXPLANATION & ARCHITECTURE
    # -------------------------------------------------------------
    story.append(Paragraph("SECTION 1: Project Explanation & System Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_BOX, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("<b>The 30-Second Elevator Pitch:</b>", h2_style))
    pitch_text = (
        "\"I engineered an Autonomous Multi-Agent Research Platform that transforms high-level research questions into "
        "publication-grade, evidence-grounded reports. Unlike standard single-pass LLM prompts or basic RAG bots that hallucinate "
        "or miss niche papers, my system coordinates 13 specialized agents across LangGraph state machines. It executes parallel "
        "retrieval across arXiv, Semantic Scholar, Tavily web search, and internal documents, fuses dense and lexical retrieval "
        "using Reciprocal Rank Fusion, performs research gap analysis, writes structured multi-section reports, and runs a mathematical "
        "claim-level citation verification engine that checks factual grounding against retrieved evidence.\""
    )
    story.append(Paragraph(pitch_text, body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>The 2-Minute Architectural Walkthrough:</b>", h2_style))
    walkthrough_steps = [
        "<b>1. Client Ingestion & Event Loop Isolation:</b> User inputs a research objective via Next.js 14. FastAPI validates input, persists a job record in SQLAlchemy (`pending`), and offloads execution to an asynchronous worker thread (`asyncio.to_thread`), preventing event-loop deadlocks.",
        "<b>2. Dynamic Decomposition:</b> The <b>Planner Agent</b> decomposes the objective into 4 parallel sub-tasks targeting Academic Papers, Web Sources, GitHub Codebases, and Internal Documents.",
        "<b>3. Parallel Retrieval Fan-Out:</b> LangGraph executes PaperRetrievalAgent (arXiv + Semantic Scholar), WebResearchAgent (Tavily API), GitHubResearchAgent, and DocRetrievalAgent (ChromaDB + BM25) simultaneously with independent failure isolation.",
        "<b>4. Synthesis & Reasoning:</b> KnowledgeSynthesizer deduplicates evidence; ComparisonAgent builds a Markdown trade-off matrix; GapAnalyzer discovers open problems with severity scores; ExperimentPlanner formulates testable empirical protocols.",
        "<b>5. Publication-Grade Synthesis:</b> WriterAgent formats a 10-section publication report with explicit in-text citations ([1], [2]); CriticAgent reviews structural completeness.",
        "<b>6. Mathematical Verification & Evaluation:</b> CitationVerificationAgent extracts factual claims, maps citation anchors to source texts, checks lexical/semantic overlap, and classifies claims as supported, partially supported, or unsupported. EvaluationAgent calculates Precision@5, Recall@5, and MRR.",
        "<b>7. Pure Conditional Quality Routing:</b> `should_continue_or_refine` checks acceptable quality standards or iteration limits, routing cleanly to END or triggering refinement."
    ]
    for step in walkthrough_steps:
        story.append(Paragraph(f"- {step}", body_style))
    story.append(Spacer(1, 8))

    # Agent Table
    story.append(Paragraph("<b>The 13 Specialized Agent Nodes:</b>", h2_style))
    agent_rows = [
        ["Agent Node", "Role & Execution Responsibility", "Key Output Artifact"],
        ["1. Planner Agent", "Deconstructs research goal into multi-stream subtasks", "4 structured sub-tasks with assigned roles"],
        ["2. Paper Retrieval", "Queries arXiv and Semantic Scholar APIs", "Academic papers with abstracts, authors, years"],
        ["3. Web Research", "Fetches live technical blogs, docs, and benchmarks", "High-signal web snippets via Tavily API"],
        ["4. GitHub Research", "Discovers open-source implementations and repos", "Top repos, star counts, and codebase links"],
        ["5. Doc Retrieval", "Executes hybrid search across uploaded PDF/Word docs", "Hybrid dense + lexical internal context chunks"],
        ["6. Synthesizer", "Normalizes and cross-references multi-source data", "Deduplicated knowledge corpus with provenance"],
        ["7. Comparator", "Analyzes architectural trade-offs across paradigms", "Structured Markdown comparison matrix"],
        ["8. Gap Analyzer", "Identifies unsolved domain bottlenecks & limitations", "Prioritized research gaps with severity ratings"],
        ["9. Exp. Planner", "Formulates empirical hypotheses and test plans", "Hypotheses, benchmarks, step-by-step roadmap"],
        ["10. Writer Agent", "Compiles comprehensive publication-grade report", "10-section report in Markdown & PDF"],
        ["11. Critic Agent", "Audits structural coherence and analytical depth", "Actionable critique feedback for refinement"],
        ["12. Citation Verifier", "Verifies factual claims against raw source sentences", "Claim statuses (supported, unsupported, etc.)"],
        ["13. Evaluator", "Calculates Precision@5, Recall@5, MRR, Faithfulness", "Mathematical IR & groundedness metrics"]
    ]
    t_agent = Table(agent_rows, colWidths=[90, 244, 170])
    t_agent.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('LEADING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BOX),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_BOX]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_agent)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # SECTION 2: TECH STACK CHEAT-SHEET
    # -------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("SECTION 2: Deep-Dive on Technologies Used", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_BOX, spaceBefore=0, spaceAfter=8))

    tech_data = [
        ("LangGraph (v0.2+)", "Stateful cyclical multi-actor orchestration framework.", 
         "Why chosen over vanilla LangChain/CrewAI: LangChain is purely linear (DAGs) and cannot handle self-reflection loops. CrewAI relies on conversational autonomy which risks non-deterministic wandering. LangGraph provides deterministic state machine control with TypedDict schemas and custom reducer functions (paper_reducer, log_reducer)."),
        
        ("FastAPI & Uvicorn", "Modern asynchronous ASGI Python web framework.",
         "High throughput, automatic OpenAPI documentation, and native Pydantic v2 validation. Critical design detail: LangGraph's synchronous graph.invoke() was offloaded to asyncio.to_thread(_execute_graph_sync) to prevent blocking the Python asyncio event loop."),

        ("ChromaDB (v0.5+)", "Embedded AI-native vector database with local persistence.",
         "Stores dense cosine embeddings under ./data/chroma. Solved critical reboot bug: Implemented _hydrate_from_chroma() during startup to re-populate the in-memory registry and BM25 index from persistent disk records."),

        ("Rank-BM25 & RRF", "Probabilistic lexical search (Okapi BM25) with Reciprocal Rank Fusion.",
         "Hybrid RAG combines dense semantic vectors (conceptual recall) with BM25 keyword matching (exact terms, numbers, acronyms). Handled small-corpus N<=2 edge cases where BM25 IDF evaluates to 0.0 by blending term frequency."),

        ("SQLAlchemy 2.0", "Enterprise-grade relational database ORM and state management.",
         "Database-agnostic persistence layer. Defaults to SQLite (data/researchmind.db) for zero-setup local execution, while connecting seamlessly to PostgreSQL in production via DATABASE_URL. Manages full job lifecycle (pending -> running -> completed/failed)."),

        ("Document Loaders", "Multi-format parser engine (pypdf, python-docx, python-pptx).",
         "Sliding-window chunker (1000 chars, 200 overlap) breaking at paragraph/sentence boundaries. Strict magic byte validation (%PDF-, PK zip containers) and elimination of silent placeholder fallbacks."),

        ("External Search APIs", "Tavily API, arXiv API, Semantic Scholar API, GitHub API.",
         "Tavily extracts high-signal, clean web text without scraping noise. arXiv provides CS/AI preprints. Semantic Scholar provides citation graphs and abstracts. Bounded 3-second timeouts with fault-tolerant fallbacks."),

        ("Next.js 14 & React 18", "Modern SaaS frontend utilizing the App Router and Tailwind CSS.",
         "Non-blocking job polling (/api/v1/jobs/{id}), interactive synthesis depth configuration, granular claim verification inspection badges, and multi-format client export (Markdown, TXT, PDF)."),

        ("Docker & Docker Compose", "Multi-stage containerization with microservice orchestration.",
         "Docker Compose provisions backend, frontend, and PostgreSQL with container health checks (curl http://localhost:8000/api/v1/health) and persistent volume bindings.")
    ]

    for tech_name, summary, details in tech_data:
        story.append(Paragraph(f"<b>{tech_name}</b> - <font color='#2563EB'>{summary}</font>", h2_style))
        story.append(Paragraph(details, body_style))
        story.append(Spacer(1, 4))

    # -------------------------------------------------------------
    # SECTION 3: TOP 25 INTERVIEW QUESTIONS & ANSWERS
    # -------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("SECTION 3: Top 25 Technical Interview Questions & Answers", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_BOX, spaceBefore=0, spaceAfter=8))

    qa_list = [
        # Category A: Architecture & Multi-Agent Design
        ("Q1: Why build a multi-agent system for research instead of a single prompt with a large context window (e.g. Gemini 1.5/2.0 with 1M tokens)?",
         "A single-pass prompt suffers from four fundamental failure modes: (1) 'Lost-in-the-middle' attention degradation when reading thousands of context lines; (2) Inability to specialize simultaneously in retrieval, critique, factual verification, and publication formatting; (3) Non-deterministic tool calling when coordinating 4+ external APIs; and (4) Lack of objective self-verification (the model generating text cannot reliably evaluate its own hallucinations). Decomposing into 13 LangGraph agents gives each step dedicated schemas, retries, and bounded state."),

        ("Q2: How does LangGraph manage state, and why did you use custom reducers?",
         "LangGraph uses a typed state dictionary (ResearchState). When parallel retrieval agents fan out from the Planner, a standard dictionary would overwrite concurrent updates. I implemented custom Annotated reducers: `paper_reducer` deduplicates incoming papers by title, and `log_reducer` appends execution logs chronologically (left + right). This guarantees safe parallel fan-in to the Knowledge Synthesizer."),

        ("Q3: What prevents your agent loop from spinning into an infinite cycle?",
         "Two deterministic safeguards: (1) An explicit iteration budget (`max_iterations`, default 2) checked against `iteration_count`; (2) A quality gate in the pure conditional edge `should_continue_or_refine`. If `iteration_count >= max_iterations` OR `evaluation_metrics.is_acceptable == True`, the graph unconditionally routes to END. The edge function is completely pure and does not mutate state."),

        ("Q4: How do you handle failures when an external API like Semantic Scholar or Tavily is down or rate-limited?",
         "Fault isolation at the agent boundary. Calls to arXiv, Semantic Scholar, and Tavily are wrapped in individual try/except blocks with 3-second timeouts. If Semantic Scholar returns an HTTP 429 or Tavily suffers network jitter, the agent logs a `partial_failure` warning and falls back to alternate sources. The workflow completes with partial results rather than failing."),

        ("Q5: What is the core architectural difference between LangGraph, CrewAI, and AutoGen?",
         "CrewAI and AutoGen are conversational multi-agent frameworks where agents chat autonomously until completion, which can cause unpredictable drift and runaway token costs. LangGraph is a deterministic, cyclical compute graph providing explicit control-flow transitions, custom state reducers, and reliable conditional routing."),

        # Category B: Retrieval & RAG Infrastructure
        ("Q6: Why implement Hybrid Dense + Lexical RAG instead of standard vector search?",
         "Vector embeddings excel at semantic concepts (e.g. 'cardiac arrest' to 'heart failure') but struggle with exact keywords, version numbers ('v2.5 vs v3.8'), acronyms ('RRF', 'MoE'), and error codes. BM25 excels at exact lexical matching. Combining both via Reciprocal Rank Fusion: Score = (1 - alpha) * BM25 + alpha * Dense delivers both conceptual recall and keyword precision."),

        ("Q7: How did you solve the ChromaDB persistence and reboot issue?",
         "ChromaDB stores embeddings on disk in `./data/chroma`, but BM25 indices operate in memory. On server reboot, documents previously indexed in Chroma were missing from memory, causing hybrid_search to drop them. I engineered `_hydrate_from_chroma()` during vector store startup to scan ChromaDB and repopulate the in-memory cache and lexical index."),

        ("Q8: How does your document chunking strategy work, and what chunk size did you pick?",
         "I implemented a sliding-window chunker with 1,000 character chunks and 200 character overlap. Rather than slicing at arbitrary character counts, it searches backward for paragraph breaks (`\\n\\n`) and sentence endings (`. `) to ensure semantic coherence."),

        ("Q9: How do you prevent duplicate documents from polluting the vector database?",
         "In `VectorStoreService.add_documents()`, incoming documents are checked against existing IDs in memory. If a document ID already exists, it is omitted before touching disk or ChromaDB, preserving clean BM25 term frequency calculations."),

        ("Q10: Why choose ChromaDB over Qdrant or Pinecone for this stage?",
         "ChromaDB's embedded mode runs directly in-process with zero external container dependencies, making local development and automated test suites fast and self-contained. The `VectorStoreService` uses an abstract interface so Qdrant or Milvus can be dropped in for multi-tenant scaling without modifying agents."),

        # Category C: Citation Verification & Grounding
        ("Q11: Explain your citation verification algorithm. How does it eliminate hallucinations?",
         "The Citation Verification Agent operates in 5 steps: (1) Extracts factual assertions from report sections; (2) Resolves citation anchors ([1], [2]) to the literature corpus; (3) Extracts the highest-overlap sentence from the source text; (4) Classifies claims based on keyword containment (Supported >= 35%, Partially Supported 18-34%, Unsupported < 18%, Unverified if missing citation); (5) Calculates aggregate Citation Coverage and Correctness."),

        ("Q12: Why is count-based citation verification dangerous?",
         "Checking `if len(references) > 0: status = 'Passed'` is a major flaw because an LLM can hallucinate fake facts while citing real, unrelated papers (e.g. claiming 'Bitcoin accelerates solar panels' and citing an authentic solar study). Genuine verification must check the semantic alignment between the claim and the cited text."),

        ("Q13: How does the system handle paywalled academic papers?",
         "When full-text PDFs are behind paywalls, only titles, abstracts, and OpenAccess snippets are accessible. The Citation Verifier checks claims against the available abstract and explicitly records in the report metadata that full-text validation was bounded by abstract availability."),

        ("Q14: How does the final report distinguish between verified facts, interpretations, and hypotheses?",
         "The Writer Agent enforces explicit section numbering: Section 4 is restricted to Verified Empirical Findings grounded by citation anchors; Section 5 contains Comparative Interpretations; Section 7 is reserved for Proposed Experimental Hypotheses."),

        # Category D: Evaluation Metrics
        ("Q15: Why eliminate hardcoded evaluation scores?",
         "Many RAG projects fabricate fixed constants like `faithfulness = 0.94`. This provides zero diagnostic signal. I replaced all constants with deterministic mathematical formulas derived from retrieval logs and claim checks. When data is absent, the system returns None or an explicit `no_telemetry_collected` status."),

        ("Q16: Define Precision@K, Recall@K, and MRR in your retrieval pipeline.",
         "Given top-5 retrieved sources: Precision@5 is the fraction of top-5 sources relevant to the objective; Recall@5 is the fraction of all relevant sources captured; Mean Reciprocal Rank (MRR) is 1 / rank of the first relevant document. If rank 1 is relevant, MRR = 1.0; if rank 3, MRR = 0.33."),

        ("Q17: How is Faithfulness / Groundedness calculated?",
         "Faithfulness is derived directly from claim verification: (Supported Claims + 0.5 * Partially Supported) / Total Claims. Hallucination risk is defined deterministically as 1.0 - Faithfulness."),

        ("Q18: What is the difference between deterministic metrics and LLM-as-a-judge?",
         "Deterministic metrics (Precision@K, MRR, Citation Coverage) are 100% reproducible, run in <1ms, and have zero API cost. LLM-as-a-judge metrics introduce non-determinism, latency, and model bias. My platform uses deterministic metrics as the primary ground truth."),

        # Category E: Concurrency, Security & Backend
        ("Q19: How did you prevent long research workflows from blocking the FastAPI event loop?",
         "Running `graph.invoke()` synchronously inside an async endpoint blocks the single-threaded asyncio event loop for up to 45 seconds. I offloaded execution using `asyncio.to_thread(_execute_graph_sync, ...)` with a 300-second timeout, keeping the main loop free for other requests."),

        ("Q20: What security measures protect the document upload endpoint?",
         "Multi-layered defense: (1) Path traversal protection via `os.path.realpath` checking containment inside UPLOAD_DIR; (2) Extension whitelist (.pdf, .docx, .pptx, .txt, .md); (3) Magic byte validation (%PDF-, PK zip headers); (4) Streaming 64KB chunking with strict 15MB limits (HTTP 413); (5) Guaranteed cleanup in finally blocks."),

        ("Q21: Explain your database persistence architecture across multiple worker processes.",
         "SQLAlchemy manages `ResearchJobModel` across states (pending, running, completed, failed, cancelled). Because all state transitions and reports are committed to SQLite/PostgreSQL, multiple Uvicorn workers can query job statuses without sharing process memory."),

        ("Q22: How does the system handle job cancellation?",
         "The endpoint `POST /api/v1/jobs/{id}/cancel` transitions the job to `cancelled` and logs the timestamp. Worker threads check job status at node boundaries to terminate early and release compute resources."),

        # Category F: Tough "Grill-Me" Scenarios
        ("Q23: Your resume previously listed Qdrant and PostgreSQL. What is your honest answer if asked about this?",
         "During early architecture exploration, I configured Qdrant and Redis in Docker Compose. However, during profiling, I realized external containers added unnecessary operational overhead for local single-user testing. I modularized the storage layer: ChromaDB and BM25 handle retrieval, and SQLAlchemy provides persistence supporting both zero-setup SQLite and PostgreSQL via DATABASE_URL. This kept the repo clean and portable."),

        ("Q24: What makes this project production-ready compared to a weekend prototype?",
         "Four key pillars: (1) Relational job persistence with a complete state machine rather than in-memory dicts; (2) Non-blocking asynchronous worker thread execution; (3) Hardened upload security with path traversal and magic byte checks; (4) 100% automated test suite with 32 unit and integration tests."),

        ("Q25: If you had 2 more weeks to improve this platform, what would you build next?",
         "Three high-impact additions: (1) Neural cross-encoder reranker (bge-reranker-large) after hybrid retrieval; (2) Distributed task queue using Celery/Redis for multi-node clustering; (3) Automated crawler integration with Unpaywall API to extract full-text bodies of open-access papers beyond abstracts.")
    ]

    for q, a in qa_list:
        story.append(Paragraph(q, q_style))
        story.append(Paragraph(a, ans_style))
        story.append(Spacer(1, 3))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated Interview Master Guide PDF at: {PDF_OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
