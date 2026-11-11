# Architecture decision register (ADR-lite)

**Status:** proposals below reflect the current scope; they are not decisions about installed software or implemented functionality. Before deviating, explain tradeoffs to the learner and obtain approval. Record small ADRs with context, options, decision and consequences.

| ID | Topic | Proposed default | Status / rationale |
|---|---|---|---|
| ADR-001 | Primary language | Python 3.12+ for backend; TypeScript for Next.js | Proposed. Builds Python depth while using existing React skills. |
| ADR-002 | API framework | FastAPI + Pydantic v2 | Proposed. Clear typed boundaries and OpenAPI. |
| ADR-003 | Persistence | PostgreSQL; SQLAlchemy 2 + Alembic; Supabase Auth/pgvector when needed | Proposed. Separate domain data modeling from session provider; preserve migrations. |
| ADR-004 | AI model | Provider adapter, begin with Azure OpenAI or compatible provider after comparing availability/cost | Open provider/config decision. No keys without explicit user action. |
| ADR-005 | Agent framework | Python functions first; add LangGraph only for durable/conditional HITL workflows | Proposed. Avoid premature orchestration. |
| ADR-006 | Inbox providers | Gmail API and Microsoft Graph delegated OAuth, shared normalized schema | Target requirement; connect read-only first. |
| ADR-007 | Ingestion | Local polling/delta baseline before webhook push | Proposed. Simple to debug; add reliability later. |
| ADR-008 | Sending | Human approval required before every outbound reply in v1 | **Accepted product safety rule** from project intent. |
| ADR-009 | Tenancy | Model organization IDs early, harden multi-tenant access before live SaaS | Proposed. Single test org initially. |
| ADR-010 | Deployment | Local first; Azure containers + managed Postgres/Vercel or Azure frontend later | Open. Compare data residency, secrets and cost. |
| ADR-011 | Frontend/API auth boundary | Supabase SSR session with verified FastAPI auth; choose direct API vs BFF during M2 | Open. Must consider browser cookie security & authorization. |
| ADR-012 | Worker | Persistent queue with separate worker at M8 | Open backend technology; do not rely solely on process memory. |

## Template for a new decision

```markdown
### ADR-XXX — Title
Date: YYYY-MM-DD
Status: Proposed / Accepted / Superseded
Context: What problem are we solving now?
Options: A (advantages, costs), B (advantages, costs)
Decision: What did the learner approve?
Consequences: What becomes simpler/harder? What must be tested?
```

## Unresolved questions (not blockers for M0)

- What is the desired long-term hosting setup and monthly budget?
- Which Azure OpenAI deployment is available for testing, or should an alternate model provider be used?
- Should first pilot support organization have only one mailbox or multiple connections?
- How much retention of email content is actually needed, and what jurisdictions/customer requirements apply?
- For commercial Gmail launch, what authorization/verification process applies to the actual deployment and data handling?

Do not demand answers to all questions before teaching M0. Raise them only when the relevant milestone is reached.
