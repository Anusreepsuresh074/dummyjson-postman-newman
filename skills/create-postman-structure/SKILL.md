---
name: create-postman-structure
description: Builds the empty skeleton of a Postman + Newman API test project from a blank repo — confirms the Newman version, environments and CI platform, presents the target folder structure with the reason for each folder, then creates each layer (collection, environment and data shelves, the local Newman install, the single run script, the secret-leak check, ignore rules, docs) only after explaining it. Never writes a request, a test script, a schema or API-specific logic — those belong to get-context, get-api-auth, api-test-design and postman-collection. Use once, at the start of a new Postman project, when there is no existing structure to extend.
---

# Create Postman Structure

Builds the skeleton that every other skill in the Postman workflow fills later:
`get-context` and `get-api-auth` write `context/`, `api-test-design` writes the
test case matrix, `postman-collection` writes the collection, environment and
data, `newman-report` writes reports, and `postman-ci-integration` writes the
pipeline. This skill never writes a request, a test or anything specific to
one API's business logic.

## When to use

- Once, on a blank repo, before any other skill in this workflow has anything
  to read.
- Never mid-project "to add a folder": extend an existing structure by hand.

## Guardrails

- **Plan before you build.** Present the full target tree with a one-line
  purpose per folder and get the user's confirmation before creating anything.
- **Local tools only.** Install Newman and its reporters as project
  `devDependencies` (`npm install --save-dev`), never globally, so every
  machine and CI run uses the versions pinned in `package-lock.json`.
- **No credentials, ever.** The committed environment file holds only
  non-secret values (`baseUrl`, limits). Usernames, passwords and tokens are
  passed at run time (`--env-var` from environment variables or CI secrets) or
  set by scripts during the run, and are never exported back to disk.
- **One way to run.** Every run, local or CI, goes through
  `scripts/run-newman.sh`. Downstream skills call it instead of writing their
  own `newman run` lines.
- **Create only what the current phase needs.** `collections/`,
  `environments/` and `data/` start empty with a short README each. Don't
  pre-create sample requests or guessed data.

## Target structure

```
<project>/
├── collections/        # the Postman collection (source of truth, v2.1 JSON)
├── environments/       # environment files: non-secret values only
├── data/               # CSV/JSON iteration data for data-driven runs
├── context/            # API facts, auth notes, test case matrix (other skills)
├── scripts/
│   ├── run-newman.sh   # the one way to run: env vars in, reports out, exit code
│   └── check-secrets.sh# fails if a password or token appears in any report
├── skills/, agents/    # this workflow's skills and the agent that orders them
├── .github/workflows/  # CI (postman-ci-integration)
├── reports/            # run output: gitignored
├── package.json        # Newman + reporters, pinned by package-lock.json
└── README.md
```

## Build phases

Explain each phase (what, why, where, how it connects), then create it:

1. **Step 0: confirm** the target base URL per environment, the Newman major
   version, the report formats (CLI, HTML, JUnit) and the CI platform
   (GitHub Actions by default).
2. **Shelves:** the folders above, each with a README saying which skill fills
   it; `.gitignore` for `node_modules/`, `reports/`, `.env` and `*.local.json`.
3. **Tooling:** `package.json`, then `npm install --save-dev newman
   newman-reporter-htmlextra`; confirm with `npx newman --version`.
4. **Run script:** `scripts/run-newman.sh <mode>`, one mode per kind of run
   (for example `main`, `data`, `defects`), reads credentials from
   environment variables, passes them with `--env-var`, writes CLI, HTML
   (htmlextra) and JUnit output plus Newman's exit code under
   `reports/<UTC time>-<mode>/`, and exits with Newman's code. Expose the
   modes as npm scripts (`npm test` for the gating run).
5. **Secret check:** `scripts/check-secrets.sh <report dir>` greps the reports
   for the password value and for anything shaped like a JWT, and fails if it
   finds one.
6. **Docs:** a README skeleton (purpose, how to run, structure). The results
   and design sections are filled by later skills.

## Output

The folders, `package.json` + lock file, the two scripts, `.gitignore` and the
README skeleton. Hand over to `get-context`.
