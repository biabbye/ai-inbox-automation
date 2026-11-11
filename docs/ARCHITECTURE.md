# Architecture — target design and progressive implementation

Status: **proposed target architecture**, not implemented. Decisions with alternatives live in `docs/DECISIONS.md`.

## Conceptual flow

```text
[Gmail mailbox] --- OAuth + Gmail API ---\
                                      [Email connector layer]
[Outlook mailbox] -- OAuth + Graph ----/        |
                                               v
                                      [Ingestion + dedup]
                                               |
                             [Persistent queue / worker, later]
                                               |
                                         [Python FastAPI]
                                      [Pydantic normalized data]
                                               |
                               [Classification / RAG / draft]
                                               |
                                         [PostgreSQL]
                                               |
     [Supabase Auth] -> [Next.js dashboard] -> [review/approve]
                                               |
                                 [policy-checked send action]
                                               |
                               [Gmail API OR Microsoft Graph]
```

**Reminder:** a polling loop is enough for a local learning pilot. Webhooks/push and a persistent worker are later production concerns; external callbacks must never do expensive LLM work synchronously.

## Responsibilities and boundaries

### Frontend (Next.js, TypeScript)

- Sign-in, dashboard, ticket list/detail, search/filter, knowledge management, connection status and approval UI.
- Use server-side auth validation; don't expose provider refresh tokens or Supabase privileged secrets to browser JS.
- Use a browser-to-backend strategy that preserves safe auth/session behavior; formalize BFF vs direct API in an ADR before implementing.

### API (Python 3.12+, FastAPI, Pydantic v2)

- Auth verification, authorization checks, API validation, tickets, OAuth callbacks, connection lifecycle, approval/send commands.
- Use explicit service boundaries: `tickets`, `integrations`, `ai`, `knowledge`, `audit`, `auth`.
- Use async I/O for network/DB where appropriate; don't block API requests with long-running sync or LLM processing.

### Database & identity

- Chosen target: **PostgreSQL, Supabase Auth** for app accounts; local Supabase CLI stack once auth is introduced, with containerized Postgres for initial experimentation if needed. Prefer a *single logical schema/migration history* rather than two competing environments.
- SQLAlchemy 2 + Alembic for backend domain models; use Postgres `pgvector` when RAG arrives.
- Start with organization-aware tables (`organization_id` foreign keys), even if only one test company exists in early stages.
- Browser-to-Postgres access must respect RLS. If backend uses a privileged DB credential that bypasses RLS, ensure explicit membership/tenant checks on every query and action. Prefer a least-privilege backend role and apply RLS where feasible.

### LLM & knowledge

- Initial LLM adapter for Azure OpenAI/OpenAI with mockable interface; model/version configured, not embedded throughout code.
- Begin with classification and Pydantic structured results; add RAG later using approved company documents.
- Retrieval filtered by organization, document permissions and state; store source IDs, versions and citations in drafts.
- Never pass provider tokens, secrets, or other organizations' material into LLM context.
- LangChain components are optional; introduce LangGraph when approvals/resume/branching justify it, not by default.

### Email integration module

- A provider-neutral `EmailProvider` contract with `list_changes`, `get_message`, `send_reply`, `get_connection_status`.
- Two adapters: Gmail API and Microsoft Graph; do not leak Graph/Gmail response fields into core ticket models.
- Inbound DTO includes: `organization_id` (resolved by trusted server), `connection_id`, `provider`, `provider_message_id`, `provider_thread_id`, `sender`, `recipients`, `subject`, `plain_text_body`, `received_at`, `attachment_metadata`.
- Sanitization and text extraction are separate from provider SDK mapping. No raw HTML rendered without sanitization.

## Suggested logical data model (initial, evolve through ADRs)

- `organizations`, `organization_members`, `profiles` (map to Supabase auth IDs)
- `mailbox_connections` (provider, external account ID, state, encrypted token reference, last sync cursor)
- `inbound_messages` (unique on connection + provider message ID), `tickets`, `ticket_events`
- `draft_replies` (version, source evidence, status), `send_attempts` (idempotency key)
- `knowledge_documents`, `knowledge_chunks` (org-scoped embeddings)
- `processing_jobs`, `audit_events`, `ai_runs` (status, costs and non-sensitive error categories)

Do not implement every table immediately. Define them as milestones require, through migrations and tests.

## Internal processing state machine

```text
RECEIVED -> VALIDATED -> CLASSIFIED -> DRAFTED -> AWAITING_REVIEW
                                            |           |
                               NEEDS_HUMAN <-+           +-> APPROVED
                                                               |
                                                            SENDING
                                                               |
                                                   SENT / SEND_FAILED
```

- A ticket and a draft are **not the same entity**. A draft can be edited/versioned; approved version must be the version sent.
- Terminal/exception states (`FAILED`, `RETRY_PENDING`, `RECONNECT_REQUIRED`) are explicit, not hidden.
- Send requires authorization, a matching connection, an approved draft version, anti-duplicate constraints and an audit event.

## Target deployment (later)

- Next.js on Vercel or Azure; Python API + worker on Azure Container Apps (or equivalent); managed Postgres/Supabase; secrets in a managed vault; HTTPS only; structured logging/metrics/traces; queue; backup/restore tests.
- Cross-cloud egress, data residency, vendor DPAs and customer policy must be evaluated **before** real external data are processed. Azure Foundry may be explored only after core architecture is stable.

## Official documentation

- Supabase Auth: https://supabase.com/docs/guides/auth
- Supabase Auth SSR (Next.js): https://supabase.com/docs/guides/auth/server-side
- Supabase local development: https://supabase.com/docs/guides/local-development
- PostgreSQL pgvector: https://github.com/pgvector/pgvector
- FastAPI background tasks caveat: https://fastapi.tiangolo.com/tutorial/background-tasks/
