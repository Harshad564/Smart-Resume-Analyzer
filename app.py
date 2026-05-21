from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def extract_text_from_pdf(pdf_path):
    text = ""

    try:
        reader = PdfReader(pdf_path)

        for page in reader.pages:
            extracted_text = page.extract_text()

            if extracted_text:
                text += extracted_text + " "

    except Exception as e:
        print("Error:", e)

    return text.lower()


def analyze_resume(resume_text, job_description):
    resume_words = set(resume_text.split())
    jd_words = set(job_description.lower().split())

    matched_keywords = resume_words.intersection(jd_words)

    if len(jd_words) == 0:
        return 0, []

    score = (len(matched_keywords) / len(jd_words)) * 100

    return round(score, 2), sorted(matched_keywords)


@app.route("/", methods=["GET", "POST"])
def index():
    score = None
    matched_keywords = []

    if request.method == "POST":
        uploaded_file = request.files["resume"]
        job_description = request.form["job_description"]

        if uploaded_file:
            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                uploaded_file.filename
            )

            uploaded_file.save(filepath)

            resume_text = extract_text_from_pdf(filepath)

            score, matched_keywords = analyze_resume(
                resume_text,
                job_description
            )

    return render_template(
        "index.html",
        score=score,
        matched_keywords=matched_keywords
    )


if __name__ == "__main__":
    app.run(debug=True)
