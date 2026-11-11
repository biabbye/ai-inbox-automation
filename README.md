# SupportFlow AI — project playbook for Claude Code & Codex

> Status: **documentation and learning plan only**. No application code or real integrations have been implemented. Updated: 2026-11-10.

## The goal

Build, **step by step**, a production-ready AI-powered customer-support inbox automation system. A company connects a **Gmail or Outlook** inbox, authorized users log in to a secure **Next.js** dashboard, and a **Python/FastAPI** pipeline classifies inbound messages, retrieves relevant company knowledge, creates support tickets, and proposes replies. **A human approves sending**. We start as a safe, single-organization local pilot, and later harden the design for multiple organizations.

**This is a learning project, not a request for an AI agent to build the complete application on its own.** The human developer writes and understands the code. Claude and Codex act as senior pair programmers and teachers.

## Put these files at the root of your repository

- `CLAUDE.md` — Claude Code's persistent project entry point.
- `AGENTS.md` — Codex's persistent repository instructions.
- `docs/LEARNING_CONTRACT.md` — **mandatory** teaching and collaboration protocol.
- `docs/PROJECT_OBJECTIVE.md` — product vision, scope, non-goals.
- `docs/ARCHITECTURE.md` — target architecture and boundaries.
- `docs/SECURITY.md` — security threats and safeguards.
- `docs/EMAIL_INTEGRATIONS.md` — Gmail/Outlook APIs, OAuth, sync and send.
- `docs/ROADMAP.md` — learning milestones with exit criteria.
- `docs/ENGINEERING_STANDARDS.md` — coding, testing and operations conventions.
- `docs/TESTING_AND_EVALUATION.md` — test strategy and AI quality gates.
- `docs/PRODUCTION_READINESS.md` — release gate checklist.
- `docs/DECISIONS.md` — architecture decision register, open choices.
- `docs/PROGRESS.md` — explicitly maintained session-to-session handoff.
- `docs/STARTER_PROMPTS.md` — copy-paste prompts for tutoring sessions.

## First session

Open the directory in VS Code. Start Claude Code or Codex **from the repository root**. Send:

> Read `CLAUDE.md` or `AGENTS.md` and the documents they reference. You are my AI Engineering study partner. Do not write application code yet. Give me a short learning map for milestone M0 in `docs/ROADMAP.md`, explain the first choice, and propose **only the first exercise**. Wait for my answer before moving on.

The assistant must respond **in Romanian**, leaving names of APIs, code, paths and technical concepts in English. Keep lessons actionable, with a short theory section, a hands-on step, a way to verify it, and a comprehension check. Never advance automatically.


## Local prerequisites (M0)

Before M1, install and verify:

- Python 3.12, invoked as `py -3.12`
- `uv`
- Node.js
- Git
- Docker Desktop with the WSL 2 backend

Verification commands:

```powershell
py -3.12 --version
uv --version
node --version
git --version
docker version

## Operating rules

1. Before a change, read the relevant docs and `docs/PROGRESS.md`.
2. One focused exercise or small change per turn; make the user do the essential work.
3. Never call a codebase or deployment "production-ready" solely because it runs locally.
4. Do not use real customer mail or production credentials until security prerequisites are in place.
5. Update `docs/PROGRESS.md` only when the user reports or verification actually shows progress; don't fabricate completion.
6. When documentation conflicts, stop and propose a small ADR in `docs/DECISIONS.md`.

## Suggested learning order

Python/FastAPI -> local Postgres & data model -> app auth -> AI classification -> knowledge retrieval -> Outlook connector -> Gmail connector -> approvals/send -> background processing -> security/evals/observability -> deployment.

## Source material

The citations and official references used to design the email and auth integrations are in `docs/EMAIL_INTEGRATIONS.md`, `docs/SECURITY.md`, and `docs/ARCHITECTURE.md`. APIs, provider policies and SDK versions can change: check official docs again *when implementing*.
