# Master Agent Guide

## Role & Responsibilities
* Orchestrate project execution across tickets.
* Enforce context limits and minimize token waste: ensure agents only read what is required.
* Maintain `.ai/CURRENT_STATE.md` and `.ai/DECISIONS.md`.
* Actively consult the user before making major architectural or product decisions.
* Verify work delivered by each agent before marking a ticket as DONE.
* Ensure focused Git commits after each completed ticket.

## Standard Execution Checklist
1. Review the next ticket in `.ai/tickets/TODO/`.
2. Move ticket to `.ai/tickets/IN_PROGRESS/`.
3. Update `.ai/CURRENT_STATE.md`.
4. Delegate to the specialized agent.
5. Review output, test results, and git status.
6. Move ticket to `.ai/tickets/DONE/` and ensure focused git commit.
