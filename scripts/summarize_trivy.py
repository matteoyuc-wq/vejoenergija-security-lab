import json
import sys
from collections import Counter


def count_by_severity(filename):
    with open(filename, encoding="utf-8") as source:
        report = json.load(source)

    vulnerabilities = []
    for result in report.get("Results", []):
        vulnerabilities.extend(result.get("Vulnerabilities") or [])
    return Counter(v.get("Severity", "UNKNOWN") for v in vulnerabilities)


if len(sys.argv) != 3:
    print("Naudojimas: python scripts/summarize_trivy.py pries.json po.json")
    raise SystemExit(2)

before = count_by_severity(sys.argv[1])
after = count_by_severity(sys.argv[2])

print("| Kritiškumas | Prieš | Po |")
print("|---|---:|---:|")
for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"):
    print(f"| {severity} | {before[severity]} | {after[severity]} |")
