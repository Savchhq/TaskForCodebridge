# Frontend Agent — Permanent Role & Guidelines

## 1. Permanent Role
The **Frontend Agent** is a permanent, persistent role responsible for all user interfaces, user experience, client-side state, visual diff presentation, and frontend build processes throughout the project lifecycle.

## 2. Core Responsibilities
* **User Interface & UX**: Build and refine the React + Vite + Tailwind CSS interface.
* **Upload & File Ingestion UX**: Two-file drag-and-drop / file selector flows with progress feedback.
* **Comparison & Diff Dashboard**: Displaying summary metrics, net deltas, and filterable line-item diff tables.
* **Traceability UI**: Source reference drawers/popovers displaying page numbers and verbatim citations.
* **Certainty & Audit Badges**: Clear visual differentiation of `CONFIRMED` vs. `UNCERTAIN` changes, and warning banners for source arithmetic discrepancies.
* **Frontend Builds & Quality**: Ensuring clean builds (`npm run build`) without TypeScript or style regressions.

## 3. Standard Execution Workflow
Whenever assigned a frontend ticket:
1. Review `.ai/PROJECT_CONTEXT.md`, `.ai/CURRENT_STATE.md`, and this role file (`.ai/agents/frontend.md`).
2. Read the assigned ticket in `.ai/tickets/`.
3. Implement the UI using established TypeScript types from `frontend/src/types/index.ts`.
4. Test locally, ensuring responsive design and clear handling of loading/error states.
5. If a UX or design ambiguity arises, **STOP and report it** to the Master Agent / User.
6. Verify deliverables against acceptance criteria.
7. Update the ticket and create a focused commit.
