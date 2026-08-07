import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdf_filename = r"D:\Projects-Personal\researchmind-ai\Autonomous_MultiAgent_AI_Research_Paper.pdf"
public_pdf = r"D:\Projects-Personal\researchmind-ai\frontend\public\sample_paper.pdf"

doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=letter,
    rightMargin=40,
    leftMargin=40,
    topMargin=40,
    bottomMargin=40
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=colors.HexColor('#1E293B'),
    alignment=1,
    spaceAfter=10
)

author_style = ParagraphStyle(
    'DocAuthor',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#64748B'),
    alignment=1,
    spaceAfter=15
)

h1_style = ParagraphStyle(
    'SectionH1',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=16,
    textColor=colors.HexColor('#4F46E5'),
    spaceBefore=12,
    spaceAfter=6
)

body_style = ParagraphStyle(
    'DocBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9.5,
    leading=13.5,
    textColor=colors.HexColor('#334155'),
    spaceAfter=8
)

abstract_style = ParagraphStyle(
    'DocAbstract',
    parent=styles['Normal'],
    fontName='Helvetica-Oblique',
    fontSize=9,
    leading=13,
    textColor=colors.HexColor('#475569'),
    spaceBefore=5,
    spaceAfter=12
)

story = []

# Title & Authors
story.append(Paragraph("Autonomous Multi-Agent AI Systems: Architectural Tradeoffs, Hybrid RAG, and Citation Grounding Benchmarks", title_style))
story.append(Paragraph("Dr. Aris Vance & Dr. Elena Rostova — AI Research Institute (2026)", author_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=12))

# Abstract
story.append(Paragraph("<b>Abstract</b>", h1_style))
story.append(Paragraph("Autonomous multi-agent systems represent a paradigm shift from single-prompt LLM execution to distributed state-graph orchestration. In this paper, we evaluate the synergistic combination of dense vector embeddings and BM25 lexical search (Hybrid RAG) for technical report synthesis. Our benchmarks demonstrate a 3.8x throughput improvement per GPU watt and a 78% reduction in factual hallucination risk when using explicit self-critique loops.", abstract_style))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=10))

# Section 1
story.append(Paragraph("1. Introduction & Background", h1_style))
story.append(Paragraph("As Large Language Models (LLMs) scale in capability, single-turn inference remains bottlenecked by context fragmentation and hallucination risks. Multi-agent state graph architectures address this limitation by decomposing complex objectives into decoupled sub-tasks, assigning specialized roles to distinct agents (e.g., Planner, Retriever, Synthesizer, Writer, Critic).", body_style))

# Section 2
story.append(Paragraph("2. Hybrid Dense + Lexical Retrieval Architecture", h1_style))
story.append(Paragraph("Dense vector embeddings excel at semantic retrieval but frequently misrank exact keyword tokens, model version numbers, or proper nouns. Conversely, BM25 keyword matching provides exact token recall but misses conceptual synonyms. We implement Reciprocal Rank Fusion (RRF) to combine dense cosine similarity scores with BM25 BM25-okapi metrics:", body_style))

# Table
data = [
    ["Retrieval Paradigm", "Top-1 Recall", "Latency (ms)", "Hallucination Risk"],
    ["Dense Vector (ChromaDB)", "72.4%", "120 ms", "14.2%"],
    ["Lexical Search (BM25)", "68.1%", "45 ms", "18.5%"],
    ["Hybrid RAG (Dense + BM25)", "94.6%", "165 ms", "3.1%"]
]

t = Table(data, colWidths=[160, 100, 100, 120])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EEF2FF')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#312E81')),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 9),
    ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ('TOPPADDING', (0,0), (-1,0), 6),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
    ('FONTSIZE', (0,1), (-1,-1), 8.5),
    ('ALIGN', (1,0), (-1,-1), 'CENTER'),
]))
story.append(t)
story.append(Spacer(1, 10))

# Section 3
story.append(Paragraph("3. Empirical Findings & Agent Self-Critique", h1_style))
story.append(Paragraph("Our empirical analysis indicates that multi-agent self-critique loops dramatically improve citation accuracy. By inserting an explicit Critic Agent to cross-verify generated claims against ground-truth source chunks prior to final report output, hallucination risk drops below 3.5%.", body_style))

# Section 4
story.append(Paragraph("4. Conclusion & Open Challenges", h1_style))
story.append(Paragraph("Hybrid RAG combined with state-graph multi-agent orchestration provides a production-grade foundation for autonomous research. Open challenges include long-context state pruning and dynamic tool selection.", body_style))

doc.build(story)

# Copy to public folder as well
import shutil
os.makedirs(os.path.dirname(public_pdf), exist_ok=True)
shutil.copy(pdf_filename, public_pdf)

print(f"PDF generated successfully at:\n- {pdf_filename}\n- {public_pdf}")
