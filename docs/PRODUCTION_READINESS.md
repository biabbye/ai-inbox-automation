# Production-readiness release gate

**A checklist is not proof of production readiness.** Each item requires an owner, evidence, and explicit human sign-off. This is a target, not current status.

## Product safety

- [ ] No outbound mail without active authorized connection, exact-version human approval and backend authorization.
- [ ] Correct sender/recipient, reply threading, idempotent send and duplicate/replay protection.
- [ ] Human escalation path visible and usable when AI is wrong or unavailable.
- [ ] Measured AI evaluation results on representative and adversarial test sets.

## Access and privacy

- [ ] Dashboard authentication, strong session security, organization membership and role enforcement.
- [ ] Cross-organization isolation tested in API, SQL/RLS, RAG, queues and audit reads.
- [ ] Google/Microsoft OAuth state, redirect URI, refresh/revoke, consent and encryption tested.
- [ ] Data minimization, retention/deletion/export, privacy notices, processor agreements and data residency reviewed.
- [ ] Gmail restricted-scope verification/security assessment obligations assessed and completed where applicable.
- [ ] Dependency review, secrets scanning, input validation and prompt injection tests passed.

## Operational resilience

- [ ] Queue and worker survive restart, recover missed changes and handle dead-letter cases.
- [ ] Gmail watch / Graph subscription lifecycle & reconciliation procedures documented (if push enabled).
- [ ] Backups/restores tested; storage and key rotation plan reviewed.
- [ ] Structured logging and metrics without sensitive content; alerting thresholds validated.
- [ ] Rate limits, API quota/backoff, provider outages and token expiry are observable and recoverable.

## Delivery

- [ ] Separate environments/configs and least-privilege deployment identities.
- [ ] CI enforces automated checks, migration review and dependency pinning.
- [ ] Runbooks cover incident response, customer disconnect, data deletion and rollback.
- [ ] Verified staging end-to-end demo with both Google and Microsoft test accounts.
- [ ] Human release review signs off documented residual risks and operational ownership.

## Release decision template

| Gate | Evidence link or test output | Owner | Status |
|---|---|---|---|
| Security / tenant isolation | TBD | TBD | Not assessed |
| Gmail OAuth/commercial obligations | TBD | TBD | Not assessed |
| Outlook consent and subscriptions | TBD | TBD | Not assessed |
| Sending + idempotency | TBD | TBD | Not assessed |
| AI eval and fallback | TBD | TBD | Not assessed |
| Backup/monitoring/incident runbook | TBD | TBD | Not assessed |
