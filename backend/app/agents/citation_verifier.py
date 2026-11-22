import re
import time
from typing import Any

from app.agents.base import BaseAgent, build_unified_source_registry
from app.schemas.evaluation import ClaimStatus, ClaimVerificationItem, CitationVerificationResult
from app.schemas.state import ResearchState

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with", "we", "this", "these", "those",
    "or", "can", "our", "their", "into", "across", "been", "through",
}


def extract_keywords(text: str) -> set[str]:
    """Extract lowercased alphanumeric keywords, stripping common stopwords."""
    words = re.findall(r"\b[a-zA-Z0-9_\-\.%]+\b", text.lower())
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


def find_best_evidence_sentence(source_text: str, claim_keywords: set[str]) -> tuple[str, float]:
    """Finds the sentence in source_text that has the highest keyword overlap with the claim."""
    if not source_text or not claim_keywords:
        return "", 0.0

    # Split into sentences
    sentences = re.split(r"(?<=[.!?])\s+", source_text.strip())
    best_sentence = ""
    best_overlap = 0.0

    for sent in sentences:
        s_clean = sent.strip()
        if len(s_clean) < 15:
            continue
        sent_kws = extract_keywords(s_clean)
        if not sent_kws:
            continue
        intersection = claim_keywords.intersection(sent_kws)
        score = len(intersection) / max(len(claim_keywords), 1)
        if score > best_overlap:
            best_overlap = score
            best_sentence = s_clean

    return best_sentence[:300], round(best_overlap, 4)


class CitationVerificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Citation Verification Agent")

    def run(self, state: ResearchState) -> dict[str, Any]:
        start_time = time.time()
        report = state.get("draft_report")
        papers = state.get("retrieved_papers", [])
        web_sources = state.get("retrieved_web_sources", [])
        user_docs = state.get("retrieved_user_docs", [])

        # Build unified source registry matching WriterAgent indexing
        _, source_registry = build_unified_source_registry(papers, web_sources, user_docs)

        # Extract claims from report
        raw_claims = self._extract_claims_from_report(report)

        claim_items: list[ClaimVerificationItem] = []
        supported_count = 0
        partially_supported_count = 0
        unsupported_count = 0
        unverified_count = 0
        claims_with_citations_count = 0

        for c_idx, (section_name, claim_text) in enumerate(raw_claims, 1):
            claim_id = f"claim_{c_idx:02d}"
            citation_indices = [int(num) for num in re.findall(r"\[(\d+)\]", claim_text)]
            named_citations = re.findall(r"\[([a-zA-Z0-9_\-\.:]+)\]", claim_text)
            all_citation_keys = [str(i) for i in citation_indices] + [k for k in named_citations if not k.isdigit()]

            claim_clean = re.sub(r"\[\d+\]", "", claim_text).strip()
            claim_kws = extract_keywords(claim_clean)

            if not all_citation_keys:
                # Claim is missing citations entirely
                item = ClaimVerificationItem(
                    claim_id=claim_id,
                    claim_text=claim_clean,
                    section=section_name,
                    citation_indices=[],
                    source_identifiers=[],
                    status="unverified",
                    evidence_snippets=[],
                    confidence_score=0.0,
                    verification_notes="Missing citation: Claim lacks an explicit reference anchor."
                )
                unverified_count += 1
                claim_items.append(item)
                continue

            claims_with_citations_count += 1
            matched_sources = []
            best_snippet = ""
            max_claim_overlap = 0.0
            source_missing = False

            for c_key in all_citation_keys:
                if c_key in source_registry:
                    src = source_registry[c_key]
                    matched_sources.append(src["id"])
                    snippet, overlap = find_best_evidence_sentence(src["text"], claim_kws)
                    if overlap > max_claim_overlap:
                        max_claim_overlap = overlap
                        best_snippet = snippet
                else:
                    source_missing = True

            # Determine claim status based on genuine evidence overlap
            status: ClaimStatus
            notes = ""
            conf = round(min(1.0, max_claim_overlap * 1.5), 3)

            if source_missing and not matched_sources:
                status = "unverified"
                notes = f"Cited source key(s) {all_citation_keys} not found in retrieved literature corpus."
                unverified_count += 1
            elif max_claim_overlap >= 0.35:
                status = "supported"
                notes = f"Strong lexical and conceptual alignment (overlap: {max_claim_overlap:.1%})."
                supported_count += 1
            elif max_claim_overlap >= 0.18:
                status = "partially_supported"
                notes = f"Partial semantic match against source context (overlap: {max_claim_overlap:.1%})."
                partially_supported_count += 1
            else:
                status = "unsupported"
                notes = f"Source text located, but evidence does not adequately ground claim (overlap: {max_claim_overlap:.1%})."
                unsupported_count += 1

            evidence_list = [best_snippet] if best_snippet else []
            claim_items.append(
                ClaimVerificationItem(
                    claim_id=claim_id,
                    claim_text=claim_clean,
                    section=section_name,
                    citation_indices=citation_indices,
                    source_identifiers=matched_sources,
                    status=status,
                    evidence_snippets=evidence_list,
                    confidence_score=conf,
                    verification_notes=notes
                )
            )

        total_claims = len(claim_items)
        claims_missing_citations = total_claims - claims_with_citations_count

        coverage = round(claims_with_citations_count / total_claims, 4) if total_claims > 0 else 0.0
        correctness = round(
            (supported_count + (0.5 * partially_supported_count)) / claims_with_citations_count, 4
        ) if claims_with_citations_count > 0 else 0.0
        unsupported_rate = round(unsupported_count / total_claims, 4) if total_claims > 0 else 0.0
        grounding_conf = round(
            (supported_count + (0.5 * partially_supported_count)) / total_claims, 4
        ) if total_claims > 0 else 0.0

        if total_claims == 0:
            v_status = "Warning: No Claims Extracted"
        elif unsupported_rate > 0.40 or coverage < 0.30:
            v_status = "Failed"
        elif partially_supported_count > supported_count or coverage < 0.60:
            v_status = "Warning"
        else:
            v_status = "Passed"

        result = CitationVerificationResult(
            total_claims=total_claims,
            supported_claims=supported_count,
            partially_supported_claims=partially_supported_count,
            unsupported_claims=unsupported_count,
            unverified_claims=unverified_count,
            claims_with_citations=claims_with_citations_count,
            claims_missing_citations=claims_missing_citations,
            citation_coverage=coverage,
            citation_correctness=correctness,
            unsupported_claim_rate=unsupported_rate,
            grounding_confidence=grounding_conf,
            verification_status=v_status,
            claim_details=claim_items
        )

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=(
                f"Evidence-based verification: {supported_count}/{total_claims} supported, "
                f"{partially_supported_count} partial, {unsupported_count} unsupported. "
                f"Coverage={coverage:.1%}, Correctness={correctness:.1%}."
            ),
            details=result.model_dump()
        )

        return {
            "citation_verification": result.model_dump(),
            "agent_logs": [log]
        }

    def _extract_claims_from_report(self, report: Any) -> list[tuple[str, str]]:
        """Extracts individual factual claims from report sections."""
        claims: list[tuple[str, str]] = []
        if not report:
            return claims

        # 1. Key Findings
        if hasattr(report, "key_findings") and report.key_findings:
            for item in report.key_findings:
                clean = item.strip().lstrip("-*• ").strip()
                if clean:
                    claims.append(("Key Findings", clean))

        # 2. Executive Summary sentences
        if hasattr(report, "executive_summary") and report.executive_summary:
            sentences = re.split(r"(?<=[.!?])\s+", report.executive_summary.strip())
            for sent in sentences:
                s = sent.strip()
                # If sentence contains a citation anchor or strong empirical claim
                if len(s) > 30 and ("[" in s or any(char.isdigit() for char in s)):
                    claims.append(("Executive Summary", s))

        # 3. Problem statement key assertions
        if hasattr(report, "problem_statement") and report.problem_statement:
            sentences = re.split(r"(?<=[.!?])\s+", report.problem_statement.strip())
            for sent in sentences:
                s = sent.strip()
                if "[" in s:
                    claims.append(("Problem Statement", s))

        return claims
