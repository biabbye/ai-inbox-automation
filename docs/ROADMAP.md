# Incremental learning roadmap — one milestone at a time

Do **not** implement all milestones. The learner explicitly starts/stops each one. Each milestone includes a minimal demo and test; later milestones must not be preemptively scaffolded. This sequence is adjustable by approved ADR, but **security prerequisites may not be skipped**.

## M0 — Repo and dev environment

**Learn:** repo organization, Python environment with `uv`, virtualenv, dependency locking, Docker Compose/Supabase CLI choices, project docs, `.gitignore` and env templates.

**Deliverable:** reproducible README for local startup and a minimal Git repo; no app code until user approves M1.

**Exit gate:** learner can explain frontend/backend/DB/AI boundaries and verify Python, Node, Docker availability. No secret committed.

**First exercise:** inspect installed `python --version`, `node --version` and `docker version`, report results, then decide Python version and package manager. **Stop there.**

## M1 — Python/FastAPI/Pydantic fundamentals

**Learn:** routers, type hints, async I/O, Pydantic schemas, input validation, HTTP errors, dependency injection, unit tests.

**Deliverable:** `GET /health` then one `POST /tickets` endpoint with synthetic input; pytest tests; Swagger/OpenAPI inspection.

**Exit gate:** malformed requests rejected appropriately; tests pass. Learner can explain request model vs response model.

## M2 — Database and authenticated dashboard baseline

**Learn:** PostgreSQL, SQLAlchemy 2, migrations, Supabase Auth, Next.js SSR session concepts, role-based API authorization.

**Deliverable:** persisted ticket list and protected dashboard route; first organization membership checks and cross-organization denial tests.

**Exit gate:** auth flow works locally; unauthorized or cross-org ticket requests denied at backend; migration is repeatable.

## M3 — AI classifier and structured extraction

**Learn:** prompts, API call lifecycle, model adapter, Pydantic structured outputs, deterministic policy checks, mocking, costs.

**Deliverable:** classify category, urgency, summary and missing information for synthetic inbox messages; persist AI run status.

**Exit gate:** evaluation fixtures demonstrate expected behavior; model failures are safe; no auto-send.

## M4 — RAG / company knowledge

**Learn:** chunking, embeddings, pgvector, retrieval, citations, grounding, fallback, prompt injection threat.

**Deliverable:** ingest controlled sample FAQ/policies, retrieve org-scoped chunks, draft a grounded answer.

**Exit gate:** unknown-answer test escalates instead of inventing policy; cross-org retrieval denied.

## M5 — Outlook read-only connection

**Learn:** Entra app registration, delegated OAuth, token storage/refresh, Microsoft Graph API, read-only polling/delta.

**Deliverable:** one consented test Outlook mailbox provides eligible inbound test messages to the normalized pipeline.

**Exit gate:** callback state validated, encrypted tokens, reconnect state, dedup and no non-test mailbox access. No send yet.

## M6 — Gmail read-only connection

**Learn:** Google Cloud OAuth consent, restricted Gmail read scope implications, sync/history, provider adapter.

**Deliverable:** one consented test Gmail mailbox uses the **same** ticket processing pipeline.

**Exit gate:** both providers pass shared contract tests; duplicate message prevention; access tokens never shown in UI/logs. No send yet.

## M7 — Review, approval and replies

**Learn:** ticket state machine, optimistic concurrency, human-in-the-loop, approval audit, send permissions and thread preservation.

**Deliverable:** operator can edit and approve a specific version; backend sends only after policy checks; provider-specific send tests.

**Exit gate:** unapproved/edited/replayed sends are blocked; correct mailbox + thread; immutable audit log entries.

## M8 — Background processing and push notifications

**Learn:** durable queue, worker design, idempotency, retry/backoff, timeouts, DLQ, Google Pub/Sub and Graph subscriptions.

**Deliverable:** resilient incremental sync with reconciliation, safely deployed webhook handlers and monitoring of queue/sync health.

**Exit gate:** simulated duplicate, delayed and lost notification tests; expired subscription renewal and recovery; worker restart recovery.

## M9 — Security, evaluation and observability hardening

**Learn:** threat modeling, RLS/tenant tests, secrets rotation, rate limits, OWASP LLM risks, traces, structured logs, eval metrics.

**Deliverable:** security checklist, evaluation suite, alerting and retention/deletion flow with evidence.

**Exit gate:** `PRODUCTION_READINESS.md` critical security and reliability items are met, with proof and exceptions documented.

## M10 — Delivery and commercialization-ready demo

**Learn:** CI/CD, containers, managed deployment, staging/prod separation, costs, documentation, handover and safe customer pilot.

**Deliverable:** deployed staging app, runbook, architecture diagram, demo dataset/metrics, clear readiness review.

**Exit gate:** human signs off on release and documented privacy/compliance/provider-verification obligations; only then call it a production candidate. Never assume Google verification is automatically satisfied.

## Progress protocol

Only one milestone is **active**. `docs/PROGRESS.md` records confirmed output and evidence. The agent always proposes the next small exercise within the active milestone and waits. If user requests a later topic, explain relevant prerequisites and teach it conceptually without pretending all earlier steps are implemented.
