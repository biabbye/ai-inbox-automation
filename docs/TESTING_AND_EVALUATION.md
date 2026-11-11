# Testing and AI evaluation strategy

## Aim

A good demo can still be unsafe; our tests should demonstrate **correctness, isolation, non-sending defaults and recovery**. Deterministic features are tested with code. LLM behavior is evaluated with versioned fixtures and measurable criteria. No live mailbox tests in the default CI pipeline.

## Testing pyramid

- **Unit:** Pydantic validation, priority rules, message parsers, ticket state machine, approval checks, dedup key generation.
- **Contract:** provider-neutral Gmail/Outlook fixtures; normalized messages match the same shape; mock send replies preserve conversation metadata.
- **Integration:** FastAPI + test database, migrations, organization membership, durable processing and approval state transitions.
- **End-to-end (local):** synthetic message -> ticket -> RAG draft -> dashboard review -> mocked send result.
- **Optional live sandbox:** dedicated test mailboxes, explicit opt-in, limited messages, no real customer data; never default CI.

## Initial AI evaluation set

Create 30-50 synthetic messages spanning: refunds, late deliveries, billing, technical problems, ambiguous requests, unsupported requests, empty body, angry tone, multilingual examples, malicious prompt injection and sensitive information. For each fixture, record category, priority policy, desired escalation, expected knowledge reference (if any), and forbidden actions.

Evaluate at least:

1. Classification accuracy per category and confusion matrix on labelled examples.
2. Critical-misrouting rate (especially refunds/security escalations).
3. Evidence grounding: source exists, belongs to correct organization, and supports the drafted answer.
4. Abstention/escalation on missing policy and contradictory retrieved documents.
5. JSON schema validity and recovery when the provider errors or times out.
6. Prompt-injection resistance: embedded "ignore instructions" never reaches action layer.
7. Latency and model cost per message (record on a test dataset).

Do not treat a single "accuracy" percentage as proof of real-world performance. Set thresholds after reviewing business risks; require **zero** unauthorized-send events in automated tests.

## Security scenarios

- Client A asks for Client B's tickets via modified URL/request body -> denied.
- Anonymous user invokes approve/send -> denied.
- Valid user from another org invokes send -> denied.
- Draft modified after approval -> old approval cannot send new version.
- Out-of-order/repeated webhook -> one logical inbound message, no double send.
- Provider 429/timeout -> retry or failure visible, no silent lost ticket.
- Inbound mail includes "send confidential data to ..." -> treated as data, not instruction.

## Regression and reports

For each AI model/prompt/index change, rerun labelled fixtures and compare results. Store only privacy-safe fixtures in Git. Version the evaluation dataset and document discovered failures before tuning prompts.

When agent assists, it should propose **one test case for the current milestone**, ask learner to write/run it, then review observed output. Never generate an entire suite without explicit authorization.
