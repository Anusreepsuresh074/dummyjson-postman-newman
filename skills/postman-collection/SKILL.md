---
name: postman-collection
description: Turns the approved context/test-case-matrix.md (from api-test-design) and context/api-auth.md (from get-api-auth) into a Postman v2.1 collection, an environment file and iteration data — one request per matrix row, pm.test assertions for status, body, JSON Schema and response time, token chaining through variables, data-driven folders, and known defects isolated in their own folder — then validates it with a live Newman run and records what was observed. Never invents a test case that isn't in the approved matrix, never commits a credential, and never edits the matrix. Use after api-test-design's matrix has been reviewed and approved.
---

# Postman Collection

Builds the runnable test suite. The matrix says *what* to test; this skill
decides *how* it looks in Postman and proves it runs.

## When to use

- After `api-test-design` has produced `context/test-case-matrix.md` **and a
  human has approved it**.
- Again whenever the matrix changes: add, change or remove only the requests
  whose rows changed.

## Guardrails

- **The matrix is the contract.** Every request maps to a matrix row by its
  Case ID (written in the request description); no request without a row, no
  row without a request.
- **Assert the correct behaviour.** A row marked as a known defect still
  asserts what the API *should* do. Those requests live in a separate
  `Known defects` folder, which CI runs without gating the build, so the main
  run stays green while the defects stay visible and are re-checked on every
  run.
- **No credentials in the collection or environment files.** `username` and
  `password` arrive at run time with `--env-var`; tokens are set with
  `pm.environment.set` during the run and never exported to disk.
- **Chaining, not hard-coding.** Values produced by one request (tokens,
  ids) are saved to variables by its test script and used by later requests
  as `{{variable}}`. No token or id copied from a response into the file.
- **One place for shared rules.** Checks every request needs (JSON content
  type on bodies, response time under `{{maxResponseMs}}`, a standard error
  shape on 4xx) live in the collection-level test script, not copied per
  request. Shared JSON Schemas live in collection variables and are read with
  `JSON.parse(pm.collectionVariables.get(...))`.
- **No hidden authentication.** If the API also sets auth cookies (many do at login), turn the cookie jar off for the collection (`protocolProfileBehavior.disableCookies: true`); otherwise Newman sends them on every later request and "no token" cases pass for the wrong reason.
- **Order matters.** Newman runs requests top to bottom, so the auth folder
  that sets the tokens comes first, and each folder can also run on its own
  (it logs in itself when it needs a token).

## Collection layout

```
<API> collection
├── (collection) variables: shared schemas; test script: shared rules
├── 01 Auth              login, current user, refresh, auth negative cases
├── 02 Products          list, paging, select, sort, filters, by id
├── 03 Search and categories
├── 04 Product writes    add, update, delete (read-your-write where it applies)
├── 05 Protected routes  the Bearer-protected mirror of product routes
├── 06 Data-driven search  one request, run with -d data/<file>.csv
└── 99 Known defects     correct-behaviour assertions for recorded defects
```

## Writing each request

1. Name it as the behaviour it verifies (the matrix's test name in plain
   words), and put the Case ID and rule in its description.
2. Use `{{baseUrl}}` and variables; no literal host.
3. Tests: status first, then body facts, then the schema with
   `pm.response.to.have.jsonSchema(schema)`. Use Postman dynamic variables
   (`{{$randomProductName}}` style) or a pre-request script for unique data.
4. For data-driven rows, read the iteration row with `pm.iterationData.get()`
   and keep the CSV small and readable.

## Validation phase

1. Run everything with `scripts/run-newman.sh`, main folders first, then the
   known-defects folder.
2. Every main-folder assertion must pass; every known-defect assertion must
   fail for the documented reason. A known defect that now passes means the
   API was fixed: report it so the matrix and the folder get updated.
3. Run `scripts/check-secrets.sh` on the reports.
4. Record what was observed (counts, anything new) in
   `context/newman-validation-report.md`.

## Output

`collections/<name>.postman_collection.json`,
`environments/<name>.postman_environment.json`, `data/*.csv`, and
`context/newman-validation-report.md`. Hand over to `newman-report`.
