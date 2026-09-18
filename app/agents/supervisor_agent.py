from app.core.logging import get_logger
from app.schemas import QueryPlan
from app.workflow.state import AgentState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.workflow.rag_workflow import RAGWorkflow

logger = get_logger(__name__)


class SupervisorAgent:
    """Coordinates query planning and routing as a LangGraph node."""

    def __init__(self, query_agent, workflow: "RAGWorkflow | None" = None):
        self.query_agent = query_agent
        self.workflow = workflow

    def supervise(self, state: AgentState):
        query_plan = self.query_agent.analyze(
            state["question"], state.get("retry_count", 0)
        )
        return {
            "query_plan": query_plan,
            "next_route": self._choose_route(query_plan),
        }

    @staticmethod
    def _choose_route(query_plan: QueryPlan) -> str:
        if query_plan.question_type in {
            "lookup",
            "summary",
            "comparison",
            "explanation",
        }:
            return "retrieve"
        return "finish"

    def attach_workflow(self, workflow: "RAGWorkflow") -> None:
        self.workflow = workflow

    def answer(self, question: str) -> str:
        if self.workflow is None:
            raise RuntimeError("Supervisor Agent is not attached to a workflow")
        logger.info("Supervisor Agent coordinating question workflow")
        return self.workflow.ask(question)
