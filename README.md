# Document Assistant

An AI-powered Document Assistant that allows users to upload PDF documents and ask questions about their content.

## Features

- Upload PDF documents through a simple web interface
- Ask natural-language questions about the document
- Retrieve relevant information from the uploaded PDF
- Generate answers using an LLM
- Supports general questions, summaries, key topics, and explanations

## Technologies Used

- Python
- FastAPI
- OpenAI API
- RAG (Retrieval-Augmented Generation)
- Embeddings
- Vector Search
- HTML, CSS, JavaScript

## How It Works

```text
Upload PDF → Process Document → Retrieve Relevant Content → LLM → Answer

## How to Run

1. Clone the repository
2. Install the required dependencies using `pip install -r requirements.txt`
3. Add your OpenAI API key to a `.env` file
4. Run the application using `uvicorn main:app --reload`
5. Open `http://127.0.0.1:8000/` in your browser

## Limitation

Currently supports PDFs with machine-readable/printed text. Handwritten or scanned image-based PDFs are not reliably supported.

## Future Improvements

- OCR support for handwritten/scanned PDFs
- Multiple document support
- Azure deployment
- Source/page references in answers
