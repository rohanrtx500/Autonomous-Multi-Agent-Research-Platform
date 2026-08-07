from app.agents.citation_verifier import CitationVerificationAgent
from app.agents.comparator import ComparisonAgent
from app.agents.critic import CriticAgent
from app.agents.doc_retriever import DocRetrievalAgent
from app.agents.evaluator import EvaluationAgent
from app.agents.experiment_planner import ExperimentPlannerAgent
from app.agents.gap_analyzer import ResearchGapAnalyzerAgent
from app.agents.github_retriever import GitHubResearchAgent
from app.agents.paper_retriever import PaperRetrievalAgent
from app.agents.planner import PlannerAgent
from app.agents.synthesizer import KnowledgeSynthesizerAgent
from app.agents.web_retriever import WebResearchAgent
from app.agents.writer import WriterAgent
from app.schemas.state import ResearchState

planner_agent = PlannerAgent()
paper_agent = PaperRetrievalAgent()
web_agent = WebResearchAgent()
github_agent = GitHubResearchAgent()
doc_agent = DocRetrievalAgent()
synthesizer_agent = KnowledgeSynthesizerAgent()
comparator_agent = ComparisonAgent()
gap_agent = ResearchGapAnalyzerAgent()
exp_planner_agent = ExperimentPlannerAgent()
writer_agent = WriterAgent()
critic_agent = CriticAgent()
citation_agent = CitationVerificationAgent()
eval_agent = EvaluationAgent()


def planner_node(state: ResearchState) -> ResearchState:
    return planner_agent.run(state)


def paper_retrieval_node(state: ResearchState) -> ResearchState:
    return paper_agent.run(state)


def web_retrieval_node(state: ResearchState) -> ResearchState:
    return web_agent.run(state)


def github_retrieval_node(state: ResearchState) -> ResearchState:
    return github_agent.run(state)


def doc_retrieval_node(state: ResearchState) -> ResearchState:
    return doc_agent.run(state)


def synthesizer_node(state: ResearchState) -> ResearchState:
    return synthesizer_agent.run(state)


def comparator_node(state: ResearchState) -> ResearchState:
    return comparator_agent.run(state)


def gap_node(state: ResearchState) -> ResearchState:
    return gap_agent.run(state)


def exp_planner_node(state: ResearchState) -> ResearchState:
    return exp_planner_agent.run(state)


def writer_node(state: ResearchState) -> ResearchState:
    return writer_agent.run(state)


def critic_node(state: ResearchState) -> ResearchState:
    return critic_agent.run(state)


def citation_node(state: ResearchState) -> ResearchState:
    return citation_agent.run(state)


def eval_node(state: ResearchState) -> ResearchState:
    return eval_agent.run(state)
