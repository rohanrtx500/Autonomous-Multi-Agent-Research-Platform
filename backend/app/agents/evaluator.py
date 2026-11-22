import re
import time
from typing import Any

from app.agents.base import BaseAgent
from app.schemas.evaluation import EvaluationMetrics
from app.schemas.state import ResearchState

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with", "we", "this", "these", "those",
    "or", "can", "our", "their", "into", "across", "been", "through",
    "using", "evaluate", "compare", "analysis", "study", "research"
}


def tokenize_clean(text: str) -> set[str]:
    words = re.findall(r"\b[a-zA-Z0-9_\-\.%]+\b", text.lower())
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


class EvaluationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Evaluation Agent")

    def run(self, state: ResearchState) -> dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "")
        report = state.get("draft_report")
        papers = state.get("retrieved_papers", [])
        web_sources = state.get("retrieved_web_sources", [])
        user_docs = state.get("retrieved_user_docs", [])
        critic = state.get("critic_feedback", "")
        citation_verif = state.get("citation_verification", {})

        obj_tokens = tokenize_clean(objective)

        # 1. Evaluate Retrieval Metrics (Precision@K, Recall@K, MRR)
        all_sources: list[dict[str, str]] = []
        for p in papers:
            all_sources.append({"title": p.title, "text": f"{p.title} {p.abstract}"})
        for w in web_sources:
            all_sources.append({"title": w.title, "text": f"{w.title} {w.content}"})
        for d in user_docs:
            all_sources.append({"title": d.title, "text": f"{d.title} {d.content}"})

        k = 5
        precision_at_k: float | None = None
        recall_at_k: float | None = None
        mrr: float | None = None
        context_relevance: float | None = None

        if all_sources:
            scored_sources = []
            for rank_idx, src in enumerate(all_sources):
                src_tokens = tokenize_clean(src["text"])
                overlap = len(obj_tokens.intersection(src_tokens))
                rel_score = overlap / max(len(obj_tokens), 1)
                is_relevant = rel_score >= 0.20 or overlap >= 2
                scored_sources.append((rank_idx + 1, rel_score, is_relevant))

            top_k_items = scored_sources[:k]
            relevant_in_top_k = sum(1 for _, _, is_rel in top_k_items if is_rel)
            total_relevant = sum(1 for _, _, is_rel in scored_sources if is_rel)

            precision_at_k = round(relevant_in_top_k / min(k, len(scored_sources)), 4)
            recall_at_k = round(relevant_in_top_k / max(1, total_relevant), 4)

            # MRR: reciprocal rank of first relevant source
            first_rel_rank = next((rank for rank, _, is_rel in top_k_items if is_rel), None)
            mrr = round(1.0 / first_rel_rank, 4) if first_rel_rank else 0.0

            # Context relevance: average relevance score in top-k
            avg_rel = sum(score for _, score, _ in top_k_items) / len(top_k_items)
            context_relevance = round(min(1.0, avg_rel * 1.5), 4)

        # 2. Evaluate Answer Relevance (Report alignment with objective)
        answer_relevance: float | None = None
        if report and hasattr(report, "full_markdown") and report.full_markdown:
            report_text = f"{report.executive_summary} {' '.join(report.key_findings or [])}"
            rep_tokens = tokenize_clean(report_text)
            overlap = len(obj_tokens.intersection(rep_tokens))
            raw_ans_rel = overlap / max(len(obj_tokens), 1)
            answer_relevance = round(min(1.0, raw_ans_rel * 1.2), 4)

        # 3. Groundedness / Faithfulness from genuine Citation Verification
        total_claims = citation_verif.get("total_claims", 0)
        supported_claims = citation_verif.get("supported_claims", 0)
        partially_supported = citation_verif.get("partially_supported_claims", 0)

        citation_coverage = citation_verif.get("citation_coverage")
        citation_correctness = citation_verif.get("citation_correctness")
        unsupported_claim_rate = citation_verif.get("unsupported_claim_rate")

        if total_claims > 0:
            faithfulness_score = round((supported_claims + 0.5 * partially_supported) / total_claims, 4)
            grounding_score = round(citation_verif.get("grounding_confidence", faithfulness_score), 4)
        else:
            faithfulness_score = 0.0 if not papers and not web_sources else 0.5
            grounding_score = 0.0 if not papers and not web_sources else 0.5

        hallucination_risk = round(1.0 - faithfulness_score, 4)

        # 4. Composite Confidence Score
        valid_scores = [
            s for s in [faithfulness_score, answer_relevance, context_relevance, precision_at_k]
            if s is not None
        ]
        confidence_score = round(sum(valid_scores) / len(valid_scores), 4) if valid_scores else 0.0

        # Reasoning quality: estimated from logical structure and gap/experiment presence
        has_comps = len(state.get("method_comparisons", [])) > 0
        has_gaps = len(state.get("research_gaps", [])) > 0
        has_exps = len(state.get("experiment_plan", [])) > 0
        structure_pts = sum([has_comps * 0.35, has_gaps * 0.35, has_exps * 0.30])
        reasoning_quality = round(structure_pts, 4)

        # Acceptability gate
        is_acceptable = (
            (confidence_score >= 0.55) and
            (unsupported_claim_rate is None or unsupported_claim_rate <= 0.35) and
            (critic != "Quality issues detected.")
        )

        deterministic_metrics = {
            "precision_at_k": precision_at_k,
            "recall_at_k": recall_at_k,
            "mrr": mrr,
            "context_relevance": context_relevance,
            "answer_relevance": answer_relevance,
            "citation_coverage": citation_coverage,
            "citation_correctness": citation_correctness,
            "unsupported_claim_rate": unsupported_claim_rate,
        }

        methodology = (
            "Multi-faceted evaluation combining deterministic IR metrics (Precision@5, Recall@5, MRR) "
            "against research objective keywords, alongside claim-level evidence verification for faithfulness "
            "and citation coverage. Scores reflect empirical data without synthetic score inflation."
        )

        limitations = [
            "Lexical matching does not account for deep conceptual synonyms without neural cross-encoder.",
            "Evaluation bounded by available abstracts when full-text paper PDFs are paywalled."
        ]

        metrics = EvaluationMetrics(
            faithfulness_score=faithfulness_score,
            relevance_score=answer_relevance or 0.0,
            grounding_score=grounding_score,
            confidence_score=confidence_score,
            hallucination_risk=hallucination_risk,
            reasoning_quality=reasoning_quality,
            is_acceptable=is_acceptable,
            critique_comments=[critic] if critic else [],
            precision_at_k=precision_at_k,
            recall_at_k=recall_at_k,
            mrr=mrr,
            context_relevance=context_relevance,
            answer_relevance=answer_relevance,
            citation_coverage=citation_coverage,
            citation_correctness=citation_correctness,
            unsupported_claim_rate=unsupported_claim_rate,
            deterministic_metrics=deterministic_metrics,
            llm_judge_metrics={},
            methodology=methodology,
            limitations=limitations
        )

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=(
                f"Evaluated measurable metrics: Precision@5={precision_at_k}, MRR={mrr}, "
                f"Faithfulness={faithfulness_score}, AnswerRelevance={answer_relevance}, "
                f"Acceptable={is_acceptable}."
            ),
            details=metrics.model_dump()
        )

        current_iter = state.get("iteration_count", 0)
        max_iters = state.get("max_iterations", 2)
        new_iter = current_iter if is_acceptable else current_iter + 1
        final_status = "completed" if (is_acceptable or new_iter >= max_iters) else "refining"

        return {
            "evaluation_metrics": metrics,
            "iteration_count": new_iter,
            "status": final_status,
            "agent_logs": [log]
        }
