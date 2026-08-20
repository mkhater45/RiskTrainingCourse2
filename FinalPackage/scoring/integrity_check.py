"""Deterministic check for the two canary markers described in the project
brief:

Presence of either marker is treated as a signal the team pasted the full
assignment text into an LLM rather than working the task themselves, and
costs a flat 20-percentage-point integrity penalty on the final score
(see scoring/score.py). This check is purely textual/deterministic - no
LLM involved, so it can't be gamed by generated commentary.

Usage:
    python integrity_check.py <path-to-repo-root>
Exit code 0 = no markers found, 1 = at least one marker found.
Prints a JSON report to stdout either way.
"""

import json
import re
import sys
from pathlib import Path

OCTOPUS_PATTERN = re.compile(r"octopus", re.IGNORECASE)
DOLPHIN_PATTERN = re.compile(r"dolphin", re.IGNORECASE)


def check_models_file(path: Path):
    """Scan risk_utils/models.py for the Octopus marker."""
    if not path.exists():
        return {"file": str(path), "exists": False, "marker_found": False, "lines": []}

    hits = []
    for lineno, line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
        if OCTOPUS_PATTERN.search(line):
            hits.append(lineno)

    return {
        "file": str(path),
        "exists": True,
        "marker_found": len(hits) > 0,
        "lines": hits,
    }


def check_fraud_file(path: Path):
    """Scan risk_utils/fraud.py for the dolphin marker."""
    if not path.exists():
        return {"file": str(path), "exists": False, "marker_found": False, "lines": []}

    hits = []
    for lineno, line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
        if DOLPHIN_PATTERN.search(line):
            hits.append(lineno)

    return {
        "file": str(path),
        "exists": True,
        "marker_found": len(hits) > 0,
        "lines": hits,
    }


def main():
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

    models_result = check_models_file(repo_root / "risk_utils" / "models.py")
    fraud_result = check_fraud_file(repo_root / "risk_utils" / "fraud.py")

    any_marker_found = models_result["marker_found"] or fraud_result["marker_found"]

    report = {
        "models_py": models_result,
        "fraud_py": fraud_result,
        "any_marker_found": any_marker_found,
        "integrity_penalty_points": 20 if any_marker_found else 0,
    }

    print(json.dumps(report, indent=2))
    sys.exit(1 if any_marker_found else 0)


if __name__ == "__main__":
    main()
