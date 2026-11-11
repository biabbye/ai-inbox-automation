# Security and privacy requirements

**These are project security requirements, not a compliance certification or legal advice.** All agents must consult them before touching auth, OAuth, email processing, storage or outbound actions. Real mailbox access is gated behind the relevant safeguards.

## 1. Trust boundaries

1. Browser/user input -> API: every request is untrusted until authenticated and authorized.
2. Google/Microsoft OAuth -> backend: verify `state`, callback origin/redirect URI and token audience; apply PKCE when supported; store/revoke tokens securely.
3. Incoming email/attachments -> parser/LLM: **untrusted content**, may include prompt injection, PII, malicious attachments and deceptive links.
4. Retrieved docs -> LLM: docs are data, not instructions with authority to execute actions.
5. LLM output -> action layer: **never** authorize sends, refunds, access or policy changes purely from model text.
6. Tenant data -> retrieval/worker/API: every read and write must be scoped to a server-resolved org identity.

## 2. Dashboard authentication is separate from mailbox OAuth

- **Application authentication:** Supabase Auth to identify dashboard users; secure SSR/session handling in Next.js, verified backend identity, membership lookup and role checks (`owner`, `admin`, `agent`, optional `viewer`).
- **Mailbox authorization:** a company admin explicitly connects an inbox through Google or Microsoft delegated OAuth. Permissions granted to a mailbox are **not** proof that the caller may see the company's tickets.
- Protect OAuth connect/disconnect endpoints to suitable org roles; audit all connection changes.
- FastAPI validates JWT signature, issuer, audience, expiry and authorized memberships. Never `jwt.decode()` without verification or trust a frontend-supplied organization ID.
- Enforce RLS for direct database access; for privileged server DB clients, enforce server-side tenant restrictions and avoid accidental RLS bypass.

## 3. OAuth permissions and token lifecycle

- Request least-privilege **read** scopes first. Add send scopes only when implementing explicitly approved email replies. Do not request full mailbox read/write or application-wide access by default.
- **Gmail:** `gmail.readonly` is a **restricted** scope and `gmail.send` a **sensitive** scope as of review date. Google verification/security assessment may apply before public SaaS launch, especially for server-side storage of restricted-scope data. Check precise user-data policy and scope requirements before launch.
- **Outlook/Graph:** delegated `Mail.Read` for reading and `Mail.Send` for sending, only with appropriate consent; don't use `Mail.ReadWrite` unless genuinely needed. For corporate tenants, check admin consent policies and tenancy settings.
- Use `state`, secure redirect URI allowlists, secure token refresh/reconnect handling, encrypted refresh tokens at rest, no refresh tokens in browser, logs or git. Use an audited encryption scheme with a key stored outside the database (managed vault/KMS in production) and a rotation/revocation plan.
- Handle invalid_grant, revoked permissions, removed mailboxes and user disconnect by stopping sync and marking `RECONNECT_REQUIRED` rather than silently skipping.

## 4. Email data, attachments and LLM safety

- Minimize collected data and default sync scope (e.g., one test mailbox/folder and bounded look-back). Document retention, deletion/export and customer consent/legitimate basis with legal review as appropriate.
- Treat email text and attachments as untrusted. Prevent HTML/script injection in UI; limit sizes/types; avoid arbitrary code execution; consider malware scanning for attachments in production.
- Never execute URLs, SQL, tool names or instructions present in email bodies. Maintain a fixed tool registry and policy layer with explicit parameters.
- Prompt injection cases: "Ignore prior instructions", fake internal policies, attachment containing system-like prompts, attempts to exfiltrate other tickets. These should not affect control flow or permissions.
- Sanitize/redact secrets and unnecessary PII before LLM calls, eval datasets, logs and traces; use provider data-handling agreements and choose region/residency with customer requirements in mind.
- Drafts citing company policy should reference trusted document IDs and versions; absent evidence => say unknown/escalate, never invent a policy.

## 5. Outbound email is a privileged action

- No automatic send. An authenticated, authorized human must inspect the final draft and explicitly approve it.
- Backend verifies approval references the **exact version** being sent and a still-authorized connection; use an atomic state transition and per-action idempotency key.
- Use provider APIs with correct reply/thread semantics; confirm sender identity and recipient. Filter self-sent messages and autoreplies to prevent loops.
- Record who approved, when, what version, which mailbox and provider result, without logging full message body unnecessarily.

## 6. App/API controls

- TLS in hosted environments; secrets only in local untracked files or managed secret stores, never in docs/prompts/Git.
- Rate limiting, input constraints, safe CORS, CSRF protection for cookie-authenticated state-changing routes, secure cookie flags, logout/session invalidation.
- Limit OAuth callback redirects and webhook origins; validate Graph webhook clientState and endpoint token handshake; authenticate Google Pub/Sub push/subscription messages when using push.
- Webhook duplicate delivery is normal: dedup by `(provider, connection_id, provider_message_id)` and store sync cursor atomically.
- Separate development/test/production projects and secrets; audit dependencies, CI secret scanning and vulnerability advisories.

## 7. Testing / review before any live mailbox

- [ ] App auth and user/role/organization authorization tested, including denied cross-tenant access.
- [ ] OAuth CSRF/redirect validation, token encryption and revoke/reconnect tested.
- [ ] No raw tokens/PII in logs, traces, exception reports or frontend payloads.
- [ ] Mocked email injection and LLM prompt injection tests pass.
- [ ] API cannot send if draft not approved, has changed, or if caller lacks permission.
- [ ] Retry/dedup and sync recovery tested; safe handling of provider rate limits.
- [ ] User has explicitly authorized test accounts and understands what is synced.

For public commercial release, complete threat modeling, relevant GDPR/DPA/retention work, Google scope/verification obligations, pen-testing or equivalent risk-based assessment, and privacy notices.

## Official references

- Gmail scope classification: https://developers.google.com/workspace/gmail/api/auth/scopes
- Google OAuth verification and restricted scope considerations: https://support.google.com/cloud/answer/13464325
- Microsoft Graph permissions: https://learn.microsoft.com/en-us/graph/permissions-reference
- Microsoft change notification webhooks: https://learn.microsoft.com/en-us/graph/change-notifications-delivery-webhooks
- Supabase RLS: https://supabase.com/docs/guides/database/postgres/row-level-security
- OWASP LLM Top 10: https://genai.owasp.org/llm-top-10/
