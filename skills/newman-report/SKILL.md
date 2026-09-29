---
name: newman-report
description: Turns Newman run output already on disk (htmlextra HTML, JUnit XML, the CLI summary) plus context/newman-validation-report.md into the deliverables people read — a browsable HTML report per run, a short Markdown summary for the README (requests, assertions, pass/fail, average response time, known defects), and an index page when several reports are published together. Never runs Newman itself, never edits the collection, and never re-decides a test result. Use after postman-collection's validation run, or standalone whenever someone wants "a report" from the latest run.
---

# Newman Report

Makes the results of a run easy to read and share. Everything it needs is
already on disk; its job is to find it and present it.

## When to use

- Right after `postman-collection`'s validation run.
- Standalone: "give me a report" from whatever the latest run left in
  `reports/`.

## Guardrails

- **Report what happened, not what should have.** Counts come from the run
  files (the CLI summary and JUnit XML), never from memory or the matrix.
  The verdict comes from Newman's exit code: JUnit XML leaves out script
  errors, so a run with a broken test script can look clean in JUnit alone.
- **Keep the two runs apart.** The main run decides pass or fail. The
  known-defects run is reported separately as "defects still present: N of
  M", so a reader never mistakes expected defect failures for regressions.
- **No secrets in any report.** Run `scripts/check-secrets.sh` before a report
  is published or linked. htmlextra must be run with its sensitive-data
  options on (`--reporter-htmlextra-skipSensitiveData` or an equivalent
  redaction), so request bodies with credentials and token headers are not
  written out.
- **Publishable paths only.** Reports that will go to GitHub Pages use
  relative links and no local file paths.

## Steps

1. Find the latest `reports/<timestamp>/` folder (or the one named).
2. Read the totals from the CLI summary: requests, assertions, failed
   assertions, failed scripts, average response time and duration.
3. Write `reports/<run>/summary.md` with a one-line verdict first (PASS or
   FAIL from the exit code; for the known-defects run, "N of M known defects
   still present"), the totals table, and one row per failed assertion
   (request and failure message) from `junit.xml`.
4. When publishing several reports together (main and known defects), write a
   small `index.html` that links to each and shows the one-line verdicts.
5. Update the README's results section with the latest totals and the date.

## Output

`reports/<timestamp>/summary.md`, the HTML reports, an `index.html` for
publishing, and the README results section. Hand over to
`postman-ci-integration`.
