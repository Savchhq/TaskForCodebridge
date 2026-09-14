# .ai Context & Governance

This directory is the single source of truth for all AI agents working on this project.

## Workflow & Decision Protocol

All significant decisions require human approval:
`USER -> MASTER (Proposal & Questions) -> USER APPROVAL -> TICKET -> SPECIALIZED AGENT (in its chat) -> IMPLEMENTATION -> MASTER REVIEW -> USER`

* The Master Agent coordinates and reviews; it is NOT the implementation agent.
* Specialized agents execute assigned tickets in separate chats and stop on blockers.

## Directory Structure

* `PROJECT_CONTEXT.md` - High-level goals, inputs, outputs, core constraints.
* `ARCHITECTURE.md` - System architecture, data flow, component boundaries.
* `DECISIONS.md` - Log of approved technical and product decisions.
* `CURRENT_STATE.md` - Real-time snapshot of what is built, active ticket, and next steps.
* `agents/` - Operational rules for each agent role (`master.md`, `architect.md`, `backend.md`, `frontend.md`, `ai.md`, `qa.md`).
* `tickets/` - Work tickets divided into `TODO/`, `IN_PROGRESS/`, and `DONE/`.
* `knowledge/` - Domain knowledge (`requirements.md`, `testing.md`, `ai-models.md`).

## Context Optimization Rules

To preserve tokens and prevent hallucination:
1. Every agent must read **only** the minimum required files before executing work:
   * `.ai/PROJECT_CONTEXT.md`
   * `.ai/CURRENT_STATE.md`
   * Its own `.ai/agents/<agent>.md`
   * The specific ticket in `.ai/tickets/`
   * Only the directly relevant section of `ARCHITECTURE.md` / `DECISIONS.md`.
2. Do **not** reread or dump the entire project into agent context.
3. Update existing documents in place instead of creating duplicate notes.
4. Keep documentation concise, accurate, and up-to-date.
