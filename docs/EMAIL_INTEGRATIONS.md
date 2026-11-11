# Gmail and Outlook integrations — provider-specific playbook

> Date reviewed: 2026-11-10. Treat API details, scopes, quotas and provider review requirements as living policies and re-check official references when implementing.

## Objective

A company admin connects **either Gmail or Outlook (eventually both)** to an organization. Our Python backend synchronizes eligible incoming support messages, normalizes data, creates a ticket and drafts an answer. A human reviews and initiates sending from the connected mailbox, in the original conversation where supported. The AI model never sees OAuth secrets and does not call provider send APIs directly.

## Separate connections from dashboard sign-in

Supabase Auth identifies dashboard users. Google/Microsoft **delegated OAuth** grants permission to a particular mailbox. Store connection ownership by organization, a sanitized provider mailbox ID and encrypted credentials on the server. Never share account access tokens with frontend JavaScript. A company admin may need their Microsoft tenant administrator to authorize the integration.

## Shared interface (conceptual, NOT an instruction to generate code now)

```python
class MailProvider(Protocol):
    async def list_changes(self, connection: MailboxConnection) -> list[EmailEvent]: ...
    async def fetch_message(self, connection: MailboxConnection, message_id: str) -> SupportEmail: ...
    async def send_reply(self, connection: MailboxConnection, approved: ApprovedReply) -> SendResult: ...
```

Normalized `SupportEmail`: `connection_id`, `provider`, `provider_message_id`, `provider_thread_id`, `from_address`, `to_addresses`, `subject`, `plain_text_body`, `received_at`, `attachments_metadata`. Organization ID must come from trusted connection lookup, never from inbound text. Do not implement this whole interface until the relevant learning task.

## Gmail integration

- Google Cloud project + Gmail API + OAuth consent screen + user/test configuration.
- OAuth 2.0 authorization code flow with state and appropriate callback security; ask for restricted `gmail.readonly` only when message body is necessary. For initial read-only learning, don't request send scope.
- Initial sync with `users.messages.list` and `users.messages.get`, bounded to messages that meet support inbox criteria. Incremental sync later with `users.history.list` and a persisted history ID. On expired/invalid history cursor (e.g. 404), perform bounded resync.
- Later: Gmail `watch` uses **Cloud Pub/Sub** and must be renewed within 7 days (daily renewal recommended). Push notification is a signal to fetch changes; it isn't itself the entire message.
- Send a reply via Gmail API with the minimum necessary send permission, preserving RFC message reply headers and Gmail thread semantics. Handle the possibility that outgoing messages are also seen during sync.
- Important product gate: `gmail.readonly` is a **restricted** Google scope; `gmail.send` is **sensitive**. Public app verification and possibly a third-party security assessment for server-side restricted-scope data may apply; design for this cost early.

## Outlook integration

- Register an app in Microsoft Entra, choose supported account types deliberately (work/school vs personal Microsoft accounts), configure redirect URIs and delegated permissions.
- `Mail.Read` (delegated) reads mailbox content; `Mail.Send` sends as the signed-in user. Request only needed scopes; `offline_access` may be required for refresh tokens, subject to account policy. Avoid application-wide Mail.Read unless a separate reviewed enterprise design requires it.
- Initial bounded sync using Microsoft Graph mailbox/messages APIs; for durable incremental sync, use **message delta query** and persist the opaque `@odata.deltaLink`. Delta is per-folder and supports pagination.
- Later: Graph change notifications -> HTTPS endpoint, validation token response, `clientState` check, subscription renewal/lifecycle handling; still use fetch/delta for reliable reconciliation.
- Use Graph reply mechanics appropriate to the original conversation (not naive standalone send); validate source mailbox, target recipients and approved draft version.

## Processing semantics shared by both

1. Sync process obtains eligible provider message IDs (not entire inbox by default).
2. Verify connection is active and corresponds to the correct organization.
3. Dedup uniquely on provider + connection + stable provider message ID.
4. Parse text safely; ignore outbound self-sent messages, bounces and auto-replies; prohibit untrusted HTML rendering.
5. Create/advance ticket. LLM classifies and drafts with provenance.
6. Operator reviews/edits/approves; backend policy checks all state transitions.
7. Send via originating connector; record provider response and audit; retry transient errors with careful idempotency/reconciliation.

**Edge cases to test:** OAuth revoked, missing refresh token, rate limits/429, 5xx, duplicate webhook, deleted email, reply chain, multiple mailboxes, forwarded email, HTML-only body, large attachments, multilingual content and webhook notifications that arrive out of order.

## Local development sequence

A. Fake provider / fixture JSON -> stable local pipeline (never contact an inbox).
B. One dedicated developer-owned Outlook test mailbox, OAuth and **read-only polling**; no external webhook necessary yet.
C. A developer-owned Gmail test mailbox with bounded read-only sync.
D. After authorization, approval and audit tests: add sending with an explicit operator click and test recipients.
E. Push/webhooks and durable worker after reliable polling baseline; Google Pub/Sub and Graph callbacks require suitable public infrastructure, HTTPS, verification and renewal.

Do not use personal or corporate mailboxes without authorization. Avoid fetching non-test messages as a convenience.

## Official references

- Gmail API scopes: https://developers.google.com/workspace/gmail/api/auth/scopes
- Gmail synchronization: https://developers.google.com/workspace/gmail/api/guides/sync
- Gmail push notifications: https://developers.google.com/workspace/gmail/api/guides/push
- Gmail sending messages: https://developers.google.com/workspace/gmail/api/guides/sending
- Microsoft Graph permissions: https://learn.microsoft.com/en-us/graph/permissions-reference
- Graph message delta query: https://learn.microsoft.com/en-us/graph/delta-query-messages
- Graph change notifications: https://learn.microsoft.com/en-us/graph/change-notifications-delivery-webhooks
- Graph subscriptions: https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions?view=graph-rest-1.0
