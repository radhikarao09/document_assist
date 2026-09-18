from functools import lru_cache

from app.agents.answer_generation_agent import AnswerGenerationAgent
from app.agents.document_processing_agent import DocumentProcessingAgent
from app.agents.evidence_agent import EvidenceAgent
from app.agents.query_agent import QueryAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.validation_agent import ValidationAgent
from app.services.document_assistant_service import DocumentAssistantService
from app.services.document_registry import DocumentRegistry
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService
from app.services.llm_service import LLMService
from app.services.vector_service import VectorService
from app.workflow.rag_workflow import RAGWorkflow


@lru_cache(maxsize=1)
def get_document_assistant_service() -> DocumentAssistantService:
    registry = DocumentRegistry()
    embedding_service = EmbeddingService()
    vector_service = VectorService()
    ingestion_service = IngestionService(embedding_service, registry)
    document_agent = DocumentProcessingAgent(ingestion_service)
    retrieval_agent = RetrievalAgent(registry, embedding_service, vector_service)
    supervisor = SupervisorAgent(QueryAgent())
    workflow = RAGWorkflow(
        supervisor_agent=supervisor,
        retrieval_agent=retrieval_agent,
        evidence_agent=EvidenceAgent(),
        answer_agent=AnswerGenerationAgent(LLMService()),
        validation_agent=ValidationAgent(),
    )
    supervisor.attach_workflow(workflow)
    return DocumentAssistantService(document_agent, supervisor)
