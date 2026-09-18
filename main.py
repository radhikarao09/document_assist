from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.routes import router
from app.core.logging import configure_logging


# =========================================================
# SETUP
# =========================================================

app = FastAPI()
configure_logging()


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


app.include_router(router)