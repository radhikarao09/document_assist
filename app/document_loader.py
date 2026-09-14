from pypdf import PdfReader

pdf_path = "documents/healthcare_policy_sample.pdf"

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    text += page.extract_text()

print(text)