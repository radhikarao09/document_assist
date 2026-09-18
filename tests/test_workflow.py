from app.agents.answer_generation_agent import AnswerGenerationAgent
from app.agents.evidence_agent import EvidenceAgent
from app.agents.query_agent import QueryAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.validation_agent import ValidationAgent
from app.schemas import DocumentChunk, RetrievedChunk
from app.workflow.rag_workflow import RAGWorkflow


class FakeRetrievalAgent:
    def semantic(self, plan):
        return [RetrievedChunk(chunk_id=1, text="Claims require hospital bills and receipts.", score=0.9, source="semantic")]

    def keyword(self, plan):
        return [RetrievedChunk(chunk_id=1, text="Claims require hospital bills and receipts.", score=1.0, source="keyword")]


class FakeLLMService:
    def generate_answer(self, question, context):
        assert "hospital bills" in context
        return "Claims require hospital bills and receipts."


class UnsupportedLLMService:
    def generate_answer(self, question, context):
        return "This answer is unrelated to the evidence."


class CountingRetrievalAgent(FakeRetrievalAgent):
    def __init__(self):
        self.semantic_calls = 0
        self.keyword_calls = 0

    def semantic(self, plan):
        self.semantic_calls += 1
        return super().semantic(plan)

    def keyword(self, plan):
        self.keyword_calls += 1
        return super().keyword(plan)


def test_workflow_merges_parallel_retrieval_and_validates_answer():
    workflow = RAGWorkflow(
        supervisor_agent=SupervisorAgent(QueryAgent()),
        retrieval_agent=FakeRetrievalAgent(),
        evidence_agent=EvidenceAgent(),
        answer_agent=AnswerGenerationAgent(FakeLLMService()),
        validation_agent=ValidationAgent(),
    )

    answer = workflow.ask("What documents are required for a claim?")

    assert "hospital bills" in answer


def test_supervisor_is_registered_as_graph_entry_and_retry_target():
    workflow = RAGWorkflow(
        supervisor_agent=SupervisorAgent(QueryAgent()),
        retrieval_agent=FakeRetrievalAgent(),
        evidence_agent=EvidenceAgent(),
        answer_agent=AnswerGenerationAgent(FakeLLMService()),
        validation_agent=ValidationAgent(),
    )

    graph = workflow.graph.get_graph()

    assert "supervisor" in graph.nodes
    assert "semantic_retrieval" in graph.nodes
    assert "keyword_retrieval" in graph.nodes


def test_failed_validation_retries_once_then_returns_not_found():
    retrieval_agent = CountingRetrievalAgent()
    workflow = RAGWorkflow(
        supervisor_agent=SupervisorAgent(QueryAgent()),
        retrieval_agent=retrieval_agent,
        evidence_agent=EvidenceAgent(),
        answer_agent=AnswerGenerationAgent(UnsupportedLLMService()),
        validation_agent=ValidationAgent(),
    )

    answer = workflow.ask("What documents are required?")

    assert answer == ValidationAgent.not_found_message
    assert retrieval_agent.semantic_calls == 2
    assert retrieval_agent.keyword_calls == 2
