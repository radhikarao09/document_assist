from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
import os


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load document
pdf_path = "documents/healthcare_policy_sample.pdf"
reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    text += page.extract_text()


# Create chunks
chunk_size = 500
chunks = []

for i in range(0, len(text), chunk_size):
    chunks.append(text[i:i + chunk_size])


# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chunk_embeddings = embedding_model.encode(chunks)


class AgentState(TypedDict):
    question: str
    context: str
    answer: str


def retrieve_document(state: AgentState):

    question = state["question"]

    query_embedding = embedding_model.encode([question])[0]

    similarities = []

    for chunk_embedding in chunk_embeddings:

        similarity = np.dot(query_embedding, chunk_embedding) / (
            np.linalg.norm(query_embedding)
            * np.linalg.norm(chunk_embedding)
        )

        similarities.append(similarity)

    best_index = np.argmax(similarities)

    return {
        "context": chunks[best_index]
    }


def generate_answer(state: AgentState):

    question = state["question"]
    context = state["context"]

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=(
            "Answer the question using only the provided healthcare "
            "document context. If the answer is not present in the "
            "context, say you cannot find it in the document."
        ),
        input=f"""
Document context:

{context}

Question:

{question}
"""
    )

    return {
        "answer": response.output_text
    }


# Create LangGraph
graph = StateGraph(AgentState)

graph.add_node("retrieve_document", retrieve_document)
graph.add_node("generate_answer", generate_answer)

graph.add_edge(START, "retrieve_document")
graph.add_edge("retrieve_document", "generate_answer")
graph.add_edge("generate_answer", END)

app = graph.compile()


# Test the agent
result = app.invoke({
    "question": "What documents are required for reimbursement?",
    "context": "",
    "answer": ""
})


print("\nQuestion:")
print(result["question"])

print("\nAnswer:")
print(result["answer"])