from app.agents.citation_verifier import CitationVerificationAgent
from app.schemas.research import ResearchReport
from app.schemas.source import PaperItem
from app.schemas.state import ResearchState


def test_citation_verification_supported_claims():
    agent = CitationVerificationAgent()

    papers = [
        PaperItem(
            id="p1",
            title="Unconditional Cash Transfers and Labor Dynamics",
            authors=["Smith et al."],
            abstract="Empirical analysis confirms unconditional cash transfers under $1,000/mo result in minimal workforce reduction below 2 percent across secondary earners.",
            url="https://arxiv.org/abs/2401.00001"
        )
    ]

    report = ResearchReport(
        title="Research Report: UBI",
        executive_summary="Overview of cash transfers.",
        problem_statement="Operational bottlenecks.",
        key_findings=[
            "Unconditional cash transfers result in minimal workforce reduction below 2% among secondary earners [1]."
        ],
        references=["[1] **Unconditional Cash Transfers and Labor Dynamics** (2024)"]
    )

    state: ResearchState = {
        "job_id": "test_cite_01",
        "objective": "Universal Basic Income",
        "retrieved_papers": papers,
        "retrieved_web_sources": [],
        "retrieved_user_docs": [],
        "draft_report": report,
        "agent_logs": []
    }

    res = agent.run(state)
    verif = res["citation_verification"]

    assert verif["total_claims"] == 1
    assert verif["supported_claims"] == 1
    assert verif["claims_with_citations"] == 1
    assert verif["citation_coverage"] == 1.0
    assert verif["citation_correctness"] == 1.0
    assert verif["unsupported_claim_rate"] == 0.0
    assert verif["claim_details"][0]["status"] == "supported"
    assert len(verif["claim_details"][0]["evidence_snippets"]) > 0


def test_citation_verification_unsupported_claim():
    agent = CitationVerificationAgent()

    papers = [
        PaperItem(
            id="p1",
            title="Solar Photovoltaic Efficiency",
            authors=["Johnson et al."],
            abstract="Study of silicon wafer crystallization under high thermal gradients in laboratory settings.",
            url="https://arxiv.org/abs/2401.00002"
        )
    ]

    # Claim talks about crypto tokenomics citing solar paper [1] -> completely unsupported
    report = ResearchReport(
        title="Research Report: Crypto",
        executive_summary="Crypto report.",
        problem_statement="Challenges.",
        key_findings=[
            "Bitcoin zero-knowledge rollups accelerate decentralized liquidity yields by 500% [1]."
        ],
        references=["[1] **Solar Photovoltaic Efficiency** (2024)"]
    )

    state: ResearchState = {
        "job_id": "test_cite_02",
        "objective": "Cryptocurrency and Solar",
        "retrieved_papers": papers,
        "retrieved_web_sources": [],
        "retrieved_user_docs": [],
        "draft_report": report,
        "agent_logs": []
    }

    res = agent.run(state)
    verif = res["citation_verification"]

    assert verif["total_claims"] == 1
    assert verif["unsupported_claims"] == 1
    assert verif["supported_claims"] == 0
    assert verif["unsupported_claim_rate"] == 1.0
    assert verif["claim_details"][0]["status"] == "unsupported"


def test_citation_verification_missing_citations():
    agent = CitationVerificationAgent()

    report = ResearchReport(
        title="Research Report: AI",
        executive_summary="AI report.",
        problem_statement="Challenges.",
        key_findings=[
            "Large language models exhibit emergent reasoning abilities at massive parameter scales."
        ],
        references=[]
    )

    state: ResearchState = {
        "job_id": "test_cite_03",
        "objective": "LLMs",
        "retrieved_papers": [],
        "retrieved_web_sources": [],
        "retrieved_user_docs": [],
        "draft_report": report,
        "agent_logs": []
    }

    res = agent.run(state)
    verif = res["citation_verification"]

    assert verif["total_claims"] == 1
    assert verif["claims_missing_citations"] == 1
    assert verif["claims_with_citations"] == 0
    assert verif["citation_coverage"] == 0.0
    assert verif["claim_details"][0]["status"] == "unverified"
    assert "Missing citation" in verif["claim_details"][0]["verification_notes"]


def test_citation_verification_invalid_source_index():
    agent = CitationVerificationAgent()

    # Only 1 paper exists, but claim cites [99]
    papers = [
        PaperItem(
            id="p1",
            title="Single Paper",
            authors=["Author"],
            abstract="Some abstract content.",
            url="https://arxiv.org/abs/2401.00003"
        )
    ]

    report = ResearchReport(
        title="Research Report",
        executive_summary="Summary.",
        problem_statement="Problem.",
        key_findings=[
            "Claim citing phantom source index [99]."
        ],
        references=[]
    )

    state: ResearchState = {
        "job_id": "test_cite_04",
        "objective": "Invalid Index Test",
        "retrieved_papers": papers,
        "retrieved_web_sources": [],
        "retrieved_user_docs": [],
        "draft_report": report,
        "agent_logs": []
    }

    res = agent.run(state)
    verif = res["citation_verification"]

    assert verif["total_claims"] == 1
    assert verif["claim_details"][0]["status"] == "unverified"
    assert "not found" in verif["claim_details"][0]["verification_notes"]
