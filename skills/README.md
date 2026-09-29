# Skills

The reusable steps this project was built with, run in order by
[`agents/postman-automation-agent.md`](../agents/postman-automation-agent.md).

| Order | Skill | Origin | What it produces here |
|---|---|---|---|
| 1 | [`create-postman-structure`](create-postman-structure/SKILL.md) | new for Postman | folders, local Newman, `scripts/run-newman.sh`, `scripts/check-secrets.sh` |
| 2 | [`get-context`](get-context/SKILL.md) | shared | `context/api-context.md` |
| 3 | [`get-api-auth`](get-api-auth/SKILL.md) | shared | `context/api-auth.md` |
| 4 | [`api-test-design`](api-test-design/SKILL.md) | shared | `context/test-case-matrix.md` (stops for review) |
| — | [`coverage-audit`](coverage-audit/SKILL.md) | shared | `context/coverage-audit-report.md` |
| 5 | [`postman-collection`](postman-collection/SKILL.md) | new for Postman | the collection, environment, data and `context/newman-validation-report.md` |
| 6 | [`newman-report`](newman-report/SKILL.md) | new for Postman | `summary.md` per run, the report site |
| 7 | [`postman-ci-integration`](postman-ci-integration/SKILL.md) | new for Postman | `.github/workflows/newman.yml` |

**Shared skills** are identical copies of the ones in the companion pytest project,
[`ecommerce-api-automation/skills/`](https://github.com/Anusreepsuresh074/ecommerce-api-automation/tree/main/skills),
so the same discovery and test-design process feeds both tools. Their text names that project's
downstream skills (`pytest-api`, `create-report`, `teardown`, `change-impact-analysis`, `flaky-test-triage`)
and pytest details such as fixtures and `conftest.py`. In this project:

- `pytest-api` → `postman-collection`, and `create-report` → `newman-report`;
- pytest fixtures → Postman variables (see `context/api-auth.md`);
- `teardown` isn't needed: DummyJSON never saves writes;
- `change-impact-analysis` and `flaky-test-triage` live in the companion project and weren't needed here.
