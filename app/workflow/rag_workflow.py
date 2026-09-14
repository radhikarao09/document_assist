from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.services.document_service import load_document, create_chunks
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService


class AgentState(TypedDict):
    question: str
    context: str
    answer: str


# Load healthcare document
PDF_PATH = "documents/healthcare_policy_sample.pdf"

document_text = load_document(PDF_PATH)
chunks = create_chunks(document_text)


# Initialize services
embedding_service = EmbeddingService()
vector_service = VectorService()
llm_service = LLMService()


# Create embeddings for document chunks
chunk_embeddings = embedding_service.create_embeddings(chunks)


def retrieve_document(state: AgentState):

    question = state["question"]

    query_embedding = embedding_service.create_query_embedding(question)

    relevant_chunks = vector_service.find_relevant_chunks(
        query_embedding,
        chunk_embeddings,
        chunks,
        top_k=3
    )

    context = "\n\n".join(relevant_chunks)

    return {
        "context": context
    }


def generate_answer(state: AgentState):

    answer = llm_service.generate_answer(
        state["question"],
        state["context"]
    )

    return {
        "answer": answer
    }


# LangGraph agent workflow
graph = StateGraph(AgentState)

graph.add_node("retrieve_document", retrieve_document)
graph.add_node("generate_answer", generate_answer)

graph.add_edge(START, "retrieve_document")
graph.add_edge("retrieve_document", "generate_answer")
graph.add_edge("generate_answer", END)

rag_app = graph.compile()


def ask_question(question: str):

    result = rag_app.invoke({
        "question": question,
        "context": "",
        "answer": ""
    })

    return result["answer"]