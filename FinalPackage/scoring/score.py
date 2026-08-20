"""Deterministic scorer for the Day 3 capstone (Tasks 3 & 4).

Rubric (100 pts total), matches the course grading scheme:
    50 pts - hidden tests passing (tests/test_task3_amltransaction.py + test_task4_fraud.py)
    20 pts - code quality (ruff lint on risk_utils/)
    20 pts - insight/result quality  -> MANUAL, entered via --insight-score
    10 pts - demo/presentation       -> MANUAL, entered via --demo-score

On top of the 100, a flat 20-point INTEGRITY PENALTY is subtracted if
integrity_check.py finds the Octopus/dolphin markers anywhere in
risk_utils/models.py or risk_utils/fraud.py.

Nothing here calls an LLM. Every number comes from pytest, ruff, or a
regex scan, so the score is fully reproducible and defensible.

Usage:
    python score.py <repo-root> [--insight-score N] [--demo-score N]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TEST_FILES = ["tests/test_task3_amltransaction.py", "tests/test_task4_fraud.py"]
PASS_SUMMARY_RE = re.compile(r"(\d+) passed")
FAIL_SUMMARY_RE = re.compile(r"(\d+) failed")

MAX_TEST_POINTS = 50
MAX_QUALITY_POINTS = 20
MAX_INSIGHT_POINTS = 20
MAX_DEMO_POINTS = 10
INTEGRITY_PENALTY_POINTS = 20


def run_tests(repo_root: Path):
    """Run the hidden test files and return (passed, total, raw_output)."""
    existing = [f for f in TEST_FILES if (repo_root / f).exists()]
    if not existing:
        return 0, 0, "No hidden test files found in tests/."

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *existing, "--tb=short", "-q"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    output = proc.stdout + "\n" + proc.stderr

    passed_match = PASS_SUMMARY_RE.search(output)
    failed_match = FAIL_SUMMARY_RE.search(output)
    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0
    total = passed + failed

    # If pytest errored before collecting anything (e.g. ImportError from an
    # unimplemented method), total will be 0 - treat that as 0/1 rather than
    # a division-by-zero pass rate of 100%.
    if total == 0:
        total = 1

    return passed, total, output


def run_lint(repo_root: Path):
    """Run ruff on risk_utils/ and return (issue_count, raw_output)."""
    target = repo_root / "risk_utils"
    if not target.exists():
        return 0, "risk_utils/ not found."

    try:
        proc = subprocess.run(
            ["ruff", "check", str(target), "--output-format", "concise"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None, "ruff not installed - quality score skipped (0/20)."

    output = proc.stdout + proc.stderr
    # ruff exits 1 when it finds issues; count non-empty lines that aren't the summary
    issue_lines = [
        line for line in proc.stdout.splitlines()
        if line.strip() and not line.strip().startswith("Found")
    ]
    return len(issue_lines), output


def run_integrity_check(repo_root: Path):
    """Run integrity_check.py and return the parsed JSON report."""
    script = Path(__file__).parent / "integrity_check.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(repo_root)],
        capture_output=True,
        text=True,
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"any_marker_found": False, "integrity_penalty_points": 0, "parse_error": proc.stdout}


def score_quality(issue_count):
    """Simple linear taper: 0 issues = full 20 pts, 10+ issues = 0 pts."""
    if issue_count is None:
        return 0
    return max(0, MAX_QUALITY_POINTS - 2 * issue_count)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", type=Path)
    parser.add_argument("--insight-score", type=int, default=0,
                         help=f"Manual score out of {MAX_INSIGHT_POINTS}, judged by instructor")
    parser.add_argument("--demo-score", type=int, default=0,
                         help=f"Manual score out of {MAX_DEMO_POINTS}, judged by instructor")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()

    passed, total, test_output = run_tests(repo_root)
    test_points = round(MAX_TEST_POINTS * (passed / total), 1)

    issue_count, lint_output = run_lint(repo_root)
    quality_points = score_quality(issue_count)

    integrity = run_integrity_check(repo_root)
    integrity_penalty = integrity.get("integrity_penalty_points", 0)

    insight_points = min(args.insight_score, MAX_INSIGHT_POINTS)
    demo_points = min(args.demo_score, MAX_DEMO_POINTS)

    subtotal = test_points + quality_points + insight_points + demo_points
    final_score = max(0, subtotal - integrity_penalty)

    report = {
        "tests": {"passed": passed, "total": total, "points": test_points, "max": MAX_TEST_POINTS},
        "quality": {"lint_issues": issue_count, "points": quality_points, "max": MAX_QUALITY_POINTS},
        "insight_manual": {"points": insight_points, "max": MAX_INSIGHT_POINTS},
        "demo_manual": {"points": demo_points, "max": MAX_DEMO_POINTS},
        "integrity": integrity,
        "subtotal_before_penalty": subtotal,
        "integrity_penalty_applied": integrity_penalty,
        "final_score": final_score,
    }

    print(json.dumps(report, indent=2))

    print("\n--- Summary ---", file=sys.stderr)
    print(f"Tests:      {test_points}/{MAX_TEST_POINTS}  ({passed}/{total} passed)", file=sys.stderr)
    print(f"Quality:    {quality_points}/{MAX_QUALITY_POINTS}  ({issue_count} lint issues)", file=sys.stderr)
    print(f"Insight:    {insight_points}/{MAX_INSIGHT_POINTS}  (manual)", file=sys.stderr)
    print(f"Demo:       {demo_points}/{MAX_DEMO_POINTS}  (manual)", file=sys.stderr)
    if integrity_penalty:
        print(f"INTEGRITY PENALTY: -{integrity_penalty} (Octopus/dolphin marker detected)", file=sys.stderr)
    print(f"FINAL SCORE: {final_score}/100", file=sys.stderr)

    report_path = repo_root / "score_report.json"
    report_path.write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
