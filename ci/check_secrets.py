"""Simple deterministic secret scanner for the classroom CI exercise.

The original Dockerfile.insecure is a deliberately insecure laboratory fixture,
so this scanner checks deployable Python and configuration files instead.
"""

import re
from pathlib import Path


RULES = {
    "AWS-like access key": re.compile(r"AKIA[A-Z0-9]{16}"),
    "hardcoded secret assignment": re.compile(
        r"(?i)(?:api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{12,}['\"]"
    ),
}

SUFFIXES = {".py", ".yaml", ".yml", ".json", ".txt"}
SKIP_DIRS = {".git", ".venv", "__pycache__", "ci", "tests", "evidence"}


def main():
    findings = []
    for path in Path(".").rglob("*"):
        if not path.is_file() or path.suffix not in SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name.startswith("requirements.insecure"):
            continue
        for number, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
            for name, rule in RULES.items():
                if rule.search(line):
                    findings.append((str(path), number, name))

    for filename, line, name in findings:
        print(f"SECRET FOUND: {filename}:{line} [{name}]")
    if findings:
        print("Quality gate FAILED: remove hardcoded secrets from current code.")
        raise SystemExit(1)
    print("Quality gate PASSED: no matching credentials found in current source.")


if __name__ == "__main__":
    main()
