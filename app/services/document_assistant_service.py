from app.agents.document_processing_agent import DocumentProcessingAgent
from app.core.logging import get_logger
from app.schemas import UploadResponse
from app.agents.supervisor_agent import SupervisorAgent

logger = get_logger(__name__)


class DocumentAssistantService:
    def __init__(self, document_agent: DocumentProcessingAgent, supervisor: SupervisorAgent):
        self.document_agent = document_agent
        self.supervisor = supervisor

    def upload(self, filename: str, source) -> UploadResponse:
        document = self.document_agent.process(filename, source)
        return UploadResponse(success=True, filename=document.filename)

    def ask(self, question: str) -> str:
        return self.supervisor.answer(question)
