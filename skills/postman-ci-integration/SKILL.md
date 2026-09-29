---
name: postman-ci-integration
description: Builds the GitHub Actions pipeline for a Postman + Newman project — installs the pinned Newman with npm ci, validates the collection JSON, runs the main folders as the gating job and the known-defects folder as a non-gating job, runs the data-driven folder with its CSV, checks the reports for leaked secrets, uploads them as artifacts, and publishes the HTML reports to GitHub Pages. Uses only secrets and schedules the user has confirmed. Never edits the collection or the matrix. Use once the collection passes locally, and again whenever a new folder, data file or environment is added.
---

# Postman CI Integration

Makes the collection run by itself on every change, and puts the reports
where anyone can see them.

## When to use

- After `postman-collection` has a collection that passes locally and
  `newman-report` has produced a report.
- Again when a folder, data file, environment or schedule is added.

## Guardrails

- **Confirmed values only.** Secret names, schedule, branches and the Pages
  set-up are confirmed with the user; none is invented.
- **Secrets from the platform.** Credentials come from repository secrets as
  environment variables and reach Newman through `scripts/run-newman.sh`.
  If the secrets are missing (for example on a fork), the live run is skipped
  with a clear message instead of failing with a login error.
- **Gate on what matters.** The main run must pass for the build to be green.
  The known-defects run never fails the build, but its summary is shown on the
  run page, so a fixed defect is noticed.
- **Same command as local.** CI calls `scripts/run-newman.sh`, exactly as a
  person would, so a local pass and a CI pass mean the same thing.
- **One run at a time** against a shared public API (a `concurrency` group).

## Pipeline

1. **Static checks:** `npm ci`; parse every collection, environment and data
   file; shellcheck the scripts.
2. **API tests (gating):** `scripts/run-newman.sh main`, then the data-driven
   folder with its CSV; `scripts/check-secrets.sh`; upload `reports/` as an
   artifact; add the summary to the job summary.
3. **Known defects (non-gating):** `scripts/run-newman.sh defects` with
   `continue-on-error: true`; its summary goes to the job summary too.
4. **Publish:** on pushes to `main` (and on manual runs), assemble the HTML
   reports and `index.html` and deploy them to GitHub Pages.
5. **Triggers:** push, pull request, a manual run, and a confirmed nightly
   schedule.

## Output

`.github/workflows/newman.yml`, a CI badge and the reports link in the
README.
