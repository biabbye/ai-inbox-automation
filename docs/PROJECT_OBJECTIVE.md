# Project objective, scope and success criteria

## Product mission

**SupportFlow AI** (working name) is a support inbox automation application for small businesses, extensible to corporate teams. It ingests **authorized Gmail and Outlook** messages, classifies and summarizes them, creates and routes tickets, looks up relevant company knowledge, drafts reliable answers, and lets a human reviewer approve/edit/reject before an answer is sent. A secure web dashboard lets authorized staff view and manage work.

## Target user journeys

**Company admin** signs up / signs in, creates or joins an organization, connects an authorized mailbox using OAuth, configures support categories, knowledge sources and assigned staff, then sees health/sync state.

**Support agent** signs into the dashboard, sees incoming tickets, priority and classification evidence, inspects cited knowledge, edits a drafted reply, approves sending via the correct mailbox, and sees delivery status/audit history.

**Customer** sends an ordinary email to the company's mailbox and receives a reviewed, relevant reply in the same conversation/thread. They do not need to know the AI service exists, though transparency/disclosure and privacy notices are company policy choices to handle appropriately.

## Outcomes that define the final product

1. Gmail **and** Outlook mailbox connections via supported APIs and delegated OAuth, reconnect/revoke, sync and send.
2. Secure Next.js dashboard with real user authentication, organizational roles, server-side authorization, protected APIs, ticket workflow and activity history.
3. Python/FastAPI ingestion, Pydantic schemas, classification, RAG on approved knowledge, confidence/uncertainty handling, draft replies and human approval.
4. Provider-independent mail abstraction; durable background processing; deduplication; mailbox/thread association; retries; failure recovery.
5. Tests, AI evaluations, observability, alerting, retention/deletion, documented security controls, CI/CD and reproducible deployment.
6. A portfolio demo with synthetic messages, architecture docs, a demo video/screen recording and metrics measured on an explicitly labelled test set.

## Milestones vs final vision

- **Learning prototype (M0-M3):** local, synthetic messages; basic database and AI behavior; *not safe for live customer mail*.
- **Connected pilot (M4-M7):** real Gmail/Outlook accounts owned/authorized by developer or a test organization, limited sync, secure token handling, explicit human approval before send.
- **Production candidate (M8-M10):** authentication/authorization, multi-tenant controls, webhook reliability, operational controls, security testing, GDPR/privacy work and release review.

Roadmap milestones are learning gates, **not a promise of number of weeks**. Scope is adjusted only with the learner.

## Explicit non-goals for the initial version

- No autonomous refunds, account resets, arbitrary tool execution, deletion of customer emails, or AI-initiated outbound marketing.
- No automatic send without an authorized human's explicit review and action.
- No voice channel, WhatsApp, Zendesk, Shopify, billing engine or no-code workflow editor in v1.
- No multi-agent swarm: start with straightforward functions and introduce LangGraph only when stateful workflow needs justify it.
- Do not create a universal SaaS platform before proving the end-to-end workflow.

## Demonstrable acceptance scenarios

- A synthetic refund request creates one ticket, category `refund`, requires human review, and includes a grounded draft or explicit insufficient-information state.
- The same inbound provider message delivered twice creates only one ticket.
- A dashboard user cannot read another organization's ticket or use that organization's mailbox connection.
- An unapproved draft cannot reach a provider send endpoint, even if an API is called directly.
- Expired OAuth permissions produce a visible reconnect state, not silent message loss.
- Gmail and Outlook work through the same normalized ticket pipeline; provider-specific send maintains proper thread relationships.
- Disconnected/revoked mailboxes stop background sync; audit history remains according to retention policy.

## What the learner should be able to explain at the end

How an OAuth authorization flow differs from app authentication; how inbound mail becomes a ticket; how Pydantic protects boundaries (but does not make model output trustworthy); why RAG can fail; why queues, idempotency and audit are necessary; how to constrain an AI model from sending emails; how to demonstrate data isolation and evaluate quality.
