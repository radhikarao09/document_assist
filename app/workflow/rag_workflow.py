from langgraph.graph import END, START, StateGraph

from app.agents.answer_generation_agent import AnswerGenerationAgent
from app.agents.evidence_agent import EvidenceAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.validation_agent import ValidationAgent
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas import RetrievedChunk
from app.workflow.state import AgentState

logger = get_logger(__name__)

class RAGWorkflow:
    """Supervisor-owned graph coordinating specialized agents."""

    def __init__(
        self,
        supervisor_agent: SupervisorAgent,
        retrieval_agent: RetrievalAgent,
        evidence_agent: EvidenceAgent,
        answer_agent: AnswerGenerationAgent,
        validation_agent: ValidationAgent,
    ):
        self.supervisor_agent = supervisor_agent
        self.retrieval_agent = retrieval_agent
        self.evidence_agent = evidence_agent
        self.answer_agent = answer_agent
        self.validation_agent = validation_agent
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("supervisor", self._supervise)
        graph.add_node("retrieval_dispatch", self._dispatch_retrieval)
        graph.add_node("semantic_retrieval", self._semantic_retrieval)
        graph.add_node("keyword_retrieval", self._keyword_retrieval)
        graph.add_node("evidence_evaluation", self._evaluate_evidence)
        graph.add_node("answer_generation", self._generate_answer)
        graph.add_node("validation", self._validate_answer)

        graph.add_edge(START, "supervisor")
        graph.add_conditional_edges(
            "supervisor",
            self._supervisor_route,
            {"retrieve": "retrieval_dispatch", "finish": END},
        )
        # Independent retrieval branches can execute in parallel.
        graph.add_edge("retrieval_dispatch", "semantic_retrieval")
        graph.add_edge("retrieval_dispatch", "keyword_retrieval")
        graph.add_edge("semantic_retrieval", "evidence_evaluation")
        graph.add_edge("keyword_retrieval", "evidence_evaluation")
        graph.add_edge("evidence_evaluation", "answer_generation")
        graph.add_edge("answer_generation", "validation")
        graph.add_conditional_edges(
            "validation",
            self._validation_route,
            {"retry": "supervisor", "finish": END},
        )
        return graph.compile()

    def _supervise(self, state: AgentState):
        return self.supervisor_agent.supervise(state)

    @staticmethod
    def _supervisor_route(state: AgentState):
        return state.get("next_route", "finish")

    @staticmethod
    def _dispatch_retrieval(state: AgentState):
        return {}

    def _semantic_retrieval(self, state: AgentState):
        return {"semantic_results": self.retrieval_agent.semantic(state["query_plan"])}

    def _keyword_retrieval(self, state: AgentState):
        return {"keyword_results": self.retrieval_agent.keyword(state["query_plan"])}

    def _evaluate_evidence(self, state: AgentState):
        evidence = self.evidence_agent.evaluate(
            state.get("semantic_results", []), state.get("keyword_results", [])
        )
        return {
            "evidence": evidence,
            "context": self._format_context(evidence),
        }

    def _generate_answer(self, state: AgentState):
        return {
            "answer": self.answer_agent.generate(
                state["question"], state.get("context", "")
            )
        }

    def _validate_answer(self, state: AgentState):
        result = self.validation_agent.validate(
            state.get("answer", ""), state.get("context", "")
        )
        retry_count = state.get("retry_count", 0)
        next_retry_count = retry_count + (0 if result.supported else 1)
        if not result.supported and retry_count >= settings.max_validation_retries:
            return {
                "validation": result,
                "answer": self.validation_agent.not_found_message,
                "retry_count": next_retry_count,
            }
        return {
            "validation": result,
            "retry_count": next_retry_count,
        }

    def _validation_route(self, state: AgentState):
        validation = state.get("validation")
        if validation and validation.supported:
            return "finish"
        if state.get("retry_count", 0) <= settings.max_validation_retries:
            logger.info("Supervisor routing back to retrieval for validation retry")
            return "retry"
        return "finish"

    @staticmethod
    def _format_context(evidence: list[RetrievedChunk]) -> str:
        return "\n\n".join(
            f"[Page {item.page_number}] {item.text}"
            if item.page_number is not None
            else item.text
            for item in evidence
        )

    def ask(self, question: str) -> str:
        result = self.graph.invoke({
            "question": question,
            "retry_count": 0,
        })
        return result["answer"]


def ask_question(question: str) -> str:
    """Compatibility entry point for existing callers."""
    from app.core.container import get_document_assistant_service

    return get_document_assistant_service().ask(question)
