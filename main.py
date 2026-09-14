from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

import os
import shutil

from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# SETUP
# =========================================================

load_dotenv()

app = FastAPI()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

UPLOAD_FOLDER = "documents/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# CURRENT DOCUMENT
# =========================================================

current_vector_store_id = None
current_filename = None


# =========================================================
# REQUEST MODEL
# =========================================================

class QuestionRequest(BaseModel):
    question: str


# =========================================================
# HOME PAGE
# =========================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>

<html>

<head>

<title>Document Assistant</title>

<style>

body {
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    margin: 0;
    padding: 40px;
}

.container {
    max-width: 950px;
    margin: auto;
    background: white;
    padding: 35px;
    border-radius: 15px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
}

h1 {
    text-align: center;
    margin-bottom: 8px;
}

.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 30px;
}

.upload-box {
    border: 2px dashed #ccc;
    padding: 30px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 25px;
}

input[type="file"] {
    font-size: 16px;
}

.status {
    margin-top: 20px;
    font-size: 16px;
}

.question-box {
    display: flex;
    gap: 10px;
    margin-top: 25px;
}

.question-box input {
    flex: 1;
    padding: 15px;
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 8px;
}

button {
    background: #222;
    color: white;
    border: none;
    padding: 13px 22px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
}

button:hover {
    background: #444;
}

button:disabled {
    background: #999;
    cursor: not-allowed;
}

.answer {
    margin-top: 25px;
    padding: 20px;
    background: #f1f3f5;
    border-radius: 10px;
    font-size: 16px;
    line-height: 1.6;
    white-space: pre-wrap;
}

</style>

</head>

<body>

<div class="container">

<h1>Document Assistant</h1>

<div class="subtitle">
Upload any PDF and ask questions about it.
</div>


<div class="upload-box">

<input
    type="file"
    id="pdfFile"
    accept=".pdf"
    onchange="uploadPDF()"
>

<div
    class="status"
    id="uploadStatus">
Choose a PDF to get started.
</div>

</div>


<div class="question-box">

<input
    type="text"
    id="question"
    placeholder="Ask any question about your document..."
>

<button
    id="askButton"
    onclick="askQuestion()"
    disabled>
Ask
</button>

</div>


<div
    class="answer"
    id="answer">
Your answer will appear here.
</div>

</div>


<script>

let pdfReady = false;


async function uploadPDF() {

    const fileInput =
        document.getElementById("pdfFile");

    const status =
        document.getElementById("uploadStatus");

    const answer =
        document.getElementById("answer");

    const askButton =
        document.getElementById("askButton");


    if (!fileInput.files.length) {
        return;
    }


    const file = fileInput.files[0];


    if (!file.name.toLowerCase().endsWith(".pdf")) {

        status.innerText =
            "Please select a PDF file.";

        return;
    }


    pdfReady = false;

    askButton.disabled = true;

    status.innerText =
        "Uploading and processing PDF...";

    answer.innerText =
        "Please wait while the document is being processed.";


    const formData = new FormData();

    formData.append("file", file);


    try {

        const response = await fetch(
            "/upload",
            {
                method: "POST",
                body: formData
            }
        );


        const data = await response.json();


        if (response.ok && data.success) {

            pdfReady = true;

            askButton.disabled = false;

            status.innerText =
                "PDF uploaded successfully ✓";

            answer.innerText =
                "Your document is ready. Ask any question about it.";

        } else {

            status.innerText =
                data.detail || "Could not process the PDF.";

            answer.innerText =
                "The PDF could not be processed.";

        }

    } catch (error) {

        pdfReady = false;

        askButton.disabled = true;

        status.innerText =
            "Could not upload the PDF.";

        answer.innerText =
            "Please try selecting the PDF again.";

    }

}


async function askQuestion() {

    const question =
        document.getElementById("question").value.trim();

    const answer =
        document.getElementById("answer");


    if (!pdfReady) {

        answer.innerText =
            "Please choose a PDF first.";

        return;
    }


    if (!question) {

        answer.innerText =
            "Please enter a question.";

        return;
    }


    answer.innerText =
        "Thinking...";


    try {

        const response = await fetch(
            "/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );


        const data = await response.json();


        if (response.ok) {

            answer.innerText =
                data.answer;

        } else {

            answer.innerText =
                data.detail ||
                "Could not answer the question.";

        }

    } catch (error) {

        answer.innerText =
            "Could not get an answer.";

    }

}

</script>

</body>

</html>
"""


# =========================================================
# UPLOAD PDF
# =========================================================

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    global current_vector_store_id
    global current_filename


    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Please select a PDF file."
        )


    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )


    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    try:

        # Create a new vector store
        vector_store = client.vector_stores.create(
            name="Document Assistant"
        )


        # Upload and index the PDF
        with open(file_path, "rb") as pdf_file:

            client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=pdf_file
            )


        current_vector_store_id = vector_store.id
        current_filename = file.filename


        return {
            "success": True,
            "filename": file.filename
        }


    except Exception as e:

        current_vector_store_id = None
        current_filename = None

        raise HTTPException(
            status_code=500,
            detail=f"Could not process PDF: {str(e)}"
        )


# =========================================================
# ASK QUESTION
# =========================================================

@app.post("/ask")
async def ask_question(request: QuestionRequest):

    if not current_vector_store_id:

        raise HTTPException(
            status_code=400,
            detail="Please choose a PDF first."
        )


    try:

        response = client.responses.create(

            model="gpt-5.6-luna",

            instructions="""
You are a document question-answering assistant.

The uploaded PDF is the ONLY source of information.

Answer questions about the document naturally.

The user may ask broad questions such as:

- What are the important topics?
- What should I study for the exam?
- Explain this document.
- Give me a summary.
- What are the main concepts?
- Explain a topic in simple words.
- What is the difference between two concepts?
- What are the key points?

For broad questions, use all relevant information
retrieved from the document and provide a useful,
well-organized answer.

Do not require the user's wording to exactly match
the wording in the PDF.

Do not use outside knowledge.

If the requested information genuinely cannot be
found in the document, say:

"I could not find relevant information in the uploaded document."

Do not invent information.
""",

            input=request.question,

            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [
                        current_vector_store_id
                    ]
                }
            ]
        )


        return {
            "answer": response.output_text
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not answer the question: {str(e)}"
        )