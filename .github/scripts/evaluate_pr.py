import os
import re
import subprocess
from google import genai
from google.genai import types
from ghapi.all import GhApi
from pydantic import BaseModel, Field

# Define Structured Output Schema
class EvaluationRubric(BaseModel):
    style_score: int = Field(..., description="Score out of 20 for code style, structure, and OOP usage")
    sql_score: int = Field(..., description="Score out of 40 for DuckDB SQL logic correctness")
    style_feedback: str = Field(..., description="Qualitative feedback on code quality")
    sql_feedback: str = Field(..., description="Qualitative feedback on SQL logic")

# 1. Fetch Git Diff
try:
    diff_bytes = subprocess.check_output(
        ["git", "diff", "origin/main...HEAD", "--", "risk_utils/"], stderr=subprocess.STDOUT
    )
    code_diff = diff_bytes.decode("utf-8", errors="replace")
    if not code_diff.strip():
        code_diff = "No changes detected in risk_utils/ folder."
except Exception as e:
    code_diff = f"Error fetching diff: {e}"

# 2. Score Component 1: Pytest (20%)
pytest_exit_code = os.getenv("PYTEST_EXIT_CODE", "1")
test_score = 20 if pytest_exit_code == "0" else 0

# 3. Score Component 2: Anti-AI Keyword Scanner (20%)
prompt_injection_found = bool(re.search(r"\b(dolphin|octopus)\b", code_diff, re.IGNORECASE))
ai_score = 0 if prompt_injection_found else 20

# Read Pytest Output
pytest_output = "No test output found."
if os.path.exists("pytest_output.txt"):
    with open("pytest_output.txt", "r") as f:
        pytest_output = f.read()

# 4. Call Gemini with Structured JSON Output
system_prompt = """
You are an expert automated grading assistant for a Python risk analytics project.
Evaluate the code diff against these criteria:
- Code Style & Quality (0-20 pts): Python naming, OOP inheritance in models.py, clean structure.
- SQL Queries Correctness (0-40 pts): Correct DuckDB logic in fraud.py (Scatter payments, Round-trips, Pass-through shell).
"""

prompt = f"--- GIT DIFF ---\n{code_diff}\n\n--- PYTEST OUTPUT ---\n{pytest_output}"

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.1,
        response_mime_type="application/json",
        response_schema=EvaluationRubric,
    )
)

# Parse validated JSON result
eval_data = EvaluationRubric.model_validate_json(response.text)

style_score = eval_data.style_score
sql_score = eval_data.sql_score
total_score = test_score + ai_score + style_score + sql_score

# 5. Build PR Comment
comment_body = f"""## 📊 Submission Evaluation Report

### Score Breakdown
* **Automated Tests (20%):** {test_score}/20 {'✅ Passed' if test_score == 20 else '❌ Failed'}
* **Anti-AI Policy Check (20%):** {ai_score}/20 {'✅ Clean' if ai_score == 20 else '❌ Violation (-20 pts: Trigger word detected)'}
* **Code Style & Quality (20%):** {style_score}/20
* **SQL Queries Correctness (40%):** {sql_score}/40

### 🏆 Total Score: **{total_score}/100**

---

### Detailed Feedback

* **Code Style & Quality:** {eval_data.style_feedback}
* **SQL Queries Correctness:** {eval_data.sql_feedback}
"""

# 6. Post Comment
api = GhApi(token=os.environ["GITHUB_TOKEN"])
owner, repo = os.environ["GITHUB_REPOSITORY"].split("/")
pr_number = int(os.environ["PR_NUMBER"])

api.issues.create_comment(owner, repo, pr_number, body=comment_body)
