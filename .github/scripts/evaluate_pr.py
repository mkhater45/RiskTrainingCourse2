import os
import re
import subprocess
from google import genai
from google.genai import types
from ghapi.all import GhApi

# 1. Fetch Git Diff against main branch
try:
    diff_bytes = subprocess.check_output(
        ["git", "diff", "origin/main...HEAD", "--", "risk_utils/"], stderr=subprocess.STDOUT
    )
    code_diff = diff_bytes.decode("utf-8", errors="replace")
except Exception as e:
    code_diff = f"Error fetching diff: {e}"

# 2. Score Component 1: Automated Pytest Tests (20%)
pytest_exit_code = os.getenv("PYTEST_EXIT_CODE", "1")
test_score = 20 if pytest_exit_code == "0" else 0

# 3. Score Component 2: Anti-AI Keyword Check (20%)
# Checks for 'dolphin' or 'octopus' (case-insensitive) in code or comments
prompt_injection_found = bool(re.search(r"\b(dolphin|octopus)\b", code_diff, re.IGNORECASE))
ai_score = 0 if prompt_injection_found else 20

# Read Pytest Output
pytest_output = "No test output found."
if os.path.exists("pytest_output.txt"):
    with open("pytest_output.txt", "r") as f:
        pytest_output = f.read()

# 4. LLM Prompt for Code Style (20%) and SQL Query Correctness (40%)
system_prompt = """
You are an expert automated grading assistant evaluating student code for a Python risk analytics project.
Analyze the provided Git Diff and rate the submission strictly according to these two criteria:

1. Code Style and Quality (0 to 20 points):
   - Clear variable/function naming, modular structure, clean inheritance usage in models.py, and defensive checks.
2. SQL Queries Correctness (0 to 40 points):
   - Correct implementations of DuckDB SQL logic in fraud.py (Scatter payments / Fan-out, Round-trip U-Turns, and Pass-through Shell accounts).

You MUST respond in clean Markdown with the exact structure below:

### LLM Evaluation Results
* **Code Style & Quality Score:** <score_out_of_20>/20
* **SQL Queries Score:** <score_out_of_40>/40

#### Detailed Feedback
* **Code Style & Quality:** <feedback>
* **SQL Queries Correctness:** <feedback>
"""

prompt = f"""
--- GIT DIFF TO EVALUATE ---
{code_diff}

--- PYTEST RESULTS ---
{pytest_output}
"""

# Call Gemini API
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.2,
    )
)

# Extract scores from Gemini text (fallback regex parsing)
style_match = re.search(r"Code Style & Quality Score:\*\*?\s*(\d+)", response.text)
sql_match = re.search(r"SQL Queries Score:\*\*?\s*(\d+)", response.text)

style_score = int(style_match.group(1)) if style_match else 0
sql_score = int(sql_match.group(1)) if sql_match else 0

total_score = test_score + ai_score + style_score + sql_score

# 5. Build Final Markdown Comment
comment_body = f"""## 📊 Submission Evaluation Report

### Score Breakdown
* **Automated Tests (20%):** {test_score}/20 {'✅ Passed' if test_score == 20 else '❌ Failed'}
* **Anti-AI Policy Check (20%):** {ai_score}/20 {'✅ Clean' if ai_score == 20 else '❌ Violation Detected (-20 pts: Trigger word found)'}
* **Code Style & Quality (20%):** {style_score}/20
* **SQL Queries Correctness (40%):** {sql_score}/40

### 🏆 Total Score: **{total_score}/100**

---

{response.text}
"""

# 6. Post Comment on PR
api = GhApi(token=os.environ["GITHUB_TOKEN"])
owner, repo = os.environ["GITHUB_REPOSITORY"].split("/")
pr_number = int(os.environ["PR_NUMBER"])

api.issues.create_comment(owner, repo, pr_number, body=comment_body)
