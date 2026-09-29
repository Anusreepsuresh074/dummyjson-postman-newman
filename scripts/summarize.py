#!/usr/bin/env python3
"""Writes summary.md for one Newman run folder (from scripts/run-newman.sh).

Usage: scripts/summarize.py reports/<run folder>

The verdict comes from Newman's exit code (JUnit XML leaves out script errors); the totals come
from the CLI summary; the per-request failures come from junit.xml. Prints the summary too, so CI
can append it to the job summary.
"""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def cli_totals(cli_text):
    totals = {}
    for row in ("iterations", "requests", "test-scripts", "assertions"):
        match = re.search(rf"│\s+{row}\s+│\s+(\d+)\s+│\s+(\d+)\s+│", cli_text)
        if match:
            totals[row] = (int(match.group(1)), int(match.group(2)))
    average = re.search(r"average response time: (\d+)ms", cli_text)
    duration = re.search(r"total run duration: ([\d.]+m?s)", cli_text)
    return totals, average.group(1) if average else "?", duration.group(1) if duration else "?"


def is_defect(suite_name):
    return suite_name.split(" / ")[-1].startswith("D-")


def failed_requests(junit_path):
    """({request name: [failure messages]} for requests with a failed assertion, number of defect requests)."""
    failures = {}
    suites = list(ET.parse(junit_path).getroot().iter("testsuite"))
    for suite in suites:
        for case in suite.iter("testcase"):
            failure = case.find("failure")
            if failure is not None:
                message = (failure.get("message") or "").splitlines()[0]
                failures.setdefault(suite.get("name"), []).append(f"{case.get('name')}: {message}")
    return failures, sum(is_defect(suite.get("name")) for suite in suites)


def main():
    run = Path(sys.argv[1])
    mode = (run / "mode").read_text().strip()
    exit_code = int((run / "exit-code").read_text().strip())
    totals, average, duration = cli_totals((run / "cli.txt").read_text())
    failures, defect_count = failed_requests(run / "junit.xml")

    requests_run, requests_failed = totals.get("requests", (0, 0))
    assertions_run, assertions_failed = totals.get("assertions", (0, 0))
    scripts_failed = totals.get("test-scripts", (0, 0))[1]

    if mode == "defects":
        present = sum(is_defect(name) for name in failures)
        verdict = f"**{present} of {defect_count} known defects still present**"
        if present < defect_count:
            verdict += f" ({defect_count - present} now pass: DummyJSON may have fixed them, update the matrix)"
    else:
        verdict = "**PASS**" if exit_code == 0 else "**FAIL**"
    title = {"main": "API tests", "data": "Data-driven search", "defects": "Known defects"}[mode]

    lines = [
        f"### {title}: {verdict}",
        "",
        "| Requests | Assertions | Failed assertions | Failed scripts | Average response | Duration |",
        "|---|---|---|---|---|---|",
        f"| {requests_run} | {assertions_run} | {assertions_failed} | {scripts_failed} | {average} ms | {duration} |",
    ]
    if requests_failed:
        lines.append(f"\n{requests_failed} request(s) had a network error.")
    if failures:
        lines += ["", "| Request | Failure |", "|---|---|"]
        for name, messages in failures.items():
            for message in messages:
                lines.append(f"| {name} | {message.replace('|', '/')} |")
    summary = "\n".join(lines) + "\n"
    (run / "summary.md").write_text(summary)
    print(summary)


if __name__ == "__main__":
    main()
