# Engineering standards (apply when code is introduced)

## General

- Favor **readable, testable, modular code over unnecessary abstraction**. No speculative framework or multi-agent architecture.
- Explain the purpose of each new file, dependency, configuration variable and background process to the learner.
- Prefer official SDKs/APIs and supported stable versions; check versions during implementation; lock dependencies.
- Avoid copy-paste secrets or personal inbox data in code, tests, prompts, screenshots or commits.
- One small, reviewable change per learner-approved implementation step.

## Python backend

- Python 3.12+ compatible target (pin tested version when creating project); `uv` + `pyproject.toml`; FastAPI; Pydantic v2; SQLAlchemy 2; Alembic.
- Type hints for public methods; API schemas separate from SQLAlchemy models; explicit service boundaries; validate inputs at all external edges.
- Use `httpx.AsyncClient` or supported provider SDKs for async HTTP; explicit timeout, retry policy for idempotent operations and bounded concurrency.
- Use pytest with fixtures, mocked LLM/provider clients, and regression cases. Avoid tests that require live OAuth credentials or real emails.
- Handle errors with structured exception types and safe user-facing messages; don't log raw auth tokens, email bodies or unredacted stack locals.

## Frontend

- Next.js + TypeScript, accessible components, typed API clients; auth-guarded routes and actions; no role checks solely in client code.
- Provide loading, empty and failure states; never make provider connection state look successful until backend confirms.
- Never render email HTML directly without sanitization; plain text is the default for early milestones.

## Database

- Migrations are version-controlled and reproducible; uniqueness constraints enforce deduplication; transactions protect multi-step state changes.
- Store UTC timestamps; stable internal IDs separate from provider IDs; use organization-scoped queries and RLS where appropriate.
- Never store OAuth secrets in plaintext; avoid destructive migrations without backup/data migration plans.

## AI and RAG

- Model provider behind a small adapter; prompt templates versioned; configured temperature/context limits.
- Pydantic schema validation is necessary but not sufficient: enforce allowlisted categories and deterministic business policies.
- Record retrieved source IDs/versions and the model/prompt version for debugging; never log full sensitive prompts by default.
- Use uncertainty fallback and human review; keep the LLM out of permission decisions.

## Reliability and deployment

- Persist processing state and sync cursor. Retries must be bounded with backoff, idempotency and clear failure status.
- Use a durable worker/queue for production-scale mail sync/LLM workloads; don't rely solely on in-process background tasks.
- Structured metrics: processing latency, queue age, error rate, sync delay, duplicate rate, model cost/token usage, review/sending outcome.
- CI: formatting/lint, types, backend/frontend tests, dependency and secret checks; deployment separately approved.

## Suggested quality commands (after tools have been installed)

```bash
# Backend candidates; actual scripts must be documented when created
uv run ruff check .
uv run pytest
uv run mypy app  # only after mypy config agreed

# Frontend candidates
npm run lint
npm run build
```

These are **examples**, not evidence that a repository already has these commands. The agent must first check actual package scripts and configuration, and should not run migrations or live integrations without permission.

## Definition of done for one implementation slice

- Explains the change in Romanian and the exact file paths.
- Verification is described and, if executed, real output recorded; no false "tests passed" claims.
- Tests cover happy path and one relevant failure/security case.
- No unexpected dependency, secret or change outside scope.
- Learner can summarize how the feature works and what should be implemented next.
