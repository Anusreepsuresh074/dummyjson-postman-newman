# DummyJSON API Tests: Postman + Newman

![API tests](https://github.com/Anusreepsuresh074/dummyjson-postman-newman/actions/workflows/newman.yml/badge.svg)
**[Live reports](https://anusreepsuresh074.github.io/dummyjson-postman-newman/)**

**Latest result** (verified locally on 2026-09-30 with the same `scripts/run-newman.sh` runs CI uses): main 219 of 219 assertions passed, data-driven 29 of 29 passed, 13 of 13 known defects still present.

A **Postman** collection for the [DummyJSON](https://dummyjson.com) e-commerce API, run from the command line and in CI with **Newman**. It covers the JWT auth flow (login, current user, refresh) and the products resource: paging, field selection, sorting, validation, search, categories and simulated writes.

**61 requests in 7 folders, built from a 61-row test case matrix that was audited against every endpoint and business rule before any request was written.** Every request asserts its status, the body facts that matter, and a JSON Schema where the shape is known; shared checks (response time, JSON content type, the standard error body) run on every request from one collection-level script. Tokens are chained through variables, one folder is data-driven from a CSV file, and 13 real API defects are kept visible in their own folder without breaking the build.

```
main run      46 requests (+3 sent by pre-request scripts), 219 assertions, 0 failed   (~22 s)
data run       6 iterations,  29 assertions, 0 failed
defects run   14 requests (+1 sent by a pre-request script), 50 assertions, 13 failed: the 13 known defects (expected)
```

This is the Postman companion to my [DummyJSON API test automation in Python + pytest](https://github.com/Anusreepsuresh074/ecommerce-api-automation) and my [DummyJSON performance tests in JMeter](https://github.com/Anusreepsuresh074/ecommerce-performance-testing): the same API, tested for correctness in two tools and for speed in a third.

## What this project demonstrates

| Skill | Where to see it |
|---|---|
| **Test design before tooling:** a 61-row matrix, each row traced to a business rule, audited with `coverage-audit` and approved before any request was built | [`context/test-case-matrix.md`](context/test-case-matrix.md), [`context/coverage-audit-report.md`](context/coverage-audit-report.md) |
| **Postman scripting:** `pm.test` assertions, `pm.response.to.have.jsonSchema`, pre-request scripts, `pm.sendRequest`, decoding a JWT with `crypto-js` | the collection's test and pre-request scripts |
| **Chaining:** the login token, the refreshed token, a new product id and category slugs flow from one request to the next through variables | `01 Auth`, `03 Search and categories`, `04 Product writes` |
| **Shared rules in one place:** collection-level scripts and JSON Schemas stored as collection variables | the collection's own Scripts and Variables tabs |
| **Data-driven testing:** one request, one iteration per CSV row | [`data/search-terms.csv`](data/search-terms.csv), `06 Data-driven search` |
| **Read-your-write checks:** DummyJSON simulates writes, and the tests prove it by reading back | `04 Product writes` |
| **Known defects handled honestly:** correct-behaviour assertions in a separate, non-gating folder | `99 Known defects` |
| **Security hygiene:** credentials only at run time, cookies off, no bodies or headers in reports, every report scanned for leaks | [`scripts/run-newman.sh`](scripts/run-newman.sh), [`scripts/check-secrets.sh`](scripts/check-secrets.sh) |
| **CI/CD:** static checks, gating and non-gating runs, job summaries, artifacts, reports on GitHub Pages, nightly schedule | [`.github/workflows/newman.yml`](.github/workflows/newman.yml) |
| **Root-causing, not retrying:** two real problems found during validation, fixed at the cause | [`context/newman-validation-report.md`](context/newman-validation-report.md) |

## Collection layout

| Folder | Requests | What it covers |
|---|---|---|
| `01 Auth` | 12 | Login (valid, wrong password, unknown user, missing fields, malformed JSON, token lifetime), current user with and without a token, refresh, and the refreshed token working (and being a new token) |
| `02 Products` | 14 | Default page, limit and skip, `limit=0` (all 194 products schema-checked), past the end, select, sort, invalid limit / skip / order / date / delay, by id, unknown and non-numeric id |
| `03 Search and categories` | 7 | Search relevance and case, no match, both category lists agree, category filter, unknown category |
| `04 Product writes` | 7 | Add (new id = total + 1), update, patch, delete, with read-backs against the original values proving nothing is saved; unknown id |
| `05 Protected routes` | 6 | The Bearer-protected `/auth/products` routes (list, add, delete), with and without a token |
| `06 Data-driven search` | 1 × 6 rows | One search per CSV term, 5 with matches and 1 without |
| `99 Known defects` | 14 | 13 defects (below) plus a login; asserts the correct behaviour, so it fails until DummyJSON fixes them |

## Defects found

The same 13 defects the companion pytest suite pins as strict xfails, re-confirmed live on 2026-09-29.

| # | What happens | Should be |
|---|---|---|
| D-01 | `/auth/me` returns the user's password, SSN, EIN, bank and crypto details | not exposed |
| D-02 | A refresh token is accepted as an access token | `401` |
| D-03 | An access token is accepted as a refresh token | `403` |
| D-04 | A used refresh token is accepted again (no rotation) | `403` |
| D-05 | A token without the `Bearer ` prefix is accepted | `401` |
| D-06 | A malformed token returns `500` | `401` |
| D-07 | A forged signature returns `500` | `401` |
| D-08 | `Authorization: Basic <token>` returns `500` | `401` |
| D-09 | `expiresInMins: 43201` returns `500` | `400` |
| D-10 | `expiresInMins: -1` returns `500` with a misleading message | `400` |
| D-11 | Adding a product with an empty body returns `201` | `400` |
| D-12 | Adding a product with `price: "free"` returns `201` | `400` |
| D-13 | `PUT` returns 11 of the product's 22 fields | the full product |

## Design choices worth asking about

- **One environment file.** DummyJSON has a single public host, so there is no dev/staging split to model; adding one would be padding. A second environment would be one more file in `environments/`.
- **Strict schemas on purpose.** The login, refresh, product and category schemas forbid undocumented fields (`additionalProperties: false`), so a silently added or renamed field fails the run. That is a contract choice: a real API change is reviewed, not absorbed.
- **Auth declared on each request.** Every request states its auth (Bearer, or none for negative cases) instead of inheriting it, because the cookie finding below showed how inherited or hidden authentication can make a "no token" test pass for the wrong reason.
- **No secrets in failure messages.** Checks on the username and on tokens (the logged-in user is the test user, access and refresh tokens differ, a refreshed token is new) assert a true/false match instead of `eql`, because Chai's `eql` prints both values when it fails and the report would then contain the test user's name or a live token.
- **Variable scopes.** `username`, `password` and the three tokens live in the environment (the tokens and password as `secret`); values passed between requests during a run (totals, ids, slugs) are collection variables; per-request values are local.

## Found while building it

- **Login cookies were authenticating "no token" requests.** DummyJSON sets the tokens as cookies at login, and Newman keeps a cookie jar like a browser, so requests meant to have no token got `200`. The collection turns the cookie jar off (`protocolProfileBehavior.disableCookies`), so each request is authenticated only by what it declares.
- **The first request of a run sometimes failed with `AggregateError`.** `dummyjson.com` resolves to IPv6 and IPv4 addresses, and Node 20 gives each connection attempt only 250 ms. The run script tries IPv4 first and allows each attempt 2 s (`--dns-result-order=ipv4first --network-family-autoselection-attempt-timeout=2000`); every run since has passed.
- **Newman's JUnit output leaves out script errors**, so the verdict always comes from Newman's exit code, not from counting JUnit failures.
- **DummyJSON's Cloudflare refuses some default script user-agents** (error 1010), so every request sends an explicit `User-Agent`.

## Running it

Requires Node.js 20.19 or later (CI uses 22 LTS, from `.nvmrc`), npm, and Python 3.11+ for the two report scripts.

```bash
npm ci                               # Newman + the htmlextra reporter, pinned by package-lock.json
cp .env.example .env                 # fill in a published DummyJSON test user (see dummyjson.com/users)

npm test                             # the gating run: every functional folder (scripts/run-newman.sh main)
npm run test:data                    # the data-driven search, one iteration per CSV row
npm run test:defects                 # the known defects (expected to fail)

npm run check-secrets                # no password or token in any report
python3 scripts/summarize.py reports/<run>/     # summary.md for one run
python3 scripts/build-site.py        # site/: the latest reports behind one index page
```

Each run writes `reports/<UTC time>-<mode>/` with `report.html` (htmlextra), `junit.xml`, the CLI output and Newman's exit code.

**In the Postman app:** import `collections/dummyjson.postman_collection.json` and `environments/dummyjson.postman_environment.json`, then set `username` and `password` in the environment's *current* value only (never the initial value, which would be saved in the file).

## CI

[`.github/workflows/newman.yml`](.github/workflows/newman.yml) runs on pushes to `main`, pull requests, on demand, and nightly at 02:30 UTC (GitHub pauses scheduled runs after 60 days without repository activity):

1. **Static checks:** `npm ci`; every collection, environment and CSV file parses; shellcheck and ruff on the scripts.
2. **API tests:** the main and data-driven runs gate the build; the known-defects run is reported but never fails it. Each run's summary is added to the job summary, reports are scanned for secrets, and everything is uploaded as an artifact.
3. **Publish:** the latest HTML reports go to [GitHub Pages](https://anusreepsuresh074.github.io/dummyjson-postman-newman/) from `main` and manual runs.

Repository secrets needed: `AUTH_USERNAME`, `AUTH_PASSWORD`. Without them the run fails with a clear error, so a green badge always means the tests really ran; only pull requests from forks, which never get secrets, skip the live tests with a warning.

## Project structure

| Path | What it is |
|---|---|
| `collections/` | The Postman collection (v2.1): the source of truth |
| `environments/` | The environment file: `baseUrl`, the response-time limit, and empty slots for credentials and tokens (filled at run time) |
| `data/search-terms.csv` | Iteration data for the data-driven folder |
| `context/api-context.md` | The API's endpoints, business rules and observed behaviour |
| `context/api-auth.md` | How login, tokens and negative auth states work, and how tokens are kept out of files |
| `context/test-case-matrix.md` | The 61-row test design every request maps to |
| `context/coverage-audit-report.md` | The review of the matrix against every endpoint and rule |
| `context/newman-validation-report.md` | What the first live runs showed, including the defects and the fixes |
| `scripts/` | `run-newman.sh` (the one way to run), `check-secrets.sh`, `summarize.py`, `build-site.py` |
| `skills/`, `agents/` | The reusable skills this project was built with, and the agent that orders them |

## How it was built

Through the same reusable, AI-assisted workflow as my other projects: written [Claude Code](https://claude.com/claude-code) skills run in order by [`agents/postman-automation-agent.md`](agents/postman-automation-agent.md).

1. `create-postman-structure`: folders, local Newman, the run and secret-check scripts.
2. `get-context` and `get-api-auth`: the API's rules, re-verified live (33 calls) on 2026-09-29.
3. `api-test-design`: the test case matrix, then a stop for review; `coverage-audit` checked it against every endpoint and rule.
4. `postman-collection`: the collection, environment and data, validated with live runs.
5. `newman-report`: summaries and the report site.
6. `postman-ci-integration`: the GitHub Actions pipeline and Pages.

`get-context`, `get-api-auth`, `api-test-design` and `coverage-audit` are shared with the companion pytest project; the four Postman skills are new. Every result was run and checked, not assumed.
