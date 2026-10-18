from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import PyPDF2
import re

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # Maximum total request size: 20 MB

MAX_RESUMES = 10
MAX_FILE_SIZE_NOTE = "Each PDF should be a reasonable size."

SKILLS_DB = [
    "spring boot", "machine learning", "data analysis", "rest api",
    "javascript", "typescript", "mongodb", "mysql", "python", "java",
    "c++", "c#", "html", "css", "react", "node.js", "node",
    "spring", "sql", "git", "github", "aws", "ml", "excel",
    "docker", "kubernetes", "redis", "hibernate", "jpa",
    "spring security", "oauth2", "jwt", "flask", "fastapi",
    "communication", "problem solving", "data structures", "algorithms"
]

# Match whole skill phrases rather than arbitrary substrings.
def extract_skills(text):
    found = set()
    normalized_text = re.sub(r"\s+", " ", text.lower())

    for skill in SKILLS_DB:
        escaped_skill = re.escape(skill.lower())
        pattern = rf"(?<![a-z0-9+#.]){escaped_skill}(?![a-z0-9+#.])"
        if re.search(pattern, normalized_text):
            found.add(skill)

    return found


def extract_text(file_storage):
    try:
        reader = PyPDF2.PdfReader(file_storage.stream)
        pages = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text)

        return "\n".join(pages).lower()
    except Exception:
        return ""


@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    message = ""
    job_desc = ""
    top_x_value = 3

    if request.method == "POST":
        job_desc = request.form.get("job_desc", "").strip()
        raw_top_x = request.form.get("top_x", "3").strip()

        try:
            top_x_value = int(raw_top_x)
        except (TypeError, ValueError):
            top_x_value = 3

        top_x_value = max(1, min(top_x_value, MAX_RESUMES))
        uploaded_files = request.files.getlist("resumes")

        valid_files = [
            file for file in uploaded_files
            if file and file.filename and file.filename.strip()
        ]

        if not valid_files:
            message = "Please select at least one PDF resume."
        elif len(valid_files) > MAX_RESUMES:
            message = f"You can upload a maximum of {MAX_RESUMES} resumes at a time."
        elif not job_desc:
            message = "Please enter the job description."
        else:
            job_skills = extract_skills(job_desc)

            if not job_skills:
                message = (
                    "No recognized skills were found in the job description. "
                    "Add skills such as Java, SQL, React or Spring Boot."
                )
            else:
                for file in valid_files:
                    filename = secure_filename(file.filename)
                    if not filename.lower().endswith(".pdf"):
                        continue

                    resume_text = extract_text(file)
                    if not resume_text.strip():
                        results.append({
                            "name": filename,
                            "score": 0,
                            "matched_skills": [],
                            "note": "Could not read text from this PDF. It may be scanned or invalid."
                        })
                        continue

                    resume_skills = extract_skills(resume_text)
                    matched = resume_skills.intersection(job_skills)
                    score = round(len(matched) / len(job_skills) * 100)

                    results.append({
                        "name": filename,
                        "score": score,
                        "matched_skills": sorted(matched),
                        "note": ""
                    })

                results.sort(key=lambda item: item["score"], reverse=True)
                matched_results = [item for item in results if item["score"] > 0]

                if not matched_results:
                    message = "No matching resumes found. Check the job description and resume text."
                    results = []
                else:
                    if len(matched_results) < top_x_value:
                        message = f"Only {len(matched_results)} resume(s) had matching skills."
                    results = matched_results[:top_x_value]

    return render_template(
        "index.html",
        results=results,
        message=message,
        job_desc=job_desc,
        top_x=top_x_value
    )


@app.errorhandler(413)
def request_entity_too_large(_error):
    return render_template(
        "index.html",
        results=[],
        message="The uploaded files are too large. Please upload smaller PDFs (20 MB total maximum).",
        job_desc="",
        top_x=3
    ), 413


if __name__ == "__main__":
    app.run(debug=True)
