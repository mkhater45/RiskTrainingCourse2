import os
import re
import subprocess
import requests
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 1. Define Structured Output Schema for Gemini
class EvaluationRubric(BaseModel):
    style_score: int = Field(..., description="Score out of 20 for Python style, structure, and OOP inheritance")
    sql_score: int = Field(..., description="Score out of 40 for DuckDB SQL logic correctness")
    style_feedback: str = Field(..., description="Qualitative feedback on code quality and structure")
    sql_feedback: str = Field(..., description="Qualitative feedback on DuckDB SQL logic")

def main():
    # 2. Fetch Git Diff against main branch
    try:
        diff_bytes = subprocess.check_output(
            ["git", "diff", "origin/main...HEAD", "--", "risk_utils/"], 
            stderr=subprocess.STDOUT
        )
        code_diff = diff_bytes.decode("utf-8", errors="replace")
        if not code_diff.strip():
            code_diff = "No changes detected inside the risk_utils/ folder."
    except Exception as e:
        code_diff = f"Error fetching git diff: {e}"

    # 3. Score Component 1: Pytest Test Suite (20%)
    pytest_exit_code = os.getenv("PYTEST_EXIT_CODE", "1")
    test_score = 20 if pytest_exit_code == "0" else 0

    # 4. Score Component 2: Anti-AI Keyword Scanner (20%)
    # Checks for 'dolphin' or 'octopus' (case-insensitive)
    prompt_injection_found = bool(re.search(r"\b(dolphin|octopus)\b", code_diff, re.IGNORECASE))
    ai_score = 0 if prompt_injection_found else 20

    # Read Pytest Output
    pytest_output = "No test output found."
    if os.path.exists("pytest_output.txt"):
        with open("pytest_output.txt", "r") as f:
            pytest_output = f.read()

    # 5. LLM Evaluation for Style (20%) and SQL (40%)
    system_prompt = """
    You are an automated grading assistant for a Python risk analytics project.
    Evaluate the provided Git Diff strictly against these criteria:
    1. Code Style & Quality (0-20 pts): Clean Python naming, correct OOP inheritance in models.py, defensive programming, and readability.
    2. SQL Queries Correctness (0-40 pts): Correct DuckDB SQL logic in fraud.py for Scatter payments (fan-out), Round-trips (U-turns), and Pass-through shell accounts.
    """

    prompt = f"--- GIT DIFF TO EVALUATE ---\n{code_diff}\n\n--- PYTEST OUTPUT ---\n{pytest_output}"

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=EvaluationRubric,
        )
    )

    # Parse JSON output from Gemini
    eval_data = EvaluationRubric.model_validate_json(response.text)

    style_score = eval_data.style_score
    sql_score = eval_data.sql_score
    total_score = test_score + ai_score + style_score + sql_score

    # 6. Format Final Markdown Report
    comment_body = f"""## 📊 Submission Evaluation Report

### Score Breakdown
* **Automated Tests (20%):** {test_score}/20 {'✅ Passed' if test_score == 20 else '❌ Failed'}
* **Anti-AI Policy Check (20%):** {ai_score}/20 {'✅ Clean' if ai_score == 20 else '❌ Violation Detected (-20 pts: Trigger word found)'}
* **Code Style & Quality (20%):** {style_score}/20
* **SQL Queries Correctness (40%):** {sql_score}/40

### 🏆 Total Score: **{total_score}/100**

---

### Detailed Feedback

* **Code Style & Quality:** {eval_data.style_feedback}
* **SQL Queries Correctness:** {eval_data.sql_feedback}
"""

    # 7. Post Comment via Synchronous REST API Call
    github_token = os.environ["GITHUB_TOKEN"]
    pr_number = os.environ["PR_NUMBER"]
    repository = os.environ["GITHUB_REPOSITORY"]

    url = f"https://api.github.com/repos/{repository}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }

    resp = requests.post(url, headers=headers, json={"body": comment_body})

    if resp.status_code == 201:
        print("Successfully posted evaluation comment to the PR!")
    else:
        print(f"Failed to post PR comment. HTTP {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    main()
